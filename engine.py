# engine.py

def score_test(questions, user_answers):
    """
    Підрахунок загального бала та статистики по категоріях.
    questions – список dict: {text, options, correct, category}
    user_answers – список індексів (або None).

    Повертає: score, total, category_stats
    де category_stats = {category: {"correct": X, "total": Y}}
    """
    total = len(questions)
    score = 0
    category_stats = {}

    for i, q in enumerate(questions):
        cat = q.get("category", "Невідомо")
        if cat not in category_stats:
            category_stats[cat] = {"correct": 0, "total": 0}
        category_stats[cat]["total"] += 1

        ua = user_answers[i]
        if ua is not None and ua == q["correct"]:
            score += 1
            category_stats[cat]["correct"] += 1

    return score, total, category_stats
