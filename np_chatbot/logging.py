import structlog
import sys
import os

processors = [
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="iso")
]

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()

if sys.stderr.isatty():
    processors.append(structlog.dev.ConsoleRenderer())
else:
    processors.append(structlog.processors.JSONRenderer())

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(log_level),
    processors=processors
)

def get_logger(name):
   return structlog.get_logger(name)