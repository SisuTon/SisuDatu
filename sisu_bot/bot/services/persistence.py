"""
Модуль для работы с состоянием бота в базе данных
"""
from sisu_bot.bot.services.state_service import get_state_db_value as get_state_from_service, set_state_db_value as set_state_from_service

def get_state(key: str) -> str:
    """
    Получает значение состояния по ключу из базы данных
    
    Args:
        key (str): Ключ состояния
        
    Returns:
        str: Значение состояния или None, если не найдено
    """
    return get_state_from_service(key)

def set_state(key: str, value: str) -> None:
    """
    Устанавливает значение состояния по ключу в базе данных
    
    Args:
        key (str): Ключ состояния
        value (str): Значение для сохранения
    """
    set_state_from_service(key, value) 