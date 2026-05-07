import numpy as np


def count_lines(level_area: np.ndarray, white_threshold: int = 220) -> int:
    gray = np.mean(level_area[:, :, :3], axis=2)
    white_mask = gray > white_threshold
    projection = np.sum(white_mask, axis=0)
    window_height = level_area.shape[0]
    threshold = max(window_height * 0.3, 2.0)
    smoothed = np.convolve(projection, np.ones(3) / 3, mode="same")

    peaks = 0
    rising = False
    for i in range(1, len(smoothed)):
        if not rising and smoothed[i] > threshold:
            rising = True
            peaks += 1
        elif rising and smoothed[i] < threshold * 0.5:
            rising = False

    return peaks
