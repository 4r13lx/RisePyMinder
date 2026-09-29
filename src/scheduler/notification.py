"""
Notification service using Apprise
"""

import logging
import os
import re
from typing import List, Optional, Union

import apprise

logger = logging.getLogger(__name__)


class NotificationService:
    """Service responsible for sending notifications"""

    def __init__(self, title: str = "Virtual Assistant Reminder"):
        """
        Initialize notification service

        Args:
            title: Default title for notifications
        """
        self.title = title

    def get_recipient_urls(
        self, recipients: Optional[Union[str, List[str]]] = None
    ) -> Optional[str]:
        """
        Resolve named recipients to Apprise URLs.

        Named recipients use RECIPIENT_<NAME> environment variables. If no
        recipient name is provided, the legacy RECIPIENTS setting is used.

        Returns:
            String with Apprise URLs separated by commas, or None if not configured
        """
        if recipients is None:
            urls = os.environ.get("RECIPIENTS")
            if not urls:
                logger.warning("RECIPIENTS environment variable not configured")
            return urls

        recipient_names = [recipients] if isinstance(recipients, str) else recipients
        resolved_urls = []

        for recipient_name in recipient_names:
            if not isinstance(recipient_name, str):
                logger.error("Recipient names must be strings")
                return None

            name = recipient_name.strip()
            if not name or not re.fullmatch(r"[A-Za-z0-9_]+", name):
                logger.error("Invalid recipient name: %r", recipient_name)
                return None

            env_name = f"RECIPIENT_{name.upper()}"
            urls = os.environ.get(env_name)
            if not urls:
                logger.error("Recipient '%s' is not configured (%s)", name, env_name)
                return None
            resolved_urls.append(urls)

        if not resolved_urls:
            logger.error("No named recipients specified")
            return None

        return ",".join(resolved_urls)

    def validate_urls(self, urls: str) -> bool:
        """
        Validate that Apprise URLs are correct

        Args:
            urls: String with URLs separated by commas

        Returns:
            True if valid, False otherwise
        """
        test_apobj = apprise.Apprise()
        try:
            return test_apobj.add(urls)
        except Exception as e:
            logger.error(f"Error validating Apprise URLs: {e}")
            return False

    def send(
        self,
        message: str,
        notify_type: str = "INFO",
        recipients: Optional[Union[str, List[str]]] = None,
    ) -> bool:
        """
        Send a message to named recipients, or to legacy RECIPIENTS by default.

        Args:
            message: Message content
            notify_type: Notification type (INFO, WARNING, FAILURE, SUCCESS)
            recipients: One or more names configured as RECIPIENT_<NAME>

        Returns:
            True if sending was successful, False otherwise
        """
        try:
            # Get configuration URLs
            apprise_urls = self.get_recipient_urls(recipients)
            if not apprise_urls:
                logger.error("No notification destinations could be resolved")
                return False

            # Build the destination list and validate it before sending.
            apobj = apprise.Apprise()
            if not apobj.add(apprise_urls):
                logger.error(
                    "Invalid URL format for configured notification destinations"
                )
                return False

            # Send notification
            result = apobj.notify(
                body=message, title=self.title, notify_type=apprise.NotifyType.INFO
            )

            if result:
                preview = message[:50] + "..." if len(message) > 50 else message
                logger.info(f"Message sent to recipients: '{preview}'")
                return True
            else:
                logger.error("Apprise could not deliver message")
                return False

        except Exception as e:
            logger.critical(f"Error sending notification: {e}")
            return False
