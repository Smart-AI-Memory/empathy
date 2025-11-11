"""
Centralized Logging Configuration for Empathy Framework

Provides professional logging setup with:
- Console and file logging
- Structured logging with context
- Log rotation for production use
- Configurable log levels

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with context."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, use_color: bool = True, include_context: bool = False):
        """
        Initialize formatter.

        Args:
            use_color: Whether to use colored output
            include_context: Whether to include contextual information
        """
        self.use_color = use_color and sys.stderr.isatty()
        self.include_context = include_context
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional colors and context."""
        # Get color for this level
        color = self.COLORS.get(record.levelname, self.RESET) if self.use_color else ""
        reset = self.RESET if self.use_color else ""

        # Build the main log message
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level_name = f"{color}{record.levelname}{reset}" if self.use_color else record.levelname

        # Format: [TIMESTAMP] [LEVEL] module.function: message
        log_msg = (
            f"[{timestamp}] [{level_name}] {record.name}:{record.funcName}: {record.getMessage()}"
        )

        # Add context if available
        if self.include_context and hasattr(record, "context"):
            context_str = " ".join(f"{k}={v}" for k, v in record.context.items())
            log_msg += f" [{context_str}]"

        # Add exception info if present
        if record.exc_info:
            log_msg += "\n" + self.formatException(record.exc_info)

        return log_msg


def create_logger(
    name: str,
    level: int = logging.INFO,
    log_file: str | None = None,
    log_dir: str | None = None,
    use_color: bool = True,
    include_context: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Create a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        log_dir: Optional log directory for file-based logging
        use_color: Whether to use colored console output
        include_context: Whether to include contextual information
        max_bytes: Max size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance

    Example:
        >>> logger = create_logger(__name__, level=logging.DEBUG)
        >>> logger.info("Application started")
        >>> logger.debug("Detailed debug information")
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_formatter = StructuredFormatter(use_color=use_color, include_context=include_context)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (if log_file or log_dir specified)
    if log_file or log_dir:
        if log_dir:
            log_dir_path = Path(log_dir)
            log_dir_path.mkdir(parents=True, exist_ok=True)
            log_file = log_dir_path / f"{name.replace('.', '_')}.log"
        else:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setLevel(level)
        file_formatter = StructuredFormatter(use_color=False, include_context=include_context)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class LoggingConfig:
    """Centralized logging configuration manager."""

    _configured = False
    _loggers: dict[str, logging.Logger] = {}

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        log_dir: str | None = None,
        use_color: bool = True,
        include_context: bool = False,
    ) -> None:
        """
        Configure global logging settings.

        Args:
            level: Default logging level
            log_dir: Directory for log files
            use_color: Whether to use colored output
            include_context: Whether to include contextual information

        Example:
            >>> LoggingConfig.configure(
            ...     level=logging.DEBUG,
            ...     log_dir="./logs",
            ...     use_color=True
            ... )
        """
        cls._level = level
        cls._log_dir = log_dir
        cls._use_color = use_color
        cls._include_context = include_context
        cls._configured = True

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: int | None = None,
    ) -> logging.Logger:
        """
        Get or create a logger instance.

        Args:
            name: Logger name (typically __name__)
            level: Optional override for logging level

        Returns:
            Configured logger instance

        Example:
            >>> logger = LoggingConfig.get_logger(__name__)
            >>> logger.info("Processing data")
        """
        if name not in cls._loggers:
            if not cls._configured:
                cls.configure()

            logger = create_logger(
                name,
                level=level or cls._level,
                log_dir=cls._log_dir,
                use_color=cls._use_color,
                include_context=cls._include_context,
            )
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def set_level(cls, level: int) -> None:
        """Set logging level for all loggers."""
        for logger in cls._loggers.values():
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.

    This is the primary function to use throughout the codebase.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from empathy_os.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
        >>> logger.debug("Processing item", extra={"context": {"item_id": 123}})
    """
    return LoggingConfig.get_logger(name)


# Initialize with environment variable support
def init_logging_from_env() -> None:
    """Initialize logging configuration from environment variables."""
    log_level_str = os.getenv("EMPATHY_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_dir = os.getenv("EMPATHY_LOG_DIR")
    use_color = os.getenv("EMPATHY_LOG_COLOR", "true").lower() == "true"
    include_context = os.getenv("EMPATHY_LOG_CONTEXT", "false").lower() == "true"

    LoggingConfig.configure(
        level=log_level,
        log_dir=log_dir,
        use_color=use_color,
        include_context=include_context,
    )
