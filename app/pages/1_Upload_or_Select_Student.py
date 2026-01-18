import streamlit as st
import pandas as pd

from src.student_data.validators import remove_blocked_columns

st.set_page_config(page_title="Upload Student Data", layout="wide")
st.title("Upload or Select Student (Prototype Data Only)")
st.caption("This tool only accepts synthetic student data. Protected attributes and PII are blocked.")

# Always-visible ethics panel
with st.container(border=True):
    st.subheader("Ethical Guardrails (Enforced)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("✅ Race / Ethnicity: **Blocked**")
        st.write("✅ Gender / Sex: **Blocked**")
        st.write("✅ Income / Poverty: **Blocked**")
    with col2:
        st.write("✅ Disability / IEP/504: **Blocked**")
        st.write("✅ PII (name/address/email/phone): **Blocked**")
        st.write("✅ Human review only: **Required**")

st.divider()

# --- Context school selection ---
st.subheader("Context School (Benchmarks)")

try:
    schools = pd.read_csv("data/schools_context.csv")
    if {"school_id", "school_name"}.issubset(set(schools.columns)):
        options = schools["school_name"].tolist()
        default_name = st.session_state.get("selected_school_name", options[0])
        selected_name = st.selectbox(
            "Choose a context school",
            options,
            index=options.index(default_name) if default_name in options else 0
        )
        selected_row = schools[schools["school_name"] == selected_name].iloc[0].to_dict()

        st.session_state["selected_school_name"] = selected_name
        st.session_state["school_context_row"] = selected_row
        st.caption(f"Current context school: **{selected_name}**")
    else:
        st.warning("schools_context.csv must include school_id and school_name for context selection.")
except FileNotFoundError:
    st.warning("Optional: add data/schools_context.csv to enable context school selection.")

st.divider()

uploaded = st.file_uploader("Upload synthetic student CSV", type=["csv"])
use_sample = st.checkbox("Use included sample file (data/student_sample.csv)")

df_raw = None
if uploaded is not None:
    df_raw = pd.read_csv(uploaded)
elif use_sample:
    try:
        df_raw = pd.read_csv("data/student_sample.csv")
    except FileNotFoundError:
        st.error("Sample file not found: data/student_sample.csv")
        st.stop()

if df_raw is None:
    st.info("Upload a CSV (or check the sample box) to begin.")
    st.stop()

# Guardrails
df_clean, guardrails = remove_blocked_columns(df_raw)

if guardrails.blocked_columns or guardrails.pii_columns:
    st.error("Protected or sensitive fields were detected and removed. This data will NOT be used.")
    blocked_all = guardrails.blocked_columns + guardrails.pii_columns
    st.write("**Blocked Fields Detected:**")
    st.code(", ".join(blocked_all))
else:
    st.success("No protected attributes or PII detected ✅")

if guardrails.missing_required:
    st.warning("Missing required columns (fix your CSV):")
    st.code(", ".join(guardrails.missing_required))
    st.stop()

st.session_state["student_df"] = df_clean
st.session_state["guardrails"] = guardrails

st.subheader("Preview (cleaned data used by the system)")
st.dataframe(df_clean.head(25), use_container_width=True)

st.success("Loaded successfully. Go to the **Student Report** page next.")
