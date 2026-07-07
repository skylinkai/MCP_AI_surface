"""Filesystem MCP connector — read files and list directories."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import uvicorn

from mcp_core.server_sdk import ConnectorApp
from mcp_core.types import ToolCallResult
from mcp_shared.schemas import text_content


def _root() -> Path:
    default = Path(__file__).resolve().parents[4] / "data"
    return Path(os.getenv("FS_ROOT", str(default))).resolve()


connector = ConnectorApp("filesystem-mcp", version="0.1.0")


def _safe_path(relative: str) -> Path:
    root = _root()
    target = (root / relative).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError("Path escapes sandbox root")
    return target


@connector.tool(
    name="read_file",
    description="Read a text file from the sandboxed filesystem root",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path under FS_ROOT"},
        },
        "required": ["path"],
    },
)
async def read_file_tool(input_data: dict[str, Any]) -> ToolCallResult:
    try:
        path = _safe_path(input_data["path"])
        if not path.is_file():
            return ToolCallResult(content=[text_content(f"Not a file: {path}")], is_error=True)
        content = path.read_text(encoding="utf-8")
        return ToolCallResult(content=[text_content(content)])
    except Exception as exc:
        return ToolCallResult(content=[text_content(str(exc))], is_error=True)


@connector.tool(
    name="list_dir",
    description="List entries in a directory under FS_ROOT",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative directory path", "default": "."},
        },
    },
)
async def list_dir_tool(input_data: dict[str, Any]) -> ToolCallResult:
    try:
        path = _safe_path(input_data.get("path", "."))
        if not path.is_dir():
            return ToolCallResult(content=[text_content(f"Not a directory: {path}")], is_error=True)
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in path.iterdir())
        return ToolCallResult(content=[text_content(json.dumps(entries, indent=2))])
    except Exception as exc:
        return ToolCallResult(content=[text_content(str(exc))], is_error=True)


async def _read_readme_resource(_uri: str) -> dict[str, Any]:
    readme = _root() / "README.md"
    if readme.exists():
        return {"contents": [{"type": "text", "text": readme.read_text(encoding="utf-8")}]}
    return {"contents": [{"type": "text", "text": "No README.md in FS_ROOT"}]}


connector.resource(
    uri="file://README.md",
    name="Sandbox README",
    description="README from the filesystem sandbox root",
    mime_type="text/markdown",
    reader=_read_readme_resource,
)


def main() -> None:
    _root().mkdir(parents=True, exist_ok=True)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3002"))
    uvicorn.run(connector.app, host=host, port=port)


if __name__ == "__main__":
    main()
