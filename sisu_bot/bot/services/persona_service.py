import random
import json
from pathlib import Path
from typing import Optional

NAME_JOKES_PATH = Path(__file__).parent.parent.parent / 'data' / 'name_jokes.json'
NAME_VARIANTS_PATH = Path(__file__).parent.parent.parent / 'data' / 'name_variants.json'
MICRO_LEGENDS_PATH = Path(__file__).parent.parent.parent / 'data' / 'sisu_micro_legends.json'
EASTER_EGGS_PATH = Path(__file__).parent.parent.parent / 'data' / 'sisu_easter_eggs.json'
MAGIC_PHRASES_PATH = Path(__file__).parent.parent.parent / 'data' / 'sisu_magic_phrases.json'

def load_name_jokes():
    try:
        with open(NAME_JOKES_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return [
            "Ну и имя у тебя, {name}... Ты точно не пароль от Wi-Fi?",
            "{name}? Это ты придумал или клавиатура сама нажалась?",
            "{name} — звучит как заклинание!",
            "{name}, надеюсь, ты не вирус?",
            "{name}? Я бы так дракона не назвала, но ладно!"
        ]

def save_name_jokes(pool):
    with open(NAME_JOKES_PATH, 'w', encoding='utf-8') as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)

def add_name_joke(text):
    pool = load_name_jokes()
    if text not in pool:
        pool.append(text)
        save_name_jokes(pool)
        return True
    return False

def remove_name_joke(text):
    pool = load_name_jokes()
    if text in pool:
        pool.remove(text)
        save_name_jokes(pool)
        return True
    return False

def list_name_jokes():
    return load_name_jokes()

def load_name_variants():
    try:
        with open(NAME_VARIANTS_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return [
            "Да-да, {name}?",
            "Ну что, {name}, опять ты?",
            "Слушаю, но не обещаю отвечать!",
            "А может, без формальностей?",
            "О, это снова ты!",
            "{name}, ты как вайб?",
            "{name}, ну удиви меня!",
            "{name}, ты не устал ещё?",
            "{name}, ну ты и настойчивый!",
            "{name}, ты сегодня особенно активен!",
        ]

def save_name_variants(pool):
    with open(NAME_VARIANTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)

def add_name_variant(text):
    pool = load_name_variants()
    if text not in pool:
        pool.append(text)
        save_name_variants(pool)
        return True
    return False

def remove_name_variant(text):
    pool = load_name_variants()
    if text in pool:
        pool.remove(text)
        save_name_variants(pool)
        return True
    return False

def list_name_variants():
    return load_name_variants()

_last_joke = None
_last_variant = None

def get_name_joke(name: str) -> str:
    global _last_joke
    pool = load_name_jokes()
    candidates = [j for j in pool if j != _last_joke]
    if not candidates:
        candidates = pool
    joke = random.choice(candidates)
    _last_joke = joke
    return joke.format(name=name)

def get_name_variant(name: str) -> str:
    global _last_variant
    pool = load_name_variants()
    candidates = [v for v in pool if v != _last_variant]
    if not candidates:
        candidates = pool
    variant = random.choice(candidates)
    _last_variant = variant
    return variant.format(name=name)

# --- Вайбовые истории (micro_legends) ---
def load_micro_legends():
    try:
        with open(MICRO_LEGENDS_PATH, encoding='utf-8') as f:
            return json.load(f).get("micro_legends", [])
    except Exception:
        return []

def save_micro_legends(pool):
    with open(MICRO_LEGENDS_PATH, 'w', encoding='utf-8') as f:
        json.dump({"micro_legends": pool}, f, ensure_ascii=False, indent=2)

def add_micro_legend(text):
    pool = load_micro_legends()
    if text not in pool:
        pool.append(text)
        save_micro_legends(pool)
        return True
    return False

def remove_micro_legend(text):
    pool = load_micro_legends()
    if text in pool:
        pool.remove(text)
        save_micro_legends(pool)
        return True
    return False

def list_micro_legends():
    return load_micro_legends()

# --- Пасхалки (easter eggs) ---
def load_easter_eggs():
    try:
        with open(EASTER_EGGS_PATH, encoding='utf-8') as f:
            return json.load(f).get("easter_eggs", [])
    except Exception:
        return []

def save_easter_eggs(pool):
    with open(EASTER_EGGS_PATH, 'w', encoding='utf-8') as f:
        json.dump({"easter_eggs": pool}, f, ensure_ascii=False, indent=2)

def add_easter_egg(text):
    pool = load_easter_eggs()
    if text not in pool:
        pool.append(text)
        save_easter_eggs(pool)
        return True
    return False

def remove_easter_egg(text):
    pool = load_easter_eggs()
    if text in pool:
        pool.remove(text)
        save_easter_eggs(pool)
        return True
    return False

def list_easter_eggs():
    return load_easter_eggs()

# --- Магические фразы (magic_phrases) ---
def load_magic_phrases():
    try:
        with open(MAGIC_PHRASES_PATH, encoding='utf-8') as f:
            return json.load(f).get("magic_phrases", [])
    except Exception:
        return []

def save_magic_phrases(pool):
    with open(MAGIC_PHRASES_PATH, 'w', encoding='utf-8') as f:
        json.dump({"magic_phrases": pool}, f, ensure_ascii=False, indent=2)

def add_magic_phrase(text):
    pool = load_magic_phrases()
    if text not in pool:
        pool.append(text)
        save_magic_phrases(pool)
        return True
    return False

def remove_magic_phrase(text):
    pool = load_magic_phrases()
    if text in pool:
        pool.remove(text)
        save_magic_phrases(pool)
        return True
    return False

def list_magic_phrases():
    return load_magic_phrases()

def get_random_micro_legend() -> Optional[str]:
    legends = load_micro_legends()
    return random.choice(legends) if legends else None

def get_random_easter_egg() -> Optional[str]:
    eggs = load_easter_eggs()
    return random.choice(eggs) if eggs else None

def get_random_magic_phrase() -> Optional[str]:
    phrases = load_magic_phrases()
    return random.choice(phrases) if phrases else None 