# MCP Platform (Python)

A universal **Model Context Protocol** aggregation layer that routes AI surfaces to pluggable data connectors.

```
AI Surface (Cursor, Copilot, CLI)
        ↓ MCP
Aggregator MCP Server  ← registry + auth + routing
        ↓ HTTP connector API
Source MCP Servers (Postgres, S3, REST, Filesystem, …)
        ↓
Actual Data
```

## Quick start

### 1. Install

```bash
cd mcp-platform
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
```

### 2. Start services (Docker)

```bash
docker compose -f docker/docker-compose.yml up --build
```

### 3. Use the CLI client

```bash
mcp-cli list-tools --endpoint http://localhost:8000/mcp
mcp-cli call-tool query.postgres-main --input '{"sql": "SELECT 1 AS ok"}'
mcp-cli list-resources
```

### 4. Cursor integration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-platform": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Project layout

| Path | Purpose |
|------|---------|
| `apps/aggregator_mcp_server/` | Central MCP router & registry |
| `apps/ai_adapters/cli_client/` | CLI MCP client |
| `packages/mcp_core/` | Protocol types, client SDK, connector interface |
| `packages/shared/` | Auth, logging, schemas |
| `packages/connectors/` | Pluggable data MCP servers |
| `docker/` | Docker Compose for local deployment |
| `docs/` | Architecture & guides |

## Tool naming convention

Downstream tools are namespaced as `{tool}.{source}`:

- `query.postgres-main` → Postgres connector `query` tool
- `read_file.filesystem-local` → Filesystem connector `read_file` tool

## Phases

- **Phase 1 (MVP)**: Core library, aggregator, Postgres + filesystem connectors, CLI
- **Phase 2**: Plugin registry, multi-server routing, auth layer
- **Phase 3**: Cursor/Copilot adapters, control plane, observability

See [docs/architecture.md](docs/architecture.md) for full design.

## Author

**Arindam Chakraborty** — [arindcha@gmail.com](mailto:arindcha@gmail.com)

## License

MIT
