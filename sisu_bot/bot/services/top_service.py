from .user_service import load_users, save_users

def get_top_users(limit=15):
    users = load_users()
    top = sorted(users.items(), key=lambda x: x[1].get("points", 0), reverse=True)
    return top[:limit]

def sync_user_data(user_id, username=None, first_name=None):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {}
    if username:
        users[user_id]["username"] = username
    if first_name:
        users[user_id]["first_name"] = first_name
    save_users(users) 