from __future__ import annotations

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

DEFAULT_CONFIG: Dict[str, Any] = {
    "threshold": 75,
    "decay_rate": 0.85,
    "weights": {
        "grades": 0.25,
        "tardies": 0.15,
        "absences": 0.20,
        "discipline_events": 0.25,
        "truancy_days": 0.15,
    },
    "school_context": None
}

REQUIRED_COLS = [
    "student_id", "week_date", "grades",
    "tardies", "absences", "discipline_events", "truancy_days"
]


def _merge_config(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    cfg = {**DEFAULT_CONFIG}
    cfg["weights"] = {**DEFAULT_CONFIG["weights"]}

    if config:
        cfg["threshold"] = int(config.get("threshold", cfg["threshold"]))
        cfg["decay_rate"] = float(config.get("decay_rate", cfg["decay_rate"]))
        if isinstance(config.get("weights"), dict):
            for k, v in config["weights"].items():
                cfg["weights"][k] = float(v)
        cfg["school_context"] = config.get("school_context", None)

    return cfg


def _require_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _normalize_negative(x: float, good_low: float, bad_high: float) -> float:
    if pd.isna(x):
        return 0.0
    if bad_high <= good_low:
        return 0.0
    return float(np.clip((float(x) - good_low) / (bad_high - good_low), 0.0, 1.0))


def _normalize_grades(g: float) -> float:
    if pd.isna(g):
        return 0.0
    g = float(np.clip(float(g), 0.0, 100.0))
    return float(np.clip((100.0 - g) / 100.0, 0.0, 1.0))


def _recency_weights(n: int, decay_rate: float) -> np.ndarray:
    if n <= 0:
        return np.array([], dtype=float)
    distances = np.arange(n - 1, -1, -1)
    w = (decay_rate ** distances).astype(float)
    w = w / w.sum() if w.sum() > 0 else np.ones(n) / n
    return w


def _anchors_from_school_context(ctx: Optional[Dict[str, Any]]) -> Dict[str, float]:
    # Defaults
    anchors = {
        "tardies_bad": 5.0,
        "absences_bad": 5.0,
        "truancy_bad": 3.0,
        "discipline_bad": 3.0,
    }
    if not isinstance(ctx, dict):
        return anchors

    abs_pct = float(ctx.get("chronic_absenteeism_pct", 0) or 0)
    tru_pct = float(ctx.get("truancy_rate_pct", 0) or 0)
    disc_per100 = float(ctx.get("discipline_incidents_per_100", 0) or 0)

    anchors["absences_bad"] = float(np.clip(2.5 + (abs_pct / 15.0), 2.0, 10.0))
    anchors["truancy_bad"] = float(np.clip(2.0 + (tru_pct / 15.0), 2.0, 10.0))
    anchors["discipline_bad"] = float(np.clip(2.0 + (disc_per100 / 20.0), 2.0, 10.0))
    return anchors


def _context_multiplier(ctx: Optional[Dict[str, Any]]) -> float:
    """
    Context calibration:
    - Safer/stronger school -> multiplier slightly LOWER (student stands out more)
    - Higher-need school -> multiplier slightly HIGHER (student stands out less)
    This affects the final score so different schools produce different signals.
    """
    if not isinstance(ctx, dict):
        return 1.0

    abs_pct = float(ctx.get("chronic_absenteeism_pct", 0) or 0)
    tru_pct = float(ctx.get("truancy_rate_pct", 0) or 0)
    disc = float(ctx.get("discipline_incidents_per_100", 0) or 0)
    grad = float(ctx.get("graduation_rate_pct", 0) or 0)

    # Normalize school climate into 0..1-ish
    # (Transparent prototype assumptions; not claiming causation.)
    climate = 0.0
    climate += np.clip(abs_pct / 50.0, 0.0, 1.0) * 0.35
    climate += np.clip(tru_pct / 50.0, 0.0, 1.0) * 0.35
    climate += np.clip(disc / 80.0, 0.0, 1.0) * 0.20
    climate += np.clip((100.0 - grad) / 50.0, 0.0, 1.0) * 0.10

    # Map climate to multiplier ~ [0.85 .. 1.15]
    return float(np.clip(0.85 + (climate * 0.30), 0.85, 1.15))


def score_dataframe(student_df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    cfg = _merge_config(config)
    _require_columns(student_df)

    df = student_df.copy()
    df["week_date"] = pd.to_datetime(df["week_date"], errors="coerce")
    df = df.sort_values("week_date")

    w_rec = _recency_weights(len(df), cfg["decay_rate"])
    ctx = cfg.get("school_context")
    anchors = _anchors_from_school_context(ctx)
    multiplier = _context_multiplier(ctx)

    # signals
    df["sig_grades"] = df["grades"].apply(_normalize_grades)
    df["sig_tardies"] = df["tardies"].apply(lambda x: _normalize_negative(x, 0, anchors["tardies_bad"]))
    df["sig_absences"] = df["absences"].apply(lambda x: _normalize_negative(x, 0, anchors["absences_bad"]))
    df["sig_discipline_events"] = df["discipline_events"].apply(lambda x: _normalize_negative(x, 0, anchors["discipline_bad"]))
    df["sig_truancy_days"] = df["truancy_days"].apply(lambda x: _normalize_negative(x, 0, anchors["truancy_bad"]))

    weights = cfg["weights"]
    w_grades = float(weights.get("grades", 0.0))
    w_tardies = float(weights.get("tardies", 0.0))
    w_absences = float(weights.get("absences", 0.0))
    w_disc = float(weights.get("discipline_events", 0.0))
    w_truancy = float(weights.get("truancy_days", 0.0))

    df["contrib_grades"] = df["sig_grades"] * w_grades
    df["contrib_tardies"] = df["sig_tardies"] * w_tardies
    df["contrib_absences"] = df["sig_absences"] * w_absences
    df["contrib_discipline_events"] = df["sig_discipline_events"] * w_disc
    df["contrib_truancy_days"] = df["sig_truancy_days"] * w_truancy

    df["row_signal"] = (
        df["contrib_grades"]
        + df["contrib_tardies"]
        + df["contrib_absences"]
        + df["contrib_discipline_events"]
        + df["contrib_truancy_days"]
    )

    overall_contribs = {
        "grades": float(np.dot(df["contrib_grades"].to_numpy(dtype=float), w_rec)),
        "tardies": float(np.dot(df["contrib_tardies"].to_numpy(dtype=float), w_rec)),
        "absences": float(np.dot(df["contrib_absences"].to_numpy(dtype=float), w_rec)),
        "discipline_events": float(np.dot(df["contrib_discipline_events"].to_numpy(dtype=float), w_rec)),
        "truancy_days": float(np.dot(df["contrib_truancy_days"].to_numpy(dtype=float), w_rec)),
    }

    total_weight = w_grades + w_tardies + w_absences + w_disc + w_truancy
    overall = float(sum(overall_contribs.values()))
    base_score = 0.0 if total_weight <= 0 else float(np.clip((overall / total_weight) * 100.0, 0.0, 100.0))

    # Apply context calibration so school changes affect score
    support_signal = float(np.clip(base_score * multiplier, 0.0, 100.0))

    df["support_signal"] = support_signal
    df["recommendation"] = "review" if support_signal >= cfg["threshold"] else "no_review"

    # Attach overall contributions
    df["contrib_overall_grades"] = overall_contribs["grades"]
    df["contrib_overall_tardies"] = overall_contribs["tardies"]
    df["contrib_overall_absences"] = overall_contribs["absences"]
    df["contrib_overall_discipline_events"] = overall_contribs["discipline_events"]
    df["contrib_overall_truancy_days"] = overall_contribs["truancy_days"]

    # Transparency columns for UI/debug
    df["context_school_name"] = str(ctx.get("school_name")) if isinstance(ctx, dict) and "school_name" in ctx else "None selected"
    df["context_multiplier"] = multiplier
    df["context_absences_bad_anchor"] = anchors["absences_bad"]
    df["context_truancy_bad_anchor"] = anchors["truancy_bad"]
    df["context_discipline_bad_anchor"] = anchors["discipline_bad"]

    return df
