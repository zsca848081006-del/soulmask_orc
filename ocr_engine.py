import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR


_ocr: RapidOCR | None = None


def get_engine() -> RapidOCR:
    global _ocr
    if _ocr is None:
        _ocr = RapidOCR()
    return _ocr


def _to_bgr(image: np.ndarray) -> np.ndarray:
    if image.ndim == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image


def recognize_full(
    image: np.ndarray,
    min_confidence: float = 0.6,
) -> list[tuple[str, float, tuple[int, int]]]:
    """对整张图跑一次 OCR, 返回 [(text, conf, (cx, cy)), ...].

    cx/cy 为文本框中心坐标 (相对于传入 image), 用于按行聚类.
    """
    engine = get_engine()
    result, _ = engine(_to_bgr(image))
    if not result:
        return []
    items: list[tuple[str, float, tuple[int, int]]] = []
    for box_info in result:
        box = box_info[0]
        text = box_info[1]
        try:
            conf = float(box_info[2])
        except (TypeError, ValueError):
            conf = 0.0
        if conf < min_confidence:
            continue
        cx = int(sum(p[0] for p in box) / 4)
        cy = int(sum(p[1] for p in box) / 4)
        items.append((text, conf, (cx, cy)))
    return items
