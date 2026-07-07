#!/bin/sh
set -e
case "$SERVICE" in
  aggregator) exec aggregator-mcp ;;
  postgres-mcp) exec postgres-mcp ;;
  filesystem-mcp) exec filesystem-mcp ;;
  rest-mcp) exec rest-mcp ;;
  *) echo "Unknown SERVICE=$SERVICE"; exit 1 ;;
esac
