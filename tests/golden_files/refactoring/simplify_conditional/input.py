"""Input file for simplify_conditional golden test.

This file contains overly complex conditionals that can be simplified.
"""


def check_eligibility(user: dict) -> bool:
    """Check if user is eligible - complex nested conditionals."""
    if user.get("age"):
        if user["age"] >= 18:
            if user.get("verified"):
                if user["verified"] is True:
                    if user.get("status"):
                        if user["status"] == "active":
                            return True
                        return False
                    return False
                return False
            return False
        return False
    return False


def get_discount(order: dict) -> float:
    """Calculate discount - redundant conditions."""
    discount = 0.0

    if order.get("is_member") == True:  # noqa: E712
        if order.get("total", 0) > 100:
            discount = 0.1
        elif order.get("total", 0) > 50:
            discount = 0.05
        elif order.get("total", 0) > 0:
            discount = 0.02
        else:
            discount = 0.0
    elif order.get("is_member") == False:  # noqa: E712
        discount = 0.0

    return discount


def is_valid_input(value: str) -> bool:
    """Validate input - can be simplified."""
    if value is not None:
        if value != "":
            if len(value) > 0:
                if value.strip() != "":
                    return True
                return False
            return False
        return False
    return False
