"""Role-based authorization for aggregated tools."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from mcp_shared.auth import AuthPolicy, authorize_tool


class AuthManager:
    """Loads policies and enforces tool-level permissions."""

    def __init__(self, policies_path: str | Path | None = None, default_role: str = "analyst"):
        self.policies: list[AuthPolicy] = []
        self.default_role = os.getenv("MCP_DEFAULT_ROLE", default_role)
        path = policies_path or os.getenv("MCP_POLICIES_PATH")
        if path and Path(path).exists():
            self.load(Path(path))

    def load(self, path: Path) -> None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        self.policies = [AuthPolicy.model_validate(p) for p in data.get("policies", [])]

    def check(self, tool_name: str, role: str | None = None) -> bool:
        if not self.policies:
            return True  # open when no policies configured
        effective_role = role or self.default_role
        return authorize_tool(tool_name, self.policies, effective_role)

    def role_from_headers(self, headers: dict[str, Any]) -> str:
        return headers.get("x-mcp-role", self.default_role)
