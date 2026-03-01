# Agent context: np-chatbot

Use this when editing or adding code in this repo.

## Architecture

- **Bot runs as a daemon.** CLI does not run the bot in-process; it talks to the daemon via RPC, socket, or HTTP API.
- **CLI subcommands** (examples): start bot, stop bot, join live channel, status, tail logs, manage scheduled messages, manage commands.

## Stack and constraints

- **Python**: 3.12+, managed with **uv** (no pip/poetry).
- **Config**: pydantic-settings only.
- **DB**: SQLite via **stdlib `sqlite3`** only (no ORM). **Single-threaded access** (no WAL; all DB work on one thread/queue). All DB functionality lives in a **database module**; encapsulate every query in helper methods.
- **Async**: One async framework for concurrency and “run at time X” scheduling.
- **Auth**: OAuth for YouTube. Credentials in memory for now; secure store later.
- **Logging**: **structlog**.
- **Style**: Non-professional: no tests, minimal comments/docs, no over-engineering.

## Layout (target)

- **YouTube-specific code** in one module; rest of app must not depend on YouTube APIs directly.
- **Database**: One **database module**; all SQLite access and queries go through helper methods in that module (stdlib `sqlite3`, no ORM).
- **Chat input**: abstracted as an **iterator** yielding shared data objects. No YouTube types outside the YouTube module.
- **Standard data types**: `ChatQuestion`, `ModerationAction`, `MemberMilestone`, `ChatCommandInvocation`.

## Behaviors

- **!ask**: Any message **starting with `!ask`** is a question; strip prefix and store the rest in SQLite. No rate limiting for now. (Google Sheet sync later.)
- **Moderation**: **Log only**—record moderation actions taken by moderators in chat; bot does not perform moderation.
- **Commands**: Stored in a **DB table**, managed by moderators. On `ChatCommandInvocation`, bot posts the configured reply. No templating yet.
- **Scheduled messages**: Add/remove at runtime; **each message has its own independent schedule**.
- **Membership milestones**: Record **member months** (“X months”) when users share milestones.

## Resilience

- Handle stream drops, disconnections, and process death (segfault, OOM). When the bot **restarts, resume where it left off** (e.g. persist enough state in DB or files).

## Testing / stress

- **Mock chat**: Replace the real chat iterator with a mock that yields fake data at a **configurable rate** and a **configurable probability distribution** over message types (regular chat most common).

## Deliverables (eventual)

- Daemon + CLI (start, stop, join channel, status, tail logs, manage scheduled messages, manage commands).
- GUI de-prioritized; may become a web app later.

When changing behavior or adding features: keep YouTube behind the iterator abstraction, DB access single-threaded, and daemon/CLI boundary clear.
