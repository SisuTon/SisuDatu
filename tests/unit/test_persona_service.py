import pytest
import json
import os
from pathlib import Path
from sisu_bot.bot.services import persona_service

# Фикстура для временного файла с шутками про имена
@pytest.fixture(scope="function")
def temp_name_jokes_file(tmp_path):
    old_path = persona_service.NAME_JOKES_PATH
    temp_file = tmp_path / "name_jokes.json"
    persona_service.NAME_JOKES_PATH = temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    # Создаем пустой файл, чтобы load_name_jokes не возвращал дефолтные значения
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump([], f)
    yield
    persona_service.NAME_JOKES_PATH = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)

# Фикстура для временного файла с вариантами имен
@pytest.fixture(scope="function")
def temp_name_variants_file(tmp_path):
    old_path = persona_service.NAME_VARIANTS_PATH
    temp_file = tmp_path / "name_variants.json"
    persona_service.NAME_VARIANTS_PATH = temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump([], f)
    yield
    persona_service.NAME_VARIANTS_PATH = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)

# Фикстура для временного файла с микро-легендами
@pytest.fixture(scope="function")
def temp_micro_legends_file(tmp_path):
    old_path = persona_service.MICRO_LEGENDS_PATH
    temp_file = tmp_path / "sisu_micro_legends.json"
    persona_service.MICRO_LEGENDS_PATH = temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({"micro_legends": []}, f)
    yield
    persona_service.MICRO_LEGENDS_PATH = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)

# Фикстура для временного файла с пасхалками
@pytest.fixture(scope="function")
def temp_easter_eggs_file(tmp_path):
    old_path = persona_service.EASTER_EGGS_PATH
    temp_file = tmp_path / "sisu_easter_eggs.json"
    persona_service.EASTER_EGGS_PATH = temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({"easter_eggs": []}, f)
    yield
    persona_service.EASTER_EGGS_PATH = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)

# Фикстура для временного файла с магическими фразами
@pytest.fixture(scope="function")
def temp_magic_phrases_file(tmp_path):
    old_path = persona_service.MAGIC_PHRASES_PATH
    temp_file = tmp_path / "sisu_magic_phrases.json"
    persona_service.MAGIC_PHRASES_PATH = temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({"magic_phrases": []}, f)
    yield
    persona_service.MAGIC_PHRASES_PATH = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)

# --- Тесты для name_jokes ---
def test_load_name_jokes_empty(temp_name_jokes_file):
    jokes = persona_service.load_name_jokes()
    assert jokes == []

def test_add_name_joke(temp_name_jokes_file):
    joke_text = "Новая шутка"
    added = persona_service.add_name_joke(joke_text)
    assert added is True
    jokes = persona_service.load_name_jokes()
    assert joke_text in jokes

def test_add_name_joke_duplicate(temp_name_jokes_file):
    joke_text = "Существующая шутка"
    persona_service.add_name_joke(joke_text)
    added = persona_service.add_name_joke(joke_text)
    assert added is False
    jokes = persona_service.load_name_jokes()
    assert jokes.count(joke_text) == 1

def test_remove_name_joke(temp_name_jokes_file):
    joke_text = "Шутка для удаления"
    persona_service.add_name_joke(joke_text)
    removed = persona_service.remove_name_joke(joke_text)
    assert removed is True
    jokes = persona_service.load_name_jokes()
    assert joke_text not in jokes

def test_remove_name_joke_non_existent(temp_name_jokes_file):
    removed = persona_service.remove_name_joke("Несуществующая шутка")
    assert removed is False

def test_list_name_jokes(temp_name_jokes_file):
    persona_service.add_name_joke("Шутка 1")
    persona_service.add_name_joke("Шутка 2")
    jokes = persona_service.list_name_jokes()
    assert len(jokes) == 2
    assert "Шутка 1" in jokes
    assert "Шутка 2" in jokes

def test_get_name_joke(temp_name_jokes_file):
    persona_service.add_name_joke("Привет, {name}!")
    joke = persona_service.get_name_joke("Сису")
    assert joke == "Привет, Сису!"

def test_get_name_joke_multiple_choices(temp_name_jokes_file):
    persona_service.add_name_joke("Joke 1, {name}")
    persona_service.add_name_joke("Joke 2, {name}")
    # Мы не можем предсказать, какая шутка будет выбрана, но можем проверить формат
    joke = persona_service.get_name_joke("User")
    assert "User" in joke
    assert "Joke 1" in joke or "Joke 2" in joke

# --- Тесты для name_variants ---
def test_load_name_variants_empty(temp_name_variants_file):
    variants = persona_service.load_name_variants()
    assert variants == []

def test_add_name_variant(temp_name_variants_file):
    variant_text = "Новый вариант"
    added = persona_service.add_name_variant(variant_text)
    assert added is True
    variants = persona_service.load_name_variants()
    assert variant_text in variants

def test_remove_name_variant(temp_name_variants_file):
    variant_text = "Вариант для удаления"
    persona_service.add_name_variant(variant_text)
    removed = persona_service.remove_name_variant(variant_text)
    assert removed is True
    variants = persona_service.load_name_variants()
    assert variant_text not in variants

def test_list_name_variants(temp_name_variants_file):
    persona_service.add_name_variant("Вариант 1")
    persona_service.add_name_variant("Вариант 2")
    variants = persona_service.list_name_variants()
    assert len(variants) == 2
    assert "Вариант 1" in variants

def test_get_name_variant(temp_name_variants_file):
    persona_service.add_name_variant("Привет, {name}!")
    variant = persona_service.get_name_variant("Сису")
    assert variant == "Привет, Сису!"

# --- Тесты для micro_legends ---
def test_load_micro_legends_empty(temp_micro_legends_file):
    legends = persona_service.load_micro_legends()
    assert legends == []

def test_add_micro_legend(temp_micro_legends_file):
    legend_text = "Новая легенда"
    added = persona_service.add_micro_legend(legend_text)
    assert added is True
    legends = persona_service.load_micro_legends()
    assert legend_text in legends

def test_remove_micro_legend(temp_micro_legends_file):
    legend_text = "Легенда для удаления"
    persona_service.add_micro_legend(legend_text)
    removed = persona_service.remove_micro_legend(legend_text)
    assert removed is True
    legends = persona_service.load_micro_legends()
    assert legend_text not in legends

def test_list_micro_legends(temp_micro_legends_file):
    persona_service.add_micro_legend("Легенда 1")
    persona_service.add_micro_legend("Легенда 2")
    legends = persona_service.list_micro_legends()
    assert len(legends) == 2

# --- Тесты для easter_eggs ---
def test_load_easter_eggs_empty(temp_easter_eggs_file):
    eggs = persona_service.load_easter_eggs()
    assert eggs == []

def test_add_easter_egg(temp_easter_eggs_file):
    egg_text = "Новая пасхалка"
    added = persona_service.add_easter_egg(egg_text)
    assert added is True
    eggs = persona_service.load_easter_eggs()
    assert egg_text in eggs

def test_remove_easter_egg(temp_easter_eggs_file):
    egg_text = "Пасхалка для удаления"
    persona_service.add_easter_egg(egg_text)
    removed = persona_service.remove_easter_egg(egg_text)
    assert removed is True
    eggs = persona_service.load_easter_eggs()
    assert egg_text not in eggs

def test_list_easter_eggs(temp_easter_eggs_file):
    persona_service.add_easter_egg("Пасхалка 1")
    persona_service.add_easter_egg("Пасхалка 2")
    eggs = persona_service.list_easter_eggs()
    assert len(eggs) == 2

# --- Тесты для magic_phrases ---
def test_load_magic_phrases_empty(temp_magic_phrases_file):
    phrases = persona_service.load_magic_phrases()
    assert phrases == []

def test_add_magic_phrase(temp_magic_phrases_file):
    phrase_text = "Новая фраза"
    added = persona_service.add_magic_phrase(phrase_text)
    assert added is True
    phrases = persona_service.load_magic_phrases()
    assert phrase_text in phrases

def test_remove_magic_phrase(temp_magic_phrases_file):
    phrase_text = "Фраза для удаления"
    persona_service.add_magic_phrase(phrase_text)
    removed = persona_service.remove_magic_phrase(phrase_text)
    assert removed is True
    phrases = persona_service.load_magic_phrases()
    assert phrase_text not in phrases

def test_list_magic_phrases(temp_magic_phrases_file):
    persona_service.add_magic_phrase("Фраза 1")
    persona_service.add_magic_phrase("Фраза 2")
    phrases = persona_service.list_magic_phrases()
    assert len(phrases) == 2 