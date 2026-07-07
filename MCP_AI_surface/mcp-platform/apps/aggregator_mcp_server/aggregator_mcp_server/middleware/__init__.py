"""Authentication middleware for aggregator requests."""

from __future__ import annotations

import os
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validate ``X-API-Key`` or ``Authorization: Bearer`` against env secret."""

    def __init__(self, app, api_key: str | None = None):
        super().__init__(app)
        self.api_key = api_key or os.getenv("AGGREGATOR_API_KEY")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.api_key or request.url.path in ("/health",):
            return await call_next(request)

        provided = request.headers.get("X-API-Key") or _bearer_token(
            request.headers.get("Authorization")
        )
        if provided != self.api_key:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


def _bearer_token(header: str | None) -> str | None:
    if header and header.lower().startswith("bearer "):
        return header[7:].strip()
    return None
