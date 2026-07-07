# Building a Connector

Every data source is a pluggable MCP connector implementing the standard HTTP API.

## Quick start

Use `ConnectorApp` from `mcp_core.server_sdk`:

```python
from mcp_core.server_sdk import ConnectorApp
from mcp_core.types import ToolCallResult
from mcp_shared.schemas import text_content

connector = ConnectorApp("my-connector")

@connector.tool(
    name="hello",
    description="Say hello",
    input_schema={
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    },
)
async def hello(input_data: dict) -> ToolCallResult:
    name = input_data["name"]
    return ToolCallResult(content=[text_content(f"Hello, {name}!")])

# connector.app is a FastAPI application
```

Run with uvicorn:

```python
import uvicorn
uvicorn.run(connector.app, host="0.0.0.0", port=3010)
```

## Required endpoints

Your FastAPI app must expose:

### `POST /tools/list`

Returns JSON array of tool descriptors:

```json
[
  {
    "name": "query",
    "description": "Run SQL",
    "input_schema": {"type": "object", "properties": {"sql": {"type": "string"}}}
  }
]
```

### `POST /tools/call`

Request:

```json
{"tool": "query", "input": {"sql": "SELECT 1"}}
```

Response:

```json
{
  "content": [{"type": "text", "text": "[{\"?column?\": 1}]"}],
  "is_error": false
}
```

### `POST /resources/list` and `POST /resources/read`

Optional read-only data exposure. See `filesystem-mcp` for an example.

### `GET /health`

Return `{"status": "ok"}` for aggregator health checks.

## Register with aggregator

Add to `config/registry.yaml`:

```yaml
servers:
  my-connector:
    type: mcp-server
    url: http://localhost:3010
    auth: service-token
    auth_token: my-secret
    capabilities:
      - hello
    enabled: true
```

Tools appear as `hello.my-connector`.

## Add CLI entry point

In `pyproject.toml`:

```toml
[project.scripts]
my-connector = "connectors.my_mcp.main:main"
```

## Security checklist

- Validate and sandbox all inputs
- Never expose write operations without explicit auth
- Use allowlists for external URLs (see `rest-mcp`)
- Path-escape protection for filesystem access (see `filesystem-mcp`)
- Read-only SQL enforcement for analytics connectors (see `postgres-mcp`)

## Examples in this repo

| Connector | Path | Tools |
|-----------|------|-------|
| Postgres | `packages/connectors/postgres_mcp/` | `query`, `schema` |
| Filesystem | `packages/connectors/filesystem_mcp/` | `read_file`, `list_dir` |
| REST | `packages/connectors/rest_mcp/` | `fetch` |
