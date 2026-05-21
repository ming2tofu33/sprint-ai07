import os
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    configured_path = os.getenv("MISSION18_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parent.parent / "data" / "mission18.db"


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_date TEXT NOT NULL,
                director TEXT NOT NULL,
                genre TEXT NOT NULL,
                poster_url TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                content TEXT NOT NULL,
                sentiment_label TEXT NOT NULL,
                sentiment_score REAL NOT NULL,
                sentiment_confidence REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
            )
            """
        )
