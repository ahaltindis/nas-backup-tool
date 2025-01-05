import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .models import BackupStats

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run

    def send_report(self, stats: BackupStats):
        msg = MIMEMultipart()
        msg["From"] = self.config["email"]["sender"]
        msg["To"] = self.config["email"]["recipient"]
        msg["Subject"] = f"Backup Report - {stats.timestamp}"

        body = self._generate_report_body(stats)
        msg.attach(MIMEText(body, "plain"))

        if self.dry_run:
            logger.info("[DRY RUN] Would send email:")
            logger.info("[DRY RUN] From: %s", msg["From"])
            logger.info("[DRY RUN] To: %s", msg["To"])
            logger.info("[DRY RUN] Subject: %s", msg["Subject"])
            logger.info("[DRY RUN] Body:\n%s", body)
            return

        try:
            with smtplib.SMTP(
                self.config["email"]["smtp_server"], self.config["email"]["smtp_port"]
            ) as server:
                server.starttls()
                server.login(
                    self.config["email"]["sender"], self.config["email"]["password"]
                )
                server.send_message(msg)
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    def _generate_report_body(self, stats: BackupStats):
        if stats.status == "failed":
            return f"""
Backup Job Failed!
Error: {stats.error}
Time: {stats.timestamp}
"""

        report = [
            "Backup Job Completed Successfully",
            f"Total Files: {stats.total_files}",
            f"Total Size: {stats.format_total_size()}",
            "\nDetails by Directory:",
        ]

        for dir_stats in stats.directories.values():
            report.extend(
                [
                    f"\nDirectory: {dir_stats.source}",
                    f"Files Transferred: {dir_stats.files_transferred}",
                    f"Size Transferred: {dir_stats.size_formatted}",
                    f"Status: {dir_stats.status}",
                    f"Details: {dir_stats.details}",
                ]
            )
            if dir_stats.status == "completed_with_errors" and dir_stats.error_log:
                report.append(f"Error Log: {dir_stats.error_log}")

        return "\n".join(report)
