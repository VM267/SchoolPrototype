import streamlit as st
from app.utils import ensure_session_defaults
from src.scoring.weights import validate_weights

st.set_page_config(page_title="Settings", layout="wide")
ensure_session_defaults()

st.title("4) Settings")

st.subheader("Threshold (tunable)")
st.session_state.threshold = st.slider(
    "Supportive check-in threshold (0–100)",
    min_value=0.0,
    max_value=100.0,
    value=float(st.session_state.threshold),
    step=1.0
)

st.subheader("Weights (human-defined, tunable)")
w = st.session_state.weights.copy()

w["grades"] = st.slider("grades weight", 0.05, 0.50, float(w["grades"]), 0.01)
w["absences"] = st.slider("absences weight", 0.05, 0.50, float(w["absences"]), 0.01)
w["tardies"] = st.slider("tardies weight", 0.05, 0.50, float(w["tardies"]), 0.01)
w["discipline_events"] = st.slider("discipline_events weight", 0.05, 0.50, float(w["discipline_events"]), 0.01)
w["truancy_days"] = st.slider("truancy_days weight", 0.05, 0.50, float(w["truancy_days"]), 0.01)

# Normalize to sum=1 automatically
total = sum(w.values())
w = {k: v / total for k, v in w.items()}

try:
    validate_weights(w)
    st.success("Weights are valid (sum to 1.0 and bounded). Saved to session.")
    st.session_state.weights = w
except Exception as e:
    st.error(f"Weights invalid: {e}")

st.subheader("Recency decay")
st.session_state.decay_rate = st.slider(
    "Decay rate (placeholder until fully wired into features)",
    0.50, 0.99, float(st.session_state.decay_rate), 0.01
)

st.caption("In this prototype, weights and thresholds are transparent and tunable by staff, not automatically learned.")