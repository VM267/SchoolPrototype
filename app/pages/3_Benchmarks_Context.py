import streamlit as st
from app.utils import ensure_session_defaults, load_school_benchmarks

st.set_page_config(page_title="Benchmarks Context", layout="wide")
ensure_session_defaults()

st.title("3) School Benchmarks Context (Synthetic)")

schools_df = load_school_benchmarks()

school_id = int(st.session_state.selected_school_id)

match = schools_df[schools_df["school_id"] == school_id]
if match.empty:
    st.error(f"school_id {school_id} not found in benchmarks.")
    st.dataframe(schools_df)
    st.stop()

school = match.iloc[0]

st.subheader(f"Selected school: {school['school_name']} (ID {school_id})")
st.dataframe(match)

st.caption("These are school-level contextual benchmarks. They are not used as student-level prediction targets.")