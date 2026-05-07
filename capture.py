import numpy as np
import mss


def capture_roi(x: int, y: int, w: int, h: int) -> np.ndarray:
    monitor = {"left": x, "top": y, "width": w, "height": h}
    with mss.mss() as sct:
        img = sct.grab(monitor)
        return np.array(img)
