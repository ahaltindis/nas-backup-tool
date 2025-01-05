import logging
import re
from datetime import datetime
from pathlib import Path

from .models import BackupStats, DirectoryStats
from .utils import CommandError, run_command

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run

    def run_backup(self) -> BackupStats:
        stats = BackupStats()

        for dir_config in self.config["backup"]["directories"]:
            dir_stats = self._backup_directory(
                dir_config["source"], dir_config["destination"]
            )
            stats.directories[dir_stats.source] = dir_stats
            stats.total_files += dir_stats.files_transferred
            stats.total_size += dir_stats.size_bytes

        return stats

    def _backup_directory(self, source, destination) -> DirectoryStats:
        # Create destination directory if it doesn't exist
        dest_path = Path(destination)
        if not self.dry_run:
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                logger.info("Created destination directory: %s", dest_path)
            except Exception as e:
                logger.error("Failed to create directory %s: %s", dest_path, e)
                raise

        # Updated rsync command with error handling and timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = dest_path / f"rsync_errors_{timestamp}.log"
        cmd = [
            "rsync",
            "-av",
            "--stats",
            "--ignore-errors",  # Continue on error
            "--partial",  # Keep partially transferred files
            "--safe-links",  # Ignore symlinks that point outside source tree
            f"--log-file={log_file}",  # Log errors to file
            "--dry-run" if self.dry_run else None,
            source,
            destination,
        ]
        cmd = [c for c in cmd if c is not None]

        try:
            stdout, _ = run_command(cmd, "Rsync failed")
            error_log = None
        except CommandError as e:
            if e.returncode == 23:  # Partial transfer due to error
                stdout = e.stderr
            else:
                raise

        # Check error log if it exists and not in dry-run mode
        if not self.dry_run and log_file.exists() and self._has_errors_in_log(log_file):
            logger.warning("Rsync reported errors. Check %s for details", log_file)
            error_log = log_file

        return self._parse_rsync_stats(stdout, source, error_log=error_log)

    def _has_errors_in_log(self, log_file: Path) -> bool:
        """Check if the rsync log file contains actual errors."""
        if not log_file.exists():
            return False

        with open(log_file, "r") as f:
            # Look for error indicators in rsync log
            for line in f:
                if any(x in line.lower() for x in ["error", "failed", "cannot"]):
                    return True
        return False

    def _parse_rsync_stats(self, output, source, error_log=None) -> DirectoryStats:
        """Parse rsync statistics output"""
        files_transferred = 0
        size_bytes = 0

        # Regular expressions for parsing rsync stats
        patterns = {
            "files": r"Number of regular files transferred: (\d+)",
            "size": r"Total transferred file size: ([\d,]+) bytes",
        }

        # Extract statistics
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                value = match.group(1)
                if key == "size":
                    size_bytes = int(value.replace(",", ""))
                elif key == "files":
                    files_transferred = int(value)

        # Update status to include error information
        status = "dry-run" if "DRY RUN" in output else "success"
        if error_log and error_log.exists():
            status = "completed_with_errors"

        # Create and return directory stats
        dir_stats = DirectoryStats(
            source=source,
            status=status,
            files_transferred=files_transferred,
            size_bytes=size_bytes,
            details=self._extract_summary(output),
            error_log=error_log,
        )

        logger.info("Backup stats for %s: %s", source, dir_stats)
        return dir_stats

    def _extract_summary(self, output: str) -> str:
        """Extract the summary line from rsync output"""
        summary_lines = []
        for line in output.splitlines():
            if any(
                x in line.lower()
                for x in ["created", "deleted", "changed", "transferred"]
            ):
                summary_lines.append(line.strip())
        return " | ".join(summary_lines)
