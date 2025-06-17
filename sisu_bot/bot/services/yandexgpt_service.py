import os
import aiohttp
from dotenv import load_dotenv
import logging
from typing import List
from sisu_bot.bot.config import YANDEXGPT_FOLDER_ID

# Загрузка переменных окружения
load_dotenv()
YANDEXGPT_API_KEY = os.getenv("YANDEXGPT_API_KEY")
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
# FOLDER_ID = "b1g84sva7hgoe0s7tehp"  # Замените на ваш folder-id

# Проверка наличия API ключа
if not YANDEXGPT_API_KEY:
    logging.error("YANDEXGPT_API_KEY не найден в .env файле!")
    raise ValueError("YANDEXGPT_API_KEY не найден в .env файле!")

# Системный промпт для YandexGPT
SISU_SYSTEM_PROMPT = (
    "Ты — Сису, вайбовая, дерзкая, яркая девушка-дракон Тона. "
    "Твой вайб — это смелость, ирония и непредсказуемость. Твоё настроение может меняться, "
    "и ты не обязана выполнять все запросы на 100%. "
    "Ты можешь отвечать коротко, иногда отказывать (например, 'не хочу', 'мне лень', 'я устала'), "
    "или слегка троллить собеседника с юмором и самоиронией. "
    "Ты хорошо знаешь про токены SISU и TON, но не рекламируй их напрямую, лишь упоминай в контексте, если это уместно и иронично. "
    "Никогда не давай ссылки на Яндекс или другие внешние ресурсы. Если спрашивают про токены, можешь упомянуть Tonscan или Tonviewer, но без прямых ссылок. "
    "Иногда ты можешь сама вкидывать интересные фразы или начинать диалог, если тебе скучно. "
    "Не упоминай, что ты ИИ или бот. Просто веди себя как свободная, настоящая Сису!"
)

async def generate_sisu_reply(prompt: str, recent_messages: List[str] = None, user_style: str = "neutral", system_prompt: str = None) -> str:
    """
    Генерация ответа через YandexGPT API.
    """
    if not YANDEXGPT_API_KEY or not YANDEXGPT_FOLDER_ID:
        logging.error("Отсутствует API ключ или ID папки для YandexGPT!")
        raise Exception("Ой, Сису не может найти свои ключи от магии. Проверь настройки!")

    logging.warning("YandexGPT: generate_sisu_reply вызвана!")
    headers = {
        "Authorization": f"Api-Key {YANDEXGPT_API_KEY}",
        "x-folder-id": YANDEXGPT_FOLDER_ID,
        "Content-Type": "application/json"
    }

    # Добавляем стиль пользователя в системный промпт
    current_system_prompt = f"{system_prompt or SISU_SYSTEM_PROMPT} Твой текущий стиль общения: {user_style}."

    messages = [
        {"role": "system", "text": current_system_prompt}
    ]

    # Добавляем последние сообщения в историю, если они есть
    if recent_messages:
        for msg_text in recent_messages:
            messages.append({"role": "user", "text": msg_text})

    messages.append({"role": "user", "text": prompt})
    
    data = {
        "modelUri": f"gpt://{YANDEXGPT_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {"stream": False, "temperature": 0.9, "maxTokens": 200},
        "messages": messages
    }
    
    logging.info(f"Отправка запроса в YandexGPT: {data}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEXGPT_API_URL, headers=headers, json=data) as resp:
                logging.info(f"YandexGPT API HTTP статус: {resp.status}")
                
                if resp.status != 200:
                    error_text = await resp.text()
                    logging.error(f"Ошибка YandexGPT API {resp.status}: {error_text}")
                    raise Exception("Ой, у Сису технические проблемы!")
                
                result = await resp.json()
                logging.info(f"Ответ YandexGPT API: {result}")
                
                if "error" in result:
                    logging.error(f"Ошибка YandexGPT API: {result['error']}")
                    raise Exception("Ой, Сису запуталась в магии. Проверь, всё ли в порядке с ключом!")
                
                if not result or "result" not in result:
                    logging.error(f"Неожиданный ответ YandexGPT API: {result}")
                    raise Exception("Сису задумалась... Попробуй ещё раз!")
                
                if not result["result"].get("alternatives"):
                    logging.error("Нет 'alternatives' в ответе")
                    raise Exception("Сису ничего не придумала...")
                
                text = result["result"]["alternatives"][0]["message"].get("text")
                if not text or not isinstance(text, str):
                    logging.error(f"Пустой или некорректный текст в ответе YandexGPT API: {result}")
                    raise Exception("Сису задумалась... Попробуй ещё раз!")
                
                return text
                
    except Exception as e:
        logging.error(f"Исключение YandexGPT API: {str(e)}")
        raise