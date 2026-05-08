import queue
import threading

import pyttsx3


_queue: queue.Queue = queue.Queue()
_thread: threading.Thread | None = None
_stop = threading.Event()


def _build_engine() -> pyttsx3.Engine:
    eng = pyttsx3.init()
    try:
        eng.setProperty("volume", 1.0)
    except Exception:
        pass
    return eng


def _worker() -> None:
    try:
        engine = _build_engine()
    except Exception as e:
        print(f"[tts] engine init failed: {e}")
        return

    while not _stop.is_set():
        try:
            text, rate = _queue.get(timeout=0.2)
        except queue.Empty:
            continue
        try:
            engine.setProperty("rate", rate)
            engine.say(text)
            engine.runAndWait()
            # SAPI 驱动 runAndWait 返回后 _inLoop 残留为 True,
            # 下一次 say/runAndWait 会被默默丢弃, 是 pyttsx3 的老 bug.
            if hasattr(engine, "_inLoop"):
                engine._inLoop = False
        except RuntimeError as e:
            # 极少见: 引擎进入坏状态. 重建一个继续干.
            print(f"[tts] runtime error, rebuilding engine: {e}")
            try:
                engine.stop()
            except Exception:
                pass
            try:
                engine = _build_engine()
            except Exception as e2:
                print(f"[tts] engine rebuild failed: {e2}")
                return
        except Exception as e:
            print(f"[tts] speak error: {e}")


def init() -> None:
    global _thread
    if _thread is not None and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_worker, name="tts-worker", daemon=True)
    _thread.start()


def speak(text: str, rate: int = 200) -> None:
    _queue.put((text, rate))


def pump() -> None:
    # 保留空实现, 兼容旧调用点; 实际播报由 worker 线程处理.
    pass


def shutdown() -> None:
    _stop.set()
