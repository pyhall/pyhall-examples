# pyhall-examples

Example workers and integrations for the [PyHall / WCP](https://pyhall.dev) ecosystem.

These are not part of the core SDK. They demonstrate how to build workers and connect
pyhall to external platforms using the Worker Class Protocol.

---

## Python

### Workers

| Example | Description |
|---|---|
| [`python/workers/hello_worker/`](python/workers/hello_worker/) | Minimal Python worker — routing, registry record, rules |
| [`python/workers/mcp_interop/`](python/workers/mcp_interop/) | Expose a WCP worker as an MCP tool (Claude Desktop, Claude Code, Cursor, etc.) |

### Integrations

| Integration | Description |
|---|---|
| [`python/discord/`](python/discord/) | Discord lab setup — create governed channels and webhooks via the Discord API |

## TypeScript

### Workers

| Example | Description |
|---|---|
| [`typescript/workers/hello-worker/`](typescript/workers/hello-worker/) | Minimal TypeScript worker |

---

## Requirements

```bash
pip install pyhall-wcp          # Python examples
npm install @pyhall/core        # TypeScript examples
```

## Docs

Full documentation at [pyhall.dev/docs](https://pyhall.dev/docs/getting-started/)

## License

Apache 2.0
