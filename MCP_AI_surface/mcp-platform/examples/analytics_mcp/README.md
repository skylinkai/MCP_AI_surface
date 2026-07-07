# Analytics MCP example

Domain-specific connector pattern for analytics workloads.

## Concept

Extend `postgres-mcp` with pre-approved analytical queries instead of free-form SQL:

```python
@connector.tool(name="daily_active_users", ...)
async def daily_active_users(input_data):
    sql = "SELECT date, count(*) FROM events WHERE ..."
    ...
```

Register as `analytics-prod` in `config/registry.yaml` → tools appear as `daily_active_users.analytics-prod`.

## When to use

- Restrict AI to curated metrics queries
- Hide raw schema complexity
- Enforce row-level filters in connector code

See `examples/ecommerce_data_mcp/` for order-focused query templates.
