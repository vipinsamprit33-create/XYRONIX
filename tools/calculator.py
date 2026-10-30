
import math
from statistics import mean, median


def calculate_statistics(values):
    """
    Calculate statistics for numerical observations.
    """
    if not isinstance(values, (list, tuple)):
        raise ValueError("Values must be a list or tuple.")

    numbers = []

    for value in values:
        number = float(value)

        if not math.isfinite(number):
            raise ValueError("Values must be finite numbers.")

        numbers.append(number)

    if not numbers:
        raise ValueError("No values provided.")

    return {
        "count": len(numbers),
        "total": round(sum(numbers), 2),
        "average": round(mean(numbers), 2),
        "median": round(median(numbers), 2),
        "minimum": round(min(numbers), 2),
        "maximum": round(max(numbers), 2)
    }


def percentage_change(old_value, new_value):
    """
    Calculate percentage increase or decrease.
    """
    old_value = float(old_value)
    new_value = float(new_value)

    if not all(map(math.isfinite, [old_value, new_value])):
        raise ValueError("Values must be finite.")

    if old_value == 0:
        raise ValueError(
            "Cannot calculate percentage change from zero."
        )

    change = (
        (new_value - old_value) / abs(old_value)
    ) * 100

    return {
        "old_value": old_value,
        "new_value": new_value,
        "percentage_change": round(change, 2)
    }


if __name__ == "__main__":
    sample = [10, 20, 30, 40, 50]

    print(calculate_statistics(sample))
    print(percentage_change(100, 80))
