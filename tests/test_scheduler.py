"""Tests for scheduler module"""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.scheduler import MessageScheduler
from src.scheduler.config import Config


class TestMessageScheduler:
    """Tests for MessageScheduler"""

    def test_initialization(self):
        """Test that scheduler initializes correctly"""
        scheduler = MessageScheduler()
        assert scheduler.schedule_path == Config.SCHEDULE_PATH
        assert scheduler.notification_service is not None
        assert isinstance(scheduler.schedule, list)

    def test_get_current_time_uses_configured_timezone(self):
        """Test that current time is returned as a datetime"""
        scheduler = MessageScheduler()
        current_time = scheduler.get_current_time()

        assert isinstance(current_time, datetime)
        assert current_time.tzinfo is not None

    def test_round_time(self):
        """Test that time rounding works correctly"""
        scheduler = MessageScheduler()

        # Create datetime with specific minutes
        dt = datetime(2026, 6, 14, 10, 23, 0)
        date, time = scheduler.round_time(dt)

        # Verify date format
        assert date == "14-06-2026"

        # The default is to round down to the hour (60 minutes).
        assert time == "10:00"

    def test_match_schedule(self):
        """Test that schedule matching works"""
        scheduler = MessageScheduler()

        reminder = {
            "date": "14-06-2026",
            "time": "10:00",
            "message": "Test",
            "audience": "students",
        }

        # Case that matches
        assert scheduler._match_schedule(reminder, "14-06-2026", "10:00") is True

        # Cases that don't match
        assert scheduler._match_schedule(reminder, "14-06-2026", "10:05") is False
        assert scheduler._match_schedule(reminder, "15-06-2026", "10:00") is False

    def test_match_schedule_pairs_date_and_time_arrays_by_position(self):
        scheduler = MessageScheduler()
        current_year = datetime.now(timezone.utc).year
        reminder = {
            "date": ["20-10", "21-10", "22-10"],
            "time": ["10:00", "11:00", "12:00"],
        }

        assert (
            scheduler._match_schedule(reminder, f"21-10-{current_year}", "11:00")
            is True
        )
        assert (
            scheduler._match_schedule(reminder, f"21-10-{current_year}", "10:00")
            is False
        )

    def test_match_schedule_reuses_scalar_date_or_time(self):
        scheduler = MessageScheduler()

        assert (
            scheduler._match_schedule(
                {"date": "21-10", "time": ["10:00", "11:00"]},
                "21-10-2026",
                "11:00",
            )
            is True
        )
        assert (
            scheduler._match_schedule(
                {"date": ["20-10", "21-10"], "time": "11:00"},
                "21-10-2026",
                "11:00",
            )
            is True
        )

    def test_match_schedule_rejects_different_array_lengths(self):
        scheduler = MessageScheduler()
        reminder = {"date": ["20-10", "21-10"], "time": ["10:00", "11:00", "12:00"]}

        assert scheduler._match_schedule(reminder, "21-10-2026", "11:00") is False

    def test_load_schedule_not_exists(self):
        """Test that load_schedule handles file not found"""
        scheduler = MessageScheduler(schedule_path=Path("/nonexistent/path.json"))
        result = scheduler.load_schedule()

        assert result is False
        assert scheduler.schedule == []

    def test_send_message_without_message(self):
        """Test that _send_message handles reminders without message"""
        scheduler = MessageScheduler()

        reminder = {"date": "14-06-2026", "time": "10:00", "audience": "students"}

        result = scheduler._send_message(reminder)
        assert result is False

    def test_send_message_routes_to_named_recipient(self, monkeypatch):
        scheduler = MessageScheduler()
        calls = []
        monkeypatch.setattr(
            scheduler.notification_service,
            "send",
            lambda **kwargs: calls.append(kwargs) or True,
        )

        result = scheduler._send_message({"message": "For math", "recipient": "math"})

        assert result is True
        assert calls == [{"message": "For math", "recipients": "math"}]

    def test_send_message_routes_to_multiple_named_recipients(self, monkeypatch):
        scheduler = MessageScheduler()
        calls = []
        monkeypatch.setattr(
            scheduler.notification_service,
            "send",
            lambda **kwargs: calls.append(kwargs) or True,
        )

        result = scheduler._send_message(
            {
                "message": "For both",
                "recipients": ["math", "history"],
            }
        )

        assert result is True
        assert calls == [{"message": "For both", "recipients": ["math", "history"]}]

    def test_send_message_without_recipient_uses_legacy_default(self, monkeypatch):
        scheduler = MessageScheduler()
        calls = []
        monkeypatch.setattr(
            scheduler.notification_service,
            "send",
            lambda **kwargs: calls.append(kwargs) or True,
        )

        result = scheduler._send_message({"message": "Legacy message"})

        assert result is True
        assert calls == [{"message": "Legacy message", "recipients": None}]

    def test_send_message_rejects_invalid_recipients(self, monkeypatch):
        scheduler = MessageScheduler()
        monkeypatch.setattr(
            scheduler.notification_service,
            "send",
            lambda **kwargs: pytest.fail(
                "send must not be called for invalid recipients"
            ),
        )

        result = scheduler._send_message({"message": "Test", "recipients": 12})

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
