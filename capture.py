import numpy as np
import mss

_sct = None


def _get_sct():
    global _sct
    if _sct is None:
        _sct = mss.mss()
    return _sct


def capture_roi(x: int, y: int, w: int, h: int) -> np.ndarray:
    monitor = {"left": x, "top": y, "width": w, "height": h}
    img = _get_sct().grab(monitor)
    return np.array(img)
