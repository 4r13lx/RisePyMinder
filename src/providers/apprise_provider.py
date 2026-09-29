from __future__ import annotations

import asyncio
import json
from typing import Any

import apprise
from loguru import logger


class AppriseProvider:
    """Notification provider that uses the Apprise library to send notifications"""

    def __init__(self, targets: dict[str, str]):
        """Initializes the provider with a dictionary of target aliases and their corresponding Apprise URLs"""
        self.targets = targets
        self.app = apprise.Apprise()

    async def send(self, notification: dict[str, Any]) -> None:
        """Sends a notification using the Apprise library"""
        urls = []
        for alias in json.loads(notification["targets"]):
            if alias not in self.targets:
                raise ValueError(f"Target '{alias}' no existe en settings.yaml")
            urls.append(self.targets[alias])

        for url in urls:
            self.app.add(url)

        logger.info(f"Enviando '{notification['id']}' a {len(urls)} destino(s).")

        ok = await asyncio.to_thread(
            self.app.notify, title=notification["title"], body=notification["body"]
        )

        if not ok:
            raise RuntimeError("Apprise devolvió False.")


# End-of-file (EOF)
