from pathlib import Path
import json

from setproctitle import logger


def sync_json(self, json_file: Path):
    """Synchronizes the scheduled notifications in the database with the provided JSON file"""
    logger.info("Sincronizando mensajes.json")

    with open(json_file, encoding="utf8") as file:
        notifications = json.load(file)

    ids = set()
    inserted = 0
    updated = 0
    disabled = 0

    with self.db.transaction():
        for notification in notifications:
            notification_id = notification["id"]
            ids.add(notification_id)
            notification_hash = self._calculate_hash(notification)
            row = self.get_by_id(notification_id)

            # If the notification does not exist in the database, insert it
            if row is None:
                self.insert(notification_id, notification_hash, notification)
                inserted += 1
                continue

            # If the notification exists but the hash is the same, skip updating
            if row["source_hash"] == notification_hash:
                continue

            # If the notification exists and the hash is different, update it
            self.update(notification_id, notification_hash, notification)
            updated += 1

        # Disable notifications that are not present in the JSON file
        self.disable(ids)
        disabled += 1

    logger.info(
        "Sincronización terminada "
        f"(insertados={inserted}, "
        f"actualizados={updated}, "
        f"deshabilitados={disabled})"
    )


def insert(self, notification_id, notification_hash, notification: dict):
    """Inserts a new notification into the database"""
    now = self._utcnow()
    self.db.execute(
        """
        INSERT INTO scheduled_notifications(
            id,
            enabled,
            schedule,
            provider,
            title,
            body,
            targets,
            source_hash,
            status,
            retry_count,
            created_at,
            updated_at
        )
        VALUES(
            ?,?,?,?,?,?,?,?,?,?,?,?
        )
        """,
        (
            notification_id,
            notification.get("enabled", True),
            notification["schedule"],
            notification.get("provider", "apprise"),
            notification.get("title"),
            notification["body"],
            json.dumps(notification["targets"]),
            notification_hash,
            "PENDING",
            0,
            now,
            now,
        ),
    )

    self._history(notification_id, "CREATED")


def update(self, notification_id, notification_hash, notification: dict):
    """Updates an existing notification in the database"""
    now = self._utcnow()
    self.db.execute(
        """
        UPDATE scheduled_notifications
        SET
            enabled=?,
            schedule=?,
            provider=?,
            title=?,
            body=?,
            targets=?,
            source_hash=?,
            updated_at=?
        WHERE id=?
        """,
        (
            notification.get("enabled", True),
            notification["schedule"],
            notification.get("provider", "apprise"),
            notification.get("title"),
            notification["body"],
            json.dumps(notification["targets"]),
            notification_hash,
            now,
            notification_id,
        ),
    )

    self._history(notification_id, "UPDATED")


def disable(self, ids: set):
    """Disables notifications that are not present in the provided set of IDs"""
    database_ids = self.fetch_all()

    for row in database_ids:
        notification_id = row["id"]

        if notification_id in ids:
            continue

        self.disable(notification_id)
        self._history(notification_id, "DISABLED")


def fetch_all(self):
    """Fetches all enabled notifications from the database"""
    return self.db.fetch_all(
        """
            SELECT id
            FROM scheduled_notifications
            WHERE enabled=1
            """
    )


# End-of-file (EOF)
