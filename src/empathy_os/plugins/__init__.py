"""
Empathy Framework - Plugin System

Enables modular extension of the Empathy Framework with domain-specific plugins.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from .base import (
    BasePlugin,
    BaseWizard,
    PluginError,
    PluginLoadError,
    PluginMetadata,
    PluginValidationError,
)
from .registry import PluginRegistry, get_global_registry

__all__ = [
    "BaseWizard",
    "BasePlugin",
    "PluginMetadata",
    "PluginError",
    "PluginLoadError",
    "PluginValidationError",
    "PluginRegistry",
    "get_global_registry",
]
