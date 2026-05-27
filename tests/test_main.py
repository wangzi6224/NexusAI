from src.app.server import app


def test_app_registers_core_routes() -> None:
    paths = {route.path for route in app.routes}

    assert "/health" in paths
    assert "/chat" in paths
    assert "/rag/ask" in paths
    assert "/agent/chat" in paths
