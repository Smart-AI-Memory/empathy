"""
Empathy LLM Toolkit

Wraps LLM providers (OpenAI, Anthropic, local models) with Empathy Framework levels.

Enables progression from Level 1 (reactive) to Level 4 (anticipatory) AI collaboration
with any LLM backend.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from .core import EmpathyLLM
from .levels import EmpathyLevel
from .providers import AnthropicProvider, LocalProvider, OpenAIProvider
from .state import CollaborationState, UserPattern

__version__ = "1.0.0"

__all__ = [
    "EmpathyLLM",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalProvider",
    "CollaborationState",
    "UserPattern",
    "EmpathyLevel",
]
