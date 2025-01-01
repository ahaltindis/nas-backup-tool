# NAS Backup Tool

A Python-based tool for automated NAS backups with Wake-on-LAN support.

- 🔄 Efficient incremental backups using rsync
- 📧 Email notifications with detailed backup reports
- 🔌 Automatic NAS power management
- 🐳 Docker support for easy deployment
- 📊 Backup statistics and reporting
- ✨ Dry-run mode for testing


## Requirements

- Python >= 3.12
- NAS with Wake-on-LAN and SSH support
- Ubuntu/Linux host system
- `rsync` installed on both systems

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nas-backup-tool.git
cd nas-backup-tool
```

2. Install dependencies using `uv`:
```bash
pip install uv
uv venv
uv pip install -e .
```

## Configuration

Copy `config/backup_config.example.yaml` to `config/backup_config.yaml` and update with your settings:
```yaml:README.md
nas:
mac_address: "00:11:22:33:44:55" # NAS MAC address for Wake-on-LAN
ip: "192.168.1.100" # NAS IP address
username: "admin" # SSH username
shutdown_command: "shutdown -h now"
backup:
directories:
source: "/home/user/documents"
destination: "/mnt/backup/documents"
source: "/home/user/photos"
destination: "/mnt/backup/photos"
frequency: "daily" # daily, weekly, monthly
email:
smtp_server: "smtp.gmail.com"
smtp_port: 587
sender: "your-email@gmail.com"
recipient: "your-personal@email.com"
password: "your-app-password" # Gmail App Password
```

## Usage

### Local Development/Testing

Use the provided script to run in dry-run mode (no actual changes):
```bash
./run-local.sh
```

### Production Deployment

1. Build and run using Docker:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

### Manual Execution

Run with dry-run mode (testing):
```bash
uv run python -m src.main --dry-run
```

Run normally:
```bash
uv run python -m src.main
```

## Backup Schedule

- **Daily**: Runs at 2 AM every day
- **Weekly**: Runs at 2 AM every Monday
- **Monthly**: Runs at 2 AM on the first Monday of each month

## Development

1. Create a virtual environment:
```bash
uv venv
```

2. Install in development mode:
```bash
uv pip install -e .
```

3. Install test dependencies:
```bash
uv pip install -e ".[test]"
```

4. Run tests:
```bash
# Run all tests with coverage report
uv run pytest
```

5. Format code:
```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Format all files
./scripts/format.sh

# Or run ruff directly
uv run ruff format .
uv run ruff check --fix .
```

6. Test changes in dry-run mode:
```bash
uv run python -m src.main --dry-run
```

## License

MIT License - See LICENSE file for details

