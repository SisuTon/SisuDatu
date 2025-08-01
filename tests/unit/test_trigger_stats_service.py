import pytest
import json
import os
from pathlib import Path
from app.domain.services import trigger_stats_service
import datetime

# Фикстура для временного файла статистики триггеров
@pytest.fixture(scope="function")
def temp_trigger_stats_file(tmp_path):
    old_path = trigger_stats_service.TRIGGER_STATS_FILE
    temp_file = tmp_path / "trigger_stats.json"
    trigger_stats_service.TRIGGER_STATS_FILE = str(temp_file) # os.path.join expects string
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
    # Убедимся, что файл пуст в начале теста
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({}, f)

    yield

    # Восстанавливаем оригинальный путь и удаляем временный файл
    trigger_stats_service.TRIGGER_STATS_FILE = old_path
    if os.path.exists(temp_file):
        os.remove(temp_file)

def test_load_stats_empty(temp_trigger_stats_file):
    stats = trigger_stats_service.load_stats()
    assert stats == {}

def test_save_stats(temp_trigger_stats_file):
    test_data = {"test_trigger": {"count": 1, "answers": {"test_answer": 1}}}
    trigger_stats_service.save_stats(test_data)

    with open(trigger_stats_service.TRIGGER_STATS_FILE, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data

def test_log_trigger_usage(temp_trigger_stats_file):
    trigger = "test_trigger"
    answer = "test_answer"
    user_id = 123
    chat_id = 456
    
    trigger_stats_service.log_trigger_usage(trigger, answer, user_id, chat_id)
    stats = trigger_stats_service.load_stats()

    assert trigger in stats
    assert stats[trigger]["count"] == 1
    assert stats[trigger]["answers"][answer] == 2 # Изначально 1, потом +1
    assert stats[trigger]["users"][str(user_id)] == 1
    assert stats[trigger]["chats"][str(chat_id)] == 1
    assert "last_used" in stats[trigger]

    # Повторное использование
    trigger_stats_service.log_trigger_usage(trigger, answer, user_id, chat_id)
    stats = trigger_stats_service.load_stats()
    assert stats[trigger]["count"] == 2
    assert stats[trigger]["answers"][answer] == 3
    assert stats[trigger]["users"][str(user_id)] == 2

def test_get_trigger_stats(temp_trigger_stats_file):
    trigger = "test_trigger_get"
    answer = "test_answer_get"
    user_id = 789
    chat_id = 1011
    trigger_stats_service.log_trigger_usage(trigger, answer, user_id, chat_id)

    stats = trigger_stats_service.get_trigger_stats(trigger)
    assert stats is not None
    assert stats["count"] == 1
    assert stats["answers"][answer] == 2

    non_existent_stats = trigger_stats_service.get_trigger_stats("non_existent_trigger")
    assert non_existent_stats is None

def test_get_all_trigger_stats(temp_trigger_stats_file):
    trigger1 = "trig1"; answer1 = "ans1"; user1 = 1; chat1 = 1
    trigger2 = "trig2"; answer2 = "ans2"; user2 = 2; chat2 = 2
    
    trigger_stats_service.log_trigger_usage(trigger1, answer1, user1, chat1)
    trigger_stats_service.log_trigger_usage(trigger2, answer2, user2, chat2)

    all_stats = trigger_stats_service.get_all_trigger_stats()
    assert len(all_stats) == 2
    assert trigger1 in all_stats
    assert trigger2 in all_stats

def test_add_like_and_dislike(temp_trigger_stats_file):
    trigger = "like_dislike_trigger"
    answer = "like_dislike_answer"
    user_id = 111
    chat_id = 222

    trigger_stats_service.log_trigger_usage(trigger, answer, user_id, chat_id)
    trigger_stats_service.add_like(trigger, answer)
    trigger_stats_service.add_dislike(trigger, answer)

    likes, dislikes = trigger_stats_service.get_likes_dislikes(trigger, answer)
    assert likes == 1
    assert dislikes == 1

def test_get_smart_answer(temp_trigger_stats_file):
    trigger = "smart_trigger"
    answers = ["answer_A", "answer_B", "answer_C"]
    user_id = 333
    chat_id = 444

    # Логируем ответы, чтобы у них были веса
    trigger_stats_service.log_trigger_usage(trigger, "answer_A", user_id, chat_id)
    trigger_stats_service.log_trigger_usage(trigger, "answer_A", user_id, chat_id)
    trigger_stats_service.log_trigger_usage(trigger, "answer_B", user_id, chat_id)

    # Добавляем лайк к ответу B
    trigger_stats_service.add_like(trigger, "answer_B")

    # Тестируем, что умный ответ выбирается (хотя с рандомом трудно предсказать точно)
    # Повторяем несколько раз, чтобы убедиться, что он выбирает из предоставленных ответов
    for _ in range(10):
        smart_answer = trigger_stats_service.get_smart_answer(trigger, answers)
        assert smart_answer in answers
    
    # Проверим с last_answer
    smart_answer_filtered = trigger_stats_service.get_smart_answer(trigger, answers, last_answer="answer_A")
    assert smart_answer_filtered in ["answer_B", "answer_C"]

def test_suggest_new_triggers(temp_trigger_stats_file):
    # Создаем тестовые данные для триггеров
    trigger_stats_service.log_trigger_usage("trig_a", "ans1", 1, 1)
    trigger_stats_service.log_trigger_usage("trig_a", "ans1", 1, 1)
    trigger_stats_service.log_trigger_usage("trig_a", "ans1", 2, 2)
    trigger_stats_service.log_trigger_usage("trig_a", "ans1", 3, 3)
    # trig_a: count=4, answers={'ans1':4}, users={1:2,2:1,3:1}, chats={1:2,2:1,3:1}

    trigger_stats_service.log_trigger_usage("trig_b", "ans_x", 1, 1)
    trigger_stats_service.log_trigger_usage("trig_b", "ans_y", 2, 2)
    trigger_stats_service.log_trigger_usage("trig_b", "ans_z", 3, 3)
    trigger_stats_service.log_trigger_usage("trig_b", "ans_x", 4, 4)
    trigger_stats_service.log_trigger_usage("trig_b", "ans_y", 5, 5)
    trigger_stats_service.log_trigger_usage("trig_b", "ans_a", 6, 6)
    # trig_b: count=6, answers={'ans_x':2, 'ans_y':2, 'ans_z':1, 'ans_a':1}, users={1:1,2:1,3:1,4:1,5:1,6:1}

    trigger_stats_service.log_trigger_usage("trig_c", "ans_q", 10, 10)
    trigger_stats_service.log_trigger_usage("trig_c", "ans_q", 11, 11)
    trigger_stats_service.log_trigger_usage("trig_c", "ans_p", 12, 12)
    # trig_c: count=3, answers={'ans_q':2, 'ans_p':1}, users={10:1,11:1,12:1}

    suggestions = trigger_stats_service.suggest_new_triggers(min_count=3, limit=5)
    # Ожидаем trig_a, так как у него >=3 пользователей и <=2 ответа (хотя answers.keys() будет 1) 
    # trig_b имеет слишком много ответов (4) для предложенной логики (<=2)

    assert len(suggestions) == 1
    assert suggestions[0][0] == "trig_a"
    assert suggestions[0][1] == 4 # count
    assert suggestions[0][2] == 3 # users

def test_auto_add_suggested_triggers(temp_trigger_stats_file, tmp_path):
    # Мокируем LEARNING_PATH для этого теста
    original_learning_path = trigger_stats_service.LEARNING_PATH
    temp_learning_file = tmp_path / "learning_data_test.json"
    trigger_stats_service.LEARNING_PATH = temp_learning_file
    
    # Создаем пустой learning_data.json для начала
    with open(temp_learning_file, 'w', encoding='utf-8') as f:
        json.dump({"triggers": {}, "responses": {}}, f)

    trigger_stats_service.log_trigger_usage("trig_suggest", "resp_suggest", 1, 1)
    trigger_stats_service.log_trigger_usage("trig_suggest", "resp_suggest", 2, 2)
    trigger_stats_service.log_trigger_usage("trig_suggest", "resp_suggest", 3, 3)
    trigger_stats_service.log_trigger_usage("trig_suggest", "resp_suggest", 4, 4)
    trigger_stats_service.log_trigger_usage("trig_suggest", "resp_suggest", 5, 5)

    added_triggers = trigger_stats_service.auto_add_suggested_triggers(min_count=5, min_users=3)

    assert "trig_suggest" in added_triggers
    
    with open(temp_learning_file, 'r', encoding='utf-8') as f:
        learning_data = json.load(f)
    assert "trig_suggest" in learning_data["triggers"]
    assert learning_data["triggers"]["trig_suggest"] == ["resp_suggest", "resp_suggest"] # Из-за особенностей log_trigger_usage

    # Восстанавливаем оригинальный путь
    trigger_stats_service.LEARNING_PATH = original_learning_path
    if os.path.exists(temp_learning_file):
        os.remove(temp_learning_file)

# Добавьте другие тесты для функций trigger_stats_service здесь 