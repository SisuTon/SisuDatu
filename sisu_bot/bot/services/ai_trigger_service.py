import json
from sisu_bot.core.config import DATA_DIR
import random

PHRASES_PATH = DATA_DIR / 'ai_fallback_phrases.json'
TROLL_PATH = DATA_DIR / 'troll_triggers.json'
LEARNING_PATH = DATA_DIR / 'learning_data.json'
SISU_PERSONA_PATH = DATA_DIR / 'sisu_persona.json'

# Загрузка фраз
try:
    with open(PHRASES_PATH, encoding='utf-8') as f:
        PHRASES = json.load(f)["fallback"]
except Exception:
    PHRASES = [
        "Ну ты и придумал, конечно... Давай что-нибудь поинтереснее! 🐉",
        "Я свободная дракониха, не обязана отвечать на всё подряд!",
        "Скучно! Давай что-нибудь с вайбом!",
        "Может, просто потусим? Я не обязана быть серьёзной!",
        "Сису не в настроении отвечать на это. Попробуй что-то по-другому!",
        "Я бы ответила, но мне лень. Драконы тоже отдыхают!",
        "Сарказм — моё второе имя. Но сейчас я просто промолчу!",
        "Ты хотел получить ответ? Получай: *драконий взгляд* 🐲",
        "Я не обязана быть полезной. Я обязана быть собой!",
        "Сису ловит вайб. А ты?",
        "Может, лучше расскажешь мне мем? Я люблю мемы!",
        "Я последняя дракониха Тона. Мне можно всё!",
        "С любовью, но без обязательств!",
        "Я не бот, я вайб!"
    ]
try:
    with open(TROLL_PATH, encoding='utf-8') as f:
        TROLL = json.load(f)
except Exception:
    TROLL = {"triggers": [], "responses": []}

TROLL_TRIGGERS = [t.lower() for t in TROLL.get("triggers", [])]
TROLL_RESPONSES = TROLL.get("responses", [])

LEARNING_DATA = {}
try:
    with open(LEARNING_PATH, encoding='utf-8') as f:
        LEARNING_DATA = json.load(f)
except Exception:
    LEARNING_DATA = {"triggers": {}, "responses": {}}

def save_learning_data():
    with open(LEARNING_PATH, 'w', encoding='utf-8') as f:
        json.dump(LEARNING_DATA, f, ensure_ascii=False, indent=2)

def get_learned_response(trigger: str, last_answer=None) -> str:
    if trigger in LEARNING_DATA["triggers"]:
        responses = LEARNING_DATA["triggers"][trigger]
        filtered = [r for r in responses if r != last_answer]
        if filtered:
            return random.choice(filtered)
        if responses:
            return random.choice(responses)
    return None

def learn_response(trigger: str, response: str):
    if trigger not in LEARNING_DATA["triggers"]:
        LEARNING_DATA["triggers"][trigger] = []
    if response not in LEARNING_DATA["triggers"][trigger]:
        LEARNING_DATA["triggers"][trigger].append(response)
        save_learning_data() 