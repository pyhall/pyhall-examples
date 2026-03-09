# ---------------------------------------------------------------------------
# discord-lab
# ---------------------------------------------------------------------------

def test_discord_lab_json_output():
    result = runner.invoke(app, ["discord-lab", "--json", "--server-name", "fafolab"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["server_name"] == "fafolab"
    assert "agent-bulletin-board" in data["channels"]
    assert data["webhook_map"]["agent-bulletin-board"] == "DISCORD_WEBHOOK_BULLETIN"


def test_discord_lab_writes_env_template(tmp_path):
    target = tmp_path / "fafo_secrets.env"
    result = runner.invoke(
        app,
        [
            "discord-lab",
            "--quiet",
            "--server-name", "fafolab",
            "--client-id", "1234567890",
            "--guild-id", "9876543210",
            "--write-env-template", str(target),
        ],
    )
    assert result.exit_code == 0
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    assert "DISCORD_WEBHOOK_BULLETIN" in text
    assert "DISCORD_GUILD_ID=9876543210" in text
    assert "https://discord.com/oauth2/authorize?" in text


def test_discord_bootstrap_writes_env_file(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")

    import pyhall.cli as cli_mod

    def fake_ensure_text_channel(guild_id, token, channel_name):
        assert guild_id == "9876543210"
        assert token == "test-token"
        return {"id": f"id-{channel_name}", "name": channel_name, "type": 0}

    def fake_create_webhook(channel_id, token, name):
        assert token == "test-token"
        assert name == "pyhall-bot"
        return {"id": f"wh-{channel_id}", "token": f"tok-{channel_id}"}

    monkeypatch.setattr(cli_mod, "_discord_ensure_text_channel", fake_ensure_text_channel)
    monkeypatch.setattr(cli_mod, "_discord_create_webhook", fake_create_webhook)

    target = tmp_path / "discord.env"
    result = runner.invoke(
        app,
        [
            "discord-bootstrap",
            "--quiet",
            "--guild-id", "9876543210",
            "--write-env-file", str(target),
        ],
    )
    assert result.exit_code == 0
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    assert "DISCORD_GUILD_ID=9876543210" in text
    assert "DISCORD_BULLETIN_CHANNEL_ID=id-agent-bulletin-board" in text
    assert "DISCORD_WEBHOOK_BULLETIN=https://discord.com/api/webhooks/wh-id-agent-bulletin-board/tok-id-agent-bulletin-board" in text
    assert "DISCORD_QUEUE=/tmp/discord_queue.jsonl" in text


def test_discord_bootstrap_existing_only_missing_channel(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token")

    import pyhall.cli as cli_mod

    def fake_find_text_channel(guild_id, token, channel_name):
        if channel_name == "agent-bulletin-board":
            return {"id": "id-agent-bulletin-board", "name": channel_name, "type": 0}
        return None

    monkeypatch.setattr(cli_mod, "_discord_find_text_channel", fake_find_text_channel)

    result = runner.invoke(
        app,
        [
            "discord-bootstrap",
            "--quiet",
            "--guild-id", "9876543210",
            "--existing-only",
        ],
    )
    assert result.exit_code == 1
    assert result.exception is not None
    assert "Missing required existing channels for --existing-only" in str(result.exception)


