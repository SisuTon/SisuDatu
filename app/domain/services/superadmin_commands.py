"""
Superadmin Commands - заглушка для совместимости с импортами.
Содержит команды для суперадминистраторов.
"""

SUPERADMIN_COMMANDS = {
    "superadmin": "Панель суперадминистратора",
    "system": "Системные команды",
    "debug": "Режим отладки",
    "migrate": "Запустить миграции",
    "restart": "Перезапустить бота",
    "shutdown": "Остановить бота",
    "config": "Управление конфигурацией",
    "admins": "Управление администраторами",
    "security": "Настройки безопасности",
    "maintenance": "Режим обслуживания"
}

# Структура для регистрации команд суперадминистратора
SUPERADMIN_COMMAND_HANDLERS = {
    "superadmin": "superadmin_panel_handler",
    "system": "system_commands_handler",
    "debug": "debug_mode_handler",
    "migrate": "migrate_handler",
    "restart": "restart_handler",
    "shutdown": "shutdown_handler",
    "config": "config_handler",
    "admins": "admins_management_handler",
    "security": "security_handler",
    "maintenance": "maintenance_handler"
} 