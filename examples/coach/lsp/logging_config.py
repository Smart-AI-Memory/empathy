"""Logging Configuration for Coach LSP Server
Structured logging with multiple outputs
"""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    enable_file_logging: bool = True,
) -> logging.Logger:
    """Set up comprehensive logging for LSP server

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (default: ~/.coach/lsp.log)
        enable_file_logging: Whether to log to file

    Returns:
        Configured logger

    """
    # Create logger
    logger = logging.getLogger("coach_lsp")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Format
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if enable_file_logging:
        if log_file is None:
            # Default log location
            log_dir = Path.home() / ".coach" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"lsp_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,  # 10 MB
        )
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    return logger


def log_wizard_execution(
    logger: logging.Logger,
    wizard_name: str,
    task: str,
    duration: float,
    confidence: float,
    success: bool = True,
):
    """Log wizard execution metrics"""
    logger.info(
        f"Wizard executed: {wizard_name} | "
        f"Task: {task[:50]}... | "
        f"Duration: {duration:.2f}s | "
        f"Confidence: {confidence:.2f} | "
        f"Success: {success}",
    )


def log_lsp_request(logger: logging.Logger, method: str, params: dict, duration: float = None):
    """Log LSP request"""
    log_msg = f"LSP Request: {method}"
    if duration:
        log_msg += f" | Duration: {duration:.3f}s"
    logger.debug(log_msg)


def log_cache_stats(logger: logging.Logger, cache):
    """Log cache statistics"""
    stats = cache.stats()
    logger.info(
        f"Cache: {stats['total_entries']} entries | "
        f"TTL: {stats['ttl']}s | "
        f"Oldest: {stats['oldest_entry_age']:.1f}s",
    )


def log_error_with_context(
    logger: logging.Logger,
    error: Exception,
    context: str = "",
    wizard_name: str = None,
):
    """Log error with full context"""
    import traceback

    error_msg = f"Error in {context}"
    if wizard_name:
        error_msg += f" ({wizard_name})"
    error_msg += f": {error}"

    logger.error(error_msg)
    logger.debug(traceback.format_exc())


# Example usage
if __name__ == "__main__":
    # Set up logging
    logger = setup_logging(level="DEBUG")

    logger.debug("This is a debug message")
    logger.info("LSP server started")
    logger.warning("Cache near capacity")
    logger.error("Wizard execution failed")

    # Log wizard execution
    log_wizard_execution(
        logger,
        wizard_name="SecurityWizard",
        task="Analyze SQL queries",
        duration=1.23,
        confidence=0.95,
    )
