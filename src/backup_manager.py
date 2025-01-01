import subprocess
import os
from datetime import datetime
import logging

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
        self._parse_rsync_stats(result.stdout, source)

    def _simulate_backup_stats(self, source):
        """Generate dummy stats for dry run"""
        self.stats['directories'][source] = {
            'files_transferred': 10,
            'size_transferred': '100MB',
            'timestamp': datetime.now().isoformat()
        }
        self.stats['total_files'] += 10
        self.stats['total_size'] += 100

    def _parse_rsync_stats(self, output, source):
        # Real implementation would parse rsync output
        self._simulate_backup_stats(source) 