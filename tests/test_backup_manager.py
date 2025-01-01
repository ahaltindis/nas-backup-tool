import pytest

from src.backup_manager import BackupManager
from src.models import BackupStats, DirectoryStats


@pytest.fixture
def config():
    return {
        "backup": {
            "directories": [{"source": "/test/source", "destination": "/test/dest"}]
        }
    }


def test_backup_manager_dry_run(config):
    manager = BackupManager(config, dry_run=True)
    stats = manager.run_backup()

    assert isinstance(stats, BackupStats)
    assert stats.total_files == 10  # From simulation
    assert stats.total_size == 100 * 1024 * 1024  # 100MB from simulation
    assert len(stats.directories) == 1

    dir_stats = stats.directories["/test/source"]
    assert isinstance(dir_stats, DirectoryStats)
    assert dir_stats.files_transferred == 10
    assert dir_stats.size_bytes == 100 * 1024 * 1024  # 100MB
    assert dir_stats.size_formatted == "100.00MB"
    assert dir_stats.status == "dry-run"


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
