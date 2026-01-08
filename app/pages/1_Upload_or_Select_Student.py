import streamlit as st
import pandas as pd
from app.utils import ensure_session_defaults, load_sample_students

st.set_page_config(page_title="Upload or Select Student", layout="wide")
ensure_session_defaults()

st.title("1) Upload or Select Student (Synthetic Data)")

st.markdown("Upload a synthetic CSV, or use the built-in sample dataset.")

uploaded = st.file_uploader("Upload student CSV", type=["csv"])

if uploaded is not None:
    df_students = pd.read_csv(uploaded)
    st.session_state.students_df = df_students
    st.success("Uploaded student CSV loaded into session.")
else:
    # Use sample
    df_students = load_sample_students()
    st.session_state.students_df = df_students
    st.info("Using sample student dataset: data/student_sample.csv")

st.subheader("Select a student_id")
student_ids = sorted(st.session_state.students_df["student_id"].unique().tolist())
selected = st.selectbox("student_id", student_ids, index=0)

st.session_state.selected_student_id = int(selected)

st.subheader("Select a school benchmark context")
st.session_state.selected_school_id = st.number_input(
    "school_id (from benchmarks_processed.csv)",
    value=int(st.session_state.selected_school_id),
    step=1
)

st.markdown("✅ Next: go to **2) Student Report**")