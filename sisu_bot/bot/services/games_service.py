from sisu_bot.bot.db.init_db import Session
from sisu_bot.bot.db.models import EmojiMovie
import random

# Bulk-добавление фильмов (admin)
def bulk_add_emoji_movies(movies: list[dict]):
    session = Session()
    for movie in movies:
        emoji = movie['emoji']
        answers = ','.join([a.strip().lower() for a in movie['answers']])
        session.add(EmojiMovie(emoji=emoji, answers=answers))
    session.commit()
    session.close()

# Получить случайный фильм
def get_random_emoji_movie():
    session = Session()
    movies = session.query(EmojiMovie).all()
    session.close()
    if not movies:
        return None
    return random.choice(movies)

# Проверить ответ пользователя
def check_emoji_movie_answer(movie_id: int, user_answer: str) -> bool:
    session = Session()
    movie = session.query(EmojiMovie).filter_by(id=movie_id).first()
    session.close()
    if not movie:
        return False
    answers = [a.strip().lower() for a in movie.answers.split(",")]
    return user_answer.strip().lower() in answers 