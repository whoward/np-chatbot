# np-chatbot

YouTube live chat bot that runs as a daemon: connects via streaming API, collects `!ask` questions, logs moderation actions, records membership months, and supports moderator-managed commands and per-message scheduled messages. State in SQLite; config via pydantic-settings. CLI talks to the daemon via RPC/socket/HTTP.

The bot must be optimized to minimize the number of calls to the YouTube Data API v3 as the
default daily quota is only 10,000 units.  This can be extended but requires approval from Google.

Here are the costs of typical API interactions:

| Action | API Method | Quota Cost (Units) |
| :--- | :--- | :--- |
| **Read Chat (Polling)** | `liveChatMessages.list` | 5 |
| **Post a Message** | `liveChatMessages.insert` | 50 |
| **Delete a Message** | `liveChatMessages.delete` | 50 |
| **Ban/Timeout User** | `liveChatBans.insert` | 50 |
| **Get Live Chat ID** | `videos.list` | 1 |
| **Search for Stream** | `search.list` | 100 |

Even though we are reading chat using the streaming API the connection is only held open up to a
maximum time by Google and we need to reconnect again to continue receiving messages.  Google may
even close the connection before the maximum time if chat is quiet.  

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

To regenerate the gRPC client after changing the proto (only needed when editing `np_chatbot/youtube/proto/stream_list.proto`):

```bash
uv run python -m grpc_tools.protoc -Inp_chatbot/youtube/proto --python_out=np_chatbot/youtube/proto --grpc_python_out=np_chatbot/youtube/proto np_chatbot/youtube/proto/stream_list.proto
```

## Run

- **Test chat iterator**: run the mock chat iterator and log yielded events to stdout (stops after 10 events):

```bash
uv sync
uv run python scripts/test_chat_iterator.py
```

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
