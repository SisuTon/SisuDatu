# bot/config.py
# Список Telegram ID админов, которые имеют доступ к админ-командам
ADMIN_IDS = [
    446318189,   # @bakeevsergey
    5857816562   # @SISU_TON
]

# Список суперадминов (централизованный)
SUPERADMIN_IDS = [
    446318189,   # @bakeevsergey
    5857816562   # @SISU_TON
]

def is_superadmin(user_id: int) -> bool:
    return user_id in SUPERADMIN_IDS