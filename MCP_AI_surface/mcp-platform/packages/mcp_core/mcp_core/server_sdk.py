"""Helpers for building HTTP-based MCP connector servers."""

from __future__ import annotations

from typing import Any, Callable, Awaitable

from fastapi import FastAPI
from pydantic import BaseModel

from mcp_core.types import ConnectorResource, ConnectorTool, ToolCallRequest, ToolCallResult


ToolHandler = Callable[[dict[str, Any]], Awaitable[ToolCallResult]]
ResourceReader = Callable[[str], Awaitable[dict[str, Any]]]


class ConnectorApp:
    """Build a FastAPI app implementing the standard connector HTTP API."""

    def __init__(self, name: str, version: str = "0.1.0"):
        self.app = FastAPI(title=name, version=version)
        self._tools: dict[str, ConnectorTool] = {}
        self._handlers: dict[str, ToolHandler] = {}
        self._resources: list[ConnectorResource] = []
        self._resource_readers: dict[str, ResourceReader] = {}
        self._register_routes()

    def tool(
        self,
        name: str,
        *,
        description: str = "",
        input_schema: dict[str, Any] | None = None,
    ) -> Callable[[ToolHandler], ToolHandler]:
        def decorator(fn: ToolHandler) -> ToolHandler:
            self._tools[name] = ConnectorTool(
                name=name,
                description=description,
                input_schema=input_schema or {"type": "object", "properties": {}},
            )
            self._handlers[name] = fn
            return fn

        return decorator

    def resource(
        self,
        uri: str,
        *,
        name: str,
        description: str = "",
        mime_type: str | None = None,
        reader: ResourceReader | None = None,
    ) -> None:
        self._resources.append(
            ConnectorResource(uri=uri, name=name, description=description, mime_type=mime_type)
        )
        if reader:
            self._resource_readers[uri] = reader

    def _register_routes(self) -> None:
        @self.app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "ok"}

        @self.app.post("/tools/list")
        async def list_tools() -> list[dict[str, Any]]:
            return [t.model_dump() for t in self._tools.values()]

        @self.app.post("/tools/call")
        async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
            handler = self._handlers.get(request.tool)
            if not handler:
                return ToolCallResult(
                    content=[{"type": "text", "text": f"Unknown tool: {request.tool}"}],
                    is_error=True,
                ).model_dump()
            result = await handler(request.input)
            return result.model_dump()

        @self.app.post("/resources/list")
        async def list_resources() -> list[dict[str, Any]]:
            return [r.model_dump() for r in self._resources]

        class ReadBody(BaseModel):
            uri: str

        @self.app.post("/resources/read")
        async def read_resource(body: ReadBody) -> dict[str, Any]:
            reader = self._resource_readers.get(body.uri)
            if not reader:
                return {"error": f"Unknown resource: {body.uri}"}
            return await reader(body.uri)
