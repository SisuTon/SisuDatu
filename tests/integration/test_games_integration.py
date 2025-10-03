import pytest
import json
from pathlib import Path

GAMES_DATA_PATH = Path("sisu_bot/data/games_data.json")

@pytest.mark.parametrize("key,min_count", [
    ("emoji_movies", 1),
    ("word_game_words", 1),
    ("riddles", 1),
])
def test_games_data_not_empty(key, min_count):
    assert GAMES_DATA_PATH.exists(), "games_data.json отсутствует!"
    with open(GAMES_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert key in data, f"В базе нет ключа {key}"
    assert isinstance(data[key], list), f"{key} не список"
    assert len(data[key]) >= min_count, f"В {key} слишком мало данных!"

def test_list_games_response():
    # Эмулируем логику ответа /list_games
    with open(GAMES_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    response = "🎮 Мои игры:\n\n"
    response += f"🎬 Фильмов: {len(data['emoji_movies'])}\n"
    response += f"📚 Слов: {len(data['word_game_words'])}\n"
    response += f"🎯 Загадок: {len(data['riddles'])}\n\n"
    assert "Фильмов:" in response
    assert "Слов:" in response
    assert "Загадок:" in response
    assert len(data['emoji_movies']) > 0
    assert len(data['word_game_words']) > 0
    assert len(data['riddles']) > 0 