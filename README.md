# NAS Backup Tool

A Python-based tool for automated NAS backups with Wake-on-LAN support.

- 🔄 Efficient incremental backups using rsync
- 📧 Email notifications with detailed backup reports
- 🔌 Automatic NAS power management
- 🔗 Secure CIFS/NFS mount support
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

Prepare your config based on `config/backup_config.yaml`.

### Mount Configuration

The tool supports both CIFS (Samba) and NFS mounts:

#### CIFS Mount
```yaml
nas:
  mount:
    type: "cifs"
    remote_path: "volume1"  # NAS share path
    local_path: "/mnt/nas-backup"
    options: "vers=3"  # CIFS mount options
    cifs:
      credentials: "/etc/nas_credentials"  # Path to credentials file
```

Create a credentials file with:
```
username=your_username
password=your_password
domain=your_domain  # Optional
```

#### NFS Mount
```yaml
nas:
  mount:
    type: "nfs"
    remote_path: "/volume1/backup"
    local_path: "/mnt/nas-backup"
    options: "vers=3,nolock"
```

The mount feature:
- Automatically mounts shares after NAS wake-up
- Creates mount points if they don't exist
- Safely unmounts before NAS shutdown
- Supports both CIFS and NFS protocols
- Handles credentials securely

__Backup Schedule:__
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

