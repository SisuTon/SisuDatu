from types import SimpleNamespace
from unittest.mock import AsyncMock

def make_fake_message(user_id: int, username: str = None, first_name: str = None, chat_id: int = -100, chat_type: str = "group"):
    """
    Создает фейковый объект сообщения для тестирования.
    
    Args:
        user_id: ID пользователя
        username: Имя пользователя (опционально)
        first_name: Имя (опционально)
        chat_id: ID чата
        chat_type: Тип чата (по умолчанию "group")
    
    Returns:
        SimpleNamespace: Объект, имитирующий сообщение Telegram
    """
    # Создаем фейковый объект сообщения
    mock = SimpleNamespace(
        from_user=SimpleNamespace(
            id=user_id,
            username=username,
            first_name=first_name
        ),
        chat=SimpleNamespace(
            id=chat_id,
            type=chat_type
        ),
        text="/checkin",
        bot=SimpleNamespace()
    )
    
    # Добавляем асинхронные методы
    mock.answer = AsyncMock()
    mock.reply = AsyncMock()
    mock.delete = AsyncMock()
    
    return mock 