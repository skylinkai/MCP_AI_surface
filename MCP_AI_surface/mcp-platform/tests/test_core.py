"""Tests for MCP platform core utilities."""

import pytest

from mcp_core.types import make_aggregated_tool_name, parse_aggregated_tool_name
from mcp_shared.auth import AuthPolicy, authorize_tool


def test_parse_aggregated_tool_name():
    tool, source = parse_aggregated_tool_name("query.postgres-main")
    assert tool == "query"
    assert source == "postgres-main"


def test_make_aggregated_tool_name():
    assert make_aggregated_tool_name("query", "postgres-main") == "query.postgres-main"


def test_parse_invalid_name():
    with pytest.raises(ValueError):
        parse_aggregated_tool_name("no-dot-here")


def test_authorize_analyst():
    policies = [
        AuthPolicy(role="analyst", allow=["query.postgres-main"]),
    ]
    assert authorize_tool("query.postgres-main", policies, "analyst")
    assert not authorize_tool("delete.postgres-main", policies, "analyst")


def test_authorize_admin_wildcard():
    policies = [AuthPolicy(role="admin", allow=["*"])]
    assert authorize_tool("anything.here", policies, "admin")
