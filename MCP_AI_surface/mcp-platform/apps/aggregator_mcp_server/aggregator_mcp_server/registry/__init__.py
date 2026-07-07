"""Server registry — stores and manages downstream MCP connector registrations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mcp_core.types import ServerRegistration
from mcp_shared.schemas import RegistryConfig


class Registry:
    """In-memory registry backed by optional YAML config."""

    def __init__(self, config_path: str | Path | None = None):
        self._servers: dict[str, ServerRegistration] = {}
        if config_path:
            self.load_from_file(config_path)

    def load_from_file(self, path: str | Path) -> None:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        config = RegistryConfig.model_validate(data or {})
        self._servers = config.servers

    def register(self, name: str, server: ServerRegistration) -> None:
        self._servers[name] = server

    def unregister(self, name: str) -> None:
        self._servers.pop(name, None)

    def get(self, name: str) -> ServerRegistration | None:
        entry = self._servers.get(name)
        if entry and entry.enabled:
            return entry
        return None

    def list_servers(self) -> dict[str, ServerRegistration]:
        return {k: v for k, v in self._servers.items() if v.enabled}

    def to_dict(self) -> dict[str, Any]:
        return {name: reg.model_dump() for name, reg in self._servers.items()}
