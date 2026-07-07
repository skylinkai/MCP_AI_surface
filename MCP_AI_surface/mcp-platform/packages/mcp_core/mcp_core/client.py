"""High-level MCP client for AI surfaces."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """Connect to the Aggregator MCP Server."""

    def __init__(self, endpoint: str, headers: dict[str, str] | None = None):
        self.endpoint = endpoint.rstrip("/")
        self.headers = headers or {}

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[ClientSession]:
        async with streamablehttp_client(self.endpoint, headers=self.headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def list_tools(self) -> list[dict[str, Any]]:
        async with self._session() as session:
            result = await session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": tool.inputSchema or {},
                }
                for tool in result.tools
            ]

    async def call_tool(self, name: str, input_data: dict[str, Any] | None = None) -> Any:
        async with self._session() as session:
            result = await session.call_tool(name, input_data or {})
            if result.isError:
                text = "".join(
                    block.text for block in result.content if hasattr(block, "text")
                )
                raise RuntimeError(text or "Tool call failed")
            parts: list[Any] = []
            for block in result.content:
                if hasattr(block, "text"):
                    parts.append(block.text)
                elif hasattr(block, "data"):
                    parts.append(block.data)
            return parts[0] if len(parts) == 1 else parts

    async def list_resources(self) -> list[dict[str, Any]]:
        async with self._session() as session:
            result = await session.list_resources()
            return [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description or "",
                    "mimeType": resource.mimeType,
                }
                for resource in result.resources
            ]

    async def read_resource(self, uri: str) -> Any:
        async with self._session() as session:
            result = await session.read_resource(uri)
            parts = []
            for block in result.contents:
                if hasattr(block, "text"):
                    parts.append(block.text)
                elif hasattr(block, "blob"):
                    parts.append(block.blob)
            return parts[0] if len(parts) == 1 else parts
