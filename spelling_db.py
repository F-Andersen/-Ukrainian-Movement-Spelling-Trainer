# spelling_db.py
import sqlite3
import datetime

DB_NAME = "spelling_trainer.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def init_db():
    """Створення таблиць для тренажера правопису."""
    with get_connection() as conn:
        cur = conn.cursor()

        # Таблиця питань
        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option CHAR(1) NOT NULL CHECK (correct_option IN ('A','B','C','D')),
            category TEXT NOT NULL
        );
        """)

        # Таблиця результатів (рейтинг)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            score_percent REAL NOT NULL,
            time_used_seconds INTEGER NOT NULL,
            taken_at TEXT NOT NULL
        );
        """)

        conn.commit()


# ---------------------- ОПЕРАЦІЇ З ПИТАННЯМИ ----------------------

def get_questions_by_category(category):
    """Отримати всі питання певної категорії."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, text, option_a, option_b, option_c, option_d, correct_option, category
            FROM questions
            WHERE category = ?
        """, (category,))
        return cur.fetchall()


def count_questions():
    """Загальна кількість питань (для контролю)."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions")
        return cur.fetchone()[0]


# ---------------------- ОПЕРАЦІЇ З РЕЗУЛЬТАТАМИ ----------------------

def save_result(full_name, total_questions, correct_answers, score_percent, time_used_seconds):
    """Зберегти результат проходження тесту."""
    taken_at = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO results
            (full_name, total_questions, correct_answers, score_percent, time_used_seconds, taken_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (full_name, total_questions, correct_answers, score_percent, time_used_seconds, taken_at))
        conn.commit()


def get_rating(limit=50):
    """
    Отримати рейтинг: найкращі результати,
    спочатку за відсотком, потім за часом.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT full_name, total_questions, correct_answers,
                   score_percent, time_used_seconds, taken_at
            FROM results
            ORDER BY score_percent DESC,
                     time_used_seconds ASC,
                     taken_at ASC
            LIMIT ?
        """, (limit,))
        return cur.fetchall()
