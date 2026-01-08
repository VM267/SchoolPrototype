import json
import streamlit as st
import pandas as pd

from app.utils import (
    ensure_session_defaults,
    load_school_benchmarks,
    get_student_timeseries
)
from src.scoring.risk_score import score_dataframe
from src.explainability.explanations import generate_explanation_report

st.set_page_config(page_title="Student Report", layout="wide")
ensure_session_defaults()

st.title("2) Student Support Report")

if "students_df" not in st.session_state or st.session_state.selected_student_id is None:
    st.warning("Go to page 1 and select a student first.")
    st.stop()

students_df = st.session_state.students_df
schools_df = load_school_benchmarks()

student_id = int(st.session_state.selected_student_id)
school_id = int(st.session_state.selected_school_id)

student_ts = get_student_timeseries(students_df, student_id)

# Step E
scored = score_dataframe(
    student_ts,
    weights=st.session_state.weights,
    threshold=st.session_state.threshold
)

score = float(scored.iloc[-1]["support_likelihood"])
needs = bool(scored.iloc[-1]["needs_supportive_check_in"])

# Step F
report = generate_explanation_report(
    student_timeseries=student_ts,
    school_benchmarks=schools_df,
    school_id=school_id,
    support_likelihood_score=score,
    needs_supportive_check_in=needs,
    top_k=5
)

left, right = st.columns([1, 1])

with left:
    st.subheader("Summary")
    st.metric("Support-likelihood score (0–100)", f"{report['score']:.2f}")
    st.metric("Supportive check-in recommended", "YES" if report["supportive_check_in_recommended"] else "NO")
    st.caption("This output is a *risk signal* for support prioritization, not a prediction or diagnosis.")

with right:
    st.subheader("Disclaimer")
    st.warning(report["disclaimer"])

st.divider()

st.subheader("Top contributing indicators (contextual)")
for item in report["top_contributing_indicators"]:
    st.write(f"**{item['indicator']}** — {item['message']}")

st.subheader("What changed recently")
for line in report["what_changed_recently"]:
    st.write(f"- {line}")

st.divider()

st.subheader("Transparency panel")
st.write("**Data used (student synthetic):** grades, absences, tardies, discipline_events, truancy_days, week_date")
st.write("**Data excluded:** protected attributes (race, gender, income, disability, etc.), PII, offset categories")
st.write("**Benchmark context used (school-level only):**")
st.json(report["benchmark_context_used"])

st.divider()

st.subheader("Export")
report_json = json.dumps(report, indent=2)
st.download_button(
    "Download report as JSON",
    data=report_json,
    file_name=f"student_{student_id}_report.json",
    mime="application/json"
)

st.markdown("✅ Next: go to **3) Benchmarks Context** to view the school baseline.")