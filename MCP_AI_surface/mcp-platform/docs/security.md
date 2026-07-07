# Security

## Threat model

AI surfaces must not have direct access to databases, files, or APIs. All access flows through:

```
AI Surface → Aggregator (authZ) → Connector (sandbox) → Data
```

## Authentication (AuthN)

### Aggregator

Set `AGGREGATOR_API_KEY` to require `X-API-Key` or `Authorization: Bearer` on all routes except `/health`.

### Connectors

Per-server bearer tokens in `registry.yaml`:

```yaml
postgres-main:
  auth: service-token
  auth_token: ${POSTGRES_MCP_TOKEN}
```

The aggregator forwards `Authorization: Bearer <token>` to connectors.

## Authorization (AuthZ)

Policies in `config/policies.yaml`:

```yaml
policies:
  - role: analyst
    allow:
      - query.postgres-main
      - read_file.filesystem-local
    deny: []

  - role: admin
    allow: ["*"]
    deny: []
```

Default role: `MCP_DEFAULT_ROLE=analyst`.

When no policies file exists, all tools are allowed (development only).

## Data isolation

| Connector | Controls |
|-----------|----------|
| **Postgres** | SELECT-only queries in MVP |
| **Filesystem** | Path canonicalization; cannot escape `FS_ROOT` |
| **REST** | Host allowlist via `REST_ALLOWED_HOSTS` |

## Secrets management

- Never commit `.env` files
- Use environment variable substitution in production
- Rotate connector tokens independently

## Production recommendations

1. Enable `AGGREGATOR_API_KEY` on all environments
2. Use TLS termination at ingress
3. Restrict connector network policies (K8s NetworkPolicy)
4. Add audit logging for every `tools/call`
5. Implement dataset-level ACLs in connectors (Phase 3)

## Reporting issues

Document security findings in your organization's standard channel. Do not open public issues with exploit details.
