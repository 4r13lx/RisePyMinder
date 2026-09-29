from __future__ import annotations

import asyncio

from loguru import logger

from app.repository import NotificationRepository
from app.notification_service import NotificationService


class PollingScheduler:
    """Scheduler that polls the database for pending notifications and processes them"""

    def __init__(
        self,
        repository: NotificationRepository,
        notification_service: NotificationService,
        interval: int = 15,
        batch_size: int = 100,
    ):
        """Initializes the scheduler with the repository, notification service, polling interval, and batch size"""
        self.repository = repository
        self.notification_service = notification_service
        self.interval = interval
        self.batch_size = batch_size
        self.running = False

    async def start(self):
        """Starts the scheduler"""
        logger.info("Polling Scheduler iniciado.")
        self.running = True

        while self.running:
            try:
                await self.process_pending()
            except Exception:
                logger.exception("Error procesando pendientes.")

            await asyncio.sleep(self.interval)

    def stop(self):
        """Stops the scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False

    async def process_pending(self):
        """Processes pending notifications in batches"""
        notifications = self.repository.get_pending(self.batch_size)

        if not notifications:
            return

        logger.info(f"{len(notifications)} mensajes pendientes.")

        for notification in notifications:
            await self.process_notification(notification)

    async def process_notification(self, notification):
        """Processes a single notification"""
        notification_id = notification["id"]

        try:
            logger.info(f"Enviando {notification_id}")

            await self.notification_service.send(notification)

            self.repository.mark_sent(notification_id)

            logger.success(f"{notification_id} enviado.")

        except Exception as ex:
            logger.exception(ex)
            self.repository.mark_error(notification_id, str(ex))


# End-of-file (EOF)
