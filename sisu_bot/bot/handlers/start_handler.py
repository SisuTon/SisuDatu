from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.services.user_service import update_user_info, load_users, save_users
from bot.services import points_service
import logging

router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    args = msg.get_args()
    user_id = str(msg.from_user.id)
    users = load_users()
    bot = msg.bot
    if user_id not in users:
        users[user_id] = {}
    # Проверяем реферала
    if args and args.startswith("ref_"):
        ref_id = args[4:]
        if ref_id != user_id:
            if "invited_by" not in users[user_id]:
                users[user_id]["invited_by"] = ref_id
                if ref_id in users:
                    users[ref_id]["points"] = users[ref_id].get("points", 0) + 100  # 100 баллов за реферала
                    users[ref_id]["referrals"] = users[ref_id].get("referrals", 0) + 1
                    logging.info(f"Реферал: {ref_id} получил 100 баллов и +1 к referrals!")
                    # Явное сообщение пригласившему
                    try:
                        await bot.send_message(ref_id, f"🎉 У тебя новый реферал! +100 баллов!")
                    except Exception as e:
                        logging.warning(f"Не удалось отправить сообщение пригласившему: {e}")
            else:
                logging.info(f"Пользователь {user_id} уже был приглашён {users[user_id]['invited_by']}")
    update_user_info(user_id, msg.from_user.username, msg.from_user.first_name)
    save_users(users)
    await msg.answer("Привет! Ты в SisuDatuBot. Используй /help для списка команд.") 