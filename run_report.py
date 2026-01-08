import pandas as pd
from src.scoring.risk_score import score_dataframe
from src.explainability.explanations import generate_explanation_report

students = pd.read_csv("data/student_sample.csv")
schools = pd.read_csv("data/benchmarks_processed.csv")

# Demo selection
student_id = 4
school_id = 1006

# IMPORTANT: copy() prevents SettingWithCopyWarning
student_ts = students[students["student_id"] == student_id].copy()

# Step E scoring
scored = score_dataframe(student_ts)
score = float(scored.iloc[-1]["support_likelihood"])
needs = bool(scored.iloc[-1]["needs_supportive_check_in"])

# Step F explainability report
report = generate_explanation_report(
    student_timeseries=student_ts,
    school_benchmarks=schools,
    school_id=school_id,
    support_likelihood_score=score,
    needs_supportive_check_in=needs,
    top_k=5
)

print(report)
