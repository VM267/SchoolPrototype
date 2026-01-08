DEFAULT_WEIGHTS = {
    "grades": 0.30,
    "absences": 0.25,
    "tardies": 0.15,
    "discipline_events": 0.20,
    "truancy_days": 0.10
}

WEIGHT_BOUNDS = {
    "min": 0.05,
    "max": 0.50
}

def validate_weights(weights: dict):
    total = sum(weights.values())
    if round(total, 2) != 1.00:
        raise ValueError("Weights must sum to 1.0")

    for k, v in weights.items():
        if not (WEIGHT_BOUNDS["min"] <= v <= WEIGHT_BOUNDS["max"]):
            raise ValueError(f"Weight {k} out of bounds")

    return True
