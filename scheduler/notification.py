"""
Notification service using Apprise
"""

import logging
from typing import Optional, List
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
        self.apobj = apprise.Apprise()
    
    def get_recipient_urls(self) -> Optional[str]:
        """
        Get recipient URLs from environment variable
        
        Returns:
            String with Apprise URLs separated by commas, or None if not configured
        """
        import os
        urls = os.environ.get("RECIPIENTS")
        
        if not urls:
            logger.warning("RECIPIENTS environment variable not configured")
            return None
        
        return urls
    
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
        notify_type: str = "INFO"
    ) -> bool:
        """
        Send a message to all configured recipients
        
        Args:
            message: Message content
            notify_type: Notification type (INFO, WARNING, FAILURE, SUCCESS)
        
        Returns:
            True if sending was successful, False otherwise
        """
        try:
            # Get configuration URLs
            apprise_urls = self.get_recipient_urls()
            if not apprise_urls:
                logger.error("No recipients configured in RECIPIENTS environment variable")
                return False
            
            # Validate URLs
            if not self.validate_urls(apprise_urls):
                logger.error("Invalid URL format in RECIPIENTS")
                return False
            
            # Create Apprise instance
            apobj = apprise.Apprise()
            apobj.add(apprise_urls)
            
            # Send notification
            result = apobj.notify(
                body=message,
                title=self.title,
                notify_type=apprise.NotifyType.INFO
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
