from __future__ import annotations

import hashlib
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from loguru import logger

from app.database import Database


class NotificationRepository:
    """Repository for managing scheduled notifications in the database"""

    def __init__(self, database: Database):
        """Initializes the repository with a database connection"""
        self.db = database

    # ==========================================================
    # Helper methods
    # ==========================================================

    @staticmethod
    def _utcnow() -> str:
        """Returns the current UTC time in ISO 8601 format"""
        return datetime.now(UTC).isoformat(timespec="seconds")

    @staticmethod
    def _calculate_hash(notification: dict[str, Any]) -> str:
        """Calculates a SHA256 hash of the notification dictionary"""
        serialized = json.dumps(notification, sort_keys=True, ensure_ascii=False)

        return hashlib.sha256(serialized.encode("utf8")).hexdigest()

    def _history(
        self, notification_id: str, event: str, detail: str | None = None
    ) -> None:
        """Inserts a record into the notification history table"""
        self.db.execute(
            """
            INSERT INTO notification_history(
                notification_id,
                event,
                detail,
                created_at
            )
            VALUES(?,?,?,?)
            """,
            (notification_id, event, detail, self._utcnow()),
        )

    # ==========================================================
    # CRUD operations
    # ==========================================================

    def exists(self, notification_id: str) -> bool:
        """Checks if a notification exists in the database"""
        row = self.db.scalar(
            """
            SELECT COUNT(*)
            FROM scheduled_notifications
            WHERE id=?
            """,
            (notification_id,),
        )

        return row > 0

    def get_by_id(self, notification_id: str):
        """Returns a notification by its ID"""
        return self.db.fetch_one(
            """
            SELECT *
            FROM scheduled_notifications
            WHERE id=?
            """,
            (notification_id,),
        )

    def get_pending(self, limit: int = 100):
        """Returns pending notifications up to the specified limit"""
        return self.db.fetch_all(
            """
            SELECT *
            FROM scheduled_notifications
            WHERE enabled=1
            AND status='PENDING'
            AND schedule<=?
            ORDER BY schedule
            LIMIT ?
            """,
            (self._utcnow(), limit),
        )

    def get_all(self):
        """Returns all scheduled notifications"""
        return self.db.fetch_all(
            """
            SELECT *
            FROM scheduled_notifications
            ORDER BY schedule
            """
        )

    # ==========================================================
    # State management
    # ==========================================================

    def mark_sent(self, notification_id: str):
        """Marks a notification as sent"""
        now = self._utcnow()

        self.db.execute(
            """
            UPDATE scheduled_notifications
            SET
                status='SENT',
                sent_at=?,
                updated_at=?
            WHERE id=?
            """,
            (now, now, notification_id),
        )

        self._history(notification_id, "SENT")

    def mark_error(self, notification_id: str, error: str):
        """Marks a notification as error and increments the retry count"""
        self.db.execute(
            """
            UPDATE scheduled_notifications
            SET
                status='ERROR',
                retry_count=retry_count+1,
                last_error=?,
                updated_at=?
            WHERE id=?
            """,
            (error, self._utcnow(), notification_id),
        )

        self._history(notification_id, "ERROR", error)

    def enable(self, notification_id: str):
        """Enables a notification for processing"""
        self.db.execute(
            """
            UPDATE scheduled_notifications
            SET
                enabled=1,
                updated_at=?
            WHERE id=?
            """,
            (self._utcnow(), notification_id),
        )

    def disable(self, notification_id: str):
        """Disables a scheduled notification"""
        self.db.execute(
            """
            UPDATE scheduled_notifications
            SET
                enabled=0,
                updated_at=?
            WHERE id=?
            """,
            (self._utcnow(), notification_id),
        )


# End-of-file (EOF)
