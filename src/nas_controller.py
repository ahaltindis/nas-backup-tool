import asyncio
import logging
import socket
import time
from pathlib import Path

import asyncssh
from wakeonlan import send_magic_packet

from .utils import run_command

logger = logging.getLogger(__name__)


class NASController:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run
        self.mount_point = Path(self.config["nas"]["mount"]["local_path"])

    def _check_nas_connection(self, timeout: int = 5) -> bool:
        """Check if NAS is accessible via SSH."""
        try:
            with socket.create_connection(
                (self.config["nas"]["ip"], 22), timeout=timeout
            ):
                return True
        except (socket.timeout, socket.error):
            return False

    def start_nas(self):
        try:
            if self.dry_run:
                logger.info(
                    "[DRY RUN] Would send WOL packet to %s",
                    self.config["nas"]["mac_address"],
                )
                logger.info("[DRY RUN] Would wait for NAS to boot")
                logger.info("[DRY RUN] Would mount NAS at %s", self.mount_point)
                return

            # Check if NAS is already online
            if self._check_nas_connection():
                logger.info("NAS is already online, skipping wake-up")
            else:
                # NAS needs to be woken up
                logger.info(
                    f"Sending WOL packet to {self.config['nas']['mac_address']}"
                )
                send_magic_packet(self.config["nas"]["mac_address"])

                logger.info("Waiting for NAS to boot...")
                self._verify_nas_online()

            # Mount NAS
            self._mount_nas()

        except Exception as e:
            logger.error(f"Failed to start NAS: {str(e)}")
            raise

    def shutdown_nas(self):
        try:
            if self.dry_run:
                logger.info("[DRY RUN] Would unmount NAS from %s", self.mount_point)
                logger.info(
                    "[DRY RUN] Would connect to NAS at %s", self.config["nas"]["ip"]
                )
                logger.info("[DRY RUN] Would execute shutdown command")
                return

            # Unmount NAS
            self._unmount_nas()

            logger.info(f"Connecting to NAS at {self.config['nas']['ip']}")
            asyncio.run(
                self._execute_ssh_command(self.config["nas"]["shutdown_command"])
            )
            logger.info("Shutdown command executed successfully")

        except Exception as e:
            logger.error(f"Failed to shutdown NAS: {str(e)}")
            raise

    def _mount_nas(self):
        """Mount NAS share"""
        mount_config = self.config["nas"]["mount"]

        # Create mount point if it doesn't exist
        self.mount_point.mkdir(parents=True, exist_ok=True)

        # Check if already mounted
        if self._is_mounted():
            logger.info("NAS is already mounted at %s", self.mount_point)
            return

        # Prepare mount command
        source = f"{self.config['nas']['ip']}:{mount_config['remote_path']}"
        options = mount_config["options"]

        if mount_config["type"] == "cifs":
            source = f"//{self.config['nas']['ip']}/{mount_config['remote_path']}"
            # Add CIFS credentials if configured
            if "cifs" in mount_config:
                cifs_opts = [f"credentials={mount_config['cifs']['credentials']}"]
                options = (
                    f"{options},{','.join(cifs_opts)}"
                    if options
                    else ",".join(cifs_opts)
                )

        cmd = [
            "mount",
            "-t",
            mount_config["type"],
            "-o",
            options,
            source,
            str(self.mount_point),
        ]
        run_command(cmd, "Failed to mount NAS", dry_run=self.dry_run)

        logger.info("NAS mounted successfully at %s", self.mount_point)

    def _unmount_nas(self):
        """Unmount NAS share"""
        if not self._is_mounted():
            logger.info("NAS is not mounted at %s", self.mount_point)
            return

        cmd = ["umount", str(self.mount_point)]
        run_command(cmd, "Failed to unmount NAS", dry_run=self.dry_run)

        logger.info("NAS unmounted successfully")

    def _is_mounted(self) -> bool:
        """Check if NAS is mounted"""
        try:
            with open("/proc/mounts", "r") as f:
                return any(str(self.mount_point) in line for line in f)
        except Exception as e:
            logger.error(f"Failed to check mount status: {str(e)}")
            return False

    async def _execute_ssh_command(self, command):
        async with asyncssh.connect(
            self.config["nas"]["ip"],
            username=self.config["nas"]["username"],
            password=self.config["nas"].get("password"),
            known_hosts=None,
            client_keys=None,
        ) as conn:
            result = await conn.run(command)
            return result.stdout

    def _verify_nas_online(self):
        if self.dry_run:
            logger.info("[DRY RUN] Would verify NAS is online")
            return True

        retry_count = 0
        max_retries = 10
        wait_time = 30  # seconds to wait between retries

        while retry_count < max_retries:
            if self._check_nas_connection():
                logger.info("NAS is online and accepting connections")
                return True
            else:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(
                        f"NAS not responding, retrying ({retry_count}/{max_retries}) \
                                after {wait_time} seconds.."
                    )
                    time.sleep(wait_time)

        raise Exception("NAS failed to come online after maximum retries")
