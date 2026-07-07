# Cursor MCP adapter

Point Cursor at the aggregator's unified MCP endpoint.

## Configuration

Copy into your project or global Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-platform": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

With API key auth enabled:

```json
{
  "mcpServers": {
    "mcp-platform": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-API-Key": "your-aggregator-key"
      }
    }
  }
}
```

## Available tools (after `docker compose up`)

| Tool | Description |
|------|-------------|
| `query.postgres-main` | Run SELECT against demo Postgres |
| `schema.postgres-main` | List public tables |
| `read_file.filesystem-local` | Read sandboxed files |
| `list_dir.filesystem-local` | List sandbox directory |
| `fetch.rest-api` | HTTP GET to allowlisted hosts |
| `registry.list_servers` | Inspect registered connectors |

## Example prompt in Cursor

> Use `query.postgres-main` to list all users, then summarize the results.
