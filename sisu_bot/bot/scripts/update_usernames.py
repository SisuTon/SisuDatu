import json
from pathlib import Path
from aiogram import Bot
import asyncio
import os

USERS_PATH = Path(__file__).parent.parent / 'data' / 'users.json'
BOT_TOKEN = os.getenv('BOT_TOKEN') or 'YOUR_BOT_TOKEN_HERE'

async def update_usernames():
    bot = Bot(token=BOT_TOKEN)
    with open(USERS_PATH, encoding='utf-8') as f:
        users = json.load(f)
    updated = 0
    for user_id in users:
        try:
            user_data = await bot.get_chat(user_id)
            if user_data.username:
                users[user_id]["username"] = user_data.username
                updated += 1
        except Exception as e:
            print(f"Не удалось получить username для {user_id}: {e}")
        await asyncio.sleep(0.1)  # чтобы не словить flood limit
    with open(USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"Обновлено пользователей: {updated}")

if __name__ == "__main__":
    asyncio.run(update_usernames()) 