# db.py
import sqlite3
import datetime

DB_NAME = "spelling_trainer.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Створити всі необхідні таблиці, якщо їх ще немає."""
    with get_connection() as conn:
        cur = conn.cursor()

        # Таблиця результатів
        cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percent REAL NOT NULL,
            date_time TEXT NOT NULL
        );
        """)

        # Таблиця питань
        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            text TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            explanation TEXT,
            level INTEGER NOT NULL DEFAULT 1
        );
        """)

        conn.commit()


# --------- Рейтинг ---------

def save_result(full_name: str, score: int, total: int) -> None:
    """Зберегти результат одного тесту до БД."""
    percent = score / total * 100 if total > 0 else 0
    dt = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO results (full_name, score, total, percent, date_time)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, score, total, percent, dt))
        conn.commit()


def get_top_results(limit: int = 20):
    """Отримати топ результатів (за відсотком, потім за датою)."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT full_name, score, total, percent, date_time
            FROM results
            ORDER BY percent DESC, date_time DESC
            LIMIT ?
        """, (limit,))
        return cur.fetchall()
