import numpy as np


def slice_rows(
    image: np.ndarray,
    row_height: int,
    max_rows: int = 20,
) -> list[np.ndarray]:
    h = image.shape[0]
    rows = []
    for i in range(max_rows):
        y0 = i * row_height
        y1 = y0 + row_height
        if y1 > h:
            break
        rows.append(image[y0:y1, :, :])
    return rows


def split_row(
    row: np.ndarray,
    icon_x: int,
    icon_width: int,
    text_x: int,
    level_y_offset: int,
    level_window: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    icon_area = row[:, icon_x : icon_x + icon_width, :]
    text_area = row[:, text_x:, :]
    level_y0 = level_y_offset
    level_y1 = level_y_offset + level_window
    level_area = icon_area[level_y0:level_y1, :, :]
    return icon_area, text_area, level_area
