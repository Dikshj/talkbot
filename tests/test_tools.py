import importlib.util
from pathlib import Path


def load_tools():
    path = Path(__file__).parents[1] / "livekit-agent" / "tools.py"
    spec = importlib.util.spec_from_file_location("livekit_tools", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_known_order_lookup():
    tools = load_tools()
    assert tools.get_order_status("ord102") == "Order ORD102 is currently out for delivery."


def test_unknown_order_is_not_invented():
    tools = load_tools()
    assert "couldn't find" in tools.get_order_status("ORD999")
