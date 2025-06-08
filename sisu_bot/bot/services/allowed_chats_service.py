import json
import os

ALLOWED_CHATS_FILE = os.path.join(os.path.dirname(__file__), '../../data/allowed_chats.json')


def load_allowed_chats():
    if not os.path.exists(ALLOWED_CHATS_FILE):
        return []
    with open(ALLOWED_CHATS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_allowed_chats(chats):
    with open(ALLOWED_CHATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

def add_allowed_chat(chat_id):
    chats = load_allowed_chats()
    if str(chat_id) not in chats:
        chats.append(str(chat_id))
        save_allowed_chats(chats)
        return True
    return False

def remove_allowed_chat(chat_id):
    chats = load_allowed_chats()
    if str(chat_id) in chats:
        chats.remove(str(chat_id))
        save_allowed_chats(chats)
        return True
    return False

def list_allowed_chats():
    return load_allowed_chats() 