# questions.py
import random
from db import get_connection

QUESTIONS_PER_CATEGORY = 3

# Базовий банк питань використовується як "seed" при першому запуску.
# Можна розширювати/редагувати.
QUESTION_BANK = {
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


def ensure_questions_seeded():
    """Якщо таблиця questions порожня – заповнити її базовими питаннями."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions")
        count = cur.fetchone()[0]
        if count > 0:
            return

        for category, q_list in QUESTION_BANK.items():
            for q in q_list:
                text = q["text"]
                o1, o2, o3, o4 = q["options"]
                correct = q["correct"]
                explanation = q.get("explanation", "")
                level = 1
                cur.execute("""
                    INSERT INTO questions
                    (category, text, option1, option2, option3, option4,
                     correct_index, explanation, level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (category, text, o1, o2, o3, o4, correct, explanation, level))
        conn.commit()


def generate_test_questions():
    """
    Обрати по QUESTIONS_PER_CATEGORY випадкових питань з кожної категорії
    та перемішати.
    Повертає список dict:
      {id, category, text, options, correct, explanation}
    """
    selected = []
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT category FROM questions")
        categories = [row[0] for row in cur.fetchall()]

        for cat in categories:
            cur.execute("""
                SELECT id, text, option1, option2, option3, option4,
                       correct_index, explanation
                FROM questions
                WHERE category = ?
            """, (cat,))
            rows = cur.fetchall()
            if len(rows) < QUESTIONS_PER_CATEGORY:
                raise ValueError(f"У категорії '{cat}' недостатньо питань.")

            chosen = random.sample(rows, QUESTIONS_PER_CATEGORY)
            for (qid, text, o1, o2, o3, o4, corr, expl) in chosen:
                selected.append({
                    "id": qid,
                    "category": cat,
                    "text": text,
                    "options": [o1, o2, o3, o4],
                    "correct": corr,
                    "explanation": expl or "",
                })

    random.shuffle(selected)
    return selected


# ---------- Функції для режиму викладача (CRUD) ----------

def get_all_questions():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, category, text,
                   option1, option2, option3, option4,
                   correct_index, explanation, level
            FROM questions
            ORDER BY category, id
        """)
        return cur.fetchall()


def insert_question(category, text, options, correct_index, explanation, level=1):
    o1, o2, o3, o4 = options
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO questions
            (category, text, option1, option2, option3, option4,
             correct_index, explanation, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, text, o1, o2, o3, o4, correct_index, explanation, level))
        conn.commit()


def update_question(qid, category, text, options, correct_index, explanation, level=1):
    o1, o2, o3, o4 = options
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE questions
            SET category = ?, text = ?,
                option1 = ?, option2 = ?, option3 = ?, option4 = ?,
                correct_index = ?, explanation = ?, level = ?
            WHERE id = ?
        """, (category, text, o1, o2, o3, o4, correct_index, explanation, level, qid))
        conn.commit()


def delete_question(qid):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM questions WHERE id = ?", (qid,))
        conn.commit()
