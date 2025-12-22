"""
Dashboard Server for Empathy Framework

Lightweight web server for viewing patterns, costs, and health.
Uses built-in http.server to avoid external dependencies.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import http.server
import json
import socketserver
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Try to import optional dependencies
try:
    from empathy_os.cost_tracker import CostTracker

    HAS_COST_TRACKER = True
except ImportError:
    CostTracker = None  # type: ignore[misc, assignment]
    HAS_COST_TRACKER = False

try:
    from empathy_os.discovery import DiscoveryEngine

    HAS_DISCOVERY = True
except ImportError:
    DiscoveryEngine = None  # type: ignore[misc, assignment]
    HAS_DISCOVERY = False

try:
    from empathy_os.workflows import get_workflow_stats, list_workflows

    HAS_WORKFLOWS = True
except ImportError:
    get_workflow_stats = None  # type: ignore[misc, assignment]
    list_workflows = None  # type: ignore[misc, assignment]
    HAS_WORKFLOWS = False


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    patterns_dir = "./patterns"
    empathy_dir = ".empathy"

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_dashboard()
        elif path == "/api/patterns":
            self._serve_patterns()
        elif path == "/api/costs":
            self._serve_costs()
        elif path == "/api/stats":
            self._serve_stats()
        elif path == "/api/health":
            self._serve_health()
        elif path == "/api/workflows":
            self._serve_workflows()
        else:
            self.send_error(404, "Not Found")

    def _serve_dashboard(self):
        """Serve the main dashboard HTML."""
        html = self._generate_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", len(html))
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_patterns(self):
        """Serve patterns as JSON."""
        patterns = self._load_patterns()
        self._send_json(patterns)

    def _serve_costs(self):
        """Serve cost data as JSON."""
        if HAS_COST_TRACKER and CostTracker is not None:
            tracker = CostTracker(self.empathy_dir)
            data = tracker.get_summary(30)
        else:
            data = {"error": "Cost tracking not available"}
        self._send_json(data)

    def _serve_stats(self):
        """Serve discovery stats as JSON."""
        if HAS_DISCOVERY and DiscoveryEngine is not None:
            engine = DiscoveryEngine(self.empathy_dir)
            data = engine.get_stats()
        else:
            data = {"error": "Discovery not available"}
        self._send_json(data)

    def _serve_health(self):
        """Serve health check."""
        self._send_json({"status": "healthy", "timestamp": datetime.now().isoformat()})

    def _serve_workflows(self):
        """Serve workflow stats as JSON."""
        if HAS_WORKFLOWS and get_workflow_stats is not None:
            data = get_workflow_stats()
            # Add available workflows
            if list_workflows is not None:
                data["available_workflows"] = list_workflows()
        else:
            data = {"error": "Workflows not available"}
        self._send_json(data)

    def _send_json(self, data):
        """Send JSON response."""
        content = json.dumps(data, indent=2, default=str)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content.encode())

    def _load_patterns(self) -> dict:
        """Load patterns from disk."""
        patterns = {
            "debugging": [],
            "security": [],
            "tech_debt": {"snapshots": []},
            "inspection": [],
        }

        patterns_path = Path(self.patterns_dir)
        if not patterns_path.exists():
            return patterns

        for name in ["debugging", "security", "tech_debt", "inspection"]:
            file_path = patterns_path / f"{name}.json"
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        patterns[name] = data
                except (OSError, json.JSONDecodeError):
                    pass

        return patterns

    def _generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML page."""
        patterns = self._load_patterns()

        # Count patterns (handle both dict and list formats)
        debugging_data = patterns.get("debugging", {})
        if isinstance(debugging_data, dict):
            bug_count = len(debugging_data.get("patterns", []))
        else:
            bug_count = len(debugging_data) if isinstance(debugging_data, list) else 0

        security_data = patterns.get("security", {})
        if isinstance(security_data, dict):
            security_count = len(security_data.get("decisions", []))
        else:
            security_count = len(security_data) if isinstance(security_data, list) else 0

        debt_items = 0
        tech_debt_data = patterns.get("tech_debt", {})
        if isinstance(tech_debt_data, dict):
            snapshots = tech_debt_data.get("snapshots", [])
            if snapshots:
                debt_items = snapshots[-1].get("total_items", 0)

        # Get cost summary
        cost_summary = {"savings": 0, "savings_percent": 0, "requests": 0}
        if CostTracker is not None:
            try:
                tracker = CostTracker(self.empathy_dir)
                cost_summary = tracker.get_summary(30)
            except Exception:
                pass

        # Get workflow stats
        workflow_stats = {
            "total_runs": 0,
            "by_workflow": {},
            "by_tier": {"cheap": 0, "capable": 0, "premium": 0},
            "recent_runs": [],
            "total_savings": 0.0,
            "avg_savings_percent": 0.0,
        }
        if HAS_WORKFLOWS and get_workflow_stats is not None:
            try:
                workflow_stats = get_workflow_stats()
            except Exception:
                pass

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empathy Framework Dashboard</title>
    <style>
        :root {{
            --primary: #4f46e5;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f3f4f6;
            --card-bg: #ffffff;
            --text: #1f2937;
            --text-muted: #6b7280;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}

        h1 {{
            color: var(--primary);
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: var(--text-muted);
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .card h2 {{
            font-size: 0.875rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text);
        }}

        .card .label {{
            color: var(--text-muted);
            font-size: 0.875rem;
        }}

        .card.success .value {{
            color: var(--success);
        }}

        .card.warning .value {{
            color: var(--warning);
        }}

        .section {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: var(--text);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid var(--bg);
        }}

        th {{
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.875rem;
        }}

        .status {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .status.resolved {{
            background: #d1fae5;
            color: #065f46;
        }}

        .status.investigating {{
            background: #fef3c7;
            color: #92400e;
        }}

        .commands {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}

        .command {{
            background: var(--bg);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.875rem;
        }}

        .workflow-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .workflow-card {{
            background: var(--bg);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}

        .workflow-card h3 {{
            font-size: 0.875rem;
            color: var(--text);
            margin-bottom: 0.5rem;
        }}

        .workflow-card .runs {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary);
        }}

        .workflow-card .savings {{
            font-size: 0.875rem;
            color: var(--success);
        }}

        .tier-bar {{
            display: flex;
            height: 24px;
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }}

        .tier-bar .tier {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 500;
            color: white;
        }}

        .tier-bar .cheap {{ background: #10b981; }}
        .tier-bar .capable {{ background: #3b82f6; }}
        .tier-bar .premium {{ background: #8b5cf6; }}

        .recent-run {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--bg);
        }}

        .recent-run:last-child {{
            border-bottom: none;
        }}

        .recent-run .name {{
            font-weight: 500;
            min-width: 100px;
        }}

        .recent-run .provider {{
            font-size: 0.75rem;
            color: var(--text-muted);
            background: var(--bg);
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
        }}

        .recent-run .result {{
            margin-left: auto;
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .recent-run .savings-badge {{
            font-size: 0.75rem;
            color: var(--success);
            font-weight: 500;
        }}

        .recent-run .time {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
            padding: 2rem 0;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #111827;
                --card-bg: #1f2937;
                --text: #f9fafb;
                --text-muted: #9ca3af;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Empathy Framework Dashboard</h1>
            <p class="subtitle">Pattern learning and cost optimization at a glance</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2>Bug Patterns</h2>
                <div class="value">{bug_count}</div>
                <div class="label">patterns learned</div>
            </div>

            <div class="card">
                <h2>Security Decisions</h2>
                <div class="value">{security_count}</div>
                <div class="label">documented</div>
            </div>

            <div class="card warning">
                <h2>Tech Debt Items</h2>
                <div class="value">{debt_items}</div>
                <div class="label">tracked</div>
            </div>

            <div class="card">
                <h2>Workflow Runs</h2>
                <div class="value">{workflow_stats.get("total_runs", 0)}</div>
                <div class="label">{workflow_stats.get("avg_savings_percent", 0):.0f}% avg savings</div>
            </div>

            <div class="card success">
                <h2>Total Savings</h2>
                <div class="value">${workflow_stats.get("total_savings", 0) + cost_summary.get("savings", 0):.2f}</div>
                <div class="label">workflows + API</div>
            </div>
        </div>

        <div class="section">
            <h2>Recent Bug Patterns</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Root Cause</th>
                        <th>Status</th>
                        <th>Resolved</th>
                    </tr>
                </thead>
                <tbody>
                    {self._render_bug_table(patterns)}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Multi-Model Workflows</h2>
            <div class="workflow-grid">
                {self._render_workflow_cards(workflow_stats)}
            </div>

            <h3 style="margin-bottom: 0.5rem; font-size: 1rem;">Model Tier Usage</h3>
            {self._render_tier_bar(workflow_stats)}

            <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1rem;">Recent Runs</h3>
            {self._render_recent_runs(workflow_stats)}
        </div>

        <div class="section">
            <h2>Quick Commands</h2>
            <p>Run these commands for common tasks:</p>
            <div class="commands">
                <span class="command">empathy morning</span>
                <span class="command">empathy ship</span>
                <span class="command">empathy fix-all</span>
                <span class="command">empathy learn</span>
                <span class="command">empathy sync-claude</span>
                <span class="command">empathy costs</span>
            </div>
        </div>

        <footer>
            <p>Empathy Framework Dashboard - Refresh to update data</p>
            <p>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>"""

    def _render_bug_table(self, patterns: dict) -> str:
        """Render bug patterns as table rows."""
        debugging_data = patterns.get("debugging", {})
        if isinstance(debugging_data, dict):
            bugs = debugging_data.get("patterns", [])
        elif isinstance(debugging_data, list):
            bugs = debugging_data
        else:
            bugs = []
        if not bugs:
            return (
                '<tr><td colspan="4">No patterns yet. Run "empathy learn" to get started.</td></tr>'
            )

        rows = []
        for bug in bugs[-10:]:  # Last 10
            status_class = bug.get("status", "investigating")
            rows.append(
                f"""
                <tr>
                    <td>{bug.get("bug_type", "unknown")}</td>
                    <td>{(bug.get("root_cause", "")[:60] + "...") if len(bug.get("root_cause", "")) > 60 else bug.get("root_cause", "-")}</td>
                    <td><span class="status {status_class}">{status_class}</span></td>
                    <td>{bug.get("resolved_at", bug.get("timestamp", "-"))[:10] if bug.get("resolved_at") or bug.get("timestamp") else "-"}</td>
                </tr>
            """
            )

        return "".join(rows)

    def _render_workflow_cards(self, workflow_stats: dict) -> str:
        """Render workflow stat cards."""
        by_workflow = workflow_stats.get("by_workflow", {})

        if not by_workflow:
            return '<div class="workflow-card"><p style="color: var(--text-muted);">No workflow runs yet. Try: empathy workflow run research</p></div>'

        cards = []
        for name, stats in by_workflow.items():
            runs = stats.get("runs", 0)
            savings = stats.get("savings", 0)
            cards.append(
                f"""
                <div class="workflow-card">
                    <h3>{name}</h3>
                    <div class="runs">{runs}</div>
                    <div class="savings">${savings:.4f} saved</div>
                </div>
            """
            )

        return "".join(cards)

    def _render_tier_bar(self, workflow_stats: dict) -> str:
        """Render model tier usage bar."""
        by_tier = workflow_stats.get("by_tier", {})
        total = sum(by_tier.values())

        if total == 0:
            return '<div class="tier-bar"><div class="tier" style="width: 100%; background: var(--bg); color: var(--text-muted);">No data yet</div></div>'

        cheap_pct = (by_tier.get("cheap", 0) / total) * 100 if total > 0 else 0
        capable_pct = (by_tier.get("capable", 0) / total) * 100 if total > 0 else 0
        premium_pct = (by_tier.get("premium", 0) / total) * 100 if total > 0 else 0

        return f"""
            <div class="tier-bar">
                <div class="tier cheap" style="width: {cheap_pct}%;">{cheap_pct:.0f}% cheap</div>
                <div class="tier capable" style="width: {capable_pct}%;">{capable_pct:.0f}% capable</div>
                <div class="tier premium" style="width: {premium_pct}%;">{premium_pct:.0f}% premium</div>
            </div>
            <div style="display: flex; gap: 1rem; font-size: 0.75rem; color: var(--text-muted);">
                <span>Cheap (Haiku/GPT-mini): ${by_tier.get("cheap", 0):.4f}</span>
                <span>Capable (Sonnet/GPT-4o): ${by_tier.get("capable", 0):.4f}</span>
                <span>Premium (Opus/GPT-5): ${by_tier.get("premium", 0):.4f}</span>
            </div>
        """

    def _render_recent_runs(self, workflow_stats: dict) -> str:
        """Render recent workflow runs."""
        recent_runs = workflow_stats.get("recent_runs", [])

        if not recent_runs:
            return '<p style="color: var(--text-muted);">No recent workflow runs.</p>'

        runs_html = []
        for run in recent_runs[:5]:  # Show last 5
            name = run.get("workflow", "unknown")
            provider = run.get("provider", "unknown")
            success = run.get("success", False)
            savings_pct = run.get("savings_percent", 0)
            started = run.get("started_at", "")

            # Format time
            time_str = started[:16].replace("T", " ") if started else "-"

            status_icon = "&#10003;" if success else "&#10007;"
            status_color = "var(--success)" if success else "var(--danger)"

            runs_html.append(
                f"""
                <div class="recent-run">
                    <span style="color: {status_color};">{status_icon}</span>
                    <span class="name">{name}</span>
                    <span class="provider">{provider}</span>
                    <span class="result">
                        <span class="savings-badge">{savings_pct:.0f}% saved</span>
                        <span class="time">{time_str}</span>
                    </span>
                </div>
            """
            )

        return "".join(runs_html)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded HTTP server."""

    allow_reuse_address = True


def run_dashboard(
    port: int = 8765,
    patterns_dir: str = "./patterns",
    empathy_dir: str = ".empathy",
    open_browser: bool = True,
) -> None:
    """
    Run the dashboard server.

    Args:
        port: Port to run on (default: 8765)
        patterns_dir: Path to patterns directory
        empathy_dir: Path to empathy data directory
        open_browser: Open browser automatically
    """
    # Configure handler
    DashboardHandler.patterns_dir = patterns_dir
    DashboardHandler.empathy_dir = empathy_dir

    url = f"http://localhost:{port}"

    print("\n  Empathy Dashboard")
    print(f"  Running at: {url}")
    print("  Press Ctrl+C to stop\n")

    if open_browser:
        # Open browser in a separate thread to not block server start
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        with ThreadedHTTPServer(("", port), DashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")


def cmd_dashboard(args):
    """CLI command handler for dashboard."""
    port = getattr(args, "port", 8765)
    patterns_dir = getattr(args, "patterns_dir", "./patterns")
    empathy_dir = getattr(args, "empathy_dir", ".empathy")
    no_browser = getattr(args, "no_browser", False)

    run_dashboard(
        port=port, patterns_dir=patterns_dir, empathy_dir=empathy_dir, open_browser=not no_browser
    )
    return 0
