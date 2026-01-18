import streamlit as st

st.set_page_config(page_title="Settings", layout="wide")
st.title("Settings")

# Initialize config in session_state
if "config" not in st.session_state:
    st.session_state["config"] = {
        "threshold": 75,
        "decay_rate": 0.85,
        "weights": {
            "grades": 0.25,
            "tardies": 0.15,
            "absences": 0.20,
            "discipline_events": 0.25,
            "truancy_days": 0.15,
        }
    }

cfg = st.session_state["config"]
w = cfg["weights"]

st.subheader("Support Signal Threshold")
cfg["threshold"] = st.slider("Review if Support Signal ≥", 0, 100, int(cfg["threshold"]))

st.subheader("Recency Decay")
cfg["decay_rate"] = st.slider(
    "Decay rate (higher = recent weeks matter more)",
    0.50, 0.99, float(cfg["decay_rate"]), step=0.01
)

st.subheader("Weights (Human-defined)")
st.write("**Note:** For clean interpretation, aim for weights that add up to **1.00**.")

w["grades"] = st.slider("Grades (low grades increase signal)", 0.0, 1.0, float(w["grades"]), step=0.01)
w["tardies"] = st.slider("Tardies", 0.0, 1.0, float(w["tardies"]), step=0.01)
w["absences"] = st.slider("Absences", 0.0, 1.0, float(w["absences"]), step=0.01)
w["discipline_events"] = st.slider("Discipline events", 0.0, 1.0, float(w["discipline_events"]), step=0.01)
w["truancy_days"] = st.slider("Truancy days", 0.0, 1.0, float(w["truancy_days"]), step=0.01)

weight_sum = sum(float(v) for v in w.values())
if abs(weight_sum - 1.0) < 0.01:
    st.success(f"Weights sum to **{weight_sum:.2f}** ✅")
else:
    st.warning(f"Weights currently sum to **{weight_sum:.2f}**. Try adjusting them to total **1.00** for clarity.")

st.divider()
st.write("Current config (this is what scoring will use):")
st.json(st.session_state["config"])
