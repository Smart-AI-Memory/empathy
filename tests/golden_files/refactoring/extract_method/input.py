"""Input file for extract_method golden test.

This file contains a function with complex logic that should be extracted.
"""


def process_order(order: dict) -> dict:
    """Process an order with validation and calculation."""
    # Validate order fields - this block should be extracted
    if not order.get("customer_id"):
        raise ValueError("Missing customer_id")
    if not order.get("items"):
        raise ValueError("Missing items")
    if not isinstance(order.get("items"), list):
        raise ValueError("Items must be a list")
    for item in order["items"]:
        if not item.get("product_id"):
            raise ValueError("Each item must have product_id")
        if not item.get("quantity") or item["quantity"] < 1:
            raise ValueError("Each item must have valid quantity")
        if not item.get("price") or item["price"] < 0:
            raise ValueError("Each item must have valid price")

    # Calculate totals - this block could also be extracted
    subtotal = 0
    for item in order["items"]:
        item_total = item["quantity"] * item["price"]
        subtotal += item_total

    tax_rate = 0.08
    tax = subtotal * tax_rate
    total = subtotal + tax

    # Build response
    return {
        "order_id": order.get("order_id", "NEW"),
        "customer_id": order["customer_id"],
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
        "status": "processed",
    }
