"""HTTP client for the standard MCP connector interface."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_core.types import (
    ConnectorResource,
    ConnectorTool,
    ToolCallRequest,
    ToolCallResult,
)


class ConnectorClient:
    """Talks to a downstream data MCP server over HTTP."""

    def __init__(self, base_url: str, auth_token: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        headers: dict[str, str] = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def list_tools(self) -> list[ConnectorTool]:
        response = await self._client.post("/tools/list")
        response.raise_for_status()
        return [ConnectorTool.model_validate(item) for item in response.json()]

    async def call_tool(self, tool: str, input_data: dict[str, Any]) -> ToolCallResult:
        payload = ToolCallRequest(tool=tool, input=input_data)
        response = await self._client.post("/tools/call", json=payload.model_dump())
        response.raise_for_status()
        return ToolCallResult.model_validate(response.json())

    async def list_resources(self) -> list[ConnectorResource]:
        response = await self._client.post("/resources/list")
        response.raise_for_status()
        return [ConnectorResource.model_validate(item) for item in response.json()]

    async def read_resource(self, uri: str) -> dict[str, Any]:
        response = await self._client.post("/resources/read", json={"uri": uri})
        response.raise_for_status()
        return response.json()

    async def health(self) -> bool:
        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
