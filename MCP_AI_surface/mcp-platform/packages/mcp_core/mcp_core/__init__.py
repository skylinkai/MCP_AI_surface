"""MCP core protocol library — types, client, and connector interface."""

from mcp_core.client import MCPClient
from mcp_core.types import (
    AggregatedTool,
    ConnectorResource,
    ConnectorTool,
    ServerRegistration,
    ToolCallRequest,
    ToolCallResult,
)

__all__ = [
    "MCPClient",
    "AggregatedTool",
    "ConnectorResource",
    "ConnectorTool",
    "ServerRegistration",
    "ToolCallRequest",
    "ToolCallResult",
]
