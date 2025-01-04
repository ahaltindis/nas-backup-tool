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
- `rsync` installed on the host system
- `cifs-utils` for cifs/samba mount

## Configuration

Prepare your config based on `config/backup_config.yaml`:
```yaml:README.md
nas:
  mac_address: "00:11:22:33:44:55" # NAS MAC address for Wake-on-LAN
  ip: "192.168.1.100" # NAS IP address
  username: "admin" # SSH username
  shutdown_command: "shutdown -h now"
backup:
  directories:
    - source: "/home/user/documents"
      destination: "/mnt/backup/documents"
    - source: "/home/user/photos"
      destination: "/mnt/backup/photos"
  frequency: "daily" # daily, weekly, monthly
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender: "your-email@gmail.com"
  recipient: "your-personal@email.com"
  password: "your-app-password" # Gmail App Password
```

### Backup Schedule

- **Daily**: Runs at 2 AM every day
- **Weekly**: Runs at 2 AM every Monday
- **Monthly**: Runs at 2 AM on the first Monday of each month

## Usage

### Local Development/Testing

Use the provided script to run in dry-run mode (no actual changes):
```bash
./run-local.sh
```

Run normally one-off with a config:
```bash
./run-local.sh --prod --once --config config/my_config.yaml
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

## Development

1. Create a virtual environment:
```bash
uv venv
```

2. Install in dependencies:
```bash
uv pip install -e .
```

3. Format code:
```bash
./scripts/format.sh
```

4. Run tests:
```bash
./scripts/test.sh
```

## License

MIT License - See LICENSE file for details

## Note
More than ~90% of this code-base developed by Cursor together with Claude 3.5 Sonnet.

