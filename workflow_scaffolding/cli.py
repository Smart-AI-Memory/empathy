"""CLI for workflow scaffolding.

Provides command-line interface for creating workflows.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from empathy_os.workflow_patterns import get_workflow_pattern_registry

from .generator import WorkflowGenerator

console = Console()


def cmd_create(args):
    """Create a new workflow."""
    workflow_name = args.name
    description = args.description or f"{workflow_name} workflow"
    patterns = args.patterns.split(",") if args.patterns else []

    # Auto-select patterns if none provided
    if not patterns:
        console.print("[yellow]No patterns specified, using defaults for simple workflow[/yellow]")
        patterns = ["single-stage"]

    # Create generator
    generator = WorkflowGenerator()
    registry = get_workflow_pattern_registry()

    # Validate patterns
    valid, error = registry.validate_pattern_combination(patterns)
    if not valid:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)

    console.print(f"[bold]Creating workflow:[/bold] {workflow_name}")
    console.print(f"[bold]Description:[/bold] {description}")
    console.print(f"[bold]Patterns:[/bold] {', '.join(patterns)}")

    # Generate and write
    output_dir = Path(args.output) if args.output else Path.cwd()

    try:
        written = generator.write_workflow(
            output_dir=output_dir,
            workflow_name=workflow_name,
            description=description,
            patterns=patterns,
            stages=args.stages.split(",") if args.stages else None,
            tier_map=_parse_tier_map(args.tier_map) if args.tier_map else None,
        )

        console.print("\n[green]✓[/green] Workflow created successfully!\n")
        console.print("[bold]Generated files:[/bold]")
        for file_type, path in written.items():
            console.print(f"  - {file_type}: {path}")

        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Review generated files")
        console.print("2. Implement stage logic (search for TODO comments)")
        console.print(f"3. Run tests: pytest {written['test']}")
        console.print(f"4. Run workflow: empathy workflow run {workflow_name}")

    except Exception as e:
        console.print(f"[red]Error creating workflow: {e}[/red]")
        sys.exit(1)


def cmd_list_patterns(args):
    """List available patterns."""
    registry = get_workflow_pattern_registry()
    patterns = registry.list_all()

    # Create table
    table = Table(title="Workflow Patterns")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Complexity", style="magenta")
    table.add_column("Risk", justify="right")

    for pattern in sorted(patterns, key=lambda p: p.id):
        table.add_row(
            pattern.id,
            pattern.name,
            pattern.category.value,
            pattern.complexity.value,
            f"{pattern.risk_weight:.1f}",
        )

    console.print(table)

    # Show usage examples
    console.print("\n[bold]Common Combinations:[/bold]")
    console.print("  Simple workflow:       single-stage")
    console.print("  Code analysis:         multi-stage,code-scanner,conditional-tier")
    console.print("  Multi-agent:           crew-based,result-dataclass")
    console.print("  Configurable:          multi-stage,config-driven")


def cmd_recommend(args):
    """Recommend patterns for a workflow type."""
    registry = get_workflow_pattern_registry()
    workflow_type = args.type

    recommendations = registry.recommend_for_workflow(workflow_type)

    if not recommendations:
        console.print(f"[yellow]No recommendations found for type: {workflow_type}[/yellow]")
        console.print(
            "\nAvailable types: code-analysis, simple, multi-agent, configurable, cost-optimized"
        )
        return

    console.print(f"[bold]Recommendations for '{workflow_type}':[/bold]\n")

    for pattern in recommendations:
        console.print(f"[cyan]{pattern.id}[/cyan] - {pattern.name}")
        console.print(f"  {pattern.description}")
        if pattern.use_cases:
            console.print(f"  Use for: {', '.join(pattern.use_cases)}")
        console.print()

    pattern_ids = [p.id for p in recommendations]
    console.print("[bold]Create command:[/bold]")
    console.print(
        f"python -m workflow_scaffolding create my-workflow --patterns {','.join(pattern_ids)}"
    )


def _parse_tier_map(tier_map_str: str) -> dict[str, str]:
    """Parse tier map from string.

    Args:
        tier_map_str: Format "stage1:CHEAP,stage2:CAPABLE"

    Returns:
        Dict mapping stage to tier

    """
    tier_map = {}
    for pair in tier_map_str.split(","):
        stage, tier = pair.split(":")
        tier_map[stage.strip()] = tier.strip()
    return tier_map


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow Factory - Create workflows 12x faster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # create command
    parser_create = subparsers.add_parser("create", help="Create a new workflow")
    parser_create.add_argument("name", help="Workflow name (kebab-case, e.g., bug-scanner)")
    parser_create.add_argument("--description", "-d", help="Workflow description")
    parser_create.add_argument(
        "--patterns",
        "-p",
        help="Comma-separated pattern IDs (e.g., multi-stage,conditional-tier)",
    )
    parser_create.add_argument("--stages", "-s", help="Comma-separated stage names")
    parser_create.add_argument(
        "--tier-map",
        "-t",
        help="Tier map (e.g., analyze:CHEAP,process:CAPABLE)",
    )
    parser_create.add_argument("--output", "-o", help="Output directory (default: current)")
    parser_create.set_defaults(func=cmd_create)

    # list-patterns command
    parser_list = subparsers.add_parser("list-patterns", help="List available patterns")
    parser_list.set_defaults(func=cmd_list_patterns)

    # recommend command
    parser_recommend = subparsers.add_parser("recommend", help="Recommend patterns for a type")
    parser_recommend.add_argument(
        "type",
        help="Workflow type (code-analysis, simple, multi-agent, etc.)",
    )
    parser_recommend.set_defaults(func=cmd_recommend)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
