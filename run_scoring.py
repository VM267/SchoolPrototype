import pandas as pd
from src.scoring.risk_score import score_dataframe

# Load synthetic student data
df = pd.read_csv("data/student_sample.csv")

# Run Step E scoring
scored_df = score_dataframe(df)

# Print only columns that ACTUALLY exist now
print(
    scored_df[
        ["student_id", "support_likelihood", "needs_supportive_check_in"]
    ]
)
