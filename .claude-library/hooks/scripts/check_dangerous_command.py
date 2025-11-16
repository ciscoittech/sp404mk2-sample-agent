#!/usr/bin/env python3
"""Block dangerous bash commands."""
import sys
import re

DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/',
    r'rm\s+-rf\s+~',
    r'rm\s+-rf\s+\.',
    r'rm\s+-rf\s+\*',
    r'chmod\s+-R\s+777',
    r'dd\s+if=',
    r'mkfs\.',
    r'format\s+',
    r'>\s*/dev/sd',
]

def check_command(command):
    """Check if command matches dangerous patterns."""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"\\n🛑 BLOCKED: Dangerous command detected!")
            print(f"Pattern: {pattern}")
            print(f"Command: {command}")
            print("\\nIf you really need to run this, use Bash tool with confirmation.")
            return 1

    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)

    sys.exit(check_command(sys.argv[1]))
