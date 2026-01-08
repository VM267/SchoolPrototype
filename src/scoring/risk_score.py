# src/scoring/risk_score.py

import pandas as pd
from src.scoring.weights import DEFAULT_WEIGHTS, validate_weights
from src.scoring.thresholds import needs_check_in, DEFAULT_THRESHOLD

def _normalize_row(row: pd.Series) -> dict:
    """
    Convert raw inputs into 0–1 concern signals (interpretable).
    """
    grades_signal = 1 - (row["grades"] / 100.0)  # lower grades -> higher concern
    absences_signal = min(row["absences"] / 20.0, 1.0)
    tardies_signal = min(row["tardies"] / 10.0, 1.0)
    discipline_signal = min(row["discipline_events"] / 5.0, 1.0)
    truancy_signal = min(row["truancy_days"] / 10.0, 1.0)

    return {
        "grades": grades_signal,
        "absences": absences_signal,
        "tardies": tardies_signal,
        "discipline_events": discipline_signal,
        "truancy_days": truancy_signal,
    }

def compute_support_likelihood(row: pd.Series, weights: dict = DEFAULT_WEIGHTS) -> float:
    """
    Deterministic weighted score.
    Output: 0–100 (higher = higher support-likelihood)
    """
    validate_weights(weights)
    signals = _normalize_row(row)
    score_0_to_1 = sum(signals[k] * weights[k] for k in weights.keys())
    return round(score_0_to_1 * 100.0, 2)

def score_dataframe(
    df: pd.DataFrame,
    weights: dict = DEFAULT_WEIGHTS,
    threshold: float = DEFAULT_THRESHOLD
) -> pd.DataFrame:
    """
    Adds:
      - support_likelihood (0–100)
      - needs_supportive_check_in (bool)
    """
    out = df.copy()  # avoids SettingWithCopyWarning

    out["support_likelihood"] = out.apply(
        lambda r: compute_support_likelihood(r, weights),
        axis=1
    )

    out["needs_supportive_check_in"] = out["support_likelihood"].apply(
        lambda s: needs_check_in(float(s), threshold)
    )

    return out
