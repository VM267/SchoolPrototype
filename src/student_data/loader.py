import pandas as pd

def load_student_data(path="data/student_sample.csv"):
    df = pd.read_csv(path)
    return df