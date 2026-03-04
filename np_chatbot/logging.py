import structlog
import sys

processors = [
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="iso")
]

if sys.stderr.isatty():
    processors.append(structlog.dev.ConsoleRenderer())
else:
    processors.append(structlog.processors.JSONRenderer())

structlog.configure(processors=processors)

def get_logger(name):
   return structlog.get_logger(name)