import pytest
from sisu_bot.bot.services import ai_trigger_service
import json
import os
from pathlib import Path

# Фикстура для временного файла данных обучения
@pytest.fixture(scope="function")
def temp_learning_data_file(tmp_path):
    old_path = ai_trigger_service.LEARNING_PATH
    temp_file = tmp_path / "learning_data.json"
    ai_trigger_service.LEARNING_PATH = temp_file

    # Убедимся, что файл пуст в начале теста
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    # Очищаем и инициализируем LEARNING_DATA в памяти, чтобы каждый тест начинался с чистого состояния
    ai_trigger_service.LEARNING_DATA.clear()
    ai_trigger_service.LEARNING_DATA.update({"triggers": {}, "responses": {}})

    yield

    # Восстанавливаем оригинальный путь и удаляем временный файл
    ai_trigger_service.LEARNING_PATH = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)
    # Очищаем LEARNING_DATA снова, чтобы избежать влияния на другие тесты
    ai_trigger_service.LEARNING_DATA.clear()
    ai_trigger_service.LEARNING_DATA.update({"triggers": {}, "responses": {}})

def test_learn_response(temp_learning_data_file):
    trigger = "hello"
    response = "hi there!"
    ai_trigger_service.learn_response(trigger, response)

    # Проверяем данные в памяти
    assert ai_trigger_service.LEARNING_DATA["triggers"][trigger] == [response]

    # Проверяем сохраненные данные
    with open(ai_trigger_service.LEARNING_PATH, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    assert saved_data["triggers"][trigger] == [response]

def test_get_learned_response(temp_learning_data_file):
    trigger = "question"
    response1 = "answer1"
    response2 = "answer2"
    ai_trigger_service.learn_response(trigger, response1)
    ai_trigger_service.learn_response(trigger, response2)

    # Тестируем получение ответа
    found_response = ai_trigger_service.get_learned_response(trigger)
    assert found_response in [response1, response2]

    # Тестируем с last_answer, чтобы убедиться, что выбирается другой ответ
    found_response_filtered = ai_trigger_service.get_learned_response(trigger, last_answer=response1)
    if len(ai_trigger_service.LEARNING_DATA["triggers"][trigger]) > 1:
        assert found_response_filtered == response2
    else:
        assert found_response_filtered == response1

    # Тестируем несуществующий триггер
    non_existent_response = ai_trigger_service.get_learned_response("nonexistent")
    assert non_existent_response is None

def test_learn_response_no_duplicate(temp_learning_data_file):
    trigger = "duplicate"
    response = "unique response"
    ai_trigger_service.learn_response(trigger, response)
    ai_trigger_service.learn_response(trigger, response) # Попытка добавить снова

    assert ai_trigger_service.LEARNING_DATA["triggers"][trigger] == [response]
    with open(ai_trigger_service.LEARNING_PATH, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    assert saved_data["triggers"][trigger] == [response]

# Добавьте другие тесты для функций ai_trigger_service здесь 