import streamlit as st
from app.utils import ensure_session_defaults

st.set_page_config(page_title="Student Support Early-Warning Prototype", layout="wide")
ensure_session_defaults()

st.title("Student Support Early-Warning & Check-In System (Prototype)")

st.markdown("""
### What this is
A **staff-in-the-loop decision-support tool** that summarizes student signals (synthetic data only) and produces a **support-likelihood score** to help staff prioritize **supportive check-ins**.

### What this is not
- Not a diagnostic tool
- Not an automated decision-maker
- Not a predictor of student outcomes
- Not using protected attributes (race, gender, income, disability, etc.)

### Ethical guardrails
- **Synthetic student data only**
- **No protected subgroup inputs**
- **School benchmarks are contextual reference only**
""")

st.info("Use the sidebar pages to upload/select a student, view the report, inspect benchmark context, and adjust settings.")