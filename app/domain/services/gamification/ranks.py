"""
Утилиты для работы с рангами.
"""
import json
from pathlib import Path

RANKS_PATH = Path(__file__).parent / "rank_table.json"

def get_rank_for_points(points: int) -> str:
    with open(RANKS_PATH, "r", encoding="utf-8") as f:
        ranks = json.load(f)
    for rank in sorted(ranks, key=lambda x: x["min_points"], reverse=True):
        if points >= rank["min_points"]:
            return rank["title"]
    return "Новичок"
