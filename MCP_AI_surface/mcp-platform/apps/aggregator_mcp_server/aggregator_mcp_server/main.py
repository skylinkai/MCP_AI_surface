"""Aggregator MCP Server — central router exposing a unified MCP endpoint."""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import mcp.types as types
import uvicorn
from mcp.server import Server
from mcp.server.fastmcp.server import StreamableHTTPASGIApp
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from aggregator_mcp_server.auth import AuthManager
from aggregator_mcp_server.middleware import APIKeyMiddleware
from aggregator_mcp_server.registry import Registry
from aggregator_mcp_server.router import Router
from aggregator_mcp_server.tools import list_servers
from mcp_shared.logging import get_logger, setup_logging

logger = get_logger(__name__)

CONFIG_PATH = os.getenv(
    "AGGREGATOR_CONFIG",
    str(Path(__file__).resolve().parents[3] / "config" / "registry.yaml"),
)
POLICIES_PATH = os.getenv(
    "MCP_POLICIES_PATH",
    str(Path(__file__).resolve().parents[3] / "config" / "policies.yaml"),
)

registry = Registry(CONFIG_PATH)
router = Router(registry)
auth_manager = AuthManager(POLICIES_PATH)
mcp_server = Server("aggregator-mcp")


@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    tools: list[types.Tool] = [
        types.Tool(
            name="registry.list_servers",
            description="List all registered downstream MCP connector servers",
            inputSchema={"type": "object", "properties": {}},
        )
    ]
    for aggregated in await router.list_aggregated_tools():
        tools.append(
            types.Tool(
                name=aggregated.name,
                description=aggregated.description,
                inputSchema=aggregated.input_schema,
            )
        )
    return tools


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    arguments = arguments or {}

    if name == "registry.list_servers":
        result = await list_servers(registry, arguments)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    if not auth_manager.check(name):
        return [
            types.TextContent(
                type="text",
                text=f"Forbidden: role lacks permission for tool {name}",
            )
        ]

    result = await router.route_tool_call(name, arguments)
    text = json.dumps(result, indent=2, default=str)
    return [types.TextContent(type="text", text=text)]


@mcp_server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    resources = await router.list_aggregated_resources()
    return [
        types.Resource(
            uri=r.uri,
            name=r.name,
            description=r.description,
            mimeType=r.mime_type,
        )
        for r in resources
    ]


@mcp_server.read_resource()
async def handle_read_resource(uri: str) -> str:
    result = await router.route_resource_read(uri)
    return json.dumps(result, indent=2, default=str)


def create_app() -> Starlette:
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        json_response=True,
        stateless=True,
    )

    @asynccontextmanager
    async def lifespan(app: Starlette):
        async with session_manager.run():
            yield

    async def health(_request: Request) -> JSONResponse:
        servers = registry.list_servers()
        status: dict[str, Any] = {"status": "ok", "servers": {}}
        from mcp_core.connector import ConnectorClient

        for name, server in servers.items():
            client = ConnectorClient(server.url, auth_token=server.auth_token, timeout=2.0)
            try:
                status["servers"][name] = await client.health()
            finally:
                await client.close()
        return JSONResponse(status)

    streamable_app = StreamableHTTPASGIApp(session_manager)

    app = Starlette(
        lifespan=lifespan,
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/mcp", endpoint=streamable_app, methods=["GET", "POST", "DELETE"]),
        ],
    )
    app.add_middleware(APIKeyMiddleware)
    return app


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()
