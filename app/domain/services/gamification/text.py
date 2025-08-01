"""
Модуль начисления баллов за текстовые сообщения.
"""

def add_text_points(user_id: int, message_text: str) -> int:
    # Пример: если больше 10 слов, начисляем 1 балл
    if len(message_text.split()) > 10:
        return 1
    return 0
