import importlib.util
from pathlib import Path


def load_tools(relative_path: str):
    path = Path(__file__).parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_livekit_order_lookup_is_deterministic():
    tools = load_tools("livekit-agent/tools.py")
    assert tools.get_order_status("ord102") == "Order ORD102 is currently out for delivery."
    assert "couldn't find" in tools.get_order_status("ORD999")


def test_pipecat_core_order_lookup_matches_livekit():
    tools = load_tools("pipecat-agent/tools_core.py")
    assert tools.get_order_status("ORD101") == "Order ORD101 is currently shipped."
    assert "couldn't find" in tools.get_order_status("ORD999")
