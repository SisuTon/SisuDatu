"""
Сервис для работы с квизами: генерация вопросов, проверка ответов.
"""
import json
from pathlib import Path

QUESTIONS_PATH = Path(__file__).parent / "questions.json"

def get_random_question():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    # Пример: вернуть первый вопрос (реализация рандома позже)
    return questions[0]
