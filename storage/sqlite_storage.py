import sqlite3
from datetime import datetime

from storage.base import BaseStorage


class SqliteStorage(BaseStorage):
    """Сохраняет результаты в SQLite и умеет анализировать снимки."""

    def __init__(self, db_path: str = "crypto.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)  #  соединение с БД в памяти
        self._conn.row_factory = sqlite3.Row  # чтобы строки возвращались как dict
        self._create_tables()  # создаёт таблицы

    def _create_tables(self) -> None:
        cursor = self._conn.cursor()
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
        self._conn.commit()

    def save(self, results: dict) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO snapshots (created_at) VALUES (?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),),
        )
        snapshot_id = cursor.lastrowid

        for coin in results.get("top_gainers", []):
            cursor.execute(
                "INSERT INTO coin_prices (snapshot_id, name, symbol, price, change_24h) VALUES (?, ?, ?, ?, ?)",
                (
                    snapshot_id,
                    coin["name"],
                    coin["symbol"],
                    coin.get("price", 0.0),
                    coin["change_24h"],
                ),
            )
        self._conn.commit()

    def list_snapshots(self) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT id, created_at FROM snapshots ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]

    def compare_snapshots(self, id1: int, id2: int) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT 
                a.name,
                a.symbol,
                a.price AS price_old,
                b.price AS price_new,
                (b.price - a.price) AS diff,
                ((b.price - a.price) / a.price * 100) AS diff_percent
            FROM coin_prices a
            JOIN coin_prices b ON a.name = b.name
            WHERE a.snapshot_id = ? AND b.snapshot_id = ?
        """,
            (id1, id2),
        )
        return [dict(row) for row in cursor.fetchall()]

    def history(self, name: str) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT s.created_at, c.price, c.change_24h
            FROM coin_prices c
            JOIN snapshots s ON c.snapshot_id = s.id
            WHERE c.name = ?
            ORDER BY s.id
        """,
            (name,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def top_movers(self, n: int = 5) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT id FROM snapshots ORDER BY id DESC LIMIT 1")
        last = cursor.fetchone()
        if not last:
            return []

        cursor.execute(
            """
            SELECT name, symbol, price, change_24h
            FROM coin_prices
            WHERE snapshot_id = ?
            ORDER BY change_24h DESC
            LIMIT ?
        """,
            (last["id"], n),
        )
        return [dict(row) for row in cursor.fetchall()]
