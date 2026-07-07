"""Authorization policies for tool-level access control."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuthPolicy(BaseModel):
    """Role-based tool access policy."""

    role: str
    allow: list[str] = Field(default_factory=list)
    deny: list[str] = Field(default_factory=list)


def authorize_tool(tool_name: str, policies: list[AuthPolicy], role: str) -> bool:
    """Return True if *role* may invoke *tool_name*."""
    role_policies = [p for p in policies if p.role == role]
    if not role_policies:
        return False

    for policy in role_policies:
        if tool_name in policy.deny:
            return False
        if policy.allow and tool_name not in policy.allow:
            # Explicit allow list — tool must be listed
            if "*" not in policy.allow:
                return False
        if "*" in policy.allow or tool_name in policy.allow:
            return True
    return False
