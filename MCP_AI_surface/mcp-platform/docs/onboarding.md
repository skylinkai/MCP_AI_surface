# Onboarding

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Optional: local Postgres if not using Docker

## 1. Clone and install

```bash
cd mcp-platform
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## 2. Start the stack

```bash
docker compose -f docker/docker-compose.yml up --build
```

Services:

| Service | Port | URL |
|---------|------|-----|
| Aggregator MCP | 8000 | http://localhost:8000/mcp |
| Postgres MCP | 3001 | http://localhost:3001 |
| Filesystem MCP | 3002 | http://localhost:3002 |
| REST MCP | 3003 | http://localhost:3003 |
| Postgres DB | 5432 | postgresql://mcp:mcp@localhost:5432/mcp_demo |

## 3. Verify health

```bash
curl http://localhost:8000/health
curl http://localhost:3001/health
```

## 4. CLI smoke test

```bash
mcp-cli list-tools
mcp-cli call-tool query.postgres-main --input "{\"sql\": \"SELECT * FROM users\"}"
mcp-cli call-tool read_file.filesystem-local --input "{\"path\": \"README.md\"}"
```

## 5. Connect Cursor

Copy `apps/ai_adapters/cursor_adapter/mcp.json` into `.cursor/mcp.json` in your workspace.

## 6. Run without Docker

Terminal 1 — Postgres (or use existing instance and set `DATABASE_URL`):

```bash
postgres-mcp
```

Terminal 2:

```bash
filesystem-mcp
```

Terminal 3:

```bash
rest-mcp
```

Terminal 4:

```bash
aggregator-mcp
```

Ensure `config/registry.yaml` points to `localhost` ports.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AGGREGATOR_CONFIG` | `config/registry.yaml` | Connector registry |
| `MCP_POLICIES_PATH` | `config/policies.yaml` | AuthZ policies |
| `AGGREGATOR_API_KEY` | (unset) | Optional API key |
| `DATABASE_URL` | local postgres DSN | Postgres connector |
| `FS_ROOT` | `./data` | Filesystem sandbox root |

## Next steps

- [Building a connector](building-a-connector.md)
- [Security](security.md)
- [Architecture](architecture.md)
