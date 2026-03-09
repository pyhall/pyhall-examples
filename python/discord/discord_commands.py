# ---------------------------------------------------------------------------
# discord-lab
# ---------------------------------------------------------------------------

_LAB_DISCORD_CHANNELS = [
    "agent-bulletin-board",
    "lab-alerts",
    "worker-status",
    "deploy",
    "agent-updates",
    "monty",
]

_LAB_DISCORD_WEBHOOKS = {
    "agent-bulletin-board": "DISCORD_WEBHOOK_BULLETIN",
    "lab-alerts": "DISCORD_WEBHOOK_ALERTS",
    "worker-status": "DISCORD_WEBHOOK_WORKER_STATUS",
    "deploy": "DISCORD_WEBHOOK_DEPLOY",
    "agent-updates": "DISCORD_WEBHOOK_AGENTS",
    "monty": "DISCORD_WEBHOOK_MONTY",
}


def _discord_oauth_url(client_id: str) -> str:
    params = urlencode({
        "client_id": client_id,
        "scope": "bot applications.commands",
        "permissions": "2147560512",
    })
    return f"https://discord.com/oauth2/authorize?{params}"


def _discord_api_request(
    method: str,
    path: str,
    token: str,
    payload: Optional[dict] = None,
) -> dict | list:
    url = f"https://discord.com/api/v10{path}"
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, method=method.upper())
    request.add_header("Authorization", f"Bot {token}")
    request.add_header("Content-Type", "application/json")
    request.add_header("User-Agent", "DiscordBot (https://fafolab.ai, 0.1) Python/3")

    try:
        with urlopen(request) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Discord API {method.upper()} {path} failed: HTTP {exc.code} {details}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Discord API {method.upper()} {path} failed: {exc.reason}") from exc


def _discord_get_guild_channels(guild_id: str, token: str) -> list[dict]:
    result = _discord_api_request("GET", f"/guilds/{guild_id}/channels", token)
    if not isinstance(result, list):
        raise RuntimeError("Discord API returned unexpected channel payload")
    return result


def _discord_ensure_text_channel(guild_id: str, token: str, channel_name: str) -> dict:
    for channel in _discord_get_guild_channels(guild_id, token):
        if channel.get("type") == 0 and channel.get("name") == channel_name:
            return channel

    result = _discord_api_request(
        "POST",
        f"/guilds/{guild_id}/channels",
        token,
        {"name": channel_name, "type": 0},
    )
    if not isinstance(result, dict):
        raise RuntimeError(f"Discord API returned unexpected channel object for #{channel_name}")
    return result


def _discord_find_text_channel(guild_id: str, token: str, channel_name: str) -> Optional[dict]:
    for channel in _discord_get_guild_channels(guild_id, token):
        if channel.get("type") == 0 and channel.get("name") == channel_name:
            return channel
    return None


def _discord_create_webhook(channel_id: str, token: str, name: str) -> dict:
    result = _discord_api_request(
        "POST",
        f"/channels/{channel_id}/webhooks",
        token,
        {"name": name},
    )
    if not isinstance(result, dict):
        raise RuntimeError(f"Discord API returned unexpected webhook object for channel {channel_id}")
    return result


def _discord_webhook_url(webhook: dict) -> str:
    webhook_id = webhook.get("id")
    webhook_token = webhook.get("token")
    if not webhook_id or not webhook_token:
        raise RuntimeError("Webhook response missing id/token")
    return f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"


def _lab_discord_env_template(server_name: str, guild_id: str = "", client_id: str = "") -> str:
    oauth_url = _discord_oauth_url(client_id) if client_id else ""
    lines = [
        f"# {server_name} Discord secrets",
        f"# Server: {server_name}",
        "",
        f"export DISCORD_GUILD_ID={guild_id or 'YOUR_GUILD_ID'}",
        "export DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN",
        "export DISCORD_BULLETIN_CHANNEL_ID=YOUR_CHANNEL_ID",
        "",
    ]
    for env_name in _LAB_DISCORD_WEBHOOKS.values():
        lines.append(f"export {env_name}=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN")
    lines.extend([
        "",
        "export DISCORD_QUEUE=/tmp/discord_queue.jsonl",
    ])
    if oauth_url:
        lines.extend(["", f"# Bot invite URL", f"# {oauth_url}"])
    lines.append("")
    return "\n".join(lines)


def _lab_discord_exports_from_bootstrap(
    guild_id: str,
    bulletin_channel_id: str,
    webhook_urls: dict[str, str],
) -> str:
    lines = [
        f"export DISCORD_GUILD_ID={guild_id}",
        "export DISCORD_BOT_TOKEN=replace_me",
        f"export DISCORD_BULLETIN_CHANNEL_ID={bulletin_channel_id}",
        "",
    ]
    for channel_name in _LAB_DISCORD_CHANNELS:
        env_name = _LAB_DISCORD_WEBHOOKS[channel_name]
        lines.append(f"export {env_name}={webhook_urls[channel_name]}")
    lines.extend(
        [
            "",
            "export DISCORD_QUEUE=/tmp/discord_queue.jsonl",
        ]
    )
    return "\n".join(lines)


@app.command("discord-lab")
def discord_lab(
    server_name: str = typer.Option("my-lab", "--server-name", help="Discord server name"),
    client_id: Optional[str] = typer.Option(None, "--client-id", help="Discord application client ID"),
    guild_id: Optional[str] = typer.Option(None, "--guild-id", help="Discord guild/server ID"),
    write_env_template: Optional[Path] = typer.Option(
        None,
        "--write-env-template",
        help="Write a ready-to-fill env template file for your host secrets",
    ),
    output_json: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress banner"),
):
    """
    Generate a Discord setup plan for your lab.

    This does not call the Discord API. It gives you:
    - the channel list
    - the webhook env var map
    - the bot invite URL if a client ID is provided
    - an optional secrets template file
    """
    if not quiet and not output_json:
        _print_banner()

    oauth_url = _discord_oauth_url(client_id) if client_id else None
    env_template_text = _lab_discord_env_template(server_name, guild_id or "", client_id or "")

    if write_env_template is not None:
        write_env_template.parent.mkdir(parents=True, exist_ok=True)
        write_env_template.write_text(env_template_text, encoding="utf-8")

    payload = {
        "server_name": server_name,
        "channels": _LAB_DISCORD_CHANNELS,
        "webhook_map": _LAB_DISCORD_WEBHOOKS,
        "guild_id": guild_id,
        "client_id": client_id,
        "oauth_url": oauth_url,
        "env_template_path": str(write_env_template) if write_env_template else None,
        "next_steps": [
            "Create the private lab channels in Discord",
            "Create one webhook per automation channel",
            "Paste the webhook URLs and bot token into your secrets file",
            "Deploy pyhall to your host and enable the Discord bot service",
        ],
    }

    if output_json:
        print(json.dumps(payload, indent=2))
        return

    console.print(Panel.fit(
        Text.from_markup(
            f"[bold cyan]Lab Discord Setup[/bold cyan]\n"
            f"Server: [bold]{server_name}[/bold]"
        ),
        border_style="cyan",
    ))

    chan_table = Table(title="Channels")
    chan_table.add_column("Channel", style="cyan")
    chan_table.add_column("Webhook Env Var", style="white")
    for channel in _LAB_DISCORD_CHANNELS:
        chan_table.add_row(f"#{channel}", _LAB_DISCORD_WEBHOOKS.get(channel, "manual"))
    console.print(chan_table)

    if oauth_url:
        console.print(Panel(oauth_url, title="Bot Invite URL", border_style="green"))
    else:
        console.print("[yellow]No --client-id provided, so no bot invite URL was generated.[/yellow]")

    if write_env_template is not None:
        console.print(f"[green]Wrote secrets template:[/green] {write_env_template}")

    console.print("\n[bold]Next steps:[/bold]")
    for idx, step in enumerate(payload["next_steps"], start=1):
        console.print(f"  {idx}. {step}")


@app.command("discord-bootstrap")
def discord_bootstrap(
    guild_id: str = typer.Option(..., "--guild-id", help="Discord guild/server ID"),
    token_env: str = typer.Option("DISCORD_BOT_TOKEN", "--token-env", help="Env var holding the Discord bot token"),
    webhook_name: str = typer.Option("pyhall-bot", "--webhook-name", help="Webhook name to create per channel"),
    existing_only: bool = typer.Option(
        False,
        "--existing-only",
        help="Do not create channels. Use only existing text channels by expected names.",
    ),
    write_env_file: Optional[Path] = typer.Option(
        None,
        "--write-env-file",
        help="Write the resolved Discord env exports to a file",
    ),
    output_json: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress banner"),
):
    """
    Bootstrap the private lab Discord server through the Discord API.

    Requires the bot token to be present in the selected environment variable and
    the bot to have permission to manage channels and webhooks in the guild.
    """
    token = os.getenv(token_env, "").strip()
    if not token:
        console.print(f"[red]Missing bot token in environment variable:[/red] {token_env}")
        raise typer.Exit(1)

    if not quiet and not output_json:
        _print_banner()

    created_channels: list[dict[str, str]] = []
    webhook_urls: dict[str, str] = {}
    bulletin_channel_id = ""

    missing_channels: list[str] = []
    existing_channels: dict[str, dict] = {}

    if existing_only:
        for channel_name in _LAB_DISCORD_CHANNELS:
            channel = _discord_find_text_channel(guild_id, token, channel_name)
            if channel is None:
                missing_channels.append(channel_name)
            else:
                existing_channels[channel_name] = channel
        if missing_channels:
            raise RuntimeError(
                "Missing required existing channels for --existing-only: "
                + ", ".join(f"#{name}" for name in missing_channels)
            )

    for channel_name in _LAB_DISCORD_CHANNELS:
        if existing_only:
            channel = existing_channels[channel_name]
        else:
            channel = _discord_ensure_text_channel(guild_id, token, channel_name)
        channel_id = str(channel["id"])
        created_channels.append({"name": channel_name, "id": channel_id})
        if channel_name == "agent-bulletin-board":
            bulletin_channel_id = channel_id

        webhook = _discord_create_webhook(channel_id, token, webhook_name)
        webhook_urls[channel_name] = _discord_webhook_url(webhook)

    exports_text = _lab_discord_exports_from_bootstrap(guild_id, bulletin_channel_id, webhook_urls)

    if write_env_file is not None:
        write_env_file.parent.mkdir(parents=True, exist_ok=True)
        write_env_file.write_text(exports_text + "\n", encoding="utf-8")

    payload = {
        "guild_id": guild_id,
        "channels": created_channels,
        "webhook_map": {
            _LAB_DISCORD_WEBHOOKS[name]: webhook_urls[name]
            for name in _LAB_DISCORD_CHANNELS
        },
        "bulletin_channel_id": bulletin_channel_id,
        "env_file": str(write_env_file) if write_env_file else None,
    }

    if output_json:
        print(json.dumps(payload, indent=2))
        return

    console.print(Panel.fit(
        Text.from_markup(
            f"[bold cyan]Discord Bootstrap Complete[/bold cyan]\n"
            f"Guild: [bold]{guild_id}[/bold]\n"
            f"Channels created/verified: [bold]{len(created_channels)}[/bold]"
        ),
        border_style="green",
    ))
    console.print("[bold]Exports:[/bold]")
    console.print(exports_text)

    if write_env_file is not None:
        console.print(f"\n[green]Wrote env file:[/green] {write_env_file}")


