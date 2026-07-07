# MCP AI Surface Platform

Python implementation of a universal **MCP aggregation platform**.

The full project lives in [`mcp-platform/`](mcp-platform/).

## Quick start

```bash
cd mcp-platform
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
docker compose -f docker/docker-compose.yml up --build
```

See [mcp-platform/README.md](mcp-platform/README.md) for architecture, CLI usage, and Cursor integration.

**Author:** Arindam Chakraborty ([arindcha@gmail.com](mailto:arindcha@gmail.com))
