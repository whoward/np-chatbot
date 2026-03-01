# np-chatbot

YouTube live chat bot that runs as a daemon: connects via streaming API, collects `!ask` questions, logs moderation actions, records membership months, and supports moderator-managed commands and per-message scheduled messages. State in SQLite; config via pydantic-settings. CLI talks to the daemon via RPC/socket/HTTP.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Run

- **Daemon**: start the bot process (details TBD).
- **CLI**: subcommands to start/stop bot, join live channel, status, tail logs, manage scheduled messages, manage commands, etc. CLI communicates with the daemon; it does not run the bot in-process.

```bash
uv run python -m np_chatbot ...
```

## Config

pydantic-settings (env vars, `.env`, or config file TBD). OAuth credentials in memory for now; secure store later.

## Project docs

- **AGENTS.md** — context for AI agents working on this repo
- **REQUIREMENTS.md** — full requirements and discovered details
