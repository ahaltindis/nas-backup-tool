def format_size(size_in_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f}{unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f}PB"
