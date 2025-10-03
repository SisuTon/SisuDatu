"""
Сервис для динамического управления админами
"""
import json
import os
from typing import List, Dict
from sisu_bot.core.config import ADMIN_IDS, ZERO_ADMIN_IDS, SUPERADMIN_IDS
from sisu_bot.bot.config import is_superadmin
import logging

logger = logging.getLogger(__name__)

# Файл для хранения динамических админов
ADMINS_FILE = "sisu_bot/data/dynamic_admins.json"

def load_dynamic_admins() -> Dict[str, List[int]]:
    """Загружает динамических админов из файла"""
    try:
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading dynamic admins: {e}")
    
    return {
        "admins": [],
        "zero_admins": []
    }

def save_dynamic_admins(admins: Dict[str, List[int]]):
    """Сохраняет динамических админов в файл"""
    try:
        os.makedirs(os.path.dirname(ADMINS_FILE), exist_ok=True)
        with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
            json.dump(admins, f, ensure_ascii=False, indent=2)
        logger.info(f"Dynamic admins saved: {admins}")
    except Exception as e:
        logger.error(f"Error saving dynamic admins: {e}")

def get_all_admins() -> Dict[str, List[int]]:
    """Получает всех админов (статичных + динамичных)"""
    dynamic = load_dynamic_admins()
    
    return {
        "superadmins": SUPERADMIN_IDS,
        "admins": list(set(ADMIN_IDS + dynamic.get("admins", []))),
        "zero_admins": list(set(ZERO_ADMIN_IDS + dynamic.get("zero_admins", [])))
    }

def add_admin(user_id: int, admin_type: str = "admin") -> bool:
    """Добавляет админа динамически"""
    if admin_type not in ["admin", "zero_admin"]:
        return False
    
    dynamic = load_dynamic_admins()
    key = "admins" if admin_type == "admin" else "zero_admins"
    
    if user_id not in dynamic[key]:
        dynamic[key].append(user_id)
        save_dynamic_admins(dynamic)
        logger.info(f"Added {admin_type} {user_id}")
        return True
    
    return False

def remove_admin(user_id: int, admin_type: str = "admin") -> bool:
    """Удаляет админа динамически"""
    if admin_type not in ["admin", "zero_admin"]:
        return False
    
    dynamic = load_dynamic_admins()
    key = "admins" if admin_type == "admin" else "zero_admins"
    
    if user_id in dynamic[key]:
        dynamic[key].remove(user_id)
        save_dynamic_admins(dynamic)
        logger.info(f"Removed {admin_type} {user_id}")
        return True
    
    return False

def is_dynamic_admin(user_id: int, admin_type: str = "admin") -> bool:
    """Проверяет, является ли пользователь динамическим админом"""
    dynamic = load_dynamic_admins()
    key = "admins" if admin_type == "admin" else "zero_admins"
    
    return user_id in dynamic[key]

def get_admin_role(user_id: int) -> str:
    """Получает роль пользователя (включая динамических админов)"""
    all_admins = get_all_admins()
    
    if user_id in all_admins["superadmins"]:
        return "superadmin"
    elif user_id in all_admins["admins"]:
        return "admin"
    elif user_id in all_admins["zero_admins"]:
        return "zero_admin"
    else:
        return "user"

def list_dynamic_admins() -> str:
    """Возвращает список динамических админов в текстовом виде"""
    dynamic = load_dynamic_admins()
    
    result = "📋 <b>Динамические админы:</b>\n\n"
    
    if dynamic["admins"]:
        result += "👑 <b>Админы:</b>\n"
        for admin_id in dynamic["admins"]:
            result += f"• {admin_id}\n"
        result += "\n"
    
    if dynamic["zero_admins"]:
        result += "🔧 <b>Zero-админы:</b>\n"
        for admin_id in dynamic["zero_admins"]:
            result += f"• {admin_id}\n"
    
    if not dynamic["admins"] and not dynamic["zero_admins"]:
        result += "Нет динамических админов"
    
    return result 