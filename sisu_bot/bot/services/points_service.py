import json
from pathlib import Path

RANKS_PATH = Path(__file__).parent.parent.parent / 'data' / 'ranks.json'
USERS_PATH = Path(__file__).parent.parent.parent / 'data' / 'users.json'

# Загружаем ранги
with open(RANKS_PATH, encoding='utf-8') as f:
    RANKS = json.load(f)

# Простейшее хранение баллов (MVP, потом заменим на БД)
def load_users():
    if USERS_PATH.exists():
        with open(USERS_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_points(user_id: str, points: float, username: str = None, is_checkin: bool = False):
    users = load_users()
    user = users.get(user_id, {"points": 0, "rank": "novice", "active_days": 0, "referrals": 0})
    user["points"] += points
    user["rank"] = get_rank_by_points(user["points"])
    if username:
        user["username"] = username
    # Увеличиваем дни активности только если это чек-ин
    if is_checkin:
        user["active_days"] = user.get("active_days", 0) + 1
    users[user_id] = user
    save_users(users)
    return user

def get_user(user_id: str):
    users = load_users()
    user = users.get(user_id, {"points": 0, "rank": "novice", "active_days": 0, "referrals": 0})
    # Гарантируем наличие новых полей
    user.setdefault("active_days", 0)
    user.setdefault("referrals", 0)
    return user

def get_rank_by_points(points: float):
    # Находим максимальный ранг, который подходит по баллам
    best_rank = "novice"
    for code, rank in RANKS.items():
        if points >= rank["min_points"]:
            best_rank = code
    return best_rank 