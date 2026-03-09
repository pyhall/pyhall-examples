# Discord Integration

Two CLI commands that connect a pyhall lab environment to a Discord server via the Discord API.

## Commands

### `discord-lab`

Generates a Discord setup plan for your lab — OAuth URL, channel list, env template.
Does **not** call the Discord API. Safe to run without credentials.

```bash
pyhall discord-lab --server-name my-lab --client-id <discord-app-client-id>
pyhall discord-lab --json   # machine-readable output
```

### `discord-bootstrap`

Bootstraps the private lab Discord server through the Discord API.
Creates channels, sets up webhooks, and writes an env file with the resulting URLs.

```bash
export DISCORD_BOT_TOKEN=<your-bot-token>
pyhall discord-bootstrap \
  --guild-id <your-guild-id> \
  --write-env-file discord.env
```

## Setup

These commands are not included in the core `pyhall-wcp` package.
To use them, copy `discord_commands.py` into your project and register the commands
with your Typer app, or run them standalone.

## Requirements

```
pip install pyhall-wcp typer rich
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DISCORD_BOT_TOKEN` | Yes (bootstrap) | Discord bot token with `MANAGE_CHANNELS` + `MANAGE_WEBHOOKS` |

## Channels created

- `agent-bulletin-board` — primary agent notification channel
- `lab-alerts` — system alerts
