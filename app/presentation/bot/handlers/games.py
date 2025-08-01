from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import json
import random
import logging
from pathlib import Path
from app.shared.config.settings import Settings
from app.domain.services.gamification import points as points_service

router = Router()

# Загружаем данные игр
DATA_DIR = Settings().data_dir
GAMES_FILE = DATA_DIR / 'games_data.json'

def load_games_data():
    """Загружает данные игр"""
    try:
        with open(GAMES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки игр: {e}")
        return {"games": {}, "emoji_movies": {}, "word_games": {}, "trivia_questions": {}}

@router.message(Command("games"))
async def games_handler(msg: Message):
    """Показывает доступные игры"""
    games_data = load_games_data()
    games = games_data.get("games", {})
    
    text = "🎮 <b>ДОСТУПНЫЕ ИГРЫ:</b>\n\n"
    
    for game_id, game_info in games.items():
        if game_info.get("enabled", False):
            name = game_info.get("name", "Неизвестная игра")
            description = game_info.get("description", "")
            points = game_info.get("points_reward", 0)
            
            text += f"🎯 <b>{name}</b>\n"
            text += f"📝 {description}\n"
            text += f"🏆 Награда: {points} баллов\n\n"
    
    text += "Используй команды:\n"
    text += "/emoji_game - Угадай фильм по эмодзи\n"
    text += "/word_game - Словесная игра\n"
    text += "/trivia - Викторина о крипте\n"
    
    await msg.answer(text, parse_mode="HTML")

@router.message(Command("emoji_game"))
async def emoji_game_handler(msg: Message):
    """Игра угадай фильм по эмодзи"""
    games_data = load_games_data()
    emoji_movies = games_data.get("emoji_movies", {})
    
    if not emoji_movies:
        await msg.answer("🎬 Игра временно недоступна!")
        return
    
    # Выбираем случайный фильм
    emoji, correct_answer = random.choice(list(emoji_movies.items()))
    
    # Создаем варианты ответов
    all_answers = list(emoji_movies.values())
    wrong_answers = [ans for ans in all_answers if ans != correct_answer]
    options = [correct_answer] + random.sample(wrong_answers, min(3, len(wrong_answers)))
    random.shuffle(options)
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=option, callback_data=f"emoji_answer:{option}:{correct_answer}")]
        for option in options
    ])
    
    text = f"🎬 <b>Угадай фильм по эмодзи:</b>\n\n{emoji}\n\nВыбери правильный ответ:"
    
    await msg.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data.startswith("emoji_answer:"))
async def emoji_answer_callback(call: CallbackQuery):
    """Обработка ответа в игре угадай фильм"""
    try:
        _, user_answer, correct_answer = call.data.split(":", 2)
        
        if user_answer == correct_answer:
            # Правильный ответ
            points = 10
            await points_service.add_points(call.from_user.id, points)
            
            await call.message.edit_text(
                f"🎉 <b>Правильно!</b>\n\n"
                f"Фильм: <b>{correct_answer}</b>\n"
                f"🏆 +{points} баллов!",
                parse_mode="HTML"
            )
        else:
            # Неправильный ответ
            await call.message.edit_text(
                f"❌ <b>Неправильно!</b>\n\n"
                f"Правильный ответ: <b>{correct_answer}</b>\n"
                f"Твой ответ: {user_answer}",
                parse_mode="HTML"
            )
        
        await call.answer()
        
    except Exception as e:
        logging.error(f"Ошибка в emoji_answer_callback: {e}")
        await call.answer("Произошла ошибка!")

@router.message(Command("word_game"))
async def word_game_handler(msg: Message):
    """Словесная игра"""
    games_data = load_games_data()
    word_games = games_data.get("word_games", {})
    
    if not word_games:
        await msg.answer("📝 Игра временно недоступна!")
        return
    
    # Выбираем случайное слово
    word, answers = random.choice(list(word_games.items()))
    
    # Перемешиваем буквы
    shuffled = list(word)
    random.shuffle(shuffled)
    shuffled_word = ''.join(shuffled)
    
    text = f"📝 <b>Словесная игра:</b>\n\n"
    text += f"Составь слово из букв: <b>{shuffled_word}</b>\n\n"
    text += "Отправь свой ответ в чат!"
    
    await msg.answer(text, parse_mode="HTML")

@router.message(Command("trivia"))
async def trivia_handler(msg: Message):
    """Викторина о крипте"""
    games_data = load_games_data()
    trivia_questions = games_data.get("trivia_questions", {})
    
    if not trivia_questions:
        await msg.answer("🧠 Викторина временно недоступна!")
        return
    
    # Выбираем случайный вопрос
    question, answers = random.choice(list(trivia_questions.items()))
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=answer, callback_data=f"trivia_answer:{answer}:{answers[0]}")]
        for answer in answers
    ])
    
    text = f"🧠 <b>Викторина о крипте:</b>\n\n{question}\n\nВыбери правильный ответ:"
    
    await msg.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data.startswith("trivia_answer:"))
async def trivia_answer_callback(call: CallbackQuery):
    """Обработка ответа в викторине"""
    try:
        _, user_answer, correct_answer = call.data.split(":", 2)
        
        if user_answer == correct_answer:
            # Правильный ответ
            points = 20
            await points_service.add_points(call.from_user.id, points)
            
            await call.message.edit_text(
                f"🎉 <b>Правильно!</b>\n\n"
                f"Ответ: <b>{correct_answer}</b>\n"
                f"🏆 +{points} баллов!",
                parse_mode="HTML"
            )
        else:
            # Неправильный ответ
            await call.message.edit_text(
                f"❌ <b>Неправильно!</b>\n\n"
                f"Правильный ответ: <b>{correct_answer}</b>\n"
                f"Твой ответ: {user_answer}",
                parse_mode="HTML"
            )
        
        await call.answer()
        
    except Exception as e:
        logging.error(f"Ошибка в trivia_answer_callback: {e}")
        await call.answer("Произошла ошибка!") 