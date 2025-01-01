import subprocess
import os
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'directories': {}
        }

    def run_backup(self):
        for dir_config in self.config['backup']['directories']:
            self._backup_directory(dir_config['source'], dir_config['destination'])
        return self.stats

    def _backup_directory(self, source, destination):
        cmd = [
            'rsync',
            '-av',
            '--stats',
            '--dry-run' if self.dry_run else None,
            source,
            destination
        ]
        cmd = [c for c in cmd if c is not None]
        
        if self.dry_run:
            logger.info("[DRY RUN] Would execute: %s", ' '.join(cmd))
            self._simulate_backup_stats(source)
            return

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Rsync failed: %s", result.stderr)
            raise Exception(f"Rsync failed with code {result.returncode}")
            
        self._parse_rsync_stats(result.stdout, source)

    def _parse_rsync_stats(self, output, source):
        """Parse rsync statistics output"""
        # Initialize stats for this directory
        dir_stats = {
            'files_transferred': 0,
            'size_transferred': '0B',
            'timestamp': datetime.now().isoformat()
        }

        # Regular expressions for parsing rsync stats
        patterns = {
            'files': r'Number of files transferred: (\d+)',
            'size': r'Total transferred file size: ([\d,]+) bytes',
            'created': r'Number of files created: (\d+)',
            'deleted': r'Number of deleted files: (\d+)',
            'speed': r'Transfer rate: ([\d.]+\w+/s)',
        }

        # Extract statistics
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                value = match.group(1)
                if key == 'size':
                    # Convert bytes to human readable format
                    bytes_val = int(value.replace(',', ''))
                    dir_stats['size_transferred'] = self._format_size(bytes_val)
                    self.stats['total_size'] += bytes_val
                elif key == 'files':
                    dir_stats['files_transferred'] = int(value)
                    self.stats['total_files'] += int(value)

        # Add additional useful information
        dir_stats.update({
            'source': source,
            'status': 'success',
            'details': self._extract_summary(output)
        })

        # Store directory stats
        self.stats['directories'][source] = dir_stats
        logger.info("Backup stats for %s: %s", source, dir_stats)

    def _format_size(self, size_in_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f}{unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.2f}PB"

    def _extract_summary(self, output):
        """Extract the summary line from rsync output"""
        summary_lines = []
        for line in output.splitlines():
            if any(x in line.lower() for x in ['created', 'deleted', 'changed', 'transferred']):
                summary_lines.append(line.strip())
        return ' | '.join(summary_lines)

    def _simulate_backup_stats(self, source):
        """Generate dummy stats for dry run"""
        self.stats['directories'][source] = {
            'files_transferred': 10,
            'size_transferred': '100MB',
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'status': 'dry-run',
            'details': 'Dry run - no actual changes made'
        }
        self.stats['total_files'] += 10
        self.stats['total_size'] += 100 * 1024 * 1024  # 100MB in bytes 