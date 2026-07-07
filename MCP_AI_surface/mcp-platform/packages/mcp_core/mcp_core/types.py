"""Shared Pydantic models for the MCP platform."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ServerRegistration(BaseModel):
    """Entry in the aggregator registry."""

    type: Literal["mcp-server"] = "mcp-server"
    url: str
    auth: str = "none"
    auth_token: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    enabled: bool = True


class ConnectorTool(BaseModel):
    """Tool descriptor returned by connector POST /tools/list."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class ConnectorResource(BaseModel):
    """Resource descriptor returned by connector POST /resources/list."""

    uri: str
    name: str
    description: str = ""
    mime_type: str | None = None


class ToolCallRequest(BaseModel):
    """Payload for connector POST /tools/call."""

    tool: str
    input: dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(BaseModel):
    """Normalized tool call response."""

    content: list[dict[str, Any]] = Field(default_factory=list)
    is_error: bool = False


class ResourceReadRequest(BaseModel):
  uri: str


class AggregatedTool(BaseModel):
    """Tool exposed by the aggregator with source namespacing."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    source: str


def parse_aggregated_tool_name(name: str) -> tuple[str, str]:
    """Split ``query.postgres-main`` into (tool, source)."""
    if "." not in name:
        raise ValueError(f"Invalid aggregated tool name: {name!r} (expected tool.source)")
    tool, source = name.rsplit(".", 1)
    if not tool or not source:
        raise ValueError(f"Invalid aggregated tool name: {name!r}")
    return tool, source


def make_aggregated_tool_name(tool: str, source: str) -> str:
    return f"{tool}.{source}"
