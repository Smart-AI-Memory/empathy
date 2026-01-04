"""Empathy Memory Dashboard API

FastAPI backend for managing and monitoring the Empathy Framework memory system.

Main components:
- FastAPI application with REST endpoints
- WebSocket for real-time metrics
- Memory service layer
- Pydantic schemas for validation
- Structured logging

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

__version__ = "1.0.0"
__author__ = "Smart AI Memory, LLC"

from .main import app

__all__ = ["app"]
