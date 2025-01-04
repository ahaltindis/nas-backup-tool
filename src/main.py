import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

import schedule
import yaml

from .backup_manager import BackupManager
from .email_sender import EmailSender
from .nas_controller import NASController

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BackupOrchestrator:
    def __init__(self, dry_run=False, config_path=None):
        self.dry_run = dry_run
        self.config = self._load_config(config_path)

        self.nas_controller = NASController(self.config, dry_run=dry_run)
        self.backup_manager = BackupManager(self.config, dry_run=dry_run)
        self.email_sender = EmailSender(self.config, dry_run=dry_run)

    def _load_config(self, config_path):
        path = Path(
            config_path
            or (Path(__file__).parent.parent / "config" / "backup_config.yaml")
        )
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def run_backup_job(self):
        try:
            logger.info("Starting backup job%s", " (DRY RUN)" if self.dry_run else "")

            # Start NAS
            logger.info("Powering on NAS")
            self.nas_controller.start_nas()

            # Run backup
            logger.info("Starting backup process")
            stats = self.backup_manager.run_backup()

            # Send report
            logger.info("Sending backup report")
            self.email_sender.send_report(stats)

            # Shutdown NAS
            logger.info("Shutting down NAS")
            self.nas_controller.shutdown_nas()

            logger.info("Backup job completed successfully")

        except Exception as e:
            error_msg = f"Backup job failed: {str(e)}"
            logger.error(error_msg)
            # Send error notification
            self.email_sender.send_report(
                {
                    "status": "failed",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                }
            )


def main():
    parser = argparse.ArgumentParser(description="NAS Backup Tool")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run in dry-run mode (no actual changes)"
    )
    parser.add_argument(
        "--config",
        help="Path to config file (default: config/backup_config.yaml)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once without scheduling",
    )
    args = parser.parse_args()

    logger.info("Starting with arguments: %s", args)

    orchestrator = BackupOrchestrator(dry_run=args.dry_run, config_path=args.config)

    # Run immediately
    orchestrator.run_backup_job()

    # Exit if --once is specified
    if args.once:
        logger.info("Completed single run, exiting")
        return

    # Schedule backup based on configuration
    frequency = orchestrator.config["backup"]["frequency"]

    if frequency == "daily":
        schedule.every().day.at("02:00").do(orchestrator.run_backup_job)
    elif frequency == "weekly":
        schedule.every().monday.at("02:00").do(orchestrator.run_backup_job)
    elif frequency == "monthly":
        schedule.every().first_monday_of_month.at("02:00").do(
            orchestrator.run_backup_job
        )
    else:
        raise ValueError(f"Unsupported backup frequency: {frequency}")

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
