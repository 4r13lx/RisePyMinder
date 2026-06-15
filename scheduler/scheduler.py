"""
Scheduled message orchestrator
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import zoneinfo

from .config import Config
from .notification import NotificationService

logger = logging.getLogger(__name__)


class MessageScheduler:
    """Manager for sending scheduled messages based on JSON schedule"""
    
    def __init__(self, schedule_path: Optional[Path] = None):
        """
        Initialize the message scheduler
        
        Args:
            schedule_path: Path to the schedule.json file
        """
        self.schedule_path = schedule_path or Config.SCHEDULE_PATH
        self.notification_service = NotificationService(
            title=Config.NOTIFICATION_TITLE
        )
        self.schedule: List[Dict] = []
    
    def load_schedule(self) -> bool:
        """
        Load schedule from JSON file
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not self.schedule_path.exists():
                logger.error(f"File not found: {self.schedule_path}")
                return False
            
            with open(self.schedule_path, "r", encoding="utf-8") as file:
                self.schedule = json.load(file)
            
            logger.info(f"Schedule loaded: {len(self.schedule)} reminders")
            return True
        
        except json.JSONDecodeError:
            logger.error(f"JSON format error in: {self.schedule_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading schedule: {e}")
            return False
    
    def get_current_time(self) -> datetime:
        """
        Get current time in configured timezone
        
        Returns:
            datetime with current time in the configured timezone
        """
        try:
            tz = zoneinfo.ZoneInfo(Config.TIMEZONE_STR)
            return datetime.now(tz)
        except zoneinfo.ZoneInfoNotFoundError:
            logger.error(f"Unknown timezone: {Config.TIMEZONE_STR}. Using UTC.")
            return datetime.now(zoneinfo.ZoneInfo("UTC"))
    
    def round_time(self, dt: datetime) -> tuple:
        """
        Round time according to configuration
        
        Args:
            dt: datetime to round
        
        Returns:
            Tuple (formatted_date, formatted_rounded_time)
        """
        date = dt.strftime("%d-%m-%Y")
        
        # Round minutes
        rounded_minute = (dt.minute // Config.TIME_ROUNDING_MINUTES) * Config.TIME_ROUNDING_MINUTES
        rounded_time = f"{dt.hour:02d}:{rounded_minute:02d}"
        
        return date, rounded_time
    
    def process_schedule(self) -> int:
        """
        Process schedule and send pending messages
        
        Returns:
            Number of messages sent
        """
        if not self.schedule:
            logger.warning("Empty schedule. Load data first with load_schedule()")
            return 0
        
        # Get current time in configured timezone
        current_now = self.get_current_time()
        current_date, current_rounded_time = self.round_time(current_now)

        logger.info(f"Processing schedule for {current_date} {current_rounded_time}")
        
        messages_sent = 0
        
        for reminder in self.schedule:
            if self._match_schedule(reminder, current_date, current_rounded_time):
                if self._send_message(reminder):
                    messages_sent += 1
        
        if messages_sent == 0:
            logger.debug(f"[{current_date} {current_rounded_time}] No pending messages")
        
        return messages_sent
    
    def _match_schedule(
        self,
        reminder: Dict,
        current_date: str,
        current_time: str
    ) -> bool:
        """
        Check if a reminder matches current time
        
        Args:
            reminder: Reminder data
            current_date: Date in DD-MM-YYYY format
            current_time: Time in HH:MM format
        
        Returns:
            True if matches, False otherwise
        """
        return (
            reminder.get("date") == current_date and
            reminder.get("time") == current_time
        )
    
    def _send_message(self, reminder: Dict) -> bool:
        """
        Send a message based on reminder data
        
        Args:
            reminder: Reminder data with 'message'
        
        Returns:
            True if sent successfully, False otherwise
        """
        message = reminder.get("message")
        
        if not message:
            logger.warning("Reminder without message defined")
            return False
        
        return self.notification_service.send(message=message)
    
    def run(self) -> bool:
        """
        Execute complete cycle: load schedule and process messages
        
        Returns:
            True if execution was successful, False otherwise
        """
        try:
            if not self.load_schedule():
                return False
            
            messages_sent = self.process_schedule()
            logger.info(f"Execution completed: {messages_sent} messages sent")
            return True
        
        except Exception as e:
            logger.critical(f"Error during scheduler execution: {e}")
            return False
