"""Tests for named notification destinations."""

from unittest.mock import Mock

from src.scheduler import notification
from src.scheduler.notification import NotificationService


def test_send_uses_only_selected_named_recipient(monkeypatch):
    monkeypatch.setenv("RECIPIENT_DISCORD_MATH", "discord://math_id/math_token")
    monkeypatch.setenv("RECIPIENT_DISCORD_STAFF", "discord://staff_id/staff_token")

    apprise_instance = Mock()
    apprise_instance.add.return_value = True
    apprise_instance.notify.return_value = True
    monkeypatch.setattr(
        notification.apprise, "Apprise", Mock(return_value=apprise_instance)
    )

    result = NotificationService().send("Math reminder", recipients="discord_math")

    assert result is True
    apprise_instance.add.assert_called_once_with("discord://math_id/math_token")
    apprise_instance.notify.assert_called_once()


def test_send_combines_multiple_named_recipients(monkeypatch):
    monkeypatch.setenv("RECIPIENT_MATH", "discord://math_id/math_token")
    monkeypatch.setenv("RECIPIENT_HISTORY", "discord://history_id/history_token")

    apprise_instance = Mock()
    apprise_instance.add.return_value = True
    apprise_instance.notify.return_value = True
    monkeypatch.setattr(
        notification.apprise, "Apprise", Mock(return_value=apprise_instance)
    )

    result = NotificationService().send(
        "Shared reminder", recipients=["math", "history"]
    )

    assert result is True
    apprise_instance.add.assert_called_once_with(
        "discord://math_id/math_token,discord://history_id/history_token"
    )


def test_unknown_named_recipient_does_not_fall_back(monkeypatch):
    monkeypatch.delenv("RECIPIENTS", raising=False)
    monkeypatch.delenv("RECIPIENT_UNKNOWN", raising=False)
    apprise_factory = Mock()
    monkeypatch.setattr(notification.apprise, "Apprise", apprise_factory)

    result = NotificationService().send("Should not broadcast", recipients="unknown")

    assert result is False
    apprise_factory.assert_not_called()


def test_missing_name_uses_legacy_recipients(monkeypatch):
    monkeypatch.setenv("RECIPIENTS", "discord://legacy_id/legacy_token")
    apprise_instance = Mock()
    apprise_instance.add.return_value = True
    apprise_instance.notify.return_value = True
    monkeypatch.setattr(
        notification.apprise, "Apprise", Mock(return_value=apprise_instance)
    )

    result = NotificationService().send("Legacy message")

    assert result is True
    apprise_instance.add.assert_called_once_with("discord://legacy_id/legacy_token")
