from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class NotificationProvider(ABC):
    """Abstract base class for notification providers"""

    @abstractmethod
    async def send(self, notification: dict[str, Any]) -> None:
        """Sends a notification using the provider's implementation"""
        raise NotImplementedError


# End-of-file (EOF)
