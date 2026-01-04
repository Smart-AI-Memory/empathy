"""Empathy LLM Toolkit

Wraps LLM providers (OpenAI, Anthropic, local models) with Empathy Framework levels.

Enables progression from Level 1 (reactive) to Level 4 (anticipatory) AI collaboration
with any LLM backend.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .core import EmpathyLLM
from .levels import EmpathyLevel
from .providers import AnthropicProvider, GeminiProvider, LocalProvider, OpenAIProvider
from .state import CollaborationState, UserPattern

__version__ = "1.9.5"

__all__ = [
    "AnthropicProvider",
    "CollaborationState",
    "EmpathyLLM",
    "EmpathyLevel",
    "GeminiProvider",
    "LocalProvider",
    "OpenAIProvider",
    "UserPattern",
]
