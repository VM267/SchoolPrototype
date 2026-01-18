import streamlit as st
import pandas as pd

st.set_page_config(page_title="Benchmarks Context", layout="wide")
st.title("Benchmarks & Context School")

st.caption("School benchmarks are used only as contextual reference points (school-level only).")

# Load benchmarks
try:
    schools = pd.read_csv("data/schools_context.csv")
except FileNotFoundError:
    st.error("Missing file: data/schools_context.csv")
    st.stop()

required = {"school_id", "school_name"}
if not required.issubset(set(schools.columns)):
    st.error("schools_context.csv must include columns: school_id, school_name")
    st.write("Found columns:", list(schools.columns))
    st.stop()

st.subheader("Select context school")

options = schools["school_name"].tolist()
default_name = st.session_state.get("selected_school_name", options[0])

selected_name = st.selectbox(
    "Context school (benchmark reference)",
    options,
    index=options.index(default_name) if default_name in options else 0
)

selected_row = schools[schools["school_name"] == selected_name].iloc[0].to_dict()

st.session_state["selected_school_name"] = selected_name
st.session_state["school_context_row"] = selected_row

st.success(f"Context school set to: {selected_name}")

st.subheader("Context data preview (school-level only)")
st.json(selected_row)

st.divider()
st.subheader("All benchmark schools (synthetic)")
st.dataframe(schools, use_container_width=True)
