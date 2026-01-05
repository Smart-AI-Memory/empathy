"""Keyboard Shortcuts Workflow Package

Generates optimized keyboard shortcuts for any project following
the "Keyboard Conductor" musical scale pattern.

Features:
- Multi-source feature discovery (VSCode, Python, YAML, LLM)
- Multi-layout generation (QWERTY, Dvorak, Colemak)
- Ergonomic optimization with mnemonic phrases
- Multiple output formats (keybindings, aliases, documentation)
"""

from .generators import CLIAliasGenerator, MarkdownDocGenerator, VSCodeKeybindingsGenerator
from .parsers import (
    FeatureParser,
    LLMFeatureAnalyzer,
    PyProjectParser,
    VSCodeCommandParser,
    YAMLManifestParser,
)
from .schema import Category, Feature, FeatureManifest, LayoutConfig, ShortcutAssignment
from .workflow import KeyboardShortcutWorkflow

__all__ = [
    "CLIAliasGenerator",
    "Category",
    "Feature",
    "FeatureManifest",
    "FeatureParser",
    "KeyboardShortcutWorkflow",
    "LLMFeatureAnalyzer",
    "LayoutConfig",
    "MarkdownDocGenerator",
    "PyProjectParser",
    "ShortcutAssignment",
    "VSCodeCommandParser",
    "VSCodeKeybindingsGenerator",
    "YAMLManifestParser",
]
