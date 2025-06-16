from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import json
import os
from typing import Dict, List, Optional
from sisu_bot.bot.config import SUPERADMIN_IDS, is_superadmin
from sisu_bot.bot.services.games_service import bulk_add_emoji_movies, get_random_emoji_movie, check_emoji_movie_answer
from sisu_bot.bot.services.points_service import add_points
import asyncio

router = Router()

# Состояния для игр
class GameStates(StatesGroup):
    waiting_emoji_answer = State()
    waiting_word_answer = State()
    waiting_riddle_answer = State()
    waiting_new_emoji = State()
    waiting_new_emoji_answer = State()
    waiting_new_riddle = State()
    waiting_new_riddle_answer = State()
    waiting_new_word = State()
    # Состояния для супер-админов
    waiting_bulk_emoji = State()
    waiting_bulk_riddle = State()
    waiting_bulk_word = State()
    waiting_delete_emoji = State()
    waiting_delete_riddle = State()
    waiting_delete_word = State()

# Путь к файлу с данными игр
GAMES_DATA_FILE = "data/games_data.json"

# Загрузка данных игр
def load_games_data():
    if not os.path.exists(GAMES_DATA_FILE):
        return {
            "emoji_movies": [],
            "word_game_words": [],
            "riddles": []
        }
    with open(GAMES_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Сохранение данных игр
def save_games_data(data):
    os.makedirs(os.path.dirname(GAMES_DATA_FILE), exist_ok=True)
    with open(GAMES_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Словарь для хранения активных игр
active_games: Dict[int, Dict] = {}

# Фильмы с эмодзи
EMOJI_MOVIES = [
    {"emoji": "👻👻👻", "answer": "Три богатыря"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Немо"},
    {"emoji": "👨‍👦🐠", "answer": "В поисках Дори"}
]

# Слова для игры в слова
WORD_GAME_WORDS = [
    "дракон", "магия", "токен", "тон", "вайб", "снуп", "догг", "токио",
    "крипта", "блокчейн", "мем", "пам", "луна", "солнце", "звезда",
    "космос", "время", "пространство", "энергия", "сила", "мудрость",
    "знание", "истина", "путь", "судьба", "жизнь", "смерть", "любовь",
    "ненависть", "радость", "печаль", "счастье", "горе", "удача",
    "неудача", "победа", "поражение", "начало", "конец", "вечность"
]

# Загадки
RIDDLES = [
    {
        "riddle": "Я не живая, но расту; не дышу, но умираю. Что я?",
        "answer": "свеча"
    },
    {
        "riddle": "Чем больше берёшь, тем больше становится. Что это?",
        "answer": "яма"
    },
    {
        "riddle": "Что можно сломать, даже не прикоснувшись к этому?",
        "answer": "обещание"
    },
    {
        "riddle": "Что всегда идёт, но никогда не приходит?",
        "answer": "время"
    },
    {
        "riddle": "Что можно увидеть с закрытыми глазами?",
        "answer": "сон"
    }
]

# Фразы для правильных ответов
CORRECT_ANSWERS = [
    "Вот это да! Ты настоящий знаток! 🎯",
    "Браво! Ты угадал! 🎉",
    "Потрясающе! Ты справился! 🌟",
    "Отличная работа! Ты молодец! 👏",
    "Великолепно! Ты настоящий мастер! 🏆"
]

# Фразы для неправильных ответов
WRONG_ANSWERS = [
    "Увы, это неверно. Попробуй ещё раз! 🤔",
    "Не угадал! Но не сдавайся! 💪",
    "Почти, но не то! Думай дальше! 🧠",
    "Неправильно! Но ты близко! 🔍",
    "Не то! Но ты на верном пути! 🎯"
]

# Фразы для отказа от игры
DECLINE_PHRASES = [
    "Сегодня не мой день для игр. Может, в другой раз!",
    "Не хочу, не буду! Я дракон, а не аниматор!",
    "Сначала подними мне настроение, потом поговорим об играх!",
    "Я бы сыграла, но вайб не тот...",
    "Может быть позже, когда будет больше вайба!"
]

@router.message(Command("emoji_movie"))
async def emoji_movie_handler(msg: Message):
    movie = get_random_emoji_movie()
    if not movie:
        await msg.answer("Нет фильмов для игры. Попроси суперадмина загрузить их через /bulk_emoji!")
        return
    # Анимация выбора
    for _ in range(3):
        await msg.answer("🎲 Крутим барабан...", disable_notification=True)
        await asyncio.sleep(0.5)
    await msg.answer(f"Угадай фильм по эмодзи: {movie.emoji}\nОтветь на это сообщение!")
    # Сохраняем id фильма в state (или можно через in-memory dict, если нет FSM)
    # Для простоты: ждём ответ в течение 60 секунд
    def check_reply(m):
        return m.reply_to_message and m.reply_to_message.message_id == msg.message_id + 4  # 4 сообщения анимации
    try:
        reply = await msg.bot.wait_for('message', timeout=60, check=check_reply)
        if check_emoji_movie_answer(movie.id, reply.text):
            add_points(reply.from_user.id, 10)
            await reply.answer("Респект! +10 баллов!")
        else:
            await reply.answer("Увы, неверно! Попробуй ещё раз через /emoji_movie")
    except asyncio.TimeoutError:
        await msg.answer("Время вышло! Попробуй снова через /emoji_movie")

@router.message(Command("teach_emoji"))
async def teach_emoji_start(msg: Message, state: FSMContext):
    await msg.answer("Отлично! Давай научим меня новому фильму! Сначала напиши эмодзи для фильма.")
    await state.set_state(GameStates.waiting_new_emoji)

@router.message(GameStates.waiting_new_emoji)
async def teach_emoji_emoji(msg: Message, state: FSMContext):
    emoji = msg.text.strip()
    await state.update_data(new_emoji=emoji)
    await msg.answer("Теперь напиши название фильма.")
    await state.set_state(GameStates.waiting_new_emoji_answer)

@router.message(GameStates.waiting_new_emoji_answer)
async def teach_emoji_answer(msg: Message, state: FSMContext):
    answer = msg.text.strip()
    data = await state.get_data()
    emoji = data["new_emoji"]
    
    # Загружаем текущие данные
    games_data = load_games_data()
    
    # Добавляем новый фильм
    games_data["emoji_movies"].append({
        "emoji": emoji,
        "answer": answer
    })
    
    # Сохраняем обновленные данные
    save_games_data(games_data)
    
    await msg.answer(f"Спасибо! Теперь я знаю, что {emoji} — это {answer}! 🎬")
    await state.clear()

@router.message(Command("teach_riddle"))
async def teach_riddle_start(msg: Message, state: FSMContext):
    await msg.answer("Отлично! Давай научим меня новой загадке! Сначала напиши саму загадку.")
    await state.set_state(GameStates.waiting_new_riddle)

@router.message(GameStates.waiting_new_riddle)
async def teach_riddle_riddle(msg: Message, state: FSMContext):
    riddle = msg.text.strip()
    await state.update_data(new_riddle=riddle)
    await msg.answer("Теперь напиши ответ на загадку.")
    await state.set_state(GameStates.waiting_new_riddle_answer)

@router.message(GameStates.waiting_new_riddle_answer)
async def teach_riddle_answer(msg: Message, state: FSMContext):
    answer = msg.text.strip()
    data = await state.get_data()
    riddle = data["new_riddle"]
    
    # Загружаем текущие данные
    games_data = load_games_data()
    
    # Добавляем новую загадку
    games_data["riddles"].append({
        "riddle": riddle,
        "answer": answer
    })
    
    # Сохраняем обновленные данные
    save_games_data(games_data)
    
    await msg.answer(f"Спасибо! Теперь я знаю новую загадку! 🎯")
    await state.clear()

@router.message(Command("teach_word"))
async def teach_word_start(msg: Message, state: FSMContext):
    await msg.answer("Отлично! Давай научим меня новому слову для игры! Напиши слово.")
    await state.set_state(GameStates.waiting_new_word)

@router.message(GameStates.waiting_new_word)
async def teach_word_word(msg: Message, state: FSMContext):
    word = msg.text.strip().lower()
    
    # Загружаем текущие данные
    games_data = load_games_data()
    
    # Добавляем новое слово
    if word not in games_data["word_game_words"]:
        games_data["word_game_words"].append(word)
        # Сохраняем обновленные данные
        save_games_data(games_data)
        await msg.answer(f"Спасибо! Теперь я знаю новое слово: {word}! 📚")
    else:
        await msg.answer("Ой, я уже знаю это слово! 🤔")
    
    await state.clear()

@router.message(Command("list_games"))
async def list_games(msg: Message):
    games_data = load_games_data()
    response = "🎮 Мои игры:\n\n"
    response += f"🎬 Фильмов: {len(games_data['emoji_movies'])}\n"
    response += f"📚 Слов: {len(games_data['word_game_words'])}\n"
    response += f"🎯 Загадок: {len(games_data['riddles'])}\n\n"
    response += "Команды для обучения:\n"
    response += "/teach_emoji - научить новому фильму\n"
    response += "/teach_riddle - научить новой загадке\n"
    response += "/teach_word - научить новому слову"
    await msg.answer(response)

@router.message(GameStates.waiting_emoji_answer)
async def emoji_movie_answer(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    if chat_id not in active_games or active_games[chat_id]["type"] != "emoji_movie":
        await state.clear()
        return
    
    user_answer = msg.text.lower().strip()
    correct_answer = active_games[chat_id]["answer"]
    
    if user_answer == correct_answer:
        await msg.answer(random.choice(CORRECT_ANSWERS))
    else:
        await msg.answer(random.choice(WRONG_ANSWERS))
    
    del active_games[chat_id]
    await state.clear()

@router.message(Command("word_game"))
async def word_game_start(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    if chat_id in active_games:
        await msg.answer("У нас уже идет игра! Дождись её окончания.")
        return
    
    if random.random() > 0.6:
        await msg.answer(random.choice(DECLINE_PHRASES))
        return
    
    word = random.choice(WORD_GAME_WORDS)
    active_games[chat_id] = {
        "type": "word_game",
        "answer": word
    }
    
    await msg.answer(f"Давай поиграем в слова! Я загадала слово. Твоя задача - угадать его, задавая вопросы, на которые я могу ответить только 'да' или 'нет'.\n\nНачни с вопроса!")
    await state.set_state(GameStates.waiting_word_answer)

@router.message(GameStates.waiting_word_answer)
async def word_game_answer(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    if chat_id not in active_games or active_games[chat_id]["type"] != "word_game":
        await state.clear()
        return
    
    word = active_games[chat_id]["answer"]
    question = msg.text.lower().strip()
    
    # Простая логика ответов на вопросы
    if "это" in question and word in question:
        await msg.answer("Да! Ты угадал! 🎉")
        del active_games[chat_id]
        await state.clear()
    elif word in question:
        await msg.answer("Да! 🔥")
    elif any(letter in word for letter in question):
        await msg.answer("Возможно! 🤔")
    else:
        await msg.answer("Нет! ❌")

@router.message(Command("riddle"))
async def riddle_start(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    if chat_id in active_games:
        await msg.answer("У нас уже идет игра! Дождись её окончания.")
        return
    
    if random.random() > 0.6:
        await msg.answer(random.choice(DECLINE_PHRASES))
        return
    
    riddle = random.choice(RIDDLES)
    active_games[chat_id] = {
        "type": "riddle",
        "answer": riddle["answer"]
    }
    
    await msg.answer(f"Загадка:\n{riddle['riddle']}\n\nОтвечай в reply!")
    await state.set_state(GameStates.waiting_riddle_answer)

@router.message(GameStates.waiting_riddle_answer)
async def riddle_answer(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    if chat_id not in active_games or active_games[chat_id]["type"] != "riddle":
        await state.clear()
        return
    
    user_answer = msg.text.lower().strip()
    correct_answer = active_games[chat_id]["answer"]
    
    if user_answer == correct_answer:
        await msg.answer(random.choice(CORRECT_ANSWERS))
    else:
        await msg.answer(random.choice(WRONG_ANSWERS))
    
    del active_games[chat_id]
    await state.clear()

# Команды для супер-админов
@router.message(Command("games_admin"))
async def games_admin_help(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("У вас нет прав для использования этой команды.")
        return
    
    help_text = "🎮 Команды управления играми (только для супер-админов):\n\n"
    help_text += "📝 Массовое добавление:\n"
    help_text += "/bulk_emoji - добавить несколько фильмов\n"
    help_text += "/bulk_riddle - добавить несколько загадок\n"
    help_text += "/bulk_word - добавить несколько слов\n\n"
    help_text += "🗑 Удаление:\n"
    help_text += "/delete_emoji - удалить фильм\n"
    help_text += "/delete_riddle - удалить загадку\n"
    help_text += "/delete_word - удалить слово\n\n"
    help_text += "📊 Статистика:\n"
    help_text += "/games_stats - подробная статистика игр"
    
    await msg.answer(help_text)

@router.message(Command("bulk_emoji"))
async def bulk_emoji_handler(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Нет прав!")
        return
    lines = msg.text.split("\n")[1:]
    movies = []
    for line in lines:
        if "|" in line:
            emoji, answers = line.split("|", 1)
            movies.append({"emoji": emoji.strip(), "answers": [a.strip() for a in answers.split(",")]})
    if not movies:
        await msg.answer("Формат: эмодзи | ответ1, ответ2, ...")
        return
    bulk_add_emoji_movies(movies)
    await msg.answer(f"Загружено фильмов: {len(movies)}")

@router.message(Command("bulk_riddle"))
async def bulk_riddle_start(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("У вас нет прав для использования этой команды.")
        return
    
    await msg.answer(
        "Отправьте список загадок в формате:\n"
        "загадка | ответ\n"
        "загадка | ответ\n"
        "Например:\n"
        "Я не живая, но расту; не дышу, но умираю. | свеча\n"
        "Чем больше берёшь, тем больше становится. | яма"
    )
    await state.set_state(GameStates.waiting_bulk_riddle)

@router.message(GameStates.waiting_bulk_riddle)
async def bulk_riddle_process(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id):
        await state.clear()
        return
    
    lines = msg.text.strip().split('\n')
    games_data = load_games_data()
    added = 0
    skipped = 0
    
    for line in lines:
        if '|' not in line:
            continue
        riddle, answer = [part.strip() for part in line.split('|', 1)]
        if not riddle or not answer:
            continue
        
        # Проверяем на дубликаты
        if not any(r["riddle"].lower() == riddle.lower() for r in games_data["riddles"]):
            games_data["riddles"].append({
                "riddle": riddle,
                "answer": answer.lower()
            })
            added += 1
        else:
            skipped += 1
    
    save_games_data(games_data)
    await msg.answer(f"✅ Добавлено новых загадок: {added}\n⏭ Пропущено дубликатов: {skipped}")
    await state.clear()

@router.message(Command("bulk_word"))
async def bulk_word_start(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("У вас нет прав для использования этой команды.")
        return
    
    await msg.answer(
        "Отправьте список слов, каждое с новой строки.\n"
        "Например:\n"
        "дракон\n"
        "магия\n"
        "токен"
    )
    await state.set_state(GameStates.waiting_bulk_word)

@router.message(GameStates.waiting_bulk_word)
async def bulk_word_process(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id):
        await state.clear()
        return
    
    words = [word.strip().lower() for word in msg.text.strip().split('\n') if word.strip()]
    games_data = load_games_data()
    added = 0
    skipped = 0
    
    for word in words:
        if word not in games_data["word_game_words"]:
            games_data["word_game_words"].append(word)
            added += 1
        else:
            skipped += 1
    
    save_games_data(games_data)
    await msg.answer(f"✅ Добавлено новых слов: {added}\n⏭ Пропущено дубликатов: {skipped}")
    await state.clear()

@router.message(Command("delete_emoji"))
async def delete_emoji_start(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("У вас нет прав для использования этой команды.")
        return
    
    games_data = load_games_data()
    if not games_data["emoji_movies"]:
        await msg.answer("Список фильмов пуст!")
        return
    
    # Формируем список фильмов для удаления
    movies_list = "\n".join(f"{i+1}. {m['emoji']} | {m['answer']}" 
                           for i, m in enumerate(games_data["emoji_movies"]))
    await msg.answer(f"Выберите номер фильма для удаления:\n\n{movies_list}")
    await state.set_state(GameStates.waiting_delete_emoji)

@router.message(GameStates.waiting_delete_emoji)
async def delete_emoji_process(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id):
        await state.clear()
        return
    
    try:
        index = int(msg.text.strip()) - 1
        games_data = load_games_data()
        if 0 <= index < len(games_data["emoji_movies"]):
            deleted = games_data["emoji_movies"].pop(index)
            save_games_data(games_data)
            await msg.answer(f"✅ Удален фильм: {deleted['emoji']} | {deleted['answer']}")
        else:
            await msg.answer("❌ Неверный номер фильма!")
    except ValueError:
        await msg.answer("❌ Пожалуйста, введите номер фильма!")
    
    await state.clear()

@router.message(Command("games_stats"))
async def games_stats(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("У вас нет прав для использования этой команды.")
        return
    
    games_data = load_games_data()
    stats = "📊 Статистика игр:\n\n"
    
    # Статистика по фильмам
    stats += "🎬 Фильмы:\n"
    stats += f"Всего: {len(games_data['emoji_movies'])}\n"
    if games_data["emoji_movies"]:
        stats += "Последние добавленные:\n"
        for movie in games_data["emoji_movies"][-5:]:
            stats += f"- {movie['emoji']} | {movie['answer']}\n"
    
    # Статистика по загадкам
    stats += "\n🎯 Загадки:\n"
    stats += f"Всего: {len(games_data['riddles'])}\n"
    if games_data["riddles"]:
        stats += "Последние добавленные:\n"
        for riddle in games_data["riddles"][-5:]:
            stats += f"- {riddle['riddle']} | {riddle['answer']}\n"
    
    # Статистика по словам
    stats += "\n📚 Слова:\n"
    stats += f"Всего: {len(games_data['word_game_words'])}\n"
    if games_data["word_game_words"]:
        stats += "Последние добавленные:\n"
        for word in games_data["word_game_words"][-5:]:
            stats += f"- {word}\n"
    
    await msg.answer(stats) 