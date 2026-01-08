import pandas as pd
import numpy as np

def apply_recency_decay(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    decay_rate: float = 0.1
) -> float:
    """
    Applies exponential recency decay to a time series.
    Returns a single weighted value.
    """

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    # Most recent date
    most_recent = df[date_col].max()

    # Days since most recent
    df["days_ago"] = (most_recent - df[date_col]).dt.days

    # Exponential decay weight
    df["weight"] = np.exp(-decay_rate * df["days_ago"])

    # Weighted average
    weighted_value = np.average(df[value_col], weights=df["weight"])

    return float(weighted_value)
