#!/usr/bin/env python3
import argparse
import asyncio

import structlog

from np_chatbot.faketube import mock_chat_iterator

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)
log = structlog.get_logger()


async def main(rate: float, count: int) -> None:
    log.info("starting chat iterator", rate=rate, count=count)
    n = 0
    async for event in mock_chat_iterator(rate=rate):
        n += 1
        log.info("event", event_type=type(event).__name__, obj=event)
        if n >= count:
            log.info("stopping", events=n)
            break


def _run() -> None:
    p = argparse.ArgumentParser(description="Run mock chat iterator and log events to stdout.")
    p.add_argument("--rate", type=float, default=2.0, help="Events per second (default: 2.0)")
    p.add_argument("--count", type=int, default=10, help="Number of events to consume (default: 10)")
    args = p.parse_args()
    asyncio.run(main(rate=args.rate, count=args.count))


if __name__ == "__main__":
    _run()
