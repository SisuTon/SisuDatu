import json
from pathlib import Path

USERS_PATH = Path(__file__).parent.parent.parent / 'data' / 'users.json'

def load_users():
    if USERS_PATH.exists():
        with open(USERS_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def update_user_info(user_id, username=None, first_name=None):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {}
    if username:
        users[user_id]["username"] = username
    if first_name:
        users[user_id]["first_name"] = first_name
    save_users(users)

def get_top_users(limit=5):
    users = load_users()
    top = sorted(users.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:limit]
    return top 