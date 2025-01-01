from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from .utils import format_size

@dataclass
class DirectoryStats:
    source: str
    files_transferred: int
    size_bytes: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = 'success'
    details: str = ''

    @property
    def size_formatted(self) -> str:
        return format_size(self.size_bytes)

@dataclass
class BackupStats:
    total_files: int = 0
    total_size: int = 0  # in bytes
    status: str = 'success'
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    directories: Dict[str, DirectoryStats] = field(default_factory=dict)

    def format_total_size(self) -> str:
        return format_size(self.total_size) 