# pyhall-examples

This repo is dedicated to example workers and integrations for use within the pyhall ecosystem, which is a compliant implementation of the [Worker Class Protocol](https://workerclassprotocol.dev). Users are encouraged to post examples of their own integrations.

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

---

## TypeScript

### Workers

| Example | Description |
|---|---|
| [`typescript/workers/hello-worker/`](typescript/workers/hello-worker/) | Minimal TypeScript worker |

---

## Go

### Workers

| Example | Description |
|---|---|
| [`go/workers/hello-worker/`](go/workers/hello-worker/) | Minimal Go worker using pyhall-go |

---

## Requirements

```bash
pip install pyhall-wcp              # Python examples
npm install @pyhall/core            # TypeScript examples
go get github.com/pyhall/pyhall-go  # Go examples
```

## Contributing

Have an integration to share? Open a PR. Examples for any language or platform are welcome.

Planned official SDK support: **PHP · Ruby · Rust · Elixir · Java · .NET**

## Docs

Full documentation at [pyhall.dev/docs](https://pyhall.dev/docs/getting-started/)

## License

Apache 2.0
