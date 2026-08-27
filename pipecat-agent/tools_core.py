"""Framework-independent order lookup used by the Pipecat tool adapter."""

ORDERS = {"ORD101": "Shipped", "ORD102": "Out for delivery", "ORD103": "Delivered"}


def get_order_status(order_id: str) -> str:
    normalized = order_id.strip().upper()
    status = ORDERS.get(normalized)
    if status is None:
        return f"I couldn't find order {normalized}."
    return f"Order {normalized} is currently {status.lower()}."
