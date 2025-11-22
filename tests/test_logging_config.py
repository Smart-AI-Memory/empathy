"""
Tests for Logging Configuration Module

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import logging
import os
import shutil
import sys
import tempfile
from unittest.mock import patch

import pytest

from empathy_os.logging_config import (
    LoggingConfig,
    StructuredFormatter,
    create_logger,
    get_logger,
    init_logging_from_env,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture(autouse=True)
def reset_logging_config():
    """Reset LoggingConfig state before each test"""
    LoggingConfig._configured = False
    LoggingConfig._loggers = {}
    yield
    LoggingConfig._configured = False
    LoggingConfig._loggers = {}


class TestStructuredFormatter:
    """Test StructuredFormatter class"""

    def test_formatter_without_color(self):
        """Test formatter without color support"""
        formatter = StructuredFormatter(use_color=False, include_context=False)
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_func",
        )

        output = formatter.format(record)
        assert "test.module:test_func: Test message" in output
        assert "INFO" in output
        assert "\033[" not in output  # No ANSI color codes

    def test_formatter_with_color(self):
        """Test formatter with color support"""
        with patch.object(sys.stderr, "isatty", return_value=True):
            formatter = StructuredFormatter(use_color=True, include_context=False)
            record = logging.LogRecord(
                name="test.module",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error message",
                args=(),
                exc_info=None,
                func="test_func",
            )

            output = formatter.format(record)
            assert "test.module:test_func: Error message" in output
            # Should contain color codes when use_color=True and isatty=True
            assert "\033[" in output or "ERROR" in output

    def test_formatter_with_context(self):
        """Test formatter with context information (lines 64-65)"""
        formatter = StructuredFormatter(use_color=False, include_context=True)
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_func",
        )
        # Add context attribute
        record.context = {"user_id": "123", "request_id": "abc"}

        output = formatter.format(record)
        assert "user_id=123" in output
        assert "request_id=abc" in output

    def test_formatter_without_context_attribute(self):
        """Test formatter when record has no context attribute"""
        formatter = StructuredFormatter(use_color=False, include_context=True)
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_func",
        )
        # No context attribute added

        output = formatter.format(record)
        assert "test.module:test_func: Test message" in output
        # Should not fail when context is missing

    def test_formatter_with_exception(self):
        """Test formatter with exception info (line 69)"""
        formatter = StructuredFormatter(use_color=False, include_context=False)

        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.module",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
            func="test_func",
        )

        output = formatter.format(record)
        assert "Error occurred" in output
        assert "ValueError: Test exception" in output
        assert "Traceback" in output

    def test_formatter_color_levels(self):
        """Test different log levels have appropriate colors"""
        with patch.object(sys.stderr, "isatty", return_value=True):
            formatter = StructuredFormatter(use_color=True, include_context=False)

            levels = [
                (logging.DEBUG, "DEBUG"),
                (logging.INFO, "INFO"),
                (logging.WARNING, "WARNING"),
                (logging.ERROR, "ERROR"),
                (logging.CRITICAL, "CRITICAL"),
            ]

            for level, level_name in levels:
                record = logging.LogRecord(
                    name="test.module",
                    level=level,
                    pathname="test.py",
                    lineno=10,
                    msg=f"{level_name} message",
                    args=(),
                    exc_info=None,
                    func="test_func",
                )

                output = formatter.format(record)
                assert level_name in output


class TestCreateLogger:
    """Test create_logger function"""

    def test_create_basic_logger(self):
        """Test creating a basic logger"""
        logger = create_logger("test.basic", level=logging.DEBUG)

        assert logger.name == "test.basic"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1  # Console handler only

    def test_logger_already_has_handlers(self):
        """Test early return when logger already has handlers (line 109)"""
        # Create logger first time
        logger1 = create_logger("test.duplicate", level=logging.INFO)
        handler_count1 = len(logger1.handlers)

        # Try to create same logger again
        logger2 = create_logger("test.duplicate", level=logging.DEBUG)

        # Should be same logger instance
        assert logger1 is logger2
        # Handler count should not increase
        assert len(logger2.handlers) == handler_count1

    def test_create_logger_with_log_file(self, temp_dir):
        """Test creating logger with log file (lines 127-128)"""
        log_file = os.path.join(temp_dir, "subdir", "test.log")
        logger = create_logger("test.file", level=logging.INFO, log_file=log_file)

        assert len(logger.handlers) == 2  # Console and file handler
        # File should be created
        assert os.path.exists(log_file)

        # Test logging to file
        logger.info("Test message")
        with open(log_file) as f:
            content = f.read()
            assert "Test message" in content

    def test_create_logger_with_log_dir(self, temp_dir):
        """Test creating logger with log directory (lines 122-126)"""
        log_dir = os.path.join(temp_dir, "logs")
        logger = create_logger("test.module.sub", level=logging.INFO, log_dir=log_dir)

        assert len(logger.handlers) == 2  # Console and file handler
        # Directory should be created
        assert os.path.exists(log_dir)

        # Log file should be named after the logger with dots replaced
        expected_log_file = os.path.join(log_dir, "test_module_sub.log")
        assert os.path.exists(expected_log_file)

        # Test logging
        logger.warning("Warning message")
        with open(expected_log_file) as f:
            content = f.read()
            assert "Warning message" in content

    def test_create_logger_with_rotation(self, temp_dir):
        """Test log rotation configuration (lines 130-138)"""
        log_file = os.path.join(temp_dir, "rotate.log")
        max_bytes = 1024  # 1KB for testing
        backup_count = 3

        logger = create_logger(
            "test.rotation",
            level=logging.INFO,
            log_file=log_file,
            max_bytes=max_bytes,
            backup_count=backup_count,
        )

        # Verify file handler is RotatingFileHandler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert file_handler.maxBytes == max_bytes
        assert file_handler.backupCount == backup_count

    def test_create_logger_color_control(self):
        """Test color control in logger creation"""
        logger_color = create_logger("test.color", use_color=True)
        logger_no_color = create_logger("test.nocolor", use_color=False)

        # Both should have console handlers
        assert len(logger_color.handlers) >= 1
        assert len(logger_no_color.handlers) >= 1

    def test_create_logger_context_control(self):
        """Test context control in logger creation"""
        logger = create_logger("test.context", include_context=True)

        # Should have console handler with context-enabled formatter
        assert len(logger.handlers) >= 1
        console_handler = logger.handlers[0]
        assert isinstance(console_handler.formatter, StructuredFormatter)
        assert console_handler.formatter.include_context is True


class TestLoggingConfig:
    """Test LoggingConfig class"""

    def test_configure(self):
        """Test configuring global logging settings"""
        LoggingConfig.configure(
            level=logging.DEBUG,
            log_dir="/tmp/logs",
            use_color=False,
            include_context=True,
        )

        assert LoggingConfig._configured is True
        assert LoggingConfig._level == logging.DEBUG
        assert LoggingConfig._log_dir == "/tmp/logs"
        assert LoggingConfig._use_color is False
        assert LoggingConfig._include_context is True

    def test_get_logger_unconfigured(self):
        """Test getting logger when not configured (lines 200-201)"""
        # Ensure not configured
        assert LoggingConfig._configured is False

        logger = LoggingConfig.get_logger("test.unconfigured")

        # Should auto-configure with defaults
        assert LoggingConfig._configured is True
        assert logger.name == "test.unconfigured"

    def test_get_logger_configured(self, temp_dir):
        """Test getting logger when configured (lines 203-210)"""
        LoggingConfig.configure(
            level=logging.WARNING,
            log_dir=temp_dir,
            use_color=False,
        )

        logger = LoggingConfig.get_logger("test.configured")

        assert logger.name == "test.configured"
        assert logger.level == logging.WARNING
        assert "test.configured" in LoggingConfig._loggers

    def test_get_logger_with_level_override(self):
        """Test getting logger with level override"""
        LoggingConfig.configure(level=logging.INFO)

        logger = LoggingConfig.get_logger("test.override", level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_get_logger_cached(self):
        """Test that loggers are cached"""
        logger1 = LoggingConfig.get_logger("test.cached")
        logger2 = LoggingConfig.get_logger("test.cached")

        # Should return same instance
        assert logger1 is logger2

    def test_set_level(self):
        """Test setting logging level for all loggers (lines 217-220)"""
        # Create multiple loggers
        logger1 = LoggingConfig.get_logger("test.logger1")
        logger2 = LoggingConfig.get_logger("test.logger2")

        # Set new level
        LoggingConfig.set_level(logging.ERROR)

        # All loggers and their handlers should have new level
        assert logger1.level == logging.ERROR
        assert logger2.level == logging.ERROR

        for handler in logger1.handlers:
            assert handler.level == logging.ERROR
        for handler in logger2.handlers:
            assert handler.level == logging.ERROR

    def test_set_level_no_loggers(self):
        """Test set_level when no loggers exist"""
        # Should not raise error
        LoggingConfig.set_level(logging.CRITICAL)


class TestGetLogger:
    """Test get_logger convenience function"""

    def test_get_logger_function(self):
        """Test get_logger convenience function"""
        logger = get_logger("test.convenience")

        assert logger.name == "test.convenience"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns cached instances"""
        logger1 = get_logger("test.same")
        logger2 = get_logger("test.same")

        assert logger1 is logger2


class TestInitLoggingFromEnv:
    """Test init_logging_from_env function"""

    def test_init_from_env_defaults(self):
        """Test initialization with default environment variables (lines 247-254)"""
        # Clear any existing env vars
        env_vars = [
            "EMPATHY_LOG_LEVEL",
            "EMPATHY_LOG_DIR",
            "EMPATHY_LOG_COLOR",
            "EMPATHY_LOG_CONTEXT",
        ]
        old_values = {}
        for var in env_vars:
            old_values[var] = os.environ.pop(var, None)

        try:
            init_logging_from_env()

            # Should use defaults
            assert LoggingConfig._configured is True
            assert LoggingConfig._level == logging.INFO
            assert LoggingConfig._log_dir is None
            assert LoggingConfig._use_color is True
            assert LoggingConfig._include_context is False
        finally:
            # Restore env vars
            for var, value in old_values.items():
                if value is not None:
                    os.environ[var] = value

    def test_init_from_env_custom_level(self):
        """Test initialization with custom log level (line 248)"""
        with patch.dict(os.environ, {"EMPATHY_LOG_LEVEL": "DEBUG"}):
            init_logging_from_env()

            assert LoggingConfig._level == logging.DEBUG

    def test_init_from_env_invalid_level(self):
        """Test initialization with invalid log level"""
        with patch.dict(os.environ, {"EMPATHY_LOG_LEVEL": "INVALID"}):
            init_logging_from_env()

            # Should fall back to INFO
            assert LoggingConfig._level == logging.INFO

    def test_init_from_env_log_dir(self):
        """Test initialization with log directory (line 250)"""
        with patch.dict(os.environ, {"EMPATHY_LOG_DIR": "/tmp/test_logs"}):
            init_logging_from_env()

            assert LoggingConfig._log_dir == "/tmp/test_logs"

    def test_init_from_env_color_false(self):
        """Test initialization with color disabled (line 251)"""
        with patch.dict(os.environ, {"EMPATHY_LOG_COLOR": "false"}):
            init_logging_from_env()

            assert LoggingConfig._use_color is False

    def test_init_from_env_color_true(self):
        """Test initialization with color enabled"""
        with patch.dict(os.environ, {"EMPATHY_LOG_COLOR": "true"}):
            init_logging_from_env()

            assert LoggingConfig._use_color is True

    def test_init_from_env_context_true(self):
        """Test initialization with context enabled (line 252)"""
        with patch.dict(os.environ, {"EMPATHY_LOG_CONTEXT": "true"}):
            init_logging_from_env()

            assert LoggingConfig._include_context is True

    def test_init_from_env_context_false(self):
        """Test initialization with context disabled"""
        with patch.dict(os.environ, {"EMPATHY_LOG_CONTEXT": "false"}):
            init_logging_from_env()

            assert LoggingConfig._include_context is False

    def test_init_from_env_all_settings(self, temp_dir):
        """Test initialization with all environment variables set"""
        env_settings = {
            "EMPATHY_LOG_LEVEL": "WARNING",
            "EMPATHY_LOG_DIR": temp_dir,
            "EMPATHY_LOG_COLOR": "false",
            "EMPATHY_LOG_CONTEXT": "true",
        }

        with patch.dict(os.environ, env_settings):
            init_logging_from_env()

            assert LoggingConfig._level == logging.WARNING
            assert LoggingConfig._log_dir == temp_dir
            assert LoggingConfig._use_color is False
            assert LoggingConfig._include_context is True


class TestIntegration:
    """Integration tests for logging configuration"""

    def test_full_logging_workflow(self, temp_dir):
        """Test complete logging workflow"""
        # Configure
        LoggingConfig.configure(
            level=logging.DEBUG,
            log_dir=temp_dir,
            use_color=False,
            include_context=True,
        )

        # Get logger
        logger = get_logger("test.integration")

        # Log messages
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Check log file
        log_file = os.path.join(temp_dir, "test_integration.log")
        assert os.path.exists(log_file)

        with open(log_file) as f:
            content = f.read()
            assert "Debug message" in content
            assert "Info message" in content
            assert "Warning message" in content
            assert "Error message" in content

    def test_multiple_loggers_same_config(self, temp_dir):
        """Test multiple loggers share configuration"""
        LoggingConfig.configure(level=logging.INFO, log_dir=temp_dir)

        logger1 = get_logger("test.multi1")
        logger2 = get_logger("test.multi2")

        # Both should be at INFO level
        assert logger1.level == logging.INFO
        assert logger2.level == logging.INFO

        # Change level globally
        LoggingConfig.set_level(logging.ERROR)

        # Both should update
        assert logger1.level == logging.ERROR
        assert logger2.level == logging.ERROR

    def test_logger_with_exception_logging(self, temp_dir):
        """Test logging exceptions with full traceback"""
        logger = create_logger("test.exception", log_file=os.path.join(temp_dir, "exc.log"))

        try:
            raise RuntimeError("Test error")
        except RuntimeError:
            logger.exception("An error occurred")

        log_file = os.path.join(temp_dir, "exc.log")
        with open(log_file) as f:
            content = f.read()
            assert "An error occurred" in content
            assert "RuntimeError: Test error" in content
            assert "Traceback" in content
