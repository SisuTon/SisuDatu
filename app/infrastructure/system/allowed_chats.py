import json
import os
from app.shared.config.settings import Settings
DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    from pathlib import Path
    DATA_DIR = Path(DATA_DIR)
ALLOWED_CHATS_FILE = DATA_DIR / 'allowed_chats.json'

class AllowedChatsService:
    """Сервис для управления разрешёнными чатами."""
    def __init__(self, *args, **kwargs):
        pass

    def load(self):
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []

    def save(self, chats):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(chats, f, ensure_ascii=False, indent=2)

    def add(self, chat_id):
        chats = self.load()
        if str(chat_id) not in chats:
            chats.append(str(chat_id))
            self.save(chats)
            return True
        return False

    def remove(self, chat_id):
        chats = self.load()
        if str(chat_id) in chats:
            chats.remove(str(chat_id))
            self.save(chats)
            return True
        return False

    def list(self):
        return self.load()

# Функции для обратной совместимости
def list_allowed_chats():
    """Список разрешённых чатов (для обратной совместимости)"""
    service = AllowedChatsService()
    service.data_file = ALLOWED_CHATS_FILE
    return service.list()

def add_allowed_chat(chat_id):
    """Добавить разрешённый чат (для обратной совместимости)"""
    service = AllowedChatsService()
    service.data_file = ALLOWED_CHATS_FILE
    return service.add(chat_id)

def remove_allowed_chat(chat_id):
    """Удалить разрешённый чат (для обратной совместимости)"""
    service = AllowedChatsService()
    service.data_file = ALLOWED_CHATS_FILE
    return service.remove(chat_id) 