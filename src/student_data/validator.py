import pandas as pd

def validate_student_data(df: pd.DataFrame):
    """
    Validates synthetic student data for your AI prototype.
    Checks for:
    - Protected columns
    - Value ranges
    - Required columns
    """

    # Protected attributes that should never be included
    protected_columns = [
        'White', 'Low Income', 'Black', 'Hispanic', 'Asian', 
        'Am. Indian', 'Two or More', 'Pacific Islander', 
        'w/ IEPs', 'Male', 'Female', 'w/ Disabilities', 'Non Binary', 'MENA'
    ]

    for col in protected_columns:
        if col in df.columns:
            raise ValueError(f"Protected column found: {col}")

    # Required columns for your prototype
    required_columns = [
        'student_id', 'week_date', 'grades', 
        'tardies', 'absences', 'discipline_events', 'truancy_days'
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Value range checks
    if not df['grades'].between(0, 100).all():
        raise ValueError("Grades out of bounds (0-100)")

    numeric_columns = ['tardies', 'absences', 'discipline_events', 'truancy_days']
    for col in numeric_columns:
        if (df[col] < 0).any():
            raise ValueError(f"Negative values found in {col}")

    # Check student_id uniqueness
    if df['student_id'].duplicated().any():
        raise ValueError("Duplicate student_id found")

    return True


# Example usage
if __name__ == "__main__":
    # Load synthetic student CSV
    df = pd.read_csv("data/student_sample.csv")
    try:
        if validate_student_data(df):
            print("Student data passed all checks ✅")
    except ValueError as e:
        print(f"Validation Error: {e}")
