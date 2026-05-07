import numpy as np


def count_marks(
    icon_area: np.ndarray,
    white_thr: int = 200,
    color_tol: int = 15,
    max_band_height: int = 12,
    min_gap: int = 1,
) -> int:
    """统计 icon 区域底部的等级标记数 (I/II/III).

    思路:
      1. 仅保留中性白 (R≈G≈B>white_thr), 过滤掉 icon 本体彩色像素.
      2. 按行求白像素是否存在, 找最靠下的一段连续白色行带.
      3. 行带高度 > max_band_height 的当作 icon 本体或文字, 跳过.
      4. 在选中的行带内沿列方向数被 >= min_gap 像素空隙隔开的列簇.
    """
    if icon_area.size == 0:
        return 0
    r = icon_area[..., 0].astype(np.int16)
    g = icon_area[..., 1].astype(np.int16)
    b = icon_area[..., 2].astype(np.int16)
    mask = (
        (r > white_thr) & (g > white_thr) & (b > white_thr)
        & (np.abs(r - g) < color_tol) & (np.abs(g - b) < color_tol)
    )
    if not mask.any():
        return 0

    row_has_white = mask.any(axis=1)
    bands: list[tuple[int, int]] = []
    in_run = False
    s = 0
    for y in range(len(row_has_white)):
        if row_has_white[y]:
            if not in_run:
                s = y
                in_run = True
        elif in_run:
            bands.append((s, y))
            in_run = False
    if in_run:
        bands.append((s, len(row_has_white)))

    chosen: tuple[int, int] | None = None
    for bs, be in reversed(bands):
        if (be - bs) <= max_band_height:
            chosen = (bs, be)
            break
    if chosen is None:
        return 0

    bs, be = chosen
    col_has_white = mask[bs:be, :].any(axis=0)

    count = 0
    gap_run = min_gap
    in_col = False
    for x in range(len(col_has_white)):
        if col_has_white[x]:
            if not in_col and gap_run >= min_gap:
                count += 1
                in_col = True
            gap_run = 0
        else:
            in_col = False
            gap_run += 1
    return count
