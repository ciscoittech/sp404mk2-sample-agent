"""
CLI Output Validation Utilities

Validates CLI command outputs, parses Rich table formatting,
and checks for expected patterns in logs.

All validation uses real CLI output - no mocks.
"""

import re
import subprocess
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class CLIOutputValidator:
    """Validates CLI output against expected patterns."""

    @staticmethod
    def validate_output(
        command: List[str],
        expected_patterns: List[str],
        timeout_seconds: int = 30,
        user_input: Optional[str] = None
    ) -> Dict:
        """
        Run CLI command and validate output patterns.

        Args:
            command: Command to run (e.g., ['python', 'sp404_chat.py'])
            expected_patterns: List of regex patterns that should appear in output
            timeout_seconds: Command timeout
            user_input: Input to send to stdin (optional)

        Returns:
            {
                'success': bool,
                'output': str,
                'matched_patterns': [str],
                'missing_patterns': [str],
                'all_matched': bool,
                'return_code': int,
                'execution_time_seconds': float
            }
        """
        start_time = datetime.now()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                input=user_input
            )

            execution_time = (datetime.now() - start_time).total_seconds()
            output = result.stdout + result.stderr

            matched = []
            missing = []

            for pattern in expected_patterns:
                try:
                    if re.search(pattern, output, re.MULTILINE | re.DOTALL):
                        matched.append(pattern)
                    else:
                        missing.append(pattern)
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{pattern}': {e}")
                    missing.append(pattern)

            return {
                'success': result.returncode == 0,
                'output': output,
                'matched_patterns': matched,
                'missing_patterns': missing,
                'all_matched': len(missing) == 0,
                'return_code': result.returncode,
                'execution_time_seconds': execution_time,
                'command': ' '.join(command)
            }

        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                'success': False,
                'output': '',
                'matched_patterns': [],
                'missing_patterns': expected_patterns,
                'all_matched': False,
                'return_code': -1,
                'execution_time_seconds': execution_time,
                'error': f'Command timeout after {timeout_seconds}s',
                'command': ' '.join(command)
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                'success': False,
                'output': '',
                'matched_patterns': [],
                'missing_patterns': expected_patterns,
                'all_matched': False,
                'return_code': -1,
                'execution_time_seconds': execution_time,
                'error': str(e),
                'command': ' '.join(command)
            }

    @staticmethod
    def validate_cli_help(command: List[str]) -> Dict:
        """
        Validate that a CLI command has help text.

        Args:
            command: Command to check (e.g., ['python', '-m', 'src.cli_download_manager', '--help'])

        Returns:
            {
                'has_help': bool,
                'help_text': str,
                'usage_line': str or None
            }
        """
        result = CLIOutputValidator.validate_output(
            command=command,
            expected_patterns=[r'usage:', r'--help', r'optional arguments'],
            timeout_seconds=5
        )

        # Extract usage line
        usage_match = re.search(r'usage:\s*(.+?)(?:\n|$)', result['output'])
        usage_line = usage_match.group(1) if usage_match else None

        return {
            'has_help': len(result['matched_patterns']) >= 2,
            'help_text': result['output'],
            'usage_line': usage_line
        }


class RichTableParser:
    """Parses Rich library table output."""

    @staticmethod
    def extract_table_rows(output: str) -> List[Dict[str, str]]:
        """
        Extract rows from Rich table output.

        Looks for pattern like:
        ┏━━━━┳━━━━┳━━━━┓
        ┃ ID ┃ Title ┃ Duration ┃
        ┡━━━━╇━━━━╇━━━━┩
        │ 1  │ Sample │ 4.5s │
        │ 2  │ Loop   │ 8.0s │
        └────┴───────┴──────────┘

        Returns:
            List of dicts with column headers as keys
        """
        rows = []

        # Find header line (contains column names between ┃)
        header_pattern = r'┃\s*(.+?)\s*┃(?:.*?\s*┃\s*(.+?)\s*┃)*'
        header_match = re.search(header_pattern, output)

        if not header_match:
            return rows

        # Extract column headers
        headers = re.findall(r'┃\s*([^┃]+?)\s*┃', output.split('\n')[1])

        if not headers:
            return rows

        # Find data rows (between ┡ and ┛)
        data_section = re.search(r'┡.+?┩(.*?)└', output, re.DOTALL)

        if not data_section:
            return rows

        data_lines = data_section.group(1).strip().split('\n')

        for line in data_lines:
            if not line.startswith('│'):
                continue

            cells = re.findall(r'│\s*([^│]+?)\s*│', line)

            if len(cells) == len(headers):
                row = {}
                for header, cell in zip(headers, cells):
                    row[header.strip()] = cell.strip()
                rows.append(row)

        return rows

    @staticmethod
    def validate_table_structure(
        output: str,
        expected_columns: List[str],
        min_rows: int = 1
    ) -> Dict:
        """
        Validate Rich table structure.

        Args:
            output: CLI output containing table
            expected_columns: List of column headers expected
            min_rows: Minimum number of data rows expected

        Returns:
            {
                'valid': bool,
                'has_headers': bool,
                'column_count': int,
                'row_count': int,
                'missing_columns': [str],
                'errors': [str]
            }
        """
        errors = []

        # Check for table borders
        has_borders = all(char in output for char in ['┏', '┃', '┗', '│'])

        if not has_borders:
            errors.append('Missing Rich table borders')

        rows = RichTableParser.extract_table_rows(output)
        row_count = len(rows)

        if row_count < min_rows:
            errors.append(f'Expected >= {min_rows} rows, got {row_count}')

        # Check columns
        columns_in_output = []
        if rows:
            columns_in_output = list(rows[0].keys())

        missing_columns = [
            col for col in expected_columns
            if col not in columns_in_output
        ]

        return {
            'valid': len(errors) == 0,
            'has_borders': has_borders,
            'column_count': len(columns_in_output),
            'row_count': row_count,
            'missing_columns': missing_columns,
            'errors': errors
        }


class LogValidator:
    """Validates log files."""

    @staticmethod
    def validate_log_file(
        log_file: str,
        expected_patterns: List[str],
        follow: bool = False,
        timeout_seconds: int = 30
    ) -> Dict:
        """
        Validate log file contains expected patterns.

        Args:
            log_file: Path to log file
            expected_patterns: Regex patterns expected in log
            follow: If True, wait for patterns in real-time (like tail -f)
            timeout_seconds: Timeout if following

        Returns:
            {
                'valid': bool,
                'matched_patterns': [str],
                'missing_patterns': [str],
                'line_count': int,
                'recent_lines': [str]
            }
        """
        try:
            log_path = Path(log_file)

            if not log_path.exists():
                return {
                    'valid': False,
                    'matched_patterns': [],
                    'missing_patterns': expected_patterns,
                    'error': f'Log file not found: {log_file}',
                    'line_count': 0,
                    'recent_lines': []
                }

            with open(log_path, 'r') as f:
                content = f.read()

            lines = content.split('\n')

            matched = []
            missing = []

            for pattern in expected_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    matched.append(pattern)
                else:
                    missing.append(pattern)

            return {
                'valid': len(missing) == 0,
                'matched_patterns': matched,
                'missing_patterns': missing,
                'line_count': len(lines),
                'recent_lines': lines[-10:],  # Last 10 lines
                'file_path': str(log_path),
                'file_size_bytes': log_path.stat().st_size
            }

        except Exception as e:
            return {
                'valid': False,
                'matched_patterns': [],
                'missing_patterns': expected_patterns,
                'error': str(e),
                'line_count': 0,
                'recent_lines': []
            }

    @staticmethod
    def extract_log_lines_matching(
        log_file: str,
        pattern: str,
        context_before: int = 0,
        context_after: int = 0
    ) -> List[str]:
        """
        Extract lines from log file matching pattern.

        Args:
            log_file: Path to log file
            pattern: Regex pattern to match
            context_before: Lines to include before match
            context_after: Lines to include after match

        Returns:
            List of matching lines with context
        """
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()

            matches = []

            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    # Add context
                    start = max(0, i - context_before)
                    end = min(len(lines), i + context_after + 1)

                    matches.extend(lines[start:end])

            return matches

        except Exception as e:
            logger.error(f"Error extracting log lines: {e}")
            return []


class TimestampExtractor:
    """Extract and validate YouTube timestamps from CLI output."""

    @staticmethod
    def extract_timestamps_from_table(output: str) -> List[Dict]:
        """
        Extract timestamp entries from table output.

        Expected table format:
        ┏━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━┓
        ┃ Time ┃ Duration ┃ Description ┃ Type ┃
        ┡━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━┩
        │ 0:15 │ 4.5s    │ Kick drum   │ drum │
        │ 0:30 │ 8.0s    │ Snare roll  │ drum │
        └──────┴────────┴─────────────┴──────┘

        Returns:
            List of {time, duration, description, type}
        """
        rows = RichTableParser.extract_table_rows(output)

        timestamps = []
        for row in rows:
            try:
                timestamp = {
                    'time': row.get('Time', '').strip(),
                    'duration': row.get('Duration', '').strip(),
                    'description': row.get('Description', '').strip(),
                    'type': row.get('Type', '').strip()
                }

                # Validate time format (MM:SS or M:SS)
                if re.match(r'^\d{1,2}:\d{2}$', timestamp['time']):
                    timestamps.append(timestamp)

            except (KeyError, ValueError):
                continue

        return timestamps

    @staticmethod
    def validate_timestamp_count(output: str, expected_min: int = 1) -> Dict:
        """
        Validate that output contains expected number of timestamps.

        Returns:
            {
                'valid': bool,
                'timestamp_count': int,
                'expected_min': int,
                'timestamps': [dict]
            }
        """
        timestamps = TimestampExtractor.extract_timestamps_from_table(output)

        return {
            'valid': len(timestamps) >= expected_min,
            'timestamp_count': len(timestamps),
            'expected_min': expected_min,
            'timestamps': timestamps
        }


class BatchLogValidator:
    """Validates batch processing logs."""

    @staticmethod
    def validate_batch_completion(log_file: str) -> Dict:
        """
        Validate batch processing completed successfully.

        Checks for:
        - Start marker
        - File processing lines
        - Embedding generation lines
        - Completion marker
        - No errors

        Returns:
            {
                'valid': bool,
                'started': bool,
                'completed': bool,
                'files_processed': int,
                'embeddings_generated': int,
                'errors': [str],
                'warnings': [str]
            }
        """
        validator = LogValidator()

        status = validator.validate_log_file(
            log_file,
            expected_patterns=[
                r'\[.*\] Starting automated batch',
                r'Processing directory:',
                r'processed \d+ files',
                r'Embeddings generated:',
                r'Automation complete'
            ]
        )

        # Extract counts
        files_match = re.search(r'(\d+) files processed', ''.join(status.get('recent_lines', [])))
        files_processed = int(files_match.group(1)) if files_match else 0

        embeddings_match = re.search(r'Embeddings generated: (\d+)', ''.join(status.get('recent_lines', [])))
        embeddings_generated = int(embeddings_match.group(1)) if embeddings_match else 0

        # Find errors and warnings
        errors = []
        warnings = []

        for line in status.get('recent_lines', []):
            if '[ERROR]' in line:
                errors.append(line.strip())
            elif '[WARN]' in line:
                warnings.append(line.strip())

        return {
            'valid': status['valid'] and len(errors) == 0,
            'started': '[INFO] Starting' in ''.join(status.get('recent_lines', [])),
            'completed': 'Automation complete' in ''.join(status.get('recent_lines', [])),
            'files_processed': files_processed,
            'embeddings_generated': embeddings_generated,
            'errors': errors,
            'warnings': warnings,
            'matched_patterns': status.get('matched_patterns', []),
            'missing_patterns': status.get('missing_patterns', [])
        }
