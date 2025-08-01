"""
Default Commands - заглушка для совместимости с импортами.
Содержит команды по умолчанию для обычных пользователей.
"""

DEFAULT_COMMANDS = {
    "start": "Начать работу с ботом",
    "help": "Показать справку",
    "profile": "Показать профиль",
    "games": "Доступные игры",
    "motivation": "Получить мотивацию",
    "points": "Показать очки",
    "rank": "Показать ранг",
    "top": "Таблица лидеров",
    "donate": "Поддержать проект",
    "settings": "Настройки"
}

# Структура для регистрации команд
DEFAULT_COMMAND_HANDLERS = {
    "start": "start_handler",
    "help": "help_handler", 
    "profile": "profile_handler",
    "games": "games_handler",
    "motivation": "motivation_handler",
    "points": "points_handler",
    "rank": "rank_handler",
    "top": "top_handler",
    "donate": "donate_handler",
    "settings": "settings_handler"
} 