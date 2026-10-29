"""Processing module: compares readings to thresholds.
Limits are indicative, based on BIS IS 10500 / WHO. Verify before submitting.
"""

SAFE, CAUTION, UNSAFE = "Safe", "Caution", "Unsafe"
RANK = {SAFE: 0, CAUTION: 1, UNSAFE: 2}

# (safe_max, caution_max): above caution_max is Unsafe
LIMITS = {
    "tds": (500, 2000),
    "turbidity": (1, 5),
}
PH_SAFE = (6.5, 8.5)
PH_CAUTION = (6.0, 9.0)  # outside safe but inside this = Caution


def _classify_upper(value, safe_max, caution_max):
    if value <= safe_max:
        return SAFE
    if value <= caution_max:
        return CAUTION
    return UNSAFE


def _classify_ph(ph):
    if PH_SAFE[0] <= ph <= PH_SAFE[1]:
        return SAFE
    if PH_CAUTION[0] <= ph <= PH_CAUTION[1]:
        return CAUTION
    return UNSAFE


def classify(reading):
    """Returns per-parameter status and overall status (worst parameter)."""
    statuses = {
        "tds": _classify_upper(reading["tds"], *LIMITS["tds"]),
        "turbidity": _classify_upper(reading["turbidity"], *LIMITS["turbidity"]),
        "ph": _classify_ph(reading["ph"]),
    }
    overall = max(statuses.values(), key=lambda s: RANK[s])
    return statuses, overall
