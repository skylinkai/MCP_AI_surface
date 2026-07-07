# Copilot Studio adapter (Phase 3)

Microsoft Copilot Studio can connect to external MCP servers via HTTP transport.

## Configuration

1. Deploy the aggregator to a reachable HTTPS endpoint.
2. In Copilot Studio, add a custom MCP connector pointing to:

   ```
   https://your-host/mcp
   ```

3. Pass authentication headers if `AGGREGATOR_API_KEY` is set.

## Tool discovery

Copilot Studio will auto-discover namespaced tools such as:

- `query.postgres-main`
- `read_file.filesystem-local`

## AuthZ

Map Copilot roles to MCP policies in `config/policies.yaml`. Use a dedicated `copilot` role with least-privilege tool allowlists.
