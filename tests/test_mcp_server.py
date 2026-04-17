from __future__ import annotations

import pytest

from repobrain.engine.core import RepoBrainEngine
from repobrain.mcp_server import RepoBrainMCPServer


def test_mcp_server_rejects_missing_query(mixed_repo) -> None:
    engine = RepoBrainEngine(mixed_repo)
    server = RepoBrainMCPServer(engine)

    with pytest.raises(ValueError):
        server._validate_tool_call("search_codebase", {})


def test_mcp_server_rejects_unknown_tool(mixed_repo) -> None:
    engine = RepoBrainEngine(mixed_repo)
    server = RepoBrainMCPServer(engine)

    with pytest.raises(ValueError):
        server._validate_tool_call("unknown_tool", {})


def test_mcp_server_accepts_review_focus(mixed_repo) -> None:
    engine = RepoBrainEngine(mixed_repo)
    server = RepoBrainMCPServer(engine)

    payload = server._validate_tool_call("review_codebase", {"focus": "security"})

    assert payload == {"focus": "security"}


def test_mcp_server_accepts_ship_baseline_label(mixed_repo) -> None:
    engine = RepoBrainEngine(mixed_repo)
    server = RepoBrainMCPServer(engine)

    payload = server._validate_tool_call("assess_ship_readiness", {"baseline_label": "release-1"})

    assert payload == {"baseline_label": "release-1"}
