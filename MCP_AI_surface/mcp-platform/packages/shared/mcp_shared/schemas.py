"""JSON-schema helpers and registry config validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from mcp_core.types import ServerRegistration


class RegistryConfig(BaseModel):
    """Top-level aggregator configuration."""

    servers: dict[str, ServerRegistration] = Field(default_factory=dict)
    policies: list[dict[str, Any]] = Field(default_factory=list)


def text_content(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}
