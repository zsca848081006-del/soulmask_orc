import json
import time
from datetime import datetime, timezone
from pathlib import Path

import keyboard

import capture
import detect_icons
import detect_level
import ocr_engine
import talent_db
import watchlist
from config import load_config
from output import tts

_log_dir = Path(__file__).parent / "logs"
_log_dir.mkdir(exist_ok=True)

_running = True

LEVEL_MAP = {0: "--", 1: "Lv1", 2: "Lv2", 3: "Lv3"}


def _log(entry: dict) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_path = _log_dir / f"session_{ts}.jsonl"
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _group_ocr_by_rows(
    ocr_items: list[tuple[str, float, tuple[int, int]]],
    rows: list[tuple[int, int]],
    text_x: int,
) -> list[str]:
    """把 OCR 结果按 y 中心归到对应 icon 行, 同行按 x 顺序拼接."""
    buckets: list[list[tuple[int, str]]] = [[] for _ in rows]
    for text, _conf, (cx, cy) in ocr_items:
        if cx < text_x:
            continue
        for i, (ys, ye) in enumerate(rows):
            if ys <= cy < ye:
                buckets[i].append((cx, text))
                break
    out: list[str] = []
    for items in buckets:
        items.sort(key=lambda t: t[0])
        out.append("".join(t for _, t in items))
    return out


def _scan_and_speak(mode: str) -> None:
    cfg = load_config()
    roi = cfg["roi"]
    layout = cfg["layout"]
    min_conf = cfg.get("ocr", {}).get("min_confidence", 0.6)
    min_score = cfg.get("fuzzy_match", {}).get("min_score", 75)
    voice_rate = cfg.get("output", {}).get("voice_rate", 200)

    icon_x = layout["icon_x"]
    icon_width = layout["icon_width"]
    text_x = layout["text_x"]

    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    mode_label = "WATCH" if mode == "watchlist" else "FULL"
    print(f"\n[{ts}] [{mode_label}] 扫描中...")

    t0 = time.perf_counter()
    img = capture.capture_roi(roi["x"], roi["y"], roi["width"], roi["height"])
    t_cap = time.perf_counter()

    rows = detect_icons.find_icon_rows(img, icon_x, icon_width)
    t_rows = time.perf_counter()

    ocr_items = ocr_engine.recognize_full(img, min_confidence=min_conf)
    t_ocr = time.perf_counter()

    row_texts = _group_ocr_by_rows(ocr_items, rows, text_x)

    detected: list[dict] = []
    for (ys, ye), full_text in zip(rows, row_texts):
        if not full_text:
            continue
        icon_area = detect_icons.crop_icon_area(img, ys, ye, icon_x, icon_width)
        marks = detect_level.count_marks(icon_area)
        level_str = str(marks) if marks in (1, 2, 3) else None
        result = talent_db.lookup(full_text, min_score=min_score, level=level_str)
        if result:
            detected.append(result)
            lvl_tag = LEVEL_MAP.get(marks, "")
            tag = "=" if result.get("exact") else f"~{result.get('score',0)}%"
            print(f"  [{tag}] [{lvl_tag}] {result['name']}: {result['effect'][:60]}")
    t_match = time.perf_counter()

    print(
        f"  共匹配 {len(detected)} 个天赋  "
        f"[capture {(t_cap-t0)*1000:.0f}ms | rows {(t_rows-t_cap)*1000:.0f}ms | "
        f"ocr {(t_ocr-t_rows)*1000:.0f}ms | match {(t_match-t_ocr)*1000:.0f}ms | "
        f"total {(t_match-t0)*1000:.0f}ms]"
    )

    if mode == "watchlist":
        all_names = [d["name"] for d in detected]
        matched = watchlist.check_matches(all_names, min_score=min_score)
        print(f"  监视命中: {matched if matched else '无'}")
        _log({
            "event": "scan",
            "mode": "watchlist",
            "detected": all_names,
            "matched": matched,
            "details": detected,
        })
        if matched:
            tts.speak("匹配到：" + "、".join(matched), rate=voice_rate)
        elif not detected:
            tts.speak("未识别到天赋，请确认悬停面板已弹出", rate=voice_rate)
        else:
            tts.speak("未命中监视清单", rate=voice_rate)
    else:
        _log({
            "event": "scan",
            "mode": "full",
            "resolved": [f"{d['name']}Lv{d.get('level','?')}" for d in detected],
            "details": detected,
        })
        if not detected:
            tts.speak("未识别到天赋，请确认悬停面板已弹出", rate=voice_rate)
            return
        lines = [f"{d['name']}：{d['effect']}" for d in detected]
        tts.speak("，".join(lines), rate=voice_rate)


def _on_scan_watchlist() -> None:
    _scan_and_speak("watchlist")


def _on_scan_full() -> None:
    _scan_and_speak("full")


def _on_reload() -> None:
    talent_db.load()
    tts.speak("配置已重新加载", rate=200)


def _on_exit() -> None:
    global _running
    _running = False


def main() -> None:
    global _running

    cfg = load_config()
    hotkeys = cfg["hotkeys"]

    keyboard.add_hotkey(hotkeys["scan_watchlist"], _on_scan_watchlist)
    keyboard.add_hotkey(hotkeys["scan_full"], _on_scan_full)
    keyboard.add_hotkey(hotkeys["reload"], _on_reload)
    keyboard.add_hotkey(hotkeys["exit"], _on_exit)

    tts.init()

    print("=" * 50)
    print("  NPC 天赋 OCR 辅助工具 已启动  v1.2")
    print(f"  {hotkeys['scan_watchlist']} : 监视扫描（仅命中播报）")
    print(f"  {hotkeys['scan_full']}     : 全量查询（播报所有效果）")
    print(f"  {hotkeys['reload']}  : 重新加载配置 & 监视清单")
    print(f"  {hotkeys['exit']}   : 退出")
    print(f"  ROI: {cfg['roi']}")
    print(f"  扫描: 单次 OCR + 动态行检测 + 中性白等级识别")
    print("=" * 50)

    if cfg.get("output", {}).get("voice_enabled", True):
        tts.speak("天赋助手已启动", rate=cfg.get("output", {}).get("voice_rate", 200))

    while _running:
        time.sleep(0.1)

    print("正在退出...")
    tts.shutdown()
    keyboard.unhook_all_hotkeys()


if __name__ == "__main__":
    main()
