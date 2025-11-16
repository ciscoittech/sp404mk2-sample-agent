#!/usr/bin/env python3
"""
Batch Queue Manager - State Management for Automated Sample Processing

Manages the queue of directories to process and tracks automation state.
Used by automated_batch_runner.sh for coordinating processing runs.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class QueueItem:
    """Represents a directory in the processing queue"""
    directory: str
    priority: int = 10
    max_samples: Optional[int] = None
    status: str = "pending"  # pending, processing, completed, failed
    attempts: int = 0
    last_attempt: Optional[str] = None
    samples_processed: int = 0
    error_message: Optional[str] = None


@dataclass
class AutomationState:
    """Current state of the automation system"""
    last_run: Optional[str] = None
    total_runs: int = 0
    total_samples_processed: int = 0
    queue: List[Dict] = None

    def __post_init__(self):
        if self.queue is None:
            self.queue = []


class BatchQueueManager:
    """Manages batch processing queue and automation state"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        self.project_root = Path(self.config["project_root"])
        self.state_file = self.project_root / self.config["state_file"]
        self.db_path = self.project_root / self.config["database_path"]

        self.state = self._load_state()

    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        with open(self.config_path) as f:
            return json.load(f)

    def _load_state(self) -> AutomationState:
        """Load automation state from file"""
        if not self.state_file.exists():
            return AutomationState()

        try:
            with open(self.state_file) as f:
                data = json.load(f)
                return AutomationState(**data)
        except Exception as e:
            print(f"Warning: Could not load state file: {e}")
            return AutomationState()

    def _save_state(self):
        """Save automation state to file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, 'w') as f:
            json.dump(asdict(self.state), f, indent=2)

    def initialize_queue(self):
        """Initialize queue from config if empty"""
        if not self.state.queue:
            for directory in self.config["directories"]["queue"]:
                item = QueueItem(
                    directory=directory,
                    max_samples=self.config["processing"]["max_samples_per_run"]
                )
                self.state.queue.append(asdict(item))

            self._save_state()
            print(f"Initialized queue with {len(self.state.queue)} directories")

    def get_next_pending(self) -> Optional[QueueItem]:
        """Get next pending directory to process"""
        for item_dict in self.state.queue:
            if item_dict["status"] == "pending":
                return QueueItem(**item_dict)

        return None

    def mark_processing(self, directory: str):
        """Mark directory as currently processing"""
        for item in self.state.queue:
            if item["directory"] == directory:
                item["status"] = "processing"
                item["last_attempt"] = datetime.now().isoformat()
                item["attempts"] += 1
                break

        self._save_state()

    def mark_completed(self, directory: str, samples_processed: int):
        """Mark directory as completed"""
        for item in self.state.queue:
            if item["directory"] == directory:
                item["status"] = "completed"
                item["samples_processed"] = samples_processed
                break

        self.state.total_samples_processed += samples_processed
        self._save_state()

    def mark_failed(self, directory: str, error_message: str):
        """Mark directory as failed"""
        for item in self.state.queue:
            if item["directory"] == directory:
                item["status"] = "failed"
                item["error_message"] = error_message
                break

        self._save_state()

    def record_run(self):
        """Record a successful automation run"""
        self.state.last_run = datetime.now().isoformat()
        self.state.total_runs += 1
        self._save_state()

    def get_database_stats(self) -> Dict:
        """Get statistics from the database"""
        if not self.db_path.exists():
            return {"total_samples": 0, "error": "Database not found"}

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM samples")
            total_samples = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM samples WHERE created_at > datetime('now', '-24 hours')")
            recent_samples = cursor.fetchone()[0]

            conn.close()

            return {
                "total_samples": total_samples,
                "samples_last_24h": recent_samples
            }
        except Exception as e:
            return {"total_samples": 0, "error": str(e)}

    def get_status_summary(self) -> Dict:
        """Get summary of current queue status"""
        status_counts = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }

        for item in self.state.queue:
            status_counts[item["status"]] += 1

        db_stats = self.get_database_stats()

        return {
            "queue": status_counts,
            "automation": {
                "total_runs": self.state.total_runs,
                "last_run": self.state.last_run,
                "samples_processed": self.state.total_samples_processed
            },
            "database": db_stats
        }

    def reset_failed(self):
        """Reset all failed items back to pending"""
        count = 0
        for item in self.state.queue:
            if item["status"] == "failed":
                item["status"] = "pending"
                item["error_message"] = None
                count += 1

        if count > 0:
            self._save_state()
            print(f"Reset {count} failed items to pending")

    def add_directory(self, directory: str, priority: int = 10):
        """Add a new directory to the queue"""
        item = QueueItem(
            directory=directory,
            priority=priority,
            max_samples=self.config["processing"]["max_samples_per_run"]
        )

        self.state.queue.append(asdict(item))
        self._save_state()
        print(f"Added {directory} to queue")


def main():
    """CLI interface for queue management"""
    import argparse

    parser = argparse.ArgumentParser(description="Batch Queue Manager")
    parser.add_argument("--config", default="scripts/batch_automation/config.json",
                       help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Init command
    subparsers.add_parser("init", help="Initialize queue from config")

    # Status command
    subparsers.add_parser("status", help="Show queue status")

    # Next command
    subparsers.add_parser("next", help="Get next pending directory")

    # Mark commands
    mark_parser = subparsers.add_parser("mark", help="Mark directory status")
    mark_parser.add_argument("status", choices=["processing", "completed", "failed"])
    mark_parser.add_argument("directory")
    mark_parser.add_argument("--samples", type=int, default=0)
    mark_parser.add_argument("--error", default="")

    # Reset failed
    subparsers.add_parser("reset-failed", help="Reset failed items to pending")

    # Add directory
    add_parser = subparsers.add_parser("add", help="Add directory to queue")
    add_parser.add_argument("directory")
    add_parser.add_argument("--priority", type=int, default=10)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load manager
    manager = BatchQueueManager(args.config)

    # Execute command
    if args.command == "init":
        manager.initialize_queue()

    elif args.command == "status":
        summary = manager.get_status_summary()
        print(json.dumps(summary, indent=2))

    elif args.command == "next":
        next_item = manager.get_next_pending()
        if next_item:
            print(next_item.directory)
        else:
            print("No pending items", file=sys.stderr)
            return 1

    elif args.command == "mark":
        if args.status == "processing":
            manager.mark_processing(args.directory)
        elif args.status == "completed":
            manager.mark_completed(args.directory, args.samples)
        elif args.status == "failed":
            manager.mark_failed(args.directory, args.error)

        print(f"Marked {args.directory} as {args.status}")

    elif args.command == "reset-failed":
        manager.reset_failed()

    elif args.command == "add":
        manager.add_directory(args.directory, args.priority)

    return 0


if __name__ == "__main__":
    sys.exit(main())
