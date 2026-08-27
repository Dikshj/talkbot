"""Small deterministic tools exposed to the LiveKit LLM."""

ORDERS = {
    "ORD101": "Shipped",
    "ORD102": "Out for delivery",
    "ORD103": "Delivered",
}


def get_order_status(order_id: str) -> str:
    """Return the status of a known mock order without inventing one."""
    normalized = order_id.strip().upper()
    status = ORDERS.get(normalized)
    if status is None:
        return f"I couldn't find order {normalized}."
    return f"Order {normalized} is currently {status.lower()}."

