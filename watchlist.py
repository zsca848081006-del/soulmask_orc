from rapidfuzz import fuzz

from config import load_watchlist, save_watchlist


def get_active() -> list[str]:
    return load_watchlist().get("active", [])


def set_active(names: list[str]) -> None:
    save_watchlist({"active": names})


def check_matches(
    detected: list[str], min_score: int = 75
) -> list[str]:
    active = get_active()
    if not active:
        return []
    matched: list[str] = []
    for d in detected:
        best = 0
        best_target = ""
        for target in active:
            score = fuzz.ratio(d, target)
            if score > best:
                best = score
                best_target = target
        if best >= min_score and best_target not in matched:
            matched.append(best_target)
    return matched
