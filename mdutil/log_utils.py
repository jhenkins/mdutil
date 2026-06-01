"""Logging utilities with auto-timestamps."""

from __future__ import annotations

from datetime import datetime


def timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def timestamp_local() -> str:
    """Get current local timestamp in ISO format."""
    return datetime.now().isoformat()


def format_log_message(level: str, message: str) -> str:
    """Format a log message with timestamp."""
    return f"[{timestamp()}] [{level}] {message}"


def log_message(level: str, message: str, filename: str | None = None) -> None:
    """Log a timestamped message to stdout."""
    log_string = format_log_message(level, message)
    if filename:
        log_string = f"{filename}: {log_string}"
    print(log_string)


class TimestampedLogger:
    """Simple timestamped logger."""

    def __init__(self, name: str = "mdutil") -> None:
        self.name = name

    def debug(self, message: str) -> None:
        log_message("DEBUG", message, self.name)

    def info(self, message: str) -> None:
        log_message("INFO", message, self.name)

    def warning(self, message: str) -> None:
        log_message("WARNING", message, self.name)

    def error(self, message: str) -> None:
        log_message("ERROR", message, self.name)


logger = TimestampedLogger("mdutil")


def create_logger(name: str) -> TimestampedLogger:
    """Create a timestamped logger with the given name."""
    return TimestampedLogger(name)
