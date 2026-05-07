import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import keyboard

import capture
import ocr_engine
import talent_db
import watchlist
from config import load_config
from output import tts

_log_dir = Path(__file__).parent / "logs"
_log_dir.mkdir(exist_ok=True)

_running = True


def _log(entry: dict) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_path = _log_dir / f"session_{ts}.jsonl"
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _scan_and_speak(mode: str) -> None:
    cfg = load_config()
    roi = cfg["roi"]
    min_conf = cfg.get("ocr", {}).get("min_confidence", 0.6)
    min_score = cfg.get("fuzzy_match", {}).get("min_score", 75)
    voice_rate = cfg.get("output", {}).get("voice_rate", 200)

    img = capture.capture_roi(roi["x"], roi["y"], roi["width"], roi["height"])

    raw_items = ocr_engine.recognize(img, min_confidence=min_conf)

    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    mode_label = "WATCH" if mode == "watchlist" else "FULL"
    print(f"\n[{ts}] [{mode_label}] 扫描完成")

    if not raw_items:
        print(f"  OCR: 未识别到任何文字")
        _log({"event": "scan", "mode": mode, "detected": [], "matched": []})
        if cfg.get("output", {}).get("voice_enabled", True):
            tts.speak("未识别到天赋，请确认悬停面板已弹出", rate=voice_rate)
        return

    detected_texts = [text for text, _ in raw_items]
    print(f"  OCR 原始识别 ({len(raw_items)}): {', '.join(raw_items[:30])}")

    resolved: list[dict] = []
    for text in detected_texts:
        result = talent_db.lookup(text, min_score=min_score)
        if result:
            resolved.append(result)

    if mode == "watchlist":
        matched = watchlist.check_matches(detected_texts, min_score=min_score)
        print(f"  已匹配: {matched if matched else '无'}")
        _log({
            "event": "scan",
            "mode": "watchlist",
            "detected": detected_texts,
            "matched": matched,
        })
        if matched:
            tts.speak("匹配到：" + "、".join(matched), rate=voice_rate)
        else:
            tts.speak("未命中监视清单", rate=voice_rate)
    else:
        print(f"  天赋匹配: {len(resolved)} 个")
        for r in resolved:
            tag = "=" if r.get("exact") else f"~{r.get('score',0)}%"
            print(f"    [{tag}] {r['name']}: {r['effect'][:60]}")
        _log({
            "event": "scan",
            "mode": "full",
            "detected": detected_texts,
            "resolved": [r["name"] for r in resolved],
        })
        if not resolved:
            tts.speak("未匹配到任何天赋", rate=voice_rate)
            return
        lines = []
        for r in resolved:
            lines.append(f"{r['name']}：{r['effect']}")
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
    print("  NPC 天赋 OCR 辅助工具 已启动")
    print(f"  {hotkeys['scan_watchlist']} : 监视扫描（仅命中播报）")
    print(f"  {hotkeys['scan_full']}     : 全量查询（播报所有效果）")
    print(f"  {hotkeys['reload']}  : 重新加载配置 & 监视清单")
    print(f"  {hotkeys['exit']}   : 退出")
    print(f"  ROI: {cfg['roi']}")
    print("=" * 50)

    if cfg.get("output", {}).get("voice_enabled", True):
        tts.speak("天赋助手已启动", rate=cfg.get("output", {}).get("voice_rate", 200))

    while _running:
        tts.pump()
        time.sleep(0.1)

    print("正在退出...")
    keyboard.unhook_all_hotkeys()


if __name__ == "__main__":
    main()
