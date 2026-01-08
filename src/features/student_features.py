import pandas as pd
from src.features.recency import apply_recency_decay

def build_student_features(
    df: pd.DataFrame,
    decay_rate: float = 0.1
) -> dict:
    """
    Aggregates student time-series data into decayed features.
    Returns a dictionary of features.
    """

    features = {}

    features["grades_recent"] = apply_recency_decay(
        df, "week_date", "grades", decay_rate
    )

    features["absences_recent"] = apply_recency_decay(
        df, "week_date", "absences", decay_rate
    )

    features["tardies_recent"] = apply_recency_decay(
        df, "week_date", "tardies", decay_rate
    )

    features["discipline_recent"] = apply_recency_decay(
        df, "week_date", "discipline_events", decay_rate
    )

    features["truancy_recent"] = apply_recency_decay(
        df, "week_date", "truancy_days", decay_rate
    )

    return features
