"""Threshold and consecutive-window logic for drift monitoring."""
import math


def classify_consecutive_threshold(
    value: float,
    threshold: float,
    consecutive_windows: int,
    required_windows: int = 2,
) -> tuple[str, int]:
    """Classify a strict threshold breach as stable, watch, or alert."""
    if not math.isfinite(value) or not math.isfinite(threshold):
        raise ValueError("value and threshold must be finite")
    if consecutive_windows < 0:
        raise ValueError("consecutive_windows must be non-negative")
    if required_windows < 1:
        raise ValueError("required_windows must be positive")

    if value <= threshold:
        return "stable", 0

    count = consecutive_windows + 1
    if count >= required_windows:
        return "alert", count
    return "watch", count


def classify_income_psi(value: float, consecutive_high_windows: int) -> tuple[str, int]:
    """Watch PSI from 0.1 through 0.2; alert above 0.2 twice consecutively."""
    if not math.isfinite(value) or value < 0:
        raise ValueError("PSI must be finite and non-negative")
    if consecutive_high_windows < 0:
        raise ValueError("consecutive_high_windows must be non-negative")

    if value > 0.2:
        return classify_consecutive_threshold(value, 0.2, consecutive_high_windows)
    if value >= 0.1:
        return "watch", 0
    return "stable", 0
