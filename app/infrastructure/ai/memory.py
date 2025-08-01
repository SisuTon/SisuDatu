from collections import defaultdict, deque

# Память: последние 30 обращений в каждом чате
sisu_memory = defaultdict(lambda: deque(maxlen=30))  # chat_id -> deque of last messages
# Настроение: от -4 (сарказм/тролль) до +4 (максимальный вайб)
sisu_mood = defaultdict(lambda: 0)  # chat_id -> mood

def update_mood(chat_id, text):
    text = text.lower()
    if any(word in text for word in [
        "спасибо", "круто", "топ", "обожаю", "лучший", "супер", "огонь", "респект", "аплодисменты", "лайк", "восторг", "класс", "молодец", "дракон топ", "сила", "люблю", "обнял", "дружба"
    ]):
        sisu_mood[chat_id] = min(sisu_mood[chat_id] + 1, 4)
    elif any(word in text for word in [
        "лох", "дура", "тупая", "слабая", "идиотка", "тролль", "троллишь", "бот", "шлюха"
    ]):
        sisu_mood[chat_id] = max(sisu_mood[chat_id] - 1, -4)
    else:
        import random
        if random.random() < 0.1:
            sisu_mood[chat_id] += random.choice([-1, 1])
            sisu_mood[chat_id] = max(-4, min(4, sisu_mood[chat_id]))

def get_mood_local(chat_id):
    return sisu_mood[chat_id] 