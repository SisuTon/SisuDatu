import json
import os
import datetime
import random

TRIGGER_STATS_FILE = os.path.join(os.path.dirname(__file__), '../../data/trigger_stats.json')


def load_stats():
    if not os.path.exists(TRIGGER_STATS_FILE):
        return {}
    with open(TRIGGER_STATS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_stats(stats):
    with open(TRIGGER_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def log_trigger_usage(trigger, answer, user_id, chat_id):
    stats = load_stats()
    t = stats.setdefault(trigger, {
        "count": 0,
        "answers": {},
        "last_used": None,
        "users": {},
        "chats": {},
        "likes": {},
        "dislikes": {}
    })
    t["count"] += 1
    t["last_used"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t["answers"].setdefault(answer, 1)
    t["answers"][answer] += 1
    t["users"].setdefault(str(user_id), 0)
    t["users"][str(user_id)] += 1
    t["chats"].setdefault(str(chat_id), 0)
    t["chats"][str(chat_id)] += 1
    t["likes"].setdefault(answer, 0)
    t["dislikes"].setdefault(answer, 0)
    stats[trigger] = t
    save_stats(stats)

def add_like(trigger, answer):
    stats = load_stats()
    t = stats.setdefault(trigger, {
        "count": 0,
        "answers": {},
        "last_used": None,
        "users": {},
        "chats": {},
        "likes": {},
        "dislikes": {}
    })
    t["likes"].setdefault(answer, 0)
    t["likes"][answer] += 1
    stats[trigger] = t
    save_stats(stats)

def add_dislike(trigger, answer):
    stats = load_stats()
    t = stats.setdefault(trigger, {
        "count": 0,
        "answers": {},
        "last_used": None,
        "users": {},
        "chats": {},
        "likes": {},
        "dislikes": {}
    })
    t["dislikes"].setdefault(answer, 0)
    t["dislikes"][answer] += 1
    stats[trigger] = t
    save_stats(stats)

def get_likes_dislikes(trigger, answer):
    stats = load_stats()
    t = stats.get(trigger, {})
    likes = t.get("likes", {}).get(answer, 0)
    dislikes = t.get("dislikes", {}).get(answer, 0)
    return likes, dislikes

def get_trigger_stats(trigger):
    stats = load_stats()
    return stats.get(trigger, None)

def get_all_trigger_stats():
    return load_stats()

def get_smart_answer(trigger, answers, last_answer=None):
    stats = get_trigger_stats(trigger)
    if not stats or not stats.get("answers"):
        # Исключаем повтор, если есть альтернатива
        filtered = [a for a in answers if a != last_answer]
        if filtered:
            return random.choice(filtered)
        return random.choice(answers)
    answer_counts = stats["answers"]
    likes = stats.get("likes", {})
    dislikes = stats.get("dislikes", {})
    weights = [answer_counts.get(a, 1) + 2*likes.get(a, 0) - dislikes.get(a, 0) + 1 for a in answers]
    # Исключаем повтор, если есть альтернатива
    filtered = [(a, w) for a, w in zip(answers, weights) if a != last_answer]
    if filtered:
        answers, weights = zip(*filtered)
    # Если все веса равны, всё равно используем random.choice
    if len(set(weights)) == 1:
        return random.choice(answers)
    return random.choices(answers, weights=weights, k=1)[0]

def suggest_new_triggers(min_count=5, limit=10):
    # MVP: ищем фразы, которые часто встречаются как текст сообщений, но не в базе триггеров
    # Для этого нужен отдельный сбор всех входящих сообщений (или анализировать users/chats)
    # Здесь просто возвращаем триггеры с большим количеством разных пользователей, но малым количеством ответов
    stats = load_stats()
    suggestions = []
    for trig, data in stats.items():
        # Если у триггера только 1-2 ответа, но много разных пользователей — возможно, это новый паттерн
        if data["count"] >= min_count and len(data["answers"]) <= 2 and len(data["users"]) >= 3:
            suggestions.append((trig, data["count"], len(data["users"]), list(data["answers"].keys())))
    suggestions.sort(key=lambda x: (-x[1], -x[2]))
    return suggestions[:limit]

def auto_add_suggested_triggers(min_count=5, min_users=3):
    # Загружаем предложения
    suggestions = suggest_new_triggers(min_count=min_count)
    # Загружаем learning_data.json
    import json
    import os
    LEARNING_PATH = os.path.join(os.path.dirname(__file__), '../../data/learning_data.json')
    try:
        with open(LEARNING_PATH, encoding='utf-8') as f:
            learning_data = json.load(f)
    except Exception:
        learning_data = {"triggers": {}, "responses": {}}
    added = []
    for trig, count, users, answers in suggestions:
        if trig not in learning_data["triggers"]:
            learning_data["triggers"][trig] = answers
            added.append(trig)
    if added:
        with open(LEARNING_PATH, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, ensure_ascii=False, indent=2)
    return added 