import pandas as pd

LOW_IS_BETTER = {
    "absences": "chronic_absenteeism_pct",
    "truancy_days": "chronic_truancy_pct",
    "discipline_events": "discipline_incidents_per_100",
}

HIGH_IS_BETTER_SCHOOL = {
    "grades": ["math_achievement_pct", "ela_achievement_pct", "science_achievement_pct"]
}

def _get_school_row(schools_df: pd.DataFrame, school_id: int) -> pd.Series:
    school = schools_df[schools_df["school_id"] == school_id]
    if school.empty:
        raise ValueError(f"school_id {school_id} not found in benchmarks_processed.csv")
    return school.iloc[0]

def _school_academic_avg(school_row: pd.Series) -> float:
    cols = HIGH_IS_BETTER_SCHOOL["grades"]
    return float(sum(school_row[c] for c in cols) / len(cols))

def _ratio(student_val: float, school_val: float) -> float:
    if school_val is None or school_val == 0:
        return 0.0
    return float(student_val / school_val)

def _recent_change_summary(student_timeseries: pd.DataFrame) -> list[str]:
    """
    Simple, interpretable 'what changed recently':
    compares latest week to average of prior weeks.
    """
    df = student_timeseries.copy()
    df["week_date"] = pd.to_datetime(df["week_date"])
    df = df.sort_values("week_date")

    if len(df) < 2:
        return ["Not enough history to compute recent change."]

    latest = df.iloc[-1]
    prior = df.iloc[:-1]

    changes = []

    def delta_msg(col: str, label: str, higher_is_worse: bool):
        prior_avg = prior[col].mean()
        latest_val = latest[col]
        diff = latest_val - prior_avg

        # only report meaningful changes
        if abs(diff) < 0.25:
            return

        direction = "increased" if diff > 0 else "decreased"
        if higher_is_worse:
            impact = "which may signal increased support need" if diff > 0 else "which may signal improvement"
        else:
            impact = "which may signal improvement" if diff > 0 else "which may signal increased support need"

        changes.append(f"{label} {direction} recently (latest {latest_val:.1f} vs prior avg {prior_avg:.1f}), {impact}.")

    # Higher is worse:
    delta_msg("absences", "Absences", True)
    delta_msg("tardies", "Tardies", True)
    delta_msg("discipline_events", "Discipline events", True)
    delta_msg("truancy_days", "Truancy days", True)

    # Higher is better:
    delta_msg("grades", "Grades", False)

    return changes[:3] if changes else ["No major recent changes detected."]

def top_contributing_indicators(
    student_latest_row: pd.Series,
    school_row: pd.Series,
    top_k: int = 5
) -> list[dict]:
    """
    Build interpretable indicators using ratios to school benchmarks.
    Returns a list of dicts, each describing an indicator.
    """
    indicators = []

    # Low-is-better metrics: ratio > 1 is "worse than school context"
    for student_col, school_col in LOW_IS_BETTER.items():
        student_val = float(student_latest_row[student_col])
        school_val = float(school_row[school_col])
        r = _ratio(student_val, school_val)

        indicators.append({
            "indicator": student_col,
            "direction": "higher_is_worse",
            "student_value": student_val,
            "school_benchmark": school_val,
            "relative_to_school": round(r, 2),
            "message": f"{student_col} is {round(r,2)}× the school benchmark ({student_val} vs {school_val})."
        })

    # Grades: compare to school academic average
    student_grade = float(student_latest_row["grades"])
    school_acad = _school_academic_avg(school_row)
    # For grades, lower than context is "worse"
    grade_ratio = student_grade / school_acad if school_acad else 0.0

    indicators.append({
        "indicator": "grades",
        "direction": "lower_is_worse",
        "student_value": student_grade,
        "school_benchmark": round(school_acad, 2),
        "relative_to_school": round(grade_ratio, 2),
        "message": f"grades are {round(grade_ratio,2)}× the school academic benchmark ({student_grade} vs {round(school_acad,2)})."
    })

    # Rank indicators by “concern”
    def concern_score(ind):
        if ind["direction"] == "higher_is_worse":
            return ind["relative_to_school"]  # bigger ratio = more concern
        else:
            # grades: lower ratio = more concern
            return 1.0 / ind["relative_to_school"] if ind["relative_to_school"] > 0 else 999

    indicators.sort(key=concern_score, reverse=True)
    return indicators[:top_k]

def generate_explanation_report(
    student_timeseries: pd.DataFrame,
    school_benchmarks: pd.DataFrame,
    school_id: int,
    support_likelihood_score: float,
    needs_supportive_check_in: bool,
    top_k: int = 5
) -> dict:
    """
    Full report for Step F:
    - Score
    - Recommendation
    - Top contributing indicators
    - Benchmark context used (school-level only)
    - What changed recently
    - Disclaimers
    """
    school_row = _get_school_row(school_benchmarks, school_id)

    # Use latest student row for current indicators
    df = student_timeseries.copy()
    df["week_date"] = pd.to_datetime(df["week_date"])
    latest_row = df.sort_values("week_date").iloc[-1]

    indicators = top_contributing_indicators(latest_row, school_row, top_k=top_k)
    recent_changes = _recent_change_summary(df)

    benchmark_context_used = {
        "school_id": int(school_row["school_id"]),
        "school_name": str(school_row["school_name"]),
        "benchmarks": {
            "chronic_absenteeism_pct": float(school_row["chronic_absenteeism_pct"]),
            "truancy_rate_pct": float(school_row["truancy_rate_pct"]),
            "chronic_truancy_pct": float(school_row["chronic_truancy_pct"]),
            "discipline_incidents_per_100": float(school_row["discipline_incidents_per_100"]),
            "academic_avg_pct": round(_school_academic_avg(school_row), 2),
            "graduation_rate_pct": float(school_row["graduation_rate_pct"]),
        }
    }

    return {
        "score": float(support_likelihood_score),
        "supportive_check_in_recommended": bool(needs_supportive_check_in),
        "top_contributing_indicators": indicators,
        "what_changed_recently": recent_changes,
        "benchmark_context_used": benchmark_context_used,
        "disclaimer": (
            "Staff-in-the-loop decision support only. "
            "This tool does not diagnose students, does not automate decisions, "
            "and does not predict outcomes. Use for supportive check-ins only."
        )
    }
