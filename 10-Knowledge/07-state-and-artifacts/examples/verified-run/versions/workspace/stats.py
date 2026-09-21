def mean(values):
    if not values:
        raise ValueError('empty input')
    return sum(values) / len(values)
