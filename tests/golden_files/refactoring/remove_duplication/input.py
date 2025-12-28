"""Input file for remove_duplication golden test.

This file contains duplicated code blocks that should be consolidated.
"""


def create_user_report(user: dict) -> str:
    """Create a formatted user report."""
    lines = []

    # Header formatting - duplicated below
    lines.append("=" * 50)
    lines.append(f"  User Report: {user.get('name', 'Unknown')}")
    lines.append("=" * 50)
    lines.append("")

    lines.append(f"ID: {user.get('id', 'N/A')}")
    lines.append(f"Email: {user.get('email', 'N/A')}")
    lines.append(f"Status: {user.get('status', 'N/A')}")

    # Footer formatting - same as header
    lines.append("")
    lines.append("=" * 50)
    lines.append("  End of Report")
    lines.append("=" * 50)

    return "\n".join(lines)


def create_order_report(order: dict) -> str:
    """Create a formatted order report."""
    lines = []

    # Header formatting - same pattern as above
    lines.append("=" * 50)
    lines.append(f"  Order Report: {order.get('order_id', 'Unknown')}")
    lines.append("=" * 50)
    lines.append("")

    lines.append(f"Customer: {order.get('customer', 'N/A')}")
    lines.append(f"Total: ${order.get('total', 0):.2f}")
    lines.append(f"Status: {order.get('status', 'N/A')}")

    # Footer formatting - same pattern
    lines.append("")
    lines.append("=" * 50)
    lines.append("  End of Report")
    lines.append("=" * 50)

    return "\n".join(lines)


def create_product_report(product: dict) -> str:
    """Create a formatted product report."""
    lines = []

    # Header formatting - same pattern again
    lines.append("=" * 50)
    lines.append(f"  Product Report: {product.get('name', 'Unknown')}")
    lines.append("=" * 50)
    lines.append("")

    lines.append(f"SKU: {product.get('sku', 'N/A')}")
    lines.append(f"Price: ${product.get('price', 0):.2f}")
    lines.append(f"Stock: {product.get('stock', 0)}")

    # Footer formatting - same pattern
    lines.append("")
    lines.append("=" * 50)
    lines.append("  End of Report")
    lines.append("=" * 50)

    return "\n".join(lines)
