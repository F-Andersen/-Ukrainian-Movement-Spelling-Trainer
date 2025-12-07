# main.pyw
from db import init_db
from questions import ensure_questions_seeded
from ui import SpellingTrainerApp


if __name__ == "__main__":
    init_db()
    ensure_questions_seeded()   # один раз заповнює базу стартовими питаннями, якщо вона порожня
    app = SpellingTrainerApp()
    app.mainloop()
