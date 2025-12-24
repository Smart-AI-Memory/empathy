"""
Unified CLI for Empathy Framework

A single entry point for all Empathy Framework commands using Typer.

Usage:
    empathy --help                    # Show all commands
    empathy memory status             # Memory control panel
    empathy provider                  # Show provider config
    empathy scan .                    # Scan codebase
    empathy morning                   # Start-of-day briefing

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import subprocess
import sys
from importlib.metadata import version as get_version
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

# Create the main Typer app
app = typer.Typer(
    name="empathy",
    help="Empathy Framework - Predictive AI-Developer Collaboration",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def get_empathy_version() -> str:
    """Get the installed version of empathy-framework."""
    try:
        return get_version("empathy-framework")
    except Exception:
        return "dev"


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]Empathy Framework[/bold blue] v{get_empathy_version()}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    Empathy Framework - Predictive AI-Developer Collaboration

    The AI collaboration framework that predicts problems before they happen.

    [bold]Quick Start:[/bold]
        empathy morning         Start-of-day briefing
        empathy health          Quick health check
        empathy ship            Pre-commit validation

    [bold]Memory:[/bold]
        empathy memory status   Check memory system status
        empathy memory start    Start Redis server

    [bold]Provider:[/bold]
        empathy provider        Show current provider config
        empathy provider --set hybrid   Configure provider

    [bold]Inspection:[/bold]
        empathy scan .          Scan codebase for issues
        empathy inspect .       Deep inspection with SARIF output
    """
    pass


# =============================================================================
# MEMORY SUBCOMMAND GROUP
# =============================================================================

memory_app = typer.Typer(help="Memory system control panel")
app.add_typer(memory_app, name="memory")


@memory_app.command("status")
def memory_status():
    """Check memory system status (Redis, patterns, stats)."""
    # Delegate to the existing CLI
    subprocess.run([sys.executable, "-m", "empathy_os.memory.control_panel", "status"])


@memory_app.command("start")
def memory_start():
    """Start Redis server for short-term memory."""
    subprocess.run([sys.executable, "-m", "empathy_os.memory.control_panel", "start"])


@memory_app.command("stop")
def memory_stop():
    """Stop Redis server."""
    subprocess.run([sys.executable, "-m", "empathy_os.memory.control_panel", "stop"])


@memory_app.command("stats")
def memory_stats():
    """Show memory statistics."""
    subprocess.run([sys.executable, "-m", "empathy_os.memory.control_panel", "stats"])


@memory_app.command("patterns")
def memory_patterns():
    """List stored patterns."""
    subprocess.run([sys.executable, "-m", "empathy_os.memory.control_panel", "patterns", "--list"])


# =============================================================================
# PROVIDER SUBCOMMAND GROUP
# =============================================================================

provider_app = typer.Typer(help="Multi-model provider configuration")
app.add_typer(provider_app, name="provider")


@provider_app.callback(invoke_without_command=True)
def provider_show(
    ctx: typer.Context,
    set_provider: str | None = typer.Option(
        None, "--set", "-s", help="Set provider (anthropic, openai, ollama, hybrid)"
    ),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive setup wizard"),
    format_out: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
):
    """Show or configure provider settings."""
    if ctx.invoked_subcommand is not None:
        return

    args = [sys.executable, "-m", "empathy_os.models.cli", "provider"]
    if set_provider:
        args.extend(["--set", set_provider])
    if interactive:
        args.append("--interactive")
    if format_out != "table":
        args.extend(["-f", format_out])

    subprocess.run(args)


@provider_app.command("registry")
def provider_registry(
    provider_filter: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
):
    """Show all available models in the registry."""
    args = [sys.executable, "-m", "empathy_os.models.cli", "registry"]
    if provider_filter:
        args.extend(["--provider", provider_filter])
    subprocess.run(args)


@provider_app.command("costs")
def provider_costs(
    input_tokens: int = typer.Option(10000, "--input-tokens", "-i", help="Input tokens"),
    output_tokens: int = typer.Option(2000, "--output-tokens", "-o", help="Output tokens"),
):
    """Estimate costs for token usage."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "costs",
            "--input-tokens",
            str(input_tokens),
            "--output-tokens",
            str(output_tokens),
        ]
    )


@provider_app.command("telemetry")
def provider_telemetry(
    summary: bool = typer.Option(False, "--summary", help="Show summary"),
    costs: bool = typer.Option(False, "--costs", help="Show cost breakdown"),
    providers: bool = typer.Option(False, "--providers", help="Show provider usage"),
):
    """View telemetry and analytics."""
    args = [sys.executable, "-m", "empathy_os.models.cli", "telemetry"]
    if summary:
        args.append("--summary")
    if costs:
        args.append("--costs")
    if providers:
        args.append("--providers")
    subprocess.run(args)


# =============================================================================
# SCAN COMMAND
# =============================================================================


@app.command("scan")
def scan(
    path: Path = typer.Argument(Path("."), help="Path to scan"),
    format_out: str = typer.Option(
        "text", "--format", "-f", help="Output format (text, json, sarif)"
    ),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix safe issues"),
    staged: bool = typer.Option(False, "--staged", help="Only scan staged changes"),
):
    """Scan codebase for issues."""
    args = ["empathy-scan", str(path)]
    if format_out != "text":
        args.extend(["--format", format_out])
    if fix:
        args.append("--fix")
    if staged:
        args.append("--staged")

    result = subprocess.run(args, capture_output=False)
    if result.returncode != 0:
        console.print("[yellow]Note: empathy-scan may not be installed[/yellow]")
        console.print("Install with: pip install empathy-framework[software]")


# =============================================================================
# INSPECT COMMAND
# =============================================================================


@app.command("inspect")
def inspect_cmd(
    path: Path = typer.Argument(Path("."), help="Path to inspect"),
    format_out: str = typer.Option(
        "text", "--format", "-f", help="Output format (text, json, sarif)"
    ),
):
    """Deep inspection with code analysis."""
    args = ["empathy-inspect", str(path)]
    if format_out != "text":
        args.extend(["--format", format_out])

    result = subprocess.run(args, capture_output=False)
    if result.returncode != 0:
        console.print("[yellow]Note: empathy-inspect may not be installed[/yellow]")
        console.print("Install with: pip install empathy-framework[software]")


# =============================================================================
# SYNC-CLAUDE COMMAND
# =============================================================================


@app.command("sync-claude")
def sync_claude(
    source: str = typer.Option(
        "patterns", "--source", "-s", help="Source to sync (patterns, bugs)"
    ),
):
    """Sync patterns to Claude Code memory."""
    subprocess.run(["empathy-sync-claude", "--source", source])


# =============================================================================
# WORKFLOW COMMANDS (delegate to legacy CLI)
# =============================================================================


@app.command("morning")
def morning():
    """Start-of-day briefing with patterns, git context, and priorities."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "morning"])


@app.command("ship")
def ship():
    """Pre-commit validation (lint, format, tests, security)."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "ship"])


@app.command("health")
def health(
    deep: bool = typer.Option(False, "--deep", help="Comprehensive health check"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues"),
):
    """Quick health check (lint, types, tests)."""
    args = [sys.executable, "-m", "empathy_os.cli", "health"]
    if deep:
        args.append("--deep")
    if fix:
        args.append("--fix")
    subprocess.run(args)


@app.command("fix-all")
def fix_all():
    """Fix all lint and format issues."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "fix-all"])


@app.command("learn")
def learn(
    analyze: int = typer.Option(20, "--analyze", "-a", help="Number of commits to analyze"),
):
    """Learn patterns from commit history."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "learn", "--analyze", str(analyze)])


@app.command("run")
def run_repl():
    """Start interactive REPL mode."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "run"])


# =============================================================================
# WIZARD COMMANDS
# =============================================================================

wizard_app = typer.Typer(help="AI Development Wizards")
app.add_typer(wizard_app, name="wizard")


@wizard_app.command("list")
def wizard_list():
    """List all available wizards."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "frameworks"])


@wizard_app.command("run")
def wizard_run(
    name: str = typer.Argument(..., help="Wizard name to run"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to analyze"),
):
    """Run a specific wizard on your codebase."""
    console.print(f"[yellow]Running wizard:[/yellow] {name} on {path}")
    # Delegate to empathy-scan with wizard filter
    subprocess.run(["empathy-scan", str(path), "--wizards", name])


# =============================================================================
# WORKFLOW SUBCOMMAND GROUP
# =============================================================================

workflow_app = typer.Typer(help="Multi-model workflows")
app.add_typer(workflow_app, name="workflow")


@workflow_app.command("list")
def workflow_list():
    """List available multi-model workflows."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "workflow", "list"])


@workflow_app.command("run")
def workflow_run(
    name: str = typer.Argument(..., help="Workflow name"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to run on"),
):
    """Run a multi-model workflow."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "workflow", "run", name, str(path)])


# =============================================================================
# UTILITY COMMANDS
# =============================================================================


@app.command("cheatsheet")
def cheatsheet():
    """Show quick reference for all commands."""
    console.print(
        Panel.fit(
            """[bold]Getting Started[/bold]
  empathy morning           Start-of-day briefing
  empathy health            Quick health check
  empathy ship              Pre-commit validation
  empathy run               Interactive REPL

[bold]Memory System[/bold]
  empathy memory status     Check Redis & patterns
  empathy memory start      Start Redis server
  empathy memory patterns   List stored patterns

[bold]Provider Config[/bold]
  empathy provider          Show current config
  empathy provider --set hybrid    Use best-of-breed
  empathy provider registry        List all models

[bold]Code Inspection[/bold]
  empathy scan .            Scan for issues
  empathy inspect .         Deep analysis (SARIF)
  empathy fix-all           Auto-fix everything

[bold]Pattern Learning[/bold]
  empathy learn --analyze 20    Learn from commits
  empathy sync-claude           Sync to Claude Code

[bold]Workflows[/bold]
  empathy workflow list     Show available workflows
  empathy workflow run <name>   Execute a workflow

[bold]Wizards[/bold]
  empathy wizard list       Show available wizards
  empathy wizard run <name> Execute a wizard""",
            title="[bold blue]Empathy Framework Cheatsheet[/bold blue]",
        )
    )


@app.command("dashboard")
def dashboard():
    """Launch visual dashboard."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "dashboard"])


@app.command("costs")
def costs():
    """View API cost tracking."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "costs"])


@app.command("init")
def init():
    """Create a new configuration file."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "init"])


@app.command("status")
def status():
    """What needs attention now."""
    subprocess.run([sys.executable, "-m", "empathy_os.cli", "status"])


def main():
    """Entry point for the unified CLI."""
    app()


if __name__ == "__main__":
    main()
