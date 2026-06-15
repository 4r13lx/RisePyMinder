"""Tests for scheduler module"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from scheduler import MessageScheduler
from scheduler.config import Config


class TestMessageScheduler:
    """Tests for MessageScheduler"""
    
    def test_initialization(self):
        """Test that scheduler initializes correctly"""
        scheduler = MessageScheduler()
        assert scheduler.schedule_path == Config.SCHEDULE_PATH
        assert scheduler.notification_service is not None
        assert isinstance(scheduler.schedule, list)
    
    def test_get_argentina_time(self):
        """Test that Argentina time is obtained correctly"""
        scheduler = MessageScheduler()
        argentina_time = scheduler.get_argentina_time()
        
        # Verify it's a datetime
        assert isinstance(argentina_time, datetime)
        
        # Verify offset is UTC-3
        assert argentina_time.utcoffset() == timedelta(hours=-3)
    
    def test_round_time(self):
        """Test that time rounding works correctly"""
        scheduler = MessageScheduler()
        
        # Create datetime with specific minutes
        dt = datetime(2026, 6, 14, 10, 23, 0)
        date, time = scheduler.round_time(dt)
        
        # Verify date format
        assert date == "14-06-2026"
        
        # Verify rounding (23 minutes rounded to 5 min gives 20)
        assert time == "10:20"
    
    def test_match_schedule(self):
        """Test that schedule matching works"""
        scheduler = MessageScheduler()
        
        reminder = {
            "date": "14-06-2026",
            "time": "10:00",
            "message": "Test",
            "audience": "students"
        }
        
        # Case that matches
        assert scheduler._match_schedule(reminder, "14-06-2026", "10:00") is True
        
        # Cases that don't match
        assert scheduler._match_schedule(reminder, "14-06-2026", "10:05") is False
        assert scheduler._match_schedule(reminder, "15-06-2026", "10:00") is False
    
    def test_load_schedule_not_exists(self):
        """Test that load_schedule handles file not found"""
        scheduler = MessageScheduler(schedule_path=Path("/nonexistent/path.json"))
        result = scheduler.load_schedule()
        
        assert result is False
        assert scheduler.schedule == []
    
    def test_send_message_without_message(self):
        """Test that _send_message handles reminders without message"""
        scheduler = MessageScheduler()
        
        reminder = {
            "date": "14-06-2026",
            "time": "10:00",
            "audience": "students"
        }
        
        result = scheduler._send_message(reminder)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
