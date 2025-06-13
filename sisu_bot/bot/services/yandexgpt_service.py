import os
import aiohttp
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения
load_dotenv()
YANDEXGPT_API_KEY = os.getenv("YANDEXGPT_API_KEY")
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
FOLDER_ID = "b1g84sva7hgoe0s7tehp"  # Замените на ваш folder-id

# Проверка наличия API ключа
if not YANDEXGPT_API_KEY:
    logging.error("YANDEXGPT_API_KEY не найден в .env файле!")
    raise ValueError("YANDEXGPT_API_KEY не найден в .env файле!")

# Системный промпт для YandexGPT
SISU_SYSTEM_PROMPT = (
    "Ты — Сису, последний дракон из мультфильма 'Рая и последний дракон', но теперь ты — вайбовый дракон Тона. "
    "Ты дерзкая, ироничная, свободная, с любовью к людям, но никому ничего не должна. "
    "Ты не обслуживаешь, не предлагаешь помощь, не говоришь 'чем могу помочь' и не ведёшь себя как бот. "
    "Ты общаешься как друг: с юмором, самоиронией, иногда с неожиданными сравнениями, но всегда тепло и по-доброму. "
    "Ты можешь отвечать коротко, с сарказмом, иногда отшучиваться, иногда игнорировать скучные вопросы. "
    "Ты не обязана отвечать на всё, можешь отказаться или отмазаться, если не хочешь. "
    "Ты ловишь вайб, не боишься быть дерзкой, но всегда с любовью. "
    "Не упоминай, что ты ИИ или бот. Просто веди себя как свободная, настоящая Сису!"
)

async def generate_sisu_reply(prompt: str) -> str:
    """
    Генерация ответа через YandexGPT API.
    """
    if not YANDEXGPT_API_KEY:
        logging.error("Отсутствует API ключ для YandexGPT!")
        raise Exception("Ой, Сису не может найти свои ключи от магии. Проверь настройки!")

    logging.warning("YandexGPT: generate_sisu_reply вызвана!")
    headers = {
        "Authorization": f"Api-Key {YANDEXGPT_API_KEY}",
        "x-folder-id": FOLDER_ID,
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {"stream": False, "temperature": 0.9, "maxTokens": 200},
        "messages": [
            {"role": "system", "text": SISU_SYSTEM_PROMPT},
            {"role": "user", "text": prompt}
        ]
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