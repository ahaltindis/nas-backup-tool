import asyncio
import logging
import socket
import time

import asyncssh
from wakeonlan import send_magic_packet

logger = logging.getLogger(__name__)


class NASController:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run

    def start_nas(self):
        try:
            if self.dry_run:
                logger.info(
                    "[DRY RUN] Would send WOL packet to %s",
                    self.config["nas"]["mac_address"],
                )
                logger.info("[DRY RUN] Would wait for NAS to boot")
                return

            logger.info(f"Sending WOL packet to {self.config['nas']['mac_address']}")
            send_magic_packet(self.config["nas"]["mac_address"])

            # Wait for NAS to boot
            logger.info("Waiting for NAS to boot...")
            time.sleep(10)

            # Verify NAS is accessible
            self._verify_nas_online()

        except Exception as e:
            logger.error(f"Failed to start NAS: {str(e)}")
            raise

    async def _execute_ssh_command(self, command):
        async with asyncssh.connect(
            self.config["nas"]["ip"],
            username=self.config["nas"]["username"],
            known_hosts=None,  # In production, you should use known_hosts
        ) as conn:
            result = await conn.run(command)
            return result.stdout

    def shutdown_nas(self):
        try:
            if self.dry_run:
                logger.info(
                    "[DRY RUN] Would connect to NAS at %s", self.config["nas"]["ip"]
                )
                logger.info("[DRY RUN] Would execute shutdown command")
                return

            logger.info(f"Connecting to NAS at {self.config['nas']['ip']}")
            asyncio.run(
                self._execute_ssh_command(self.config["nas"]["shutdown_command"])
            )
            logger.info("Shutdown command executed successfully")

        except Exception as e:
            logger.error(f"Failed to shutdown NAS: {str(e)}")
            raise

    def _verify_nas_online(self):
        if self.dry_run:
            logger.info("[DRY RUN] Would verify NAS is online")
            return True

        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            try:
                with socket.create_connection(
                    (self.config["nas"]["ip"], 22), timeout=5
                ):
                    logger.info("NAS is online and accepting connections")
                    return True
            except (socket.timeout, socket.error):
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(
                        f"NAS not responding, retrying ({retry_count}/{max_retries})"
                    )
                    time.sleep(30)

        raise Exception("NAS failed to come online after maximum retries")
