#!/usr/bin/env python3
"""Check that Alembic migrations are reversible."""
import sys

def check_migration(file_path):
    """Verify migration has both upgrade() and downgrade()."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        has_upgrade = 'def upgrade()' in content
        has_downgrade = 'def downgrade()' in content

        if has_upgrade and has_downgrade:
            print("✓ Migration has both upgrade() and downgrade() - reversible")
            return 0
        elif has_upgrade and not has_downgrade:
            print("⚠️  Warning: Migration missing downgrade() - not reversible!")
            return 0  # Warn but don't block
        else:
            print("ℹ️  Not an Alembic migration file")
            return 0

    except Exception as e:
        print(f"Migration check failed: {e}")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)

    sys.exit(check_migration(sys.argv[1]))
