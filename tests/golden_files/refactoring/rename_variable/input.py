"""Input file for rename_variable golden test.

This file contains poorly named variables that should be renamed.
"""


def calculate_metrics(d: list) -> dict:
    """Calculate user engagement metrics."""
    # Poorly named variables
    x = len(d)
    y = 0
    z = 0

    for i in d:
        if i.get("active"):
            y += 1
        if i.get("premium"):
            z += 1

    # More unclear names
    a = y / x if x > 0 else 0
    b = z / x if x > 0 else 0

    return {
        "total": x,
        "active_rate": a,
        "premium_rate": b,
    }


def process_data(lst: list) -> list:
    """Process data with unclear variable names."""
    r = []
    for e in lst:
        t = e.get("value", 0) * 2
        if t > 100:
            r.append({"id": e.get("id"), "result": t})
    return r
