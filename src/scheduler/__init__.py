"""
RisePyMinder - Scheduled notification system
"""

__version__ = "1.0.0"
__author__ = "Virtual Assistant Reminder"

from .scheduler import MessageScheduler
from .notification import NotificationService

__all__ = ["MessageScheduler", "NotificationService"]
