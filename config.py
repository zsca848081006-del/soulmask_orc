import json
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).parent / "data"


def _load_json(filename: str) -> dict[str, Any]:
    with open(_DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict[str, Any]:
    return _load_json("config.json")


def save_config(cfg: dict[str, Any]) -> None:
    with open(_DATA_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_watchlist() -> dict[str, Any]:
    return _load_json("watchlist.json")


def save_watchlist(data: dict[str, Any]) -> None:
    with open(_DATA_DIR / "watchlist.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
