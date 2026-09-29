from __future__ import annotations
from typing import Any
from loguru import logger
from app.providers.base import NotificationProvider


class NotificationService:
    """Service for sending notifications using a specified provider"""

    def __init__(self, provider: NotificationProvider):
        """Initializes the service with a notification provider"""
        self.provider = provider

    async def send(self, notification: dict[str, Any]) -> None:
        """Sends a notification using the configured provider"""
        logger.debug(f"Procesando notificación {notification['id']}")
        await self.provider.send(notification)


# End-of-file (EOF)
