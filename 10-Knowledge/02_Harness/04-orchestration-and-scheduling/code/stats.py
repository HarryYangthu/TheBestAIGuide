"""The corrected mean function from the Agent Loop task."""
def mean(values):
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)
