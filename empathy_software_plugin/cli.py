"""
Empathy Framework - Software Development CLI

Command-line interface for running AI development wizards on your codebase.

Usage:
    empathy-software analyze /path/to/project
    empathy-software analyze /path/to/project --wizards prompt,context,collaboration
    empathy-software list-wizards
    empathy-software wizard-info testing

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from empathy_os.logging_config import get_logger
from empathy_os.plugins import get_global_registry as _get_global_registry

logger = get_logger(__name__)


def get_global_registry():
    """Get the global plugin registry.

    This wrapper exists so tests can patch this function at the module level
    via `empathy_software_plugin.cli.get_global_registry`.
    """
    return _get_global_registry()


# Initialize colorama for cross-platform ANSI color support (especially Windows)
try:
    import colorama

    colorama.init()
except ImportError:
    # Colorama not installed - ANSI colors may not work on Windows CMD
    pass


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print("=" * len(text))


def print_alert(text: str):
    """Print alert message"""
    print(f"{Colors.YELLOW}[ALERT]{Colors.END} {text}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ{Colors.END} {text}")


async def analyze_project(
    project_path: str,
    wizard_names: list[str] = None,
    output_format: str = "text",
    verbose: bool = False,
):
    """
    Analyze a project with AI development wizards.

    Args:
        project_path: Path to project root
        wizard_names: List of wizard names to run (or None for all)
        output_format: 'text' or 'json'
        verbose: Show detailed output
    """
    logger.info(f"Starting project analysis for: {project_path} (format: {output_format})")
    print_header("Empathy Framework - AI Development Analysis")
    print(f"Project: {project_path}\n")

    # Get registry
    registry = get_global_registry()
    software_plugin = registry.get_plugin("software")

    if not software_plugin:
        logger.error("Software plugin not found in registry")
        print_error("Software plugin not found. Is it installed?")
        return 1

    # Determine which wizards to run
    if wizard_names:
        wizards_to_run = wizard_names
    else:
        # Run all AI development wizards
        wizards_to_run = [
            "prompt_engineering",
            "context_window",
            "collaboration_pattern",
            "ai_documentation",
        ]

    # Gather context
    logger.info("Gathering project context...")
    print_info("Gathering project context...")
    context = await gather_project_context(project_path)

    if verbose:
        logger.debug(f"Found {len(context.get('ai_integration_files', []))} AI integration files")
        logger.debug(f"Found {len(context.get('documentation_files', []))} documentation files")
        print_info(f"Found {len(context.get('ai_integration_files', []))} AI integration files")
        print_info(f"Found {len(context.get('documentation_files', []))} documentation files")

    # Run wizards
    all_results = {}

    for wizard_name in wizards_to_run:
        logger.info(f"Running wizard: {wizard_name}")
        print_header(f"Running {wizard_name.replace('_', ' ').title()} Wizard")

        WizardClass = software_plugin.get_wizard(wizard_name)
        if not WizardClass:
            logger.error(f"Wizard not found: {wizard_name}")
            print_error(f"Wizard '{wizard_name}' not found")
            continue

        wizard = WizardClass()

        try:
            # Prepare wizard-specific context
            wizard_context = prepare_wizard_context(wizard_name, context)

            # Run analysis
            result = await wizard.analyze(wizard_context)
            all_results[wizard_name] = result
            logger.info(f"Wizard {wizard_name} completed successfully")

            # Display results
            if output_format == "text":
                display_wizard_results(wizard, result, verbose)
            else:
                # JSON output handled at end
                pass

        except Exception as e:
            logger.error(f"Error running wizard {wizard_name}: {e}")
            print_error(f"Error running wizard: {e}")
            if verbose:
                import traceback

                traceback.print_exc()

    # Output results
    if output_format == "json":
        print(json.dumps(all_results, indent=2, default=str))
    else:
        print_summary(all_results)

    return 0


async def gather_project_context(project_path: str) -> dict[str, Any]:
    """
    Gather context about the project.

    Returns dictionary with all context needed by wizards.
    """
    project_root = Path(project_path)

    context = {
        "project_path": str(project_root),
        "ai_integration_files": [],
        "documentation_files": [],
        "prompt_files": [],
        "code_files": [],
        "test_files": [],
        "ai_calls": [],
        "context_sources": [],
        "ai_usage_patterns": [],
        "version_history": [],
    }

    # Find AI integration files
    for pattern in ["**/*.py", "**/*.js", "**/*.ts"]:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                # Check if file has AI integration
                try:
                    with open(file_path) as f:
                        content = f.read()
                        if any(
                            ai_lib in content
                            for ai_lib in [
                                "openai",
                                "anthropic",
                                "langchain",
                                "llama",
                                "ai.generate",
                            ]
                        ):
                            context["ai_integration_files"].append(str(file_path))

                            # Parse AI calls
                            context["ai_calls"].extend(parse_ai_calls(str(file_path), content))
                except Exception:
                    pass  # Skip files that can't be parsed

                # All Python/JS/TS files are code files
                context["code_files"].append(str(file_path))

    # Find documentation files
    for pattern in ["**/*.md", "**/*.rst", "**/*.txt"]:
        for file_path in project_root.glob(pattern):
            if file_path.is_file() and "node_modules" not in str(file_path):
                context["documentation_files"].append(str(file_path))

    # Find prompt files (common patterns)
    for pattern in ["**/prompts/**/*", "**/*prompt*.txt", "**/*prompt*.md"]:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                context["prompt_files"].append(str(file_path))

    # Find test files
    for pattern in ["**/test_*.py", "**/*_test.py", "**/tests/**/*.py"]:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                context["test_files"].append(str(file_path))

    # Get git history if available
    try:
        import subprocess

        result = subprocess.run(
            ["git", "log", "--oneline", "--name-only", "-50"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            context["version_history"] = parse_git_history(result.stdout)
    except Exception:
        pass  # Skip if git not available or fails

    return context


def parse_ai_calls(file_path: str, content: str) -> list[dict[str, Any]]:
    """Parse AI API calls from file content"""
    # Simplified parser - in production, use AST
    calls = []

    # Look for common AI call patterns
    if "openai.chat" in content or "anthropic.messages" in content:
        calls.append(
            {
                "id": f"{file_path}:ai_call",
                "location": file_path,
                "code_snippet": content[:500],  # First 500 chars as sample
                "prompt_size": len(content),
                "conversation_id": None,  # Could detect from context
            }
        )

    return calls


def parse_git_history(git_output: str) -> list[dict[str, Any]]:
    """Parse git log output into structured history"""
    commits = []
    current_commit = None

    for line in git_output.split("\n"):
        if line and not line.startswith(" "):
            # New commit
            if current_commit:
                commits.append(current_commit)
            current_commit = {"hash": line.split()[0], "files": []}
        elif line and current_commit:
            # File in commit
            current_commit["files"].append(line.strip())

    if current_commit:
        commits.append(current_commit)

    return commits


def prepare_wizard_context(wizard_name: str, full_context: dict[str, Any]) -> dict[str, Any]:
    """Prepare context specific to a wizard's requirements"""

    base_context = {
        "project_path": full_context["project_path"],
        "version_history": full_context.get("version_history", []),
    }

    if wizard_name == "prompt_engineering":
        return {
            **base_context,
            "prompt_files": full_context.get("prompt_files", []),
        }

    elif wizard_name == "context_window":
        return {
            **base_context,
            "ai_calls": full_context.get("ai_calls", []),
            "context_sources": full_context.get("context_sources", []),
            "ai_provider": "anthropic",  # Could detect from code
            "model_name": "claude-3-sonnet",
        }

    elif wizard_name == "collaboration_pattern":
        return {
            **base_context,
            "ai_integration_files": full_context.get("ai_integration_files", []),
            "ai_usage_patterns": full_context.get("ai_usage_patterns", []),
        }

    elif wizard_name == "ai_documentation":
        return {
            **base_context,
            "documentation_files": full_context.get("documentation_files", []),
            "code_files": full_context.get("code_files", []),
        }

    return base_context


def display_wizard_results(wizard, result: dict[str, Any], verbose: bool):
    """Display wizard results in human-readable format"""

    # Issues
    issues = result.get("issues", [])
    if issues:
        print(f"\n{Colors.BOLD}Current Issues:{Colors.END}")
        for issue in issues:
            severity = issue.get("severity", "info")
            marker = {
                "error": f"{Colors.RED}✗{Colors.END}",
                "warning": f"{Colors.YELLOW}⚠{Colors.END}",
                "info": f"{Colors.CYAN}ℹ{Colors.END}",
            }.get(severity, "ℹ")

            print(f"  {marker} {issue.get('message', 'No message')}")
            if verbose and "suggestion" in issue:
                print(f"    → {issue['suggestion']}")

    # Predictions (Level 4!)
    predictions = result.get("predictions", [])
    if predictions:
        print(f"\n{Colors.BOLD}Anticipatory Alerts (Level 4):{Colors.END}")
        for pred in predictions:
            print(f"\n  {Colors.YELLOW}[ALERT]{Colors.END} {pred.get('alert', '')}")

            if verbose:
                if "reasoning" in pred:
                    print(f"    Reasoning: {pred['reasoning']}")
                if "personal_experience" in pred:
                    print(f"    {Colors.CYAN}Experience:{Colors.END} {pred['personal_experience']}")

            print(f"    {Colors.BOLD}Prevention steps:{Colors.END}")
            for i, step in enumerate(pred.get("prevention_steps", [])[:3], 1):
                print(f"      {i}. {step}")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        for rec in recommendations[:5]:  # Top 5
            if rec.strip():
                print(f"  • {rec}")

    # Confidence
    confidence = result.get("confidence", 0)
    print(f"\n{Colors.BOLD}Analysis Confidence:{Colors.END} {confidence:.0%}")


def print_summary(all_results: dict[str, dict[str, Any]]):
    """Print overall summary of analysis"""
    print_header("Analysis Summary")

    total_issues = sum(len(r.get("issues", [])) for r in all_results.values())
    total_predictions = sum(len(r.get("predictions", [])) for r in all_results.values())

    print(f"\nWizards run: {len(all_results)}")
    print(f"Current issues found: {total_issues}")
    print(f"Anticipatory alerts: {total_predictions}")

    high_impact = sum(
        1
        for r in all_results.values()
        for p in r.get("predictions", [])
        if p.get("impact") == "high"
    )

    if high_impact > 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}High-impact alerts: {high_impact}{Colors.END}")
        print("Review these immediately to prevent future issues.")

    # Extract patterns
    all_patterns = []
    for result in all_results.values():
        all_patterns.extend(result.get("patterns", []))

    if all_patterns:
        print(f"\nCross-domain patterns discovered: {len(all_patterns)}")
        print("These patterns can be applied to other domains (Level 5 Systems Empathy)")


def list_wizards():
    """List available wizards"""
    logger.info("Listing available wizards")
    print_header("Available AI Development Wizards")

    registry = get_global_registry()
    software_plugin = registry.get_plugin("software")

    if not software_plugin:
        logger.error("Software plugin not found in registry")
        print_error("Software plugin not found")
        return 1

    wizards = software_plugin.list_wizards()
    logger.info(f"Found {len(wizards)} available wizards")

    for wizard_id in wizards:
        info = software_plugin.get_wizard_info(wizard_id)
        if info:
            print(f"\n{Colors.BOLD}{wizard_id}{Colors.END}")
            print(f"  Name: {info['name']}")
            print(
                f"  Level: {info['empathy_level']} ({'Anticipatory' if info['empathy_level'] == 4 else 'Other'})"
            )
            print(f"  Category: {info.get('category', 'N/A')}")

    return 0


def wizard_info(wizard_id: str):
    """Show detailed info about a wizard"""
    logger.info(f"Displaying info for wizard: {wizard_id}")
    registry = get_global_registry()
    software_plugin = registry.get_plugin("software")

    if not software_plugin:
        logger.error("Software plugin not found in registry")
        print_error("Software plugin not found")
        return 1

    info = software_plugin.get_wizard_info(wizard_id)
    if not info:
        logger.error(f"Wizard not found: {wizard_id}")
        print_error(f"Wizard '{wizard_id}' not found")
        return 1

    logger.debug(f"Wizard info retrieved: {wizard_id}")
    print_header(f"Wizard: {info['name']}")
    print(f"ID: {wizard_id}")
    print(f"Domain: {info['domain']}")
    print(f"Empathy Level: {info['empathy_level']}")
    print(f"Category: {info.get('category', 'N/A')}")

    print(f"\n{Colors.BOLD}Required Context:{Colors.END}")
    for ctx in info.get("required_context", []):
        print(f"  • {ctx}")

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Empathy Framework - AI Development Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  empathy-software analyze /path/to/project
  empathy-software analyze . --wizards prompt_engineering,context_window
  empathy-software analyze . --verbose --output json
  empathy-software list-wizards
  empathy-software wizard-info prompt_engineering
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project")
    analyze_parser.add_argument("path", help="Path to project")
    analyze_parser.add_argument(
        "--wizards", help="Comma-separated list of wizards to run", default=None
    )
    analyze_parser.add_argument(
        "--output", choices=["text", "json"], default="text", help="Output format"
    )
    analyze_parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    # List wizards command
    subparsers.add_parser("list-wizards", help="List available wizards")

    # Wizard info command
    info_parser = subparsers.add_parser("wizard-info", help="Show wizard details")
    info_parser.add_argument("wizard_id", help="Wizard identifier")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "analyze":
        wizard_names = None
        if args.wizards:
            wizard_names = [w.strip() for w in args.wizards.split(",")]

        return asyncio.run(
            analyze_project(
                args.path,
                wizard_names=wizard_names,
                output_format=args.output,
                verbose=args.verbose,
            )
        )

    elif args.command == "list-wizards":
        return list_wizards()

    elif args.command == "wizard-info":
        return wizard_info(args.wizard_id)

    return 0


def scan_command():
    """
    Entry point for empathy-scan command (converted from bin/empathy-scan).
    One-click security & performance scanner.
    """
    logger.info("Empathy Framework security and performance scanner started")

    if len(sys.argv) < 3:
        logger.warning("Insufficient arguments provided to scan_command")
        print("Usage: empathy-scan [security|performance|all] <file-or-directory>")
        print("\nExamples:")
        print("  empathy-scan security app.py")
        print("  empathy-scan performance ./src")
        print("  empathy-scan all ./project")
        sys.exit(1)

    scan_type = sys.argv[1].lower()
    target = sys.argv[2]

    logger.info(f"Scan initiated: type={scan_type}, target={target}")

    # Import wizards
    try:
        from coach_wizards import PerformanceWizard, SecurityWizard
    except ImportError:
        logger.error("Empathy Framework wizards not installed")
        print("Error: Empathy Framework wizards not installed.")
        print("Run: pip install empathy-framework[all]")
        sys.exit(1)

    # Determine if target is file or directory
    target_path = Path(target)
    if not target_path.exists():
        logger.error(f"Target does not exist: {target}")
        print(f"Error: {target} does not exist")
        sys.exit(1)

    # Collect files to scan
    files_to_scan = []
    if target_path.is_file():
        files_to_scan = [target_path]
    else:
        # Scan directory for Python files
        files_to_scan = list(target_path.rglob("*.py"))

    if not files_to_scan:
        logger.warning(f"No Python files found in {target}")
        print(f"No Python files found in {target}")
        sys.exit(0)

    logger.info(f"Scanning {len(files_to_scan)} file(s)")
    print(f"🔍 Scanning {len(files_to_scan)} file(s)...")
    print()

    total_issues = 0
    total_predictions = 0

    # Run appropriate wizards
    wizards = []
    if scan_type in ["security", "all"]:
        wizards.append(("Security", SecurityWizard()))
    if scan_type in ["performance", "all"]:
        wizards.append(("Performance", PerformanceWizard()))

    if not wizards:
        print(f"Unknown scan type: {scan_type}")
        print("Use: security, performance, or all")
        sys.exit(1)

    # Scan each file
    for file_path in files_to_scan:
        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            continue

        print(f"📄 {file_path}")

        for wizard_name, wizard in wizards:
            result = wizard.run_full_analysis(
                code=code, file_path=str(file_path), language="python"
            )

            if result.issues:
                print(f"  {wizard_name}: {len(result.issues)} issue(s) found")
                for issue in result.issues[:3]:  # Show first 3
                    severity_icon = (
                        "🔴"
                        if issue.severity == "high"
                        else "🟡" if issue.severity == "medium" else "🔵"
                    )
                    print(f"    {severity_icon} Line {issue.line_number}: {issue.message}")
                if len(result.issues) > 3:
                    print(f"    ... and {len(result.issues) - 3} more")
                total_issues += len(result.issues)
            else:
                print(f"  {wizard_name}: ✅ No issues")

            if result.predictions:
                print(f"  🔮 {len(result.predictions)} prediction(s) for next 90 days")
                total_predictions += len(result.predictions)

        print()

    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print(f"  Files scanned: {len(files_to_scan)}")
    print(f"  Current issues: {total_issues}")
    print(f"  Future predictions: {total_predictions}")

    if total_issues > 0:
        print(f"\n⚠️  Found {total_issues} issue(s) that need attention")
        sys.exit(1)
    else:
        print("\n✅ All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
