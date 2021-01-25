def safedivide(
    numerator: float, denominator: float, valueonfailure: float = float("nan")
) -> float:
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return valueonfailure
