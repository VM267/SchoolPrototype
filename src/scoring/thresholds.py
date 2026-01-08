# src/scoring/thresholds.py

DEFAULT_THRESHOLD = 75  # out of 100

def needs_check_in(score_0_to_100: float, threshold: float = DEFAULT_THRESHOLD) -> bool:
    return float(score_0_to_100) >= float(threshold)
