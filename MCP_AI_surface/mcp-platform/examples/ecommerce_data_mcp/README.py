"""Example: ecommerce data domain — registers orders-focused queries."""

# This example shows how a domain-specific connector would be structured.
# Copy packages/connectors/postgres_mcp/ and specialize tools for your schema.

EXAMPLE_TOOLS = [
    {
        "name": "orders_summary",
        "description": "Daily order count and revenue",
        "sql": "SELECT date_trunc('day', created_at) AS day, COUNT(*), SUM(total) FROM orders GROUP BY 1",
    },
    {
        "name": "top_products",
        "description": "Best-selling products last 30 days",
        "sql": """
            SELECT product_id, SUM(quantity) AS units
            FROM order_items
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """,
    },
]
