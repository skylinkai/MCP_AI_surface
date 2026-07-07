"""CLI MCP client for the aggregator."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from mcp_core.client import MCPClient

app = typer.Typer(help="MCP Platform CLI — talk to the Aggregator MCP Server")
console = Console()

DEFAULT_ENDPOINT = os.getenv("MCP_ENDPOINT", "http://localhost:8000/mcp")


def _headers(api_key: str | None) -> dict[str, str]:
    if api_key:
        return {"X-API-Key": api_key}
    return {}


def _run(coro):
    return asyncio.run(coro)


@app.command("list-tools")
def list_tools_cmd(
    endpoint: str = typer.Option(DEFAULT_ENDPOINT, "--endpoint", "-e"),
    api_key: str | None = typer.Option(None, "--api-key"),
) -> None:
    """List all tools exposed by the aggregator."""

    async def _list():
        client = MCPClient(endpoint, headers=_headers(api_key))
        return await client.list_tools()

    tools = _run(_list())
    table = Table(title="Aggregator Tools")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    for tool in tools:
        table.add_row(tool["name"], tool.get("description", ""))
    console.print(table)


@app.command("call-tool")
def call_tool_cmd(
    name: str = typer.Argument(..., help="Aggregated tool name, e.g. query.postgres-main"),
    input_json: str = typer.Option("{}", "--input", "-i", help="JSON tool input"),
    endpoint: str = typer.Option(DEFAULT_ENDPOINT, "--endpoint", "-e"),
    api_key: str | None = typer.Option(None, "--api-key"),
) -> None:
    """Invoke an aggregated tool."""

    async def _call():
        client = MCPClient(endpoint, headers=_headers(api_key))
        payload: dict[str, Any] = json.loads(input_json)
        return await client.call_tool(name, payload)

    try:
        result = _run(_call())
        console.print(result)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command("list-resources")
def list_resources_cmd(
    endpoint: str = typer.Option(DEFAULT_ENDPOINT, "--endpoint", "-e"),
    api_key: str | None = typer.Option(None, "--api-key"),
) -> None:
    """List aggregated resources."""

    async def _list():
        client = MCPClient(endpoint, headers=_headers(api_key))
        return await client.list_resources()

    resources = _run(_list())
    table = Table(title="Aggregator Resources")
    table.add_column("URI", style="green")
    table.add_column("Name")
    for resource in resources:
        table.add_row(resource["uri"], resource.get("name", ""))
    console.print(table)


@app.command("read-resource")
def read_resource_cmd(
    uri: str = typer.Argument(..., help="Resource URI"),
    endpoint: str = typer.Option(DEFAULT_ENDPOINT, "--endpoint", "-e"),
    api_key: str | None = typer.Option(None, "--api-key"),
) -> None:
    """Read an aggregated resource."""

    async def _read():
        client = MCPClient(endpoint, headers=_headers(api_key))
        return await client.read_resource(uri)

    console.print(_run(_read()))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
