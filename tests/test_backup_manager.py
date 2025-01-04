from pathlib import Path

import pytest

from src.backup_manager import BackupManager
from src.models import BackupStats, DirectoryStats


@pytest.fixture
def config():
    resources = Path(__file__).parent / "resources"
    return {
        "backup": {
            "directories": [
                {"source": str(resources / "test_src1"), "destination": "/test/dest1"},
                {"source": str(resources / "test_src2"), "destination": "/test/dest2"},
            ]
        }
    }


def test_backup_manager_dry_run(config):
    manager = BackupManager(config, dry_run=True)
    stats = manager.run_backup()

    assert isinstance(stats, BackupStats)
    assert stats.total_files == 3
    assert stats.total_size == 29
    assert stats.status == "success"
    assert len(stats.directories) == 2

    dir_key1 = list(stats.directories.keys())[0]
    dir_key2 = list(stats.directories.keys())[1]
    assert dir_key1.endswith("test_src1")
    assert dir_key2.endswith("test_src2")

    dir_stats1 = stats.directories[dir_key1]
    assert isinstance(dir_stats1, DirectoryStats)
    assert dir_stats1.files_transferred == 2
    assert dir_stats1.size_bytes == 18
    assert dir_stats1.size_formatted == "18.00B"
    assert dir_stats1.status == "dry-run"

    dir_stats2 = stats.directories[dir_key2]
    assert isinstance(dir_stats2, DirectoryStats)
    assert dir_stats2.files_transferred == 1
    assert dir_stats2.size_bytes == 11
    assert dir_stats2.size_formatted == "11.00B"
    assert dir_stats2.status == "dry-run"


def test_parse_rsync_stats():
    manager = BackupManager({"backup": {"directories": []}}, dry_run=False)
    rsync_output = """
Number of files: 1,234
Number of regular files transferred: 123
Total file size: 1,234,567 bytes
Total transferred file size: 123,456 bytes
Literal data: 123,456 bytes
Matched data: 0 bytes
File list size: 123
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 123,456
Total bytes received: 1,234
    """

    dir_stats = manager._parse_rsync_stats(rsync_output, "/test/source")
    assert isinstance(dir_stats, DirectoryStats)
    assert dir_stats.files_transferred == 123
    assert dir_stats.size_bytes == 123456
    assert dir_stats.size_formatted == "120.56KB"
