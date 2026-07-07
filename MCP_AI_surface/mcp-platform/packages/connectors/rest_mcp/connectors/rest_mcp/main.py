"""REST API MCP connector — fetch external HTTP endpoints."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlparse

import httpx
import uvicorn

from mcp_core.server_sdk import ConnectorApp
from mcp_core.types import ToolCallResult
from mcp_shared.schemas import text_content

ALLOWED_HOSTS = {
    h.strip()
    for h in os.getenv("REST_ALLOWED_HOSTS", "api.github.com,httpbin.org").split(",")
    if h.strip()
}

connector = ConnectorApp("rest-mcp", version="0.1.0")


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http/https URLs allowed")
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Host not in allowlist: {parsed.hostname}")


@connector.tool(
    name="fetch",
    description="HTTP GET against an allowlisted REST endpoint",
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "headers": {"type": "object", "additionalProperties": {"type": "string"}},
        },
        "required": ["url"],
    },
)
async def fetch_tool(input_data: dict[str, Any]) -> ToolCallResult:
    url = input_data["url"]
    headers = input_data.get("headers") or {}
    try:
        _validate_url(url)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            body = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:100_000],
            }
            return ToolCallResult(content=[text_content(json.dumps(body, indent=2))])
    except Exception as exc:
        return ToolCallResult(content=[text_content(str(exc))], is_error=True)


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3003"))
    uvicorn.run(connector.app, host=host, port=port)


if __name__ == "__main__":
    main()
