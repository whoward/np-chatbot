# Requirements

## Current (from spec)

1. State in local SQLite.
2. Connect to live video via streaming API (no polling).
3. Terminal CLI: start bot, connect to chat, start consuming messages.
4. Config: pydantic-settings.
5. Dependencies: uv.
6. No comments required in code.
7. YouTube logic in one module; chat consumed via an iterator yielding shared data objects.
8. Standard data objects: `ChatQuestion`, `ModerationAction`, `MemberMilestone`, `ChatCommandInvocation`.
9. Async framework: parallel tasks + schedule a task at a specific time.
10. Non-professional: no tests, minimal docs.
11. Stress test: mock iterator yielding fake data at a set rate.
12. Collect questions from `!ask` in chat; store in DB.
13. Eventually: sync questions to Google Sheet.
14. Eventually: user-defined chat commands → bot posts message.
15. SQLite access single-threaded (no WAL).
16. Eventually: scheduled messages on regular intervals.
17. On membership milestone shares, record member months in DB.
18. Bot runs as a **daemon**; CLI communicates with the bot via RPC, socket, or HTTP API.
19. CLI supports multiple subcommands: start bot, stop bot, join live channel, status, tail logs, manage scheduled messages, manage commands, etc.
20. Use the **sqlite3** stdlib directly (no ORM). Encapsulate all DB queries in helper methods; put all database functionality in a **database module**.
21. Logging with **structlog**.

## Discovered (interview)

### Auth
- **OAuth** for YouTube. Credentials in memory for now; secure store later.

### !ask and questions
- Any chat message that **starts with `!ask`** is a question; store the rest (strip the `!ask` prefix). No rate limiting for now.

### Moderation
- **Log only**: bot records moderation actions taken by moderators in chat; no bot-initiated moderation.

### Commands
- Commands stored in a **database table**, managed by moderators. No templating yet.

### Scheduled messages
- Add/remove at **runtime**. Each scheduled message has its **own schedule** and is independent of the others.

### Membership milestones
- Collect only **"X months"** (member duration).

### Stress test (mock iterator)
- Set a **message rate** and **randomize message types** via a **configurable probability distribution**, with regular chat messages the most common.

### Resilience
- Bot must handle YouTube stream drops, disconnections, and process death (segfault, OOM, etc.). When the bot **starts again it should resume where it left off**.

### GUI / packaging
- GUI de-prioritized; may be replaced by a **web application** for future features.
