import json
from pathlib import Path
from rapidfuzz import fuzz

_DATA_PATH = Path(__file__).parent / "data" / "talents.json"

_talents: dict[str, dict] = {}


def load() -> None:
    global _talents
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        _talents = json.load(f)


def lookup(name: str, min_score: int = 75) -> dict | None:
    if name in _talents:
        return {"name": name, "effect": _talents[name]["effect"], "exact": True}

    best_score = 0
    best_name = ""
    for key in _talents:
        score = fuzz.ratio(name, key)
        if score > best_score:
            best_score = score
            best_name = key

    if best_score >= min_score:
        return {
            "name": best_name,
            "effect": _talents[best_name]["effect"],
            "exact": False,
            "score": best_score,
        }

    return None


def get_all_names() -> list[str]:
    return list(_talents.keys())


load()
