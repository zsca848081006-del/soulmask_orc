import queue

import pyttsx3

_engine: pyttsx3.Engine | None = None
_queue: queue.Queue = queue.Queue()


def init() -> None:
    global _engine
    _engine = pyttsx3.init()


def speak(text: str, rate: int = 200) -> None:
    _queue.put((text, rate))


def pump() -> None:
    while not _queue.empty():
        text, rate = _queue.get_nowait()
        _engine.setProperty("rate", rate)
        _engine.say(text)
        _engine.runAndWait()
