import sqlite3
from datetime import datetime
from storage.base import BaseStorage


class SqliteStorage(BaseStorage):
    """Сохраняет результаты в SQLite (снимки рынка)."""

    def __init__(self, db_path: str = "crypto.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self) -> None:
        """Создаёт таблицы если их нет."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coin_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_24h REAL NOT NULL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                )
            """)
            conn.commit()

    def save(self, results: dict) -> None:
        """Сохраняет новый снимок с ценами."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Создаём снимок
            cursor.execute(
                "INSERT INTO snapshots (created_at) VALUES (?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
            )
            snapshot_id = cursor.lastrowid
            
            # Сохраняем цены
            for coin in results.get("top_gainers", []):
                cursor.execute(
                    "INSERT INTO coin_prices (snapshot_id, name, symbol, price, change_24h) VALUES (?, ?, ?, ?, ?)",
                    (snapshot_id, coin["name"], coin["symbol"], 0.0, coin["change_24h"])
                )
            
            conn.commit()