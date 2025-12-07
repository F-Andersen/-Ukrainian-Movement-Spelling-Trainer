# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

from db import save_result, get_top_results
from questions import (
    generate_test_questions,
    get_all_questions,
    insert_question,
    update_question,
    delete_question,
)
from engine import score_test

TEST_TIME_SECONDS = 300  # 5 хвилин


class SpellingTrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Тренажер з правопису української мови")
        self.geometry("880x560")

        self.full_name = ""
        self.questions = []
        self.user_answers = []
        self.current_index = 0
        self.remaining_seconds = TEST_TIME_SECONDS
        self.timer_id = None
        self.current_option_var = tk.IntVar(value=-1)
        self.mode = "exam"  # "exam" | "train"

        # Для режиму викладача
        self.teacher_window = None
        self.teacher_selected_qid = None

        self.start_frame = None
        self.test_frame = None
        self.result_frame = None

        self.create_start_screen()

    # ---------- Стартовий екран ----------
    def create_start_screen(self):
        self.start_frame = ttk.Frame(self)
        self.start_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(
            self.start_frame,
            text="Тренажер з правопису української мови",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        info_text = (
            "Екзаменаційний режим: 15 питань (по 3 з 5 типів), 5 хвилин, результат у рейтингу.\n"
            "Тренувальний режим: ті ж питання, але без таймера і без занесення в рейтинг,\n"
            "із можливістю переглянути правильні відповіді та пояснення."
        )
        ttk.Label(self.start_frame, text=info_text, justify="center").pack(pady=10)

        name_frame = ttk.Frame(self.start_frame)
        name_frame.pack(pady=10)
        ttk.Label(name_frame, text="Введіть ПІБ:").pack(side="left", padx=5)
        self.name_entry = ttk.Entry(name_frame, width=40)
        self.name_entry.pack(side="left", padx=5)

        # Вибір режиму
        self.mode_var = tk.StringVar(value="exam")
        mode_frame = ttk.LabelFrame(self.start_frame, text="Режим роботи")
        mode_frame.pack(pady=10, fill="x")

        ttk.Radiobutton(
            mode_frame,
            text="Екзамен (з таймером, з рейтингом)",
            variable=self.mode_var,
            value="exam"
        ).pack(anchor="w", padx=10, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="Тренування (без таймера, без рейтингу)",
            variable=self.mode_var,
            value="train"
        ).pack(anchor="w", padx=10, pady=2)

        btn_frame = ttk.Frame(self.start_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Почати тест", command=self.start_test)\
            .pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Переглянути рейтинг", command=self.show_rating_window)\
            .pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Режим викладача", command=self.open_teacher_window)\
            .pack(side="left", padx=5)

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
        self.mode = self.mode_var.get()
        self.user_answers = [None] * len(self.questions)
        self.current_index = 0
        self.current_option_var.set(-1)

        if self.mode == "exam":
            self.remaining_seconds = TEST_TIME_SECONDS
        else:
            self.remaining_seconds = None

        self.start_frame.pack_forget()
        self.build_test_ui()
        self.show_question()

        if self.mode == "exam":
            self.update_timer()
        else:
            self.timer_label.config(text="Режим тренування (без обмеження часу)")

    # ---------- Екран тесту ----------
    def build_test_ui(self):
        self.test_frame = ttk.Frame(self)
        self.test_frame.pack(fill="both", expand=True, padx=20, pady=20)

        top_frame = ttk.Frame(self.test_frame)
        top_frame.pack(fill="x")

        self.progress_label = ttk.Label(top_frame, text="")
        self.progress_label.pack(side="left")

        self.timer_label = ttk.Label(top_frame, text="", font=("Arial", 12, "bold"))
        self.timer_label.pack(side="right")

        self.category_label = ttk.Label(self.test_frame, text="", font=("Arial", 11, "italic"))
        self.category_label.pack(pady=5)

        self.question_label = ttk.Label(
            self.test_frame, text="", wraplength=820, justify="left"
        )
        self.question_label.pack(pady=10)

        self.options_frame = ttk.Frame(self.test_frame)
        self.options_frame.pack(pady=10, fill="x")

        bottom_frame = ttk.Frame(self.test_frame)
        bottom_frame.pack(fill="x", pady=10)

        self.finish_btn = ttk.Button(bottom_frame, text="Завершити тест", command=self.finish_test_manual)
        self.finish_btn.pack(side="right", padx=5)

        self.next_btn = ttk.Button(bottom_frame, text="Наступне питання", command=self.next_question)
        self.next_btn.pack(side="right", padx=5)

    def show_question(self):
        q = self.questions[self.current_index]

        self.progress_label.config(
            text=f"Питання {self.current_index + 1} із {len(self.questions)}"
        )
        self.category_label.config(text=f"Тип завдання: {q['category']}")
        self.question_label.config(text=q["text"])

        for w in self.options_frame.winfo_children():
            w.destroy()

        current_answer = self.user_answers[self.current_index]
        if current_answer is None:
            self.current_option_var.set(-1)
        else:
            self.current_option_var.set(current_answer)

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
        if self.remaining_seconds is None:
            return

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
        if messagebox.askyesno("Підтвердження", "Завершити тест достроково?"):
            self.finish_test()

    def finish_test(self, time_is_up: bool = False):
        self.store_current_answer()
        self.cancel_timer()

        score, total, category_stats = score_test(self.questions, self.user_answers)

        # У тренувальному режимі результат у рейтинг не зберігаємо
        if self.mode == "exam":
            save_result(self.full_name, score, total)

        self.test_frame.pack_forget()
        self.show_result_screen(score, total, category_stats, time_is_up)

    def show_result_screen(self, score, total, category_stats, time_is_up: bool):
        self.result_frame = ttk.Frame(self)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=20)

        if self.mode == "exam":
            title = "Час вичерпано" if time_is_up else "Тест завершено"
        else:
            title = "Тренування завершено"

        ttk.Label(self.result_frame, text=title, font=("Arial", 16, "bold")).pack(pady=10)

        percent = score / total * 100 if total > 0 else 0
        ttk.Label(self.result_frame, text=f"ПІБ: {self.full_name}").pack(pady=5)
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

        stats_frame = ttk.LabelFrame(self.result_frame, text="Результати за типами завдань")
        stats_frame.pack(pady=10, fill="x")

        for cat, st in category_stats.items():
            c = st["correct"]
            t = st["total"]
            pct = (c / t * 100) if t > 0 else 0
            ttk.Label(stats_frame, text=f"{cat}: {c}/{t} ({pct:.1f}%)").pack(anchor="w")

        btn_frame = ttk.Frame(self.result_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Переглянути відповіді",
                   command=self.show_answers_window).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Переглянути рейтинг",
                   command=self.show_rating_window).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Новий тест",
                   command=self.restart_app).pack(side="left", padx=5)

    def restart_app(self):
        self.destroy()
        app = SpellingTrainerApp()
        app.mainloop()

    # ---------- Вікно з відповідями ----------
    def show_answers_window(self):
        top = tk.Toplevel(self)
        top.title("Перегляд відповідей")
        top.geometry("980x520")

        columns = ("idx", "category", "question", "your", "correct", "result", "expl")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=20)
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tree.heading("idx", text="№")
        tree.heading("category", text="Тип")
        tree.heading("question", text="Питання")
        tree.heading("your", text="Ваша відповідь")
        tree.heading("correct", text="Правильна відповідь")
        tree.heading("result", text="✓ / ✗")
        tree.heading("expl", text="Пояснення")

        tree.column("idx", width=40, anchor="center")
        tree.column("category", width=130, anchor="center")
        tree.column("question", width=260, anchor="w")
        tree.column("your", width=150, anchor="w")
        tree.column("correct", width=150, anchor="w")
        tree.column("result", width=60, anchor="center")
        tree.column("expl", width=220, anchor="w")

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        for i, q in enumerate(self.questions):
            cat = q.get("category", "")
            text = q["text"]
            options = q["options"]
            correct_idx = q["correct"]
            correct_text = options[correct_idx]

            ua = self.user_answers[i]
            your_text = options[ua] if ua is not None and 0 <= ua < len(options) else "(немає відповіді)"
            res = "✓" if ua == correct_idx else "✗"
            expl = q.get("explanation", "") or "(пояснення не задано)"

            short_q = (text[:90] + "...") if len(text) > 90 else text

            tree.insert(
                "", "end",
                values=(i + 1, cat, short_q, your_text, correct_text, res, expl)
            )

    # ---------- Рейтинг ----------
    def show_rating_window(self):
        top = tk.Toplevel(self)
        top.title("Рейтинг результатів")
        top.geometry("700x430")

        header_frame = ttk.Frame(top)
        header_frame.pack(fill="x", pady=10)

        ttk.Label(header_frame, text="Рейтинг результатів (топ-20)",
                  font=("Arial", 12, "bold")).pack(side="left", padx=10)

        ttk.Button(header_frame, text="Експорт у CSV",
                   command=self.export_rating_csv).pack(side="right", padx=10)

        columns = ("full_name", "score", "percent", "date_time")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=15)
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tree.heading("full_name", text="ПІБ")
        tree.heading("score", text="Бал")
        tree.heading("percent", text="%")
        tree.heading("date_time", text="Дата та час")

        tree.column("full_name", width=240)
        tree.column("score", width=70, anchor="center")
        tree.column("percent", width=60, anchor="center")
        tree.column("date_time", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        rows = get_top_results(limit=20)
        for full_name, score, total, percent, dt in rows:
            tree.insert("", "end", values=(full_name, f"{score}/{total}", f"{percent:.1f}", dt))

    def export_rating_csv(self):
        filename = filedialog.asksaveasfilename(
            title="Зберегти рейтинг у CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return

        rows = get_top_results(limit=1000)
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["ПІБ", "Бал (правильно/всього)", "Відсоток", "Дата та час"])
                for full_name, score, total, percent, dt in rows:
                    writer.writerow([full_name, f"{score}/{total}", f"{percent:.1f}", dt])
            messagebox.showinfo("Експорт", "Рейтинг успішно збережено у CSV.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")

    # ---------- Режим викладача ----------
    def open_teacher_window(self):
        if self.teacher_window is not None and tk.Toplevel.winfo_exists(self.teacher_window):
            self.teacher_window.lift()
            return

        self.teacher_window = tk.Toplevel(self)
        self.teacher_window.title("Режим викладача – редагування питань")
        self.teacher_window.geometry("1050x560")

        main_frame = ttk.Frame(self.teacher_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Ліва частина – список питань
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columns = ("id", "category", "level", "text")
        self.teacher_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
        self.teacher_tree.pack(side="left", fill="both", expand=True)

        self.teacher_tree.heading("id", text="ID")
        self.teacher_tree.heading("category", text="Категорія")
        self.teacher_tree.heading("level", text="Рівень")
        self.teacher_tree.heading("text", text="Питання")

        self.teacher_tree.column("id", width=40, anchor="center")
        self.teacher_tree.column("category", width=120, anchor="center")
        self.teacher_tree.column("level", width=60, anchor="center")
        self.teacher_tree.column("text", width=280, anchor="w")

        scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.teacher_tree.yview)
        self.teacher_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        self.teacher_tree.bind("<<TreeviewSelect>>", self.teacher_on_select)

        # Права частина – форма редагування
        right_frame = ttk.LabelFrame(main_frame, text="Питання")
        right_frame.pack(side="right", fill="both", expand=True)

        # Категорія + рівень
        row = 0
        ttk.Label(right_frame, text="Категорія:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.t_cat_entry = ttk.Entry(right_frame, width=30)
        self.t_cat_entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(right_frame, text="Рівень (1–3):").grid(row=row, column=2, sticky="e", padx=5, pady=3)
        self.t_level_spin = ttk.Spinbox(right_frame, from_=1, to=3, width=5)
        self.t_level_spin.grid(row=row, column=3, sticky="w", padx=5, pady=3)
        self.t_level_spin.delete(0, tk.END)
        self.t_level_spin.insert(0, "1")

        # Текст питання
        row += 1
        ttk.Label(right_frame, text="Текст питання:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.t_text = tk.Text(right_frame, width=60, height=4, wrap="word")
        self.t_text.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=3)

        # Варіанти
        row += 1
        ttk.Label(right_frame, text="Варіант 1:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.t_opt1 = ttk.Entry(right_frame, width=40)
        self.t_opt1.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=2)

        row += 1
        ttk.Label(right_frame, text="Варіант 2:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.t_opt2 = ttk.Entry(right_frame, width=40)
        self.t_opt2.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=2)

        row += 1
        ttk.Label(right_frame, text="Варіант 3:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.t_opt3 = ttk.Entry(right_frame, width=40)
        self.t_opt3.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=2)

        row += 1
        ttk.Label(right_frame, text="Варіант 4:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.t_opt4 = ttk.Entry(right_frame, width=40)
        self.t_opt4.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=2)

        # Правильна відповідь
        row += 1
        ttk.Label(right_frame, text="Номер правильної відповіді (1–4):")\
            .grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.t_correct_spin = ttk.Spinbox(right_frame, from_=1, to=4, width=5)
        self.t_correct_spin.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.t_correct_spin.delete(0, tk.END)
        self.t_correct_spin.insert(0, "1")

        # Пояснення
        row += 1
        ttk.Label(right_frame, text="Пояснення:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.t_expl = tk.Text(right_frame, width=60, height=4, wrap="word")
        self.t_expl.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=3)

        # Кнопки
        row += 1
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=row, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Очистити форму",
                   command=self.teacher_clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Зберегти як нове",
                   command=self.teacher_save_new).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Оновити вибране",
                   command=self.teacher_update).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Видалити вибране",
                   command=self.teacher_delete).pack(side="left", padx=5)

        self.teacher_selected_qid = None
        self.teacher_refresh_list()

    def teacher_refresh_list(self):
        for row in self.teacher_tree.get_children():
            self.teacher_tree.delete(row)

        rows = get_all_questions()
        for (qid, cat, text, o1, o2, o3, o4, corr, expl, level) in rows:
            short_text = (text[:80] + "...") if len(text) > 80 else text
            self.teacher_tree.insert("", "end",
                                     values=(qid, cat, level, short_text))

    def teacher_on_select(self, event):
        sel = self.teacher_tree.selection()
        if not sel:
            self.teacher_selected_qid = None
            return

        item = self.teacher_tree.item(sel[0])
        qid = item["values"][0]
        self.teacher_selected_qid = qid

        # Дістаємо повні дані по цьому питанню
        rows = get_all_questions()
        data = None
        for row in rows:
            if row[0] == qid:
                data = row
                break
        if not data:
            return

        (_id, cat, text, o1, o2, o3, o4, corr, expl, level) = data

        self.t_cat_entry.delete(0, tk.END)
        self.t_cat_entry.insert(0, cat)

        self.t_level_spin.delete(0, tk.END)
        self.t_level_spin.insert(0, str(level))

        self.t_text.delete("1.0", tk.END)
        self.t_text.insert("1.0", text)

        for entry, val in [
            (self.t_opt1, o1),
            (self.t_opt2, o2),
            (self.t_opt3, o3),
            (self.t_opt4, o4),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, val)

        self.t_correct_spin.delete(0, tk.END)
        self.t_correct_spin.insert(0, str(corr + 1))  # в БД 0..3, у формі 1..4

        self.t_expl.delete("1.0", tk.END)
        self.t_expl.insert("1.0", expl or "")

    def teacher_clear_form(self):
        self.teacher_selected_qid = None
        self.t_cat_entry.delete(0, tk.END)
        self.t_cat_entry.insert(0, "")
        self.t_level_spin.delete(0, tk.END)
        self.t_level_spin.insert(0, "1")
        self.t_text.delete("1.0", tk.END)
        for entry in (self.t_opt1, self.t_opt2, self.t_opt3, self.t_opt4):
            entry.delete(0, tk.END)
        self.t_correct_spin.delete(0, tk.END)
        self.t_correct_spin.insert(0, "1")
        self.t_expl.delete("1.0", tk.END)

    def _teacher_read_form(self):
        cat = self.t_cat_entry.get().strip()
        level_raw = self.t_level_spin.get().strip()
        text = self.t_text.get("1.0", tk.END).strip()
        o1 = self.t_opt1.get().strip()
        o2 = self.t_opt2.get().strip()
        o3 = self.t_opt3.get().strip()
        o4 = self.t_opt4.get().strip()
        corr_raw = self.t_correct_spin.get().strip()
        expl = self.t_expl.get("1.0", tk.END).strip()

        if not cat:
            raise ValueError("Категорія обов'язкова.")
        if not text:
            raise ValueError("Текст питання обов'язковий.")
        options = [o1, o2, o3, o4]
        if any(not o for o in options):
            raise ValueError("Усі 4 варіанти відповіді мають бути заповнені.")
        try:
            level = int(level_raw)
        except Exception:
            raise ValueError("Рівень має бути числом (1–3).")
        try:
            corr = int(corr_raw)
        except Exception:
            raise ValueError("Номер правильної відповіді має бути числом від 1 до 4.")
        if not 1 <= corr <= 4:
            raise ValueError("Номер правильної відповіді має бути від 1 до 4.")

        correct_index = corr - 1  # в БД зберігаємо 0..3
        return cat, text, options, correct_index, expl, level

    def teacher_save_new(self):
        try:
            cat, text, options, correct_index, expl, level = self._teacher_read_form()
            insert_question(cat, text, options, correct_index, expl, level)
            messagebox.showinfo("Успіх", "Питання додано.")
            self.teacher_refresh_list()
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def teacher_update(self):
        if self.teacher_selected_qid is None:
            messagebox.showerror("Помилка", "Спочатку оберіть питання у списку.")
            return
        try:
            cat, text, options, correct_index, expl, level = self._teacher_read_form()
            update_question(self.teacher_selected_qid, cat, text, options, correct_index, expl, level)
            messagebox.showinfo("Успіх", "Питання оновлено.")
            self.teacher_refresh_list()
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def teacher_delete(self):
        if self.teacher_selected_qid is None:
            messagebox.showerror("Помилка", "Спочатку оберіть питання у списку.")
            return
        if not messagebox.askyesno("Підтвердження", "Видалити вибране питання?"):
            return
        delete_question(self.teacher_selected_qid)
        messagebox.showinfo("Успіх", "Питання видалено.")
        self.teacher_selected_qid = None
        self.teacher_refresh_list()
        self.teacher_clear_form()
