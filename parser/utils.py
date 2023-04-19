

GREAT_WEIGHT = 0.4
GOOD_WEIGHT = 0.3
MEDIUM_WEIGHT = -0.1
BAD_WEIGHT = -0.2


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)


def avg_rating(bad: int, medium: int, good: int, great: int) -> float:
    result = (bad * BAD_WEIGHT) + (medium * MEDIUM_WEIGHT) + (good * GOOD_WEIGHT) + (great * GREAT_WEIGHT)
    return clamp(result, 1.0, 5.0)
