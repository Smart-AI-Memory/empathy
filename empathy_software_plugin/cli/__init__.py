"""
CLI Tools for Empathy Software Plugin

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import importlib.util
import os

from .inspect import main as inspect_main

# Re-export from parent cli.py module for backwards compatibility
# This handles the cli/ package shadowing the cli.py file
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_cli_module_path = os.path.join(_parent_dir, "cli.py")

if os.path.exists(_cli_module_path):
    _spec = importlib.util.spec_from_file_location("_cli_module", _cli_module_path)
    _cli_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_cli_module)

    # Re-export all items from cli.py
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

    __all__ = [
        "inspect_main",
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
    ]
else:
    __all__ = ["inspect_main"]
