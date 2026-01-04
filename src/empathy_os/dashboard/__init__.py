"""Visual Dashboard for Empathy Framework

Web-based view of patterns, costs, and health trends.

Usage:
    empathy dashboard
    # Opens browser to http://localhost:8765

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_os.dashboard.server import cmd_dashboard, run_dashboard

__all__ = ["cmd_dashboard", "run_dashboard"]
