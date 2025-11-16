"""
SQLite to PostgreSQL Data Migration Script

Migrates all data from SQLite database to PostgreSQL database.
Handles all tables including samples, batches, user_preferences, api_usage, etc.

Usage:
    python scripts/migrate_sqlite_to_postgres.py [--dry-run] [--batch-size SIZE]

Environment Variables Required:
    SQLITE_DB_PATH: Path to SQLite database (default: ./sp404_samples.db)
    DATABASE_URL: PostgreSQL connection string (from .env)
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, MetaData, Table, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table as RichTable
from rich.panel import Panel

console = Console()


class DatabaseMigrator:
    """Migrates data from SQLite to PostgreSQL"""

    def __init__(self, sqlite_path: str, postgres_url: str, batch_size: int = 100):
        """
        Initialize migrator.

        Args:
            sqlite_path: Path to SQLite database file
            postgres_url: PostgreSQL connection URL
            batch_size: Number of rows to migrate per batch
        """
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.batch_size = batch_size

        # Create engines
        self.sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
        # Convert async URL to sync for migration
        pg_sync_url = postgres_url.replace("+asyncpg", "")
        self.postgres_engine = create_engine(pg_sync_url)

        self.metadata = MetaData()
        self.stats = {
            "tables_migrated": 0,
            "rows_migrated": 0,
            "errors": []
        }

    def get_table_names(self) -> List[str]:
        """Get list of tables from SQLite database (excluding alembic)."""
        inspector = inspect(self.sqlite_engine)
        tables = inspector.get_table_names()
        # Exclude Alembic version table
        return [t for t in tables if t != "alembic_version"]

    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table in SQLite."""
        with self.sqlite_engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()

    def read_table_data(self, table_name: str, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Read data from SQLite table in batches.

        Args:
            table_name: Name of table to read
            offset: Starting row offset
            limit: Number of rows to read

        Returns:
            List of row dictionaries
        """
        table = Table(table_name, self.metadata, autoload_with=self.sqlite_engine)

        with self.sqlite_engine.connect() as conn:
            query = table.select().offset(offset).limit(limit)
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]

    def write_table_data(self, table_name: str, rows: List[Dict[str, Any]]) -> int:
        """
        Write data to PostgreSQL table.

        Args:
            table_name: Name of table to write
            rows: List of row dictionaries

        Returns:
            Number of rows written
        """
        if not rows:
            return 0

        table = Table(table_name, self.metadata, autoload_with=self.postgres_engine)

        with self.postgres_engine.connect() as conn:
            # Use bulk insert for better performance
            conn.execute(table.insert(), rows)
            conn.commit()
            return len(rows)

    def clear_table(self, table_name: str):
        """Clear all data from PostgreSQL table (for fresh migration)."""
        with self.postgres_engine.connect() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            conn.commit()

    def migrate_table(self, table_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate a single table from SQLite to PostgreSQL.

        Args:
            table_name: Name of table to migrate
            dry_run: If True, only count rows without writing

        Returns:
            Migration statistics for the table
        """
        total_rows = self.get_table_row_count(table_name)

        if total_rows == 0:
            console.print(f"  [yellow]Table '{table_name}' is empty, skipping[/yellow]")
            return {"table": table_name, "rows": 0, "status": "skipped"}

        console.print(f"\n[bold blue]Migrating table: {table_name}[/bold blue]")
        console.print(f"  Total rows: {total_rows}")

        if dry_run:
            console.print(f"  [yellow]DRY RUN: Would migrate {total_rows} rows[/yellow]")
            return {"table": table_name, "rows": total_rows, "status": "dry_run"}

        # Clear existing data in PostgreSQL
        console.print(f"  Clearing existing data in PostgreSQL...")
        self.clear_table(table_name)

        # Migrate in batches
        migrated_rows = 0
        errors = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"  Migrating {table_name}...", total=total_rows)

            offset = 0
            while offset < total_rows:
                try:
                    # Read batch from SQLite
                    rows = self.read_table_data(table_name, offset, self.batch_size)

                    if not rows:
                        break

                    # Write batch to PostgreSQL
                    written = self.write_table_data(table_name, rows)
                    migrated_rows += written
                    offset += self.batch_size

                    progress.update(task, advance=written)

                except Exception as e:
                    error_msg = f"Error migrating batch at offset {offset}: {str(e)}"
                    errors.append(error_msg)
                    console.print(f"  [red]{error_msg}[/red]")
                    offset += self.batch_size  # Skip failed batch

        status = "success" if migrated_rows == total_rows else "partial"
        console.print(f"  [green]✓ Migrated {migrated_rows}/{total_rows} rows[/green]")

        return {
            "table": table_name,
            "rows": migrated_rows,
            "total": total_rows,
            "status": status,
            "errors": errors
        }

    def verify_migration(self) -> Dict[str, int]:
        """
        Verify row counts match between SQLite and PostgreSQL.

        Returns:
            Dictionary of table names to count mismatches
        """
        console.print("\n[bold yellow]Verifying Migration...[/bold yellow]")

        mismatches = {}
        tables = self.get_table_names()

        for table_name in tables:
            # Count in SQLite
            sqlite_count = self.get_table_row_count(table_name)

            # Count in PostgreSQL
            with self.postgres_engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                postgres_count = result.scalar()

            if sqlite_count != postgres_count:
                mismatches[table_name] = {
                    "sqlite": sqlite_count,
                    "postgres": postgres_count,
                    "diff": sqlite_count - postgres_count
                }
                console.print(f"  [red]✗ {table_name}: SQLite={sqlite_count}, PostgreSQL={postgres_count}[/red]")
            else:
                console.print(f"  [green]✓ {table_name}: {sqlite_count} rows match[/green]")

        return mismatches

    def run_migration(self, dry_run: bool = False) -> bool:
        """
        Run full database migration.

        Args:
            dry_run: If True, only simulate migration without writing

        Returns:
            True if migration successful, False otherwise
        """
        console.print(Panel.fit(
            f"[bold]SQLite to PostgreSQL Migration[/bold]\n\n"
            f"Source: {self.sqlite_path}\n"
            f"Target: PostgreSQL (via DATABASE_URL)\n"
            f"Batch Size: {self.batch_size}\n"
            f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}",
            border_style="blue"
        ))

        # Get table list
        tables = self.get_table_names()
        console.print(f"\n[bold]Found {len(tables)} tables to migrate:[/bold]")
        for table in tables:
            count = self.get_table_row_count(table)
            console.print(f"  - {table}: {count} rows")

        if dry_run:
            console.print("\n[yellow]DRY RUN MODE: No data will be written[/yellow]")

        # Confirm before proceeding
        if not dry_run:
            console.print("\n[bold red]WARNING: This will clear all existing data in PostgreSQL![/bold red]")
            confirm = console.input("[bold]Continue? (yes/no): [/bold]")
            if confirm.lower() != "yes":
                console.print("[yellow]Migration cancelled[/yellow]")
                return False

        # Migrate each table
        start_time = datetime.now()
        results = []

        for table_name in tables:
            try:
                result = self.migrate_table(table_name, dry_run)
                results.append(result)
                self.stats["tables_migrated"] += 1
                self.stats["rows_migrated"] += result.get("rows", 0)

            except Exception as e:
                error_msg = f"Failed to migrate table '{table_name}': {str(e)}"
                self.stats["errors"].append(error_msg)
                console.print(f"[red]{error_msg}[/red]")
                results.append({"table": table_name, "status": "failed", "error": str(e)})

        # Verify migration (if not dry run)
        mismatches = {}
        if not dry_run:
            mismatches = self.verify_migration()

        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary_table = RichTable(title="Migration Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Tables Migrated", str(self.stats["tables_migrated"]))
        summary_table.add_row("Total Rows Migrated", str(self.stats["rows_migrated"]))
        summary_table.add_row("Duration", f"{duration:.2f} seconds")
        summary_table.add_row("Errors", str(len(self.stats["errors"])))
        summary_table.add_row("Verification Mismatches", str(len(mismatches)))

        console.print("\n")
        console.print(summary_table)

        # Print errors if any
        if self.stats["errors"]:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in self.stats["errors"]:
                console.print(f"  [red]- {error}[/red]")

        # Success if no errors and no mismatches
        success = len(self.stats["errors"]) == 0 and len(mismatches) == 0

        if success:
            console.print("\n[bold green]✓ Migration completed successfully![/bold green]")
        else:
            console.print("\n[bold red]✗ Migration completed with errors[/bold red]")

        return success


def main():
    """Main migration script entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate SQLite database to PostgreSQL")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without writing data")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for migration (default: 100)")
    parser.add_argument("--sqlite-db", type=str, help="Path to SQLite database (default: from env or ./sp404_samples.db)")
    args = parser.parse_args()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Get database paths
    sqlite_path = args.sqlite_db or os.getenv("SQLITE_DB_PATH", "./sp404_samples.db")
    postgres_url = os.getenv("DATABASE_URL")

    if not postgres_url:
        console.print("[red]Error: DATABASE_URL environment variable not set[/red]")
        console.print("Please set DATABASE_URL in your .env file with PostgreSQL connection string")
        return 1

    if not Path(sqlite_path).exists():
        console.print(f"[red]Error: SQLite database not found at {sqlite_path}[/red]")
        return 1

    # Run migration
    migrator = DatabaseMigrator(sqlite_path, postgres_url, args.batch_size)

    try:
        success = migrator.run_migration(dry_run=args.dry_run)
        return 0 if success else 1

    except KeyboardInterrupt:
        console.print("\n[yellow]Migration cancelled by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
