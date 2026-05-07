import json
from pathlib import Path
from rapidfuzz import fuzz

_DATA_PATH = Path(__file__).parent / "data" / "talents.json"

_talents: dict[str, dict] = {}


def load() -> None:
    global _talents
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        _talents = json.load(f)


def lookup(name: str, min_score: int = 75, level: str | None = None) -> dict | None:
    if name in _talents:
        entry = _talents[name]
        return _build_result(name, entry, exact=True, level=level)

    best_score = 0
    best_name = ""
    for key in _talents:
        score = fuzz.ratio(name, key)
        if score > best_score:
            best_score = score
            best_name = key

    if best_score >= min_score:
        return _build_result(best_name, _talents[best_name], exact=False, score=best_score, level=level)

    return None


def _build_result(
    name: str,
    entry: dict,
    exact: bool,
    score: int | None = None,
    level: str | None = None,
) -> dict:
    if level and level in entry:
        effect = entry[level]
        level_used = level
    else:
        available = sorted(entry.keys(), key=int)
        level_used = available[-1]
        effect = entry[level_used]

    result = {
        "name": name,
        "effect": effect,
        "level": level_used,
        "exact": exact,
    }
    if score is not None:
        result["score"] = score
    return result


def get_all_names() -> list[str]:
    return list(_talents.keys())


load()
