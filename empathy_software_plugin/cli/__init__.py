"""CLI tools for the Empathy Software Plugin.

This package exists alongside a legacy ``cli.py`` module at the
package root. To maintain backwards compatibility with existing
callers and tests, we dynamically import the root ``cli.py`` and
re-export its public API from here.

Tests also expect a couple of small helper functions to exist at the
package level:

* ``get_logger()`` – returns the configured logger instance
* ``get_global_registry()`` – indirection around the plugin registry

These helpers make the CLI easier to patch in tests while keeping the
core implementation in the shared registry module.
"""

import importlib.util
import os

from .inspect import main as inspect_main

# Re-export from parent cli.py module for backwards compatibility
# This handles the cli/ package shadowing the cli.py file
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_cli_module_path = os.path.join(_parent_dir, "cli.py")

logger = None  # Will be populated if cli.py is found
Colors = None  # type: ignore[assignment]
analyze_project = None  # type: ignore[assignment]
display_wizard_results = None  # type: ignore[assignment]
gather_project_context = None  # type: ignore[assignment]
list_wizards = None  # type: ignore[assignment]
main = None  # type: ignore[assignment]
scan_command = None  # type: ignore[assignment]
wizard_info = None  # type: ignore[assignment]
print_header = None  # type: ignore[assignment]
print_alert = None  # type: ignore[assignment]
print_success = None  # type: ignore[assignment]
print_error = None  # type: ignore[assignment]
print_info = None  # type: ignore[assignment]
print_summary = None  # type: ignore[assignment]
parse_ai_calls = None  # type: ignore[assignment]
parse_git_history = None  # type: ignore[assignment]
prepare_wizard_context = None  # type: ignore[assignment]
get_global_registry = None  # type: ignore[assignment]
_cli_module = None  # Reference to loaded cli.py module


if os.path.exists(_cli_module_path):
    _spec = importlib.util.spec_from_file_location("_cli_module", _cli_module_path)
    if _spec is not None and _spec.loader is not None:
        _cli_module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_cli_module)

        # Re-export all items from cli.py
        logger = _cli_module.logger
        Colors = _cli_module.Colors
        analyze_project = _cli_module.analyze_project
        display_wizard_results = _cli_module.display_wizard_results
        gather_project_context = _cli_module.gather_project_context
        list_wizards = _cli_module.list_wizards
        main = _cli_module.main
        scan_command = _cli_module.scan_command
        wizard_info = _cli_module.wizard_info
        print_header = _cli_module.print_header
        print_alert = _cli_module.print_alert
        print_success = _cli_module.print_success
        print_error = _cli_module.print_error
        print_info = _cli_module.print_info
        print_summary = _cli_module.print_summary
        parse_ai_calls = _cli_module.parse_ai_calls
        parse_git_history = _cli_module.parse_git_history
        prepare_wizard_context = _cli_module.prepare_wizard_context
        # Re-export get_global_registry from cli.py so patches work correctly
        get_global_registry = _cli_module.get_global_registry

        # CRITICAL: For patches to work, we need to make the cli.py module's
        # functions point to THIS module's versions.
        # This allows tests to patch empathy_software_plugin.cli.{function}
        # and have it affect calls from main() and other functions.
        import sys

        _this_module = sys.modules[__name__]

        def _patchable_get_global_registry():
            """Wrapper that calls whatever is currently bound to this module's get_global_registry."""
            return _this_module.get_global_registry()

        async def _patchable_analyze_project(*args, **kwargs):
            """Wrapper that calls whatever is currently bound to this module's analyze_project."""
            return await _this_module.analyze_project(*args, **kwargs)

        def _patchable_list_wizards(*args, **kwargs):
            """Wrapper that calls whatever is currently bound to this module's list_wizards."""
            return _this_module.list_wizards(*args, **kwargs)

        def _patchable_wizard_info(*args, **kwargs):
            """Wrapper that calls whatever is currently bound to this module's wizard_info."""
            return _this_module.wizard_info(*args, **kwargs)

        _cli_module.get_global_registry = _patchable_get_global_registry  # type: ignore[attr-defined]
        _cli_module.analyze_project = _patchable_analyze_project  # type: ignore[attr-defined]
        _cli_module.list_wizards = _patchable_list_wizards  # type: ignore[attr-defined]
        _cli_module.wizard_info = _patchable_wizard_info  # type: ignore[attr-defined]


def get_logger():
    """Return the CLI logger instance.

    This thin wrapper exists so tests can patch the logger via
    ``empathy_software_plugin.cli.get_logger`` without reaching into
    the underlying implementation module.
    """

    return logger


__all__ = [
    "inspect_main",
    "logger",
    "Colors",
    "analyze_project",
    "display_wizard_results",
    "gather_project_context",
    "list_wizards",
    "main",
    "scan_command",
    "wizard_info",
    "print_header",
    "print_alert",
    "print_success",
    "print_error",
    "print_info",
    "print_summary",
    "parse_ai_calls",
    "parse_git_history",
    "prepare_wizard_context",
    "get_logger",
    "get_global_registry",
]
