import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import datetime

DB_NAME = "spelling_trainer.db"
TEST_TIME_SECONDS = 300  # 5 хвилин
QUESTIONS_PER_CATEGORY = 3


# ==================== БАЗА ДАНИХ ====================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
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
        conn.commit()


def save_result(full_name, score, total):
    percent = score / total * 100 if total > 0 else 0
    dt = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO results (full_name, score, total, percent, date_time)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, score, total, percent, dt))
        conn.commit()


def get_top_results(limit=20):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT full_name, score, total, percent, date_time
            FROM results
            ORDER BY percent DESC, date_time DESC
            LIMIT ?
        """, (limit,))
        return cur.fetchall()


# ==================== ПИТАННЯ ====================

# Кожне питання: category, text, options (list), correct_index (0..)
QUESTIONS = {
    "Орфографія": [
        {
            "text": "Укажіть слово, написане правильно:",
            "options": ["приймати", "прийматиь", "приимати", "приймать"],
            "correct": 0,
        },
        {
            "text": "Правильний варіант написання:",
            "options": ["будь-ласка", "будь ласка", "будласка", "будь, ласка"],
            "correct": 1,
        },
        {
            "text": "Укажіть слово з правильною кількістю 'н':",
            "options": ["здійсненя", "здійснення", "здійснєння", "здійсненння"],
            "correct": 1,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["запізнитися", "запізнтися", "запізнитись", "запізнтись"],
            "correct": 0,
        },
        {
            "text": "Яке слово написано з помилкою?",
            "options": ["звичайно", "справді", "досвідчений", "серйознийь"],
            "correct": 3,
        },
        {
            "text": "Правильне написання прислівника:",
            "options": ["по-українські", "по українські", "по українськи", "поукраїнські"],
            "correct": 0,
        },
        {
            "text": "Укажіть рядок, де всі слова написані правильно:",
            "options": [
                "щоденник, під'їзд, осінній",
                "щоденик, підїзд, осінній",
                "щоденник, під'їзд, осінїй",
                "шоденник, під'їзд, осінній",
            ],
            "correct": 0,
        },
        {
            "text": "Правильний варіант написання слова:",
            "options": ["громадський", "грамадський", "громацький", "громадскьий"],
            "correct": 0,
        },
        {
            "text": "Укажіть слово без орфографічної помилки:",
            "options": ["знищиити", "знищити", "знишити", "знишчити"],
            "correct": 1,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["відображення", "відоброження", "відображeння", "відображiння"],
            "correct": 0,
        },
    ],
    "Апостроф": [
        {
            "text": "Укажіть слово з правильним уживанням апострофа:",
            "options": ["бурян", "бур’ян", "бур'ян", "бур-ян"],
            "correct": 2,
        },
        {
            "text": "Укажіть правильне написання:",
            "options": ["пів'яблука", "півяблука", "пів’яблука", "пiв яблука"],
            "correct": 1,
        },
        {
            "text": "Де апостроф ставиться правильно?",
            "options": ["об'їзд", "об їзд", "об’їздь", "обйїзд"],
            "correct": 0,
        },
        {
            "text": "Правильно написано слово:",
            "options": ["п'ятниця", "пятниця", "п’ятниця", "п-ятниця"],
            "correct": 0,
        },
        {
            "text": "Укажіть правильне написання:",
            "options": ["зв'язок", "звязок", "з'вязок", "звязьок"],
            "correct": 0,
        },
        {
            "text": "Де апостроф вжито неправильно?",
            "options": ["ін'єкція", "п'єдестал", "м'яч", "м'ясо"],
            "correct": 1,
        },
        {
            "text": "Укажіть рядок з усіма правильними словами:",
            "options": [
                "м'ята, п'ю, роз'яснення",
                "мята, п'ю, роз'яснення",
                "м'ята, п'ю, розяснення",
                "м'ята, пю, роз'яснення",
            ],
            "correct": 0,
        },
        {
            "text": "Правильно:",
            "options": ["пів'Європи", "пів Європи", "півєвропи", "пiв'Європи"],
            "correct": 1,
        },
        {
            "text": "Укажіть слово з апострофом:",
            "options": ["сюита", "сюрприз", "сім'я", "синій"],
            "correct": 2,
        },
        {
            "text": "Укажіть слово, де апостроф НЕ потрібен:",
            "options": ["п'єса", "об'єкт", "под'їзд", "інєкція"],
            "correct": 3,
        },
    ],
    "М'який знак": [
        {
            "text": "Укажіть слово з правильним уживанням м'якого знака:",
            "options": ["кінь", "кинь", "кін", "киньь"],
            "correct": 0,
        },
        {
            "text": "У якому слові м'який знак НЕ пишеться?",
            "options": ["синьо", "синій", "кіньми", "ніччю"],
            "correct": 0,
        },
        {
            "text": "Правильно написане слово:",
            "options": ["мільйон", "мілйон", "мільон", "мільйонь"],
            "correct": 0,
        },
        {
            "text": "Укажіть слово з помилкою:",
            "options": ["безпечний", "серйозний", "знання", "кількістьь"],
            "correct": 3,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["нічь", "ніч", "ніч'", "ніч’"],
            "correct": 1,
        },
        {
            "text": "У якому рядку в усіх словах є м'який знак?",
            "options": [
                "кінь, пень, мільйон",
                "кін, пень, мільйон",
                "кінь, пен, мільйон",
                "кінь, пень, мілйон",
            ],
            "correct": 0,
        },
        {
            "text": "Укажіть слово, де м'який знак зайвий:",
            "options": ["сьогодні", "п'ять", "сьогоднішній", "кільцьо"],
            "correct": 3,
        },
        {
            "text": "Правильне написання імені:",
            "options": ["Андрій", "Андрiй", "Андрійь", "Андрий"],
            "correct": 0,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["пальця", "палця", "пальцйа", "пальц'я"],
            "correct": 0,
        },
        {
            "text": "У якому слові немає м'якого знака?",
            "options": ["кінь", "пень", "день", "сон"],
            "correct": 3,
        },
    ],
    "Правопис «не»": [
        {
            "text": "Укажіть рядок, де 'не' пишеться разом:",
            "options": ["(не)приємний", "(не) друг", "(не) може", "(не) був"],
            "correct": 0,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["незнаю", "не знаю", "незнаюь", "не знаюь"],
            "correct": 1,
        },
        {
            "text": "Де 'не' пишеться окремо?",
            "options": ["(не)правда (у значенні 'брехня')", "(не) буде", "(не)гарний", "(не)читаний"],
            "correct": 1,
        },
        {
            "text": "Укажіть правильну форму:",
            "options": ["нецікавий", "не цікавий (як заперечення)", "обидва варіанти можливі", "жоден не правильний"],
            "correct": 2,
        },
        {
            "text": "Укажіть слово з правильною формою:",
            "options": ["незручний", "не зручний (у значенні 'не комфортний')", "не зручний (як частка)", "незручнийь"],
            "correct": 0,
        },
        {
            "text": "У якому реченні 'не' пишеться разом?",
            "options": [
                "Це зовсім (не)важливо.",
                "Він (не) друг, а ворог.",
                "Вона (не)права у цій ситуації.",
                "Він (не) прийшов учора.",
            ],
            "correct": 2,
        },
        {
            "text": "Правильний варіант:",
            "options": ["невпевнений", "не впевнений (як заперечення)", "обидва варіанти можливі", "жоден"],
            "correct": 2,
        },
        {
            "text": "Позначте, де 'не' пишеться окремо:",
            "options": ["(не)зроблений", "(не) хотів", "(не)зручний", "(не)правильний"],
            "correct": 1,
        },
        {
            "text": "Де 'не' пишеться разом?",
            "options": ["(не)здоровий", "(не) здоровий спосіб життя", "(не) був", "(не) міг"],
            "correct": 0,
        },
        {
            "text": "Укажіть правильний рядок:",
            "options": [
                "нещасний (у значенні 'бідолашний')",
                "не щасний (у значенні 'зовсім не щасливий')",
                "обидва варіанти можливі",
                "усі неправильні",
            ],
            "correct": 2,
        },
    ],
    "Великі літери": [
        {
            "text": "Укажіть правильне написання власних назв:",
            "options": ["київ, дніпро", "Київ, Дніпро", "Киів, Дніпро", "Київ, дніпро"],
            "correct": 1,
        },
        {
            "text": "Як правильно написати назву свята?",
            "options": ["день незалежності україни", "День незалежності України", "День Незалежності України", "день Незалежності україни"],
            "correct": 1,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["Європейський союз", "європейський Союз", "Європейський Союз", "європейський союз"],
            "correct": 0,
        },
        {
            "text": "У якому рядку всі слова написані правильно?",
            "options": [
                "Президент України, Верховна Рада України",
                "президент України, Верховна рада України",
                "Президент України, Верховна рада України",
                "президент україни, верховна рада україни",
            ],
            "correct": 0,
        },
        {
            "text": "Правильне написання прізвища та імені:",
            "options": ["іван петренко", "Іван петренко", "Іван Петренко", "іван Петренко"],
            "correct": 2,
        },
        {
            "text": "Як правильно написати географічну назву?",
            "options": ["чорне море", "Чорне море", "Чорне Море", "чорне Море"],
            "correct": 1,
        },
        {
            "text": "Укажіть правильне написання назви вулиці:",
            "options": ["вулиця Шевченка", "Вулиця Шевченка", "вулиця шевченка", "Вулиця шевченка"],
            "correct": 0,
        },
        {
            "text": "Укажіть правильний запис:",
            "options": ["Західна Україна", "західна Україна (як частина світу)", "Західна україна", "західна україна"],
            "correct": 0,
        },
        {
            "text": "Як правильно написати назву держави?",
            "options": ["україна", "Україна", "УКРАЇНА", "уКраїна"],
            "correct": 1,
        },
        {
            "text": "Укажіть правильний варіант:",
            "options": ["Карпати, річка Дністер", "Карпати, Річка Дністер", "карпати, річка Дністер", "Карпати, річка дністер"],
            "correct": 0,
        },
    ],
}


def generate_test_questions():
    """Обираємо по 3 питання з кожної категорії, перемішуємо."""
    selected = []
    for cat, q_list in QUESTIONS.items():
        if len(q_list) < QUESTIONS_PER_CATEGORY:
            raise ValueError(f"У категорії '{cat}' недостатньо питань.")
        chosen = random.sample(q_list, QUESTIONS_PER_CATEGORY)
        # додаємо категорію всередину питання
        for q in chosen:
            q_copy = q.copy()
            q_copy["category"] = cat
            selected.append(q_copy)
    random.shuffle(selected)
    return selected


# ==================== GUI ====================

class SpellingTrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Тренажер з правопису української мови")
        self.geometry("800x500")

        self.full_name = ""
        self.questions = []
        self.current_index = 0
        self.user_answers = []
        self.remaining_seconds = TEST_TIME_SECONDS
        self.timer_id = None

        self.current_option_var = tk.IntVar(value=-1)

        self.create_widgets()

    # ---------- Стартове вікно ----------
    def create_widgets(self):
        self.start_frame = ttk.Frame(self)
        self.start_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(self.start_frame, text="Тренажер з правопису української мови",
                  font=("Arial", 16, "bold")).pack(pady=10)

        name_frame = ttk.Frame(self.start_frame)
        name_frame.pack(pady=10)
        ttk.Label(name_frame, text="Введіть ПІБ:").pack(side="left", padx=5)
        self.name_entry = ttk.Entry(name_frame, width=40)
        self.name_entry.pack(side="left", padx=5)

        ttk.Label(self.start_frame, text="У тесті 15 питань (по 3 з кожного з 5 типів).\n"
                                         "На виконання — 5 хвилин.",
                  justify="center").pack(pady=10)

        start_btn = ttk.Button(self.start_frame, text="Почати тест", command=self.start_test)
        start_btn.pack(pady=10)

        rating_btn = ttk.Button(self.start_frame, text="Переглянути рейтинг", command=self.show_rating_window)
        rating_btn.pack(pady=5)

    def start_test(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Помилка", "Будь ласка, введіть ПІБ.")
            return

        try:
            self.questions = generate_test_questions()
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            return

        self.full_name = name
        self.current_index = 0
        self.user_answers = [None] * len(self.questions)
        self.remaining_seconds = TEST_TIME_SECONDS

        self.start_frame.pack_forget()
        self.build_test_ui()
        self.show_question()
        self.update_timer()

    # ---------- Інтерфейс тесту ----------
    def build_test_ui(self):
        self.test_frame = ttk.Frame(self)
        self.test_frame.pack(fill="both", expand=True, padx=20, pady=20)

        top_frame = ttk.Frame(self.test_frame)
        top_frame.pack(fill="x")

        self.timer_label = ttk.Label(top_frame, text="", font=("Arial", 12, "bold"))
        self.timer_label.pack(side="right")

        self.progress_label = ttk.Label(top_frame, text="")
        self.progress_label.pack(side="left")

        self.category_label = ttk.Label(self.test_frame, text="", font=("Arial", 12, "italic"))
        self.category_label.pack(pady=5)

        self.question_text_label = ttk.Label(self.test_frame, text="", wraplength=700, justify="left")
        self.question_text_label.pack(pady=10)

        self.options_frame = ttk.Frame(self.test_frame)
        self.options_frame.pack(pady=10, fill="x")

        bottom_frame = ttk.Frame(self.test_frame)
        bottom_frame.pack(fill="x", pady=10)

        self.next_btn = ttk.Button(bottom_frame, text="Наступне питання", command=self.next_question)
        self.next_btn.pack(side="right", padx=5)

        self.finish_btn = ttk.Button(bottom_frame, text="Завершити тест", command=self.finish_test_manual)
        self.finish_btn.pack(side="right", padx=5)

    def show_question(self):
        q = self.questions[self.current_index]
        self.progress_label.config(
            text=f"Питання {self.current_index + 1} із {len(self.questions)}"
        )
        self.category_label.config(text=f"Тип завдання: {q['category']}")
        self.question_text_label.config(text=q["text"])

        for w in self.options_frame.winfo_children():
            w.destroy()

        self.current_option_var.set(-1 if self.user_answers[self.current_index] is None
                                    else self.user_answers[self.current_index])

        for idx, opt in enumerate(q["options"]):
            rb = ttk.Radiobutton(
                self.options_frame,
                text=opt,
                variable=self.current_option_var,
                value=idx
            )
            rb.pack(anchor="w", pady=2)

        if self.current_index == len(self.questions) - 1:
            self.next_btn.config(text="Завершити тест")
        else:
            self.next_btn.config(text="Наступне питання")

    def store_current_answer(self):
        val = self.current_option_var.get()
        if val >= 0:
            self.user_answers[self.current_index] = val

    def next_question(self):
        self.store_current_answer()
        if self.current_index == len(self.questions) - 1:
            self.finish_test()
            return
        self.current_index += 1
        self.show_question()

    # ---------- Таймер ----------
    def update_timer(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.timer_label.config(text=f"Залишилось часу: {minutes:02d}:{seconds:02d}")

        if self.remaining_seconds <= 0:
            self.finish_test(time_is_up=True)
            return

        self.remaining_seconds -= 1
        self.timer_id = self.after(1000, self.update_timer)

    def cancel_timer(self):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    # ---------- Завершення тесту ----------
    def finish_test_manual(self):
        if messagebox.askyesno("Підтвердження", "Бажаєте завершити тест достроково?"):
            self.finish_test()

    def finish_test(self, time_is_up=False):
        self.store_current_answer()
        self.cancel_timer()

        score = 0
        for i, q in enumerate(self.questions):
            if self.user_answers[i] == q["correct"]:
                score += 1

        total = len(self.questions)
        percent = score / total * 100 if total > 0 else 0

        save_result(self.full_name, score, total)

        self.test_frame.pack_forget()
        self.show_result_frame(score, total, percent, time_is_up)

    def show_result_frame(self, score, total, percent, time_is_up):
        self.result_frame = ttk.Frame(self)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = "Час вичерпано" if time_is_up else "Тест завершено"
        ttk.Label(self.result_frame, text=title, font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(
            self.result_frame,
            text=f"ПІБ: {self.full_name}"
        ).pack(pady=5)

        ttk.Label(
            self.result_frame,
            text=f"Результат: {score} із {total} ({percent:.1f}%)"
        ).pack(pady=5)

        if percent >= 90:
            level = "Високий рівень правопису"
        elif percent >= 70:
            level = "Достатній рівень правопису"
        elif percent >= 50:
            level = "Середній рівень правопису"
        else:
            level = "Потрібне додаткове тренування"

        ttk.Label(self.result_frame, text=level).pack(pady=5)

        btn_frame = ttk.Frame(self.result_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Переглянути рейтинг",
                   command=self.show_rating_window).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Новий тест",
                   command=self.restart_to_start_screen).pack(side="left", padx=5)

    def restart_to_start_screen(self):
        self.result_frame.pack_forget()
        self.destroy()
        # перезапускаємо застосунок
        new_app = SpellingTrainerApp()
        new_app.mainloop()

    # ---------- Рейтинг ----------
    def show_rating_window(self):
        top = tk.Toplevel(self)
        top.title("Рейтинг результатів")
        top.geometry("650x400")

        ttk.Label(top, text="Рейтинг результатів (топ-20)",
                  font=("Arial", 12, "bold")).pack(pady=10)

        columns = ("full_name", "score", "percent", "date_time")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=15)
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tree.heading("full_name", text="ПІБ")
        tree.heading("score", text="Бал")
        tree.heading("percent", text="%")
        tree.heading("date_time", text="Дата та час")

        tree.column("full_name", width=200)
        tree.column("score", width=60, anchor="center")
        tree.column("percent", width=60, anchor="center")
        tree.column("date_time", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        rows = get_top_results(limit=20)
        for full_name, score, total, percent, dt in rows:
            tree.insert("", "end", values=(full_name, f"{score}/{total}", f"{percent:.1f}", dt))


# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    init_db()
    app = SpellingTrainerApp()
    app.mainloop()
