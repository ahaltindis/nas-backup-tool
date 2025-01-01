import pytest
from datetime import datetime
from src.models import DirectoryStats, BackupStats

def test_directory_stats_defaults():
    stats = DirectoryStats(
        source="/test",
        files_transferred=10,
        size_bytes=1024 * 1024  # 1MB in bytes
    )
    assert stats.source == "/test"
    assert stats.files_transferred == 10
    assert stats.size_bytes == 1024 * 1024
    assert stats.size_formatted == "1.00MB"
    assert stats.status == "success"
    assert stats.details == ""
    assert datetime.fromisoformat(stats.timestamp)  # Should not raise error

def test_backup_stats_defaults():
    stats = BackupStats()
    assert stats.total_files == 0
    assert stats.total_size == 0
    assert stats.format_total_size() == "0.00B"
    assert stats.status == "success"
    assert stats.error is None
    assert stats.directories == {}
    assert datetime.fromisoformat(stats.timestamp)

def test_backup_stats_format_total_size():
    stats = BackupStats(total_size=1024 * 1024)  # 1MB
    assert stats.format_total_size() == "1.00MB"

def test_backup_stats_with_directories():
    dir_stats = DirectoryStats(
        source="/test",
        files_transferred=10,
        size_bytes=1024 * 1024  # 1MB
    )
    stats = BackupStats()
    stats.directories["/test"] = dir_stats
    assert stats.directories["/test"].source == "/test"
    assert stats.directories["/test"].files_transferred == 10
    assert stats.directories["/test"].size_bytes == 1024 * 1024
    assert stats.directories["/test"].size_formatted == "1.00MB" 