import pandas as pd
import streamlit as st

@st.cache_data
def load_school_benchmarks():
    return pd.read_csv("data/benchmarks_processed.csv")

@st.cache_data
def load_sample_students():
    return pd.read_csv("data/student_sample.csv")

def get_student_timeseries(df: pd.DataFrame, student_id: int) -> pd.DataFrame:
    out = df[df["student_id"] == student_id].copy()
    out["week_date"] = pd.to_datetime(out["week_date"])
    return out.sort_values("week_date")

def ensure_session_defaults():
    if "threshold" not in st.session_state:
        st.session_state.threshold = 75.0
    if "decay_rate" not in st.session_state:
        st.session_state.decay_rate = 0.9
    if "weights" not in st.session_state:
        st.session_state.weights = {
            "grades": 0.30,
            "absences": 0.25,
            "tardies": 0.15,
            "discipline_events": 0.20,
            "truancy_days": 0.10,
        }
    if "selected_student_id" not in st.session_state:
        st.session_state.selected_student_id = None
    if "selected_school_id" not in st.session_state:
        st.session_state.selected_school_id = 1006  # default demo school
