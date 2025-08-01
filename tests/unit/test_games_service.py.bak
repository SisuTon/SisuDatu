import pytest
from unittest.mock import MagicMock
from sisu_bot.bot.services import games_service
from sisu_bot.bot.db.models import EmojiMovie

# Фикстура для мокирования сессии базы данных
@pytest.fixture
def db_session():
    session_mock = MagicMock()
    # Патчим Session там, где она используется в games_service
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('sisu_bot.bot.services.games_service.Session', MagicMock(return_value=session_mock))
        yield session_mock

def test_bulk_add_emoji_movies(db_session):
    movies_data = [
        {"emoji": "😀🎬", "answers": ["movie1", "фильм1"]},
        {"emoji": "🚗💨", "answers": ["fast and furious", "форсаж"]}
    ]
    games_service.bulk_add_emoji_movies(movies_data)

    # Проверяем, что были вызваны add и commit для каждого фильма
    assert db_session.add.call_count == len(movies_data)
    assert db_session.commit.called
    assert db_session.close.called

    # Проверяем аргументы, переданные в add
    # Важно: mock.add.call_args_list[0].args[0] будет mock-объектом, если EmojiMovie тоже мокнуть
    # Если EmojiMovie не мокается, то это будет экземпляр EmojiMovie, который можно проверить по атрибутам
    added_movie = db_session.add.call_args_list[0].args[0]
    assert isinstance(added_movie, EmojiMovie)
    assert added_movie.emoji == "😀🎬"
    assert added_movie.answers == "movie1,фильм1"

def test_get_random_emoji_movie(db_session):
    # Мокируем возвращаемое значение query.all()
    mock_movie1 = EmojiMovie(id=1, emoji="🎬", answers="фильм")
    mock_movie2 = EmojiMovie(id=2, emoji="🚗", answers="машина")

    # Убедимся, что query().all() возвращает наш список моков
    db_session.query.return_value.all.return_value = [mock_movie1, mock_movie2]

    movie = games_service.get_random_emoji_movie()

    # Проверяем, что возвращенный фильм является одним из моков и имеет правильные атрибуты
    assert movie.id in [mock_movie1.id, mock_movie2.id]
    assert movie.emoji in [mock_movie1.emoji, mock_movie2.emoji]
    assert movie.answers in [mock_movie1.answers, mock_movie2.answers]
    assert db_session.query.called
    assert db_session.close.called

def test_get_random_emoji_movie_no_movies(db_session):
    # Мокируем, что query().all() возвращает пустой список
    db_session.query.return_value.all.return_value = []

    movie = games_service.get_random_emoji_movie()
    assert movie is None
    assert db_session.query.called
    assert db_session.close.called

def test_check_emoji_movie_answer_correct(db_session):
    mock_movie = EmojiMovie(id=1, emoji="🎬", answers="фильм,кино")
    db_session.query.return_value.filter_by.return_value.first.return_value = mock_movie

    assert games_service.check_emoji_movie_answer(1, "фильм") is True
    assert games_service.check_emoji_movie_answer(1, "Кино") is True # Проверка нечувствительности к регистру
    assert db_session.query.called
    assert db_session.close.called

def test_check_emoji_movie_answer_incorrect(db_session):
    mock_movie = EmojiMovie(id=1, emoji="🎬", answers="фильм,кино")
    db_session.query.return_value.filter_by.return_value.first.return_value = mock_movie

    assert games_service.check_emoji_movie_answer(1, "мультфильм") is False
    assert db_session.query.called
    assert db_session.close.called

def test_check_emoji_movie_answer_movie_not_found(db_session):
    db_session.query.return_value.filter_by.return_value.first.return_value = None

    assert games_service.check_emoji_movie_answer(99, "любой ответ") is False
    assert db_session.query.called
    assert db_session.close.called

# Добавьте другие тесты для функций games_service здесь 