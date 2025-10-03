from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Создает основную клавиатуру бота"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Мой ранг", callback_data="my_rank"),
                InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top_players")
            ],
            [
                InlineKeyboardButton(text="☑️ Чек-ин", callback_data="checkin"),
                InlineKeyboardButton(text="🎮 Игры", callback_data="games")
            ],
            [
                InlineKeyboardButton(text="💎 Донат", callback_data="donate"),
                InlineKeyboardButton(text="👥 Рефералы", callback_data="referral")
            ],
            [
                InlineKeyboardButton(text="❓ Помощь", callback_data="help")
            ]
        ]
    )

def get_admin_keyboard():
    """Создает клавиатуру для админов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton(text="🎯 Добавить баллы", callback_data="admin_add_points"),
                InlineKeyboardButton(text="🚫 Забанить", callback_data="admin_ban")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
            ]
        ]
    )

def get_superadmin_keyboard():
    """Создает клавиатуру для супер-админов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Настройки бота", callback_data="superadmin_settings"),
                InlineKeyboardButton(text="📈 Расширенная статистика", callback_data="superadmin_stats")
            ],
            [
                InlineKeyboardButton(text="🔧 Управление админами", callback_data="superadmin_admins"),
                InlineKeyboardButton(text="🎮 Управление играми", callback_data="superadmin_games")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
            ]
        ]
    ) 