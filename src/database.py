"""
database.py

Administrador de SQLite.

Toda la aplicación utiliza esta clase para acceder a la base.
Ningún otro módulo debe importar sqlite3 directamente.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Any, Generator

from loguru import logger


class Database:
    """Singleton class for managing SQLite database connections and operations"""

    _instance: "Database | None" = None
    _lock = Lock()

    def __new__(cls, db_path: str):
        """Ensures that only one instance of the Database class is created (Singleton pattern)"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, db_path: str):
        """Initializes the database connection and sets up the schema if not already initialized"""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(
            self.db_path, check_same_thread=False, isolation_level=None
        )

        self.connection.row_factory = sqlite3.Row
        self._configure()
        self._create_schema()
        logger.info(f"SQLite inicializada ({self.db_path})")

    # ----------------------------------------------------------

    def _configure(self):
        """Configures SQLite PRAGMA settings for performance and reliability"""
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA busy_timeout = 5000;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA cache_size = -20000;")
        cursor.close()

    # ----------------------------------------------------------

    def _create_schema(self):
        """Creates the database schema if it does not already exist"""
        cursor = self.connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS scheduled_notifications(
                id TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL,
                schedule TEXT NOT NULL,
                provider TEXT NOT NULL,
                title TEXT,
                body TEXT NOT NULL,
                targets TEXT NOT NULL,
                hash TEXT NOT NULL,
                status TEXT NOT NULL,
                retry_count INTEGER NOT NULL DEFAULT 0,
                sent_at TEXT,
                last_error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notification_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_id TEXT NOT NULL,
                event TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(notification_id)
                    REFERENCES scheduled_notifications(id)
            );

            CREATE INDEX IF NOT EXISTS idx_schedule
            ON scheduled_notifications(schedule);

            CREATE INDEX IF NOT EXISTS idx_status
            ON scheduled_notifications(status);

            CREATE INDEX IF NOT EXISTS idx_enabled
            ON scheduled_notifications(enabled);

            CREATE INDEX IF NOT EXISTS idx_history_notification
            ON notification_history(notification_id);
            """
        )

        cursor.close()

    # ----------------------------------------------------------

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for executing a transaction with rollback on error"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("BEGIN")
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            logger.exception("Rollback realizado")
            raise
        finally:
            cursor.close()

    # ----------------------------------------------------------

    def execute(self, sql: str, parameters: tuple[Any, ...] = ()) -> None:
        """Executes a single SQL statement with optional parameters"""
        with self.transaction() as conn:
            conn.execute(sql, parameters)

    # ----------------------------------------------------------

    def executemany(self, sql: str, values: list[tuple]):
        """Executes a multiple SQL statements with optional parameters"""
        with self.transaction() as conn:
            conn.executemany(sql, values)

    # ----------------------------------------------------------

    def fetch_one(
        self, sql: str, parameters: tuple[Any, ...] = ()
    ) -> sqlite3.Row | None:
        """Executes a SQL statement and returns a single resulting row"""
        cursor = self.connection.execute(sql, parameters)
        return cursor.fetchone()

    # ----------------------------------------------------------

    def fetch_all(
        self, sql: str, parameters: tuple[Any, ...] = ()
    ) -> list[sqlite3.Row]:
        """Executes a SQL statement and returns all resulting rows"""
        cursor = self.connection.execute(sql, parameters)
        return cursor.fetchall()

    # ----------------------------------------------------------

    def scalar(self, sql: str, parameters: tuple[Any, ...] = ()):
        """Executes a SQL statement and returns a single scalar value"""
        cursor = self.connection.execute(sql, parameters)
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

    # ----------------------------------------------------------

    def close(self):
        """Closes the database connection"""
        logger.info("Cerrando SQLite")
        self.connection.close()


# End-of-file (EOF)
