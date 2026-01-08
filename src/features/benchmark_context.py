import pandas as pd

def normalize_against_benchmark(student_features: dict, benchmark_row: pd.Series):
    """
    Compares student metrics against school-level benchmarks.
    Outputs normalized context signals (ratios).
    """

    normalized = {}

    for key, value in student_features.items():
        if key in benchmark_row and benchmark_row[key] > 0:
            normalized[key] = round(value / benchmark_row[key], 2)
        else:
            normalized[key] = None

    return normalized