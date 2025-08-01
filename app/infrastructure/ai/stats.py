from collections import defaultdict, deque

default_response_stats = lambda: {
    "total_uses": 0,
    "positive_reactions": 0,
    "negative_reactions": 0,
    "user_reactions": defaultdict(lambda: {"positive": 0, "negative": 0})
}

response_stats = defaultdict(default_response_stats)

user_preferences = defaultdict(lambda: {
    "favorite_topics": defaultdict(int),
    "response_style": "neutral",
    "last_interaction": None,
    "interaction_count": 0,
    "mood_history": deque(maxlen=10)
})

def update_response_stats(chat_id: int, user_id: int, response: str, is_positive: bool = True):
    stats = response_stats[response]
    stats["total_uses"] += 1
    if is_positive:
        stats["positive_reactions"] += 1
        stats["user_reactions"][user_id]["positive"] += 1
    else:
        stats["negative_reactions"] += 1
        stats["user_reactions"][user_id]["negative"] += 1

def get_user_style(user_id: int) -> str:
    prefs = user_preferences[user_id]
    if prefs["interaction_count"] < 5:
        return "neutral"
    # Можно добавить более сложную логику определения стиля
    return prefs["response_style"] 