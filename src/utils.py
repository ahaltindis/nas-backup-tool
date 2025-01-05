import logging
import subprocess
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


def format_size(size_in_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f}{unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f}PB"


class CommandError(Exception):
    def __init__(self, message: str, returncode: int, stdout: str, stderr: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(message)


def run_command(
    cmd: List[str],
    error_msg: str,
    dry_run: bool = False,
    log_cmd: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """Run a shell command with proper logging and error handling.

    Args:
        cmd: Command and arguments as list
        error_msg: Error message prefix for exceptions
        dry_run: If True, only log the command without executing
        log_cmd: Alternative command to log (e.g., to hide sensitive info)

    Returns:
        Tuple of (stdout, stderr)

    Raises:
        CommandError: If command fails
    """
    display_cmd = log_cmd if log_cmd is not None else cmd

    if dry_run:
        logger.info("[DRY RUN] Would execute: %s", " ".join(display_cmd))
        return "", ""

    logger.info("Executing: %s", " ".join(display_cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise CommandError(
            f"{error_msg}: {result.stderr}",
            result.returncode,
            result.stdout,
            result.stderr,
        )

    return result.stdout, result.stderr
