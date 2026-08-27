"""Pipecat function-tool adapter for TalkBot's mock order lookup."""

from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.services.llm_service import FunctionCallParams

from tools_core import get_order_status


async def get_order_status_handler(params: FunctionCallParams) -> None:
    order_id = str(params.arguments.get("order_id", ""))
    await params.result_callback(get_order_status(order_id))


get_order_status_function = FunctionSchema(
    name="get_order_status",
    description="Look up the status of a customer order. Never guess an order status.",
    properties={
        "order_id": {
            "type": "string",
            "description": "Order ID such as ORD101, ORD102, or ORD103.",
        }
    },
    required=["order_id"],
    handler=get_order_status_handler,
)
