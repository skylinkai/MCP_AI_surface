"""Postgres MCP connector — SQL query and schema tools."""

from __future__ import annotations

import json
import os
from typing import Any

import asyncpg
import uvicorn

from mcp_core.server_sdk import ConnectorApp
from mcp_core.types import ToolCallResult
from mcp_shared.schemas import text_content


def _dsn() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://mcp:mcp@localhost:5432/mcp_demo",
    )


connector = ConnectorApp("postgres-mcp", version="0.1.0")


async def _get_pool() -> asyncpg.Pool:
    if not hasattr(_get_pool, "_pool"):
        _get_pool._pool = await asyncpg.create_pool(_dsn(), min_size=1, max_size=5)  # type: ignore[attr-defined]
    return _get_pool._pool  # type: ignore[attr-defined]


@connector.tool(
    name="query",
    description="Run a read-only SQL query against Postgres",
    input_schema={
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "SQL SELECT statement"},
            "params": {
                "type": "array",
                "items": {},
                "description": "Optional positional parameters",
            },
        },
        "required": ["sql"],
    },
)
async def query_tool(input_data: dict[str, Any]) -> ToolCallResult:
    sql = input_data.get("sql", "").strip()
    params = input_data.get("params") or []

    if not sql.lower().startswith("select"):
        return ToolCallResult(
            content=[text_content("Only SELECT queries are allowed in MVP")],
            is_error=True,
        )

    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *params)
        data = [dict(row) for row in rows]
        return ToolCallResult(content=[text_content(json.dumps(data, indent=2, default=str))])


@connector.tool(
    name="schema",
    description="List tables in the public schema",
    input_schema={"type": "object", "properties": {}},
)
async def schema_tool(_input_data: dict[str, Any]) -> ToolCallResult:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        tables = [row["table_name"] for row in rows]
        return ToolCallResult(content=[text_content(json.dumps(tables, indent=2))])


async def _read_tables_resource(_uri: str) -> dict[str, Any]:
    result = await schema_tool({})
    return {"contents": result.content}


connector.resource(
    uri="schema://public/tables",
    name="Public tables",
    description="Metadata resource listing public schema tables",
    mime_type="application/json",
    reader=_read_tables_resource,
)


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3001"))
    uvicorn.run(connector.app, host=host, port=port)


if __name__ == "__main__":
    main()
