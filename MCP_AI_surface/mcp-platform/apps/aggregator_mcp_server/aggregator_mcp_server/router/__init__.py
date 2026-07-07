"""Request router — forwards tool/resource calls to downstream connectors."""

from __future__ import annotations

from typing import Any

from mcp_core.connector import ConnectorClient
from mcp_core.types import (
    AggregatedTool,
    ConnectorResource,
    make_aggregated_tool_name,
    parse_aggregated_tool_name,
)
from aggregator_mcp_server.registry import Registry
from mcp_shared.logging import get_logger

logger = get_logger(__name__)


class Router:
    """Routes aggregated tool/resource names to downstream MCP servers."""

    def __init__(self, registry: Registry):
        self.registry = registry
        self._cache: dict[str, list[AggregatedTool]] = {}

    async def list_aggregated_tools(self, refresh: bool = False) -> list[AggregatedTool]:
        if self._cache and not refresh:
            return self._cache.get("tools", [])

        tools: list[AggregatedTool] = []
        for source, server in self.registry.list_servers().items():
            client = ConnectorClient(server.url, auth_token=server.auth_token)
            try:
                for tool in await client.list_tools():
                    tools.append(
                        AggregatedTool(
                            name=make_aggregated_tool_name(tool.name, source),
                            description=f"[{source}] {tool.description}",
                            input_schema=tool.input_schema,
                            source=source,
                        )
                    )
            except Exception as exc:
                logger.warning("failed_to_list_tools", source=source, error=str(exc))
            finally:
                await client.close()

        self._cache["tools"] = tools
        return tools

    async def list_aggregated_resources(self) -> list[ConnectorResource]:
        resources: list[ConnectorResource] = []
        for source, server in self.registry.list_servers().items():
            client = ConnectorClient(server.url, auth_token=server.auth_token)
            try:
                for resource in await client.list_resources():
                    resources.append(
                        ConnectorResource(
                            uri=f"{source}://{resource.uri.removeprefix('file://')}",
                            name=f"[{source}] {resource.name}",
                            description=resource.description,
                            mime_type=resource.mime_type,
                        )
                    )
            except Exception as exc:
                logger.warning("failed_to_list_resources", source=source, error=str(exc))
            finally:
                await client.close()
        return resources

    async def route_tool_call(self, aggregated_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        tool, source = parse_aggregated_tool_name(aggregated_name)
        server = self.registry.get(source)
        if not server:
            return {
                "content": [{"type": "text", "text": f"Unknown source: {source}"}],
                "is_error": True,
            }

        client = ConnectorClient(server.url, auth_token=server.auth_token)
        try:
            result = await client.call_tool(tool, input_data)
            return result.model_dump()
        except Exception as exc:
            logger.error("tool_call_failed", tool=aggregated_name, error=str(exc))
            return {
                "content": [{"type": "text", "text": f"Routing error: {exc}"}],
                "is_error": True,
            }
        finally:
            await client.close()

    async def route_resource_read(self, uri: str) -> dict[str, Any]:
        if "://" not in uri:
            return {"error": f"Invalid resource URI: {uri}"}
        source, _, path = uri.partition("://")
        server = self.registry.get(source)
        if not server:
            return {"error": f"Unknown source: {source}"}

        client = ConnectorClient(server.url, auth_token=server.auth_token)
        try:
            return await client.read_resource(path)
        except Exception as exc:
            return {"error": str(exc)}
        finally:
            await client.close()
