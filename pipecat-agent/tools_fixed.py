"""Small deterministic tools for the Pipecat implementation."""

from pipecat.services.llm_service import FunctionCallParams

ORDERS = {"ORD101": "Shipped", "ORD102": "Out for delivery", "ORD103": "Delivered"}


def get_order_status(order_id: str) -> str:
    normalized = order_id.strip().upper()
    status = ORDERS.get(normalized)
    if status is None:
        return f"I couldn't find order {normalized}."
    return f"Order {normalized} is currently {status.lower()}."


async def order_status_tool(params: FunctionCallParams, order_id: str) -> None:
    """Look up a mock order status.

    Args:
        order_id: The order number, for example ORD102.
    """
    await params.result_callback({"order_id": order_id, "status": get_order_status(order_id)})

