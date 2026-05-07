import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR


_ocr: RapidOCR | None = None


def get_engine() -> RapidOCR:
    global _ocr
    if _ocr is None:
        _ocr = RapidOCR()
    return _ocr


def preprocess(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    upscaled = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return upscaled


def recognize(image: np.ndarray, min_confidence: float = 0.6) -> list[tuple[str, float]]:
    engine = get_engine()
    processed = preprocess(image)
    result, _ = engine(processed)
    if result is None:
        return []
    items: list[tuple[str, float]] = []
    for box_info in result:
        text = box_info[1]
        conf = box_info[2]
        if conf >= min_confidence:
            items.append((text, conf))
    return items
