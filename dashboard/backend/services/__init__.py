"""Service layer for Empathy Memory Dashboard API.

Provides business logic and async wrappers for memory operations.
"""

from .memory_service import MemoryService, get_memory_service

__all__ = ["MemoryService", "get_memory_service"]
