import streamlit as st
import pandas as pd
import traceback

from src.scoring.risk_score import score_dataframe

st.set_page_config(page_title="Student Report", layout="wide")
st.title("Student Report")

if "student_df" not in st.session_state:
    st.warning("No student data loaded yet. Go to the Upload page first.")
    st.stop()

df: pd.DataFrame = st.session_state["student_df"]

config = st.session_state.get("config", {"threshold": 75})
threshold = int(config.get("threshold", 75))

# >>> FORCE school context into config <<<
config = dict(config)  # avoid mutating shared object unexpectedly
config["school_context"] = st.session_state.get("school_context_row", None)

# Safety panel
with st.container(border=True):
    st.subheader("Safety & Ethics Proof")
    st.write("**Non-goal:** This system does NOT predict outcomes, rank students, or automate decisions.")
    st.write("This report is a **Support Signal**, meant for **human review only**.")

st.divider()

# Show context school clearly
ctx = config.get("school_context")
ctx_name = ctx.get("school_name") if isinstance(ctx, dict) else None
st.info(f"**Context School:** {ctx_name if ctx_name else 'None selected'}")

student_ids = sorted(df["student_id"].unique().tolist())
selected_student = st.selectbox("Select student_id", student_ids)

student_df = df[df["student_id"] == selected_student].copy()

st.subheader("Student timeline (synthetic data)")
st.dataframe(student_df, use_container_width=True)

# Scoring
try:
    scored = score_dataframe(student_df, config=config)
except Exception as e:
    st.error("Scoring failed:")
    st.code("".join(traceback.format_exception(type(e), e, e.__traceback__)))
    st.stop()

latest = scored.sort_values("week_date").iloc[-1]
score_val = float(latest["support_signal"])

st.subheader("Support Signal")
if score_val >= threshold:
    st.error(f"🔴 Support Signal: **{score_val:.1f} / 100** — Review suggested")
else:
    st.success(f"🟢 Support Signal: **{score_val:.1f} / 100** — No review suggested")

st.write(f"**Threshold:** {threshold}")

# DEBUG/Transparency (shows context is being applied)
with st.expander("Show benchmark context used (for transparency)"):
    show_cols = [c for c in latest.index if c.startswith("context_")] + ["context_school_name"]
    st.write({c: latest[c] for c in show_cols if c in latest.index})
    st.write("Raw school context row (school-level only):")
    st.json(ctx if isinstance(ctx, dict) else {})

st.divider()

st.markdown("### Top contributing indicators (overall)")
overall_cols = [c for c in scored.columns if c.startswith("contrib_overall_")]
overall = latest[overall_cols].sort_values(ascending=False).head(5)

for col, val in overall.items():
    name = col.replace("contrib_overall_", "").replace("_", " ")
    st.write(f"- **{name}** contributed **{float(val):.4f}**")

st.caption("Reminder: This is a support signal for human review only. No automated action is taken.")
