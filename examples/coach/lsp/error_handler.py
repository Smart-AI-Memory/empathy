"""
Error Handling for LSP Server
Comprehensive error handling and recovery
"""

import logging
import traceback
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Error codes for Coach LSP"""
    # LSP standard error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Coach-specific error codes
    WIZARD_NOT_FOUND = -32001
    WIZARD_EXECUTION_FAILED = -32002
    CONTEXT_COLLECTION_FAILED = -32003
    CACHE_ERROR = -32004
    COACH_ENGINE_ERROR = -32005
    LANGCHAIN_ERROR = -32006
    LLM_API_ERROR = -32007


class CoachLSPError(Exception):
    """Base exception for Coach LSP errors"""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to LSP error response format"""
        return {
            "code": self.code.value,
            "message": self.message,
            "data": self.data
        }


class WizardNotFoundError(CoachLSPError):
    """Wizard with specified name not found"""

    def __init__(self, wizard_name: str):
        super().__init__(
            message=f"Wizard '{wizard_name}' not found",
            code=ErrorCode.WIZARD_NOT_FOUND,
            data={"wizard_name": wizard_name}
        )


class WizardExecutionError(CoachLSPError):
    """Wizard execution failed"""

    def __init__(self, wizard_name: str, reason: str):
        super().__init__(
            message=f"Wizard '{wizard_name}' execution failed: {reason}",
            code=ErrorCode.WIZARD_EXECUTION_FAILED,
            data={"wizard_name": wizard_name, "reason": reason}
        )


class ContextCollectionError(CoachLSPError):
    """Failed to collect IDE context"""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Failed to collect context: {reason}",
            code=ErrorCode.CONTEXT_COLLECTION_FAILED,
            data={"reason": reason}
        )


class LLMAPIError(CoachLSPError):
    """LLM API call failed"""

    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"LLM API error ({provider}): {reason}",
            code=ErrorCode.LLM_API_ERROR,
            data={"provider": provider, "reason": reason}
        )


def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Handle and log errors consistently

    Args:
        error: The exception that occurred
        context: Additional context about where error occurred

    Returns:
        Error response dict suitable for LSP
    """
    # Log full traceback
    logger.error(f"Error in {context}: {error}")
    logger.debug(traceback.format_exc())

    # Convert to CoachLSPError if needed
    if not isinstance(error, CoachLSPError):
        error = CoachLSPError(
            message=str(error),
            code=ErrorCode.INTERNAL_ERROR,
            data={"context": context, "type": type(error).__name__}
        )

    return error.to_dict()


def safe_execute(func, *args, fallback=None, context="", **kwargs):
    """
    Safely execute a function with error handling

    Args:
        func: Function to execute
        *args: Positional arguments
        fallback: Value to return on error
        context: Context description for logging
        **kwargs: Keyword arguments

    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {context or func.__name__}: {e}")
        logger.debug(traceback.format_exc())
        return fallback


async def safe_execute_async(func, *args, fallback=None, context="", **kwargs):
    """Async version of safe_execute"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {context or func.__name__}: {e}")
        logger.debug(traceback.format_exc())
        return fallback


class ErrorRecovery:
    """Error recovery strategies"""

    @staticmethod
    def retry_with_backoff(func, max_retries=3, initial_delay=1.0):
        """Retry function with exponential backoff"""
        import time

        delay = initial_delay
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2

    @staticmethod
    async def retry_with_backoff_async(func, max_retries=3, initial_delay=1.0):
        """Async retry with exponential backoff"""
        import asyncio

        delay = initial_delay
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2

    @staticmethod
    def fallback_to_cache(cache, key, func, *args, **kwargs):
        """Try function, fall back to cache on error"""
        try:
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        except Exception as e:
            logger.warning(f"Function failed, checking cache: {e}")
            cached = cache.get(key)
            if cached:
                logger.info("Using cached result")
                return cached
            raise
