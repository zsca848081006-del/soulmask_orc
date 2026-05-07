import numpy as np


def find_icon_rows(
    image: np.ndarray,
    icon_x: int,
    icon_width: int,
    bg_thr: int = 30,
    min_cols: int = 15,
    min_height: int = 22,
    pad_below: int = 14,
) -> list[tuple[int, int]]:
    """扫描 icon 列, 返回每行 talent 的 icon 区 y 范围 [(y_start, y_end), ...].

    y_end 已经向下扩展 pad_below 像素, 把 icon 底部的等级标记包进来.
    """
    icon_strip = image[:, icon_x : icon_x + icon_width, :3]
    gray = icon_strip.mean(axis=2)
    non_bg = gray > bg_thr
    row_score = non_bg.sum(axis=1)

    bands: list[tuple[int, int]] = []
    in_run = False
    s = 0
    for y in range(len(row_score)):
        if row_score[y] > min_cols:
            if not in_run:
                s = y
                in_run = True
        elif in_run:
            if (y - s) >= min_height:
                bands.append((s, min(y + pad_below, len(row_score))))
            in_run = False
    if in_run and (len(row_score) - s) >= min_height:
        bands.append((s, len(row_score)))
    return bands


def crop_icon_area(
    image: np.ndarray,
    y_start: int,
    y_end: int,
    icon_x: int,
    icon_width: int,
) -> np.ndarray:
    return image[y_start:y_end, icon_x : icon_x + icon_width, :]
