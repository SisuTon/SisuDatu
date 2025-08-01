"""
Admin Commands - заглушка для совместимости с импортами.
Содержит команды для администраторов.
"""

ADMIN_COMMANDS = {
    "admin": "Панель администратора",
    "users": "Управление пользователями",
    "stats": "Статистика бота",
    "broadcast": "Отправить сообщение всем",
    "ban": "Забанить пользователя",
    "unban": "Разбанить пользователя",
    "logs": "Показать логи",
    "backup": "Создать резервную копию",
    "restore": "Восстановить из резервной копии",
    "settings": "Настройки бота"
}

# Структура для регистрации команд администратора
ADMIN_COMMAND_HANDLERS = {
    "admin": "admin_panel_handler",
    "users": "users_management_handler",
    "stats": "stats_handler",
    "broadcast": "broadcast_handler",
    "ban": "ban_user_handler",
    "unban": "unban_user_handler",
    "logs": "logs_handler",
    "backup": "backup_handler",
    "restore": "restore_handler",
    "settings": "admin_settings_handler"
} 