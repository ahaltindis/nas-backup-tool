import logging
import re
import subprocess

from .models import BackupStats, DirectoryStats

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
        cmd = [
            "rsync",
            "-av",
            "--stats",
            "--dry-run" if self.dry_run else None,
            source,
            destination,
        ]
        cmd = [c for c in cmd if c is not None]

        if self.dry_run:
            logger.info("[DRY RUN] Would execute: %s", " ".join(cmd))
            return self._simulate_backup_stats(source)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Rsync failed: %s", result.stderr)
            raise Exception(f"Rsync failed with code {result.returncode}")

        return self._parse_rsync_stats(result.stdout, source)

    def _parse_rsync_stats(self, output, source) -> DirectoryStats:
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

        # Create and return directory stats
        dir_stats = DirectoryStats(
            source=source,
            files_transferred=files_transferred,
            size_bytes=size_bytes,
            details=self._extract_summary(output),
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

    def _simulate_backup_stats(self, source: str) -> DirectoryStats:
        """Generate dummy stats for dry run"""
        return DirectoryStats(
            source=source,
            files_transferred=10,
            size_bytes=100 * 1024 * 1024,
            status="dry-run",
            details="Dry run - no actual changes made",
        )
