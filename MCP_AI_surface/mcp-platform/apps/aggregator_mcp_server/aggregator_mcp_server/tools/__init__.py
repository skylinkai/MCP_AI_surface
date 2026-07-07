"""Built-in aggregator management tools."""

from __future__ import annotations

from typing import Any

from aggregator_mcp_server.registry import Registry


async def list_servers(registry: Registry, _input: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": str(registry.to_dict())}],
        "is_error": False,
    }
