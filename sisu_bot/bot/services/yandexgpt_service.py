import os
import aiohttp
from dotenv import load_dotenv
import logging

load_dotenv()
YANDEXGPT_API_KEY = os.getenv("YANDEXGPT_API_KEY")
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
FOLDER_ID = "b1g84sva7hgoe0s7tehp"  # Замените на ваш folder-id

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
    logging.warning("YandexGPT: generate_sisu_reply вызвана!")
    headers = {
        "Authorization": f"Api-Key {YANDEXGPT_API_KEY}",
        "x-folder-id": FOLDER_ID,  # Добавляем folder-id в заголовки
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
    
    logging.info(f"Sending request to YandexGPT with folder-id: {FOLDER_ID}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEXGPT_API_URL, headers=headers, json=data) as resp:
                logging.info(f"YandexGPT API HTTP status: {resp.status}")
                
                if resp.status != 200:
                    error_text = await resp.text()
                    logging.error(f"YandexGPT API Error {resp.status}: {error_text}")
                    return "Ой, у Сису технические проблемы!"
                
                result = await resp.json()
                logging.info(f"YandexGPT API full response: {result}")
                
                if "error" in result:
                    logging.error(f"YandexGPT API returned error: {result['error']}")
                    return "Ой, Сису запуталась в магии. Проверь, всё ли в порядке с ключом!"
                
                if not result or "result" not in result:
                    logging.error(f"YandexGPT API unexpected response: {result}")
                    return "Сису задумалась... Попробуй ещё раз!"
                
                if not result["result"].get("alternatives"):
                    logging.error("No 'alternatives' in response")
                    return "Сису ничего не придумала..."
                
                text = result["result"]["alternatives"][0]["message"].get("text")
                if not text or not isinstance(text, str):
                    logging.error(f"YandexGPT API empty or invalid text: {result}")
                    return "Сису задумалась... Попробуй ещё раз!"
                
                return text
                
    except Exception as e:
        logging.error(f"YandexGPT API exception: {str(e)}")
        return "Сису запуталась... Попробуй позже!" 