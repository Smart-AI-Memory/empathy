"""
CLI for Multi-Model Configuration Inspection

Provides commands to:
- Print effective model registry
- Show task-to-tier mappings
- Validate configuration files
- Display cost estimates
- View telemetry and analytics

Usage:
    python -m empathy_os.models.cli registry
    python -m empathy_os.models.cli tasks
    python -m empathy_os.models.cli validate path/to/config.yaml
    python -m empathy_os.models.cli costs --input-tokens 10000 --output-tokens 2000
    python -m empathy_os.models.cli telemetry --summary
    python -m empathy_os.models.cli telemetry --costs
    python -m empathy_os.models.cli telemetry --providers

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

from .provider_config import (
    configure_provider_cli,
    configure_provider_interactive,
    get_provider_config,
)
from .registry import get_all_models
from .tasks import get_all_tasks, get_tier_for_task
from .telemetry import TelemetryAnalytics, TelemetryStore
from .validation import validate_yaml_file


def print_registry(provider: str | None = None, format: str = "table") -> None:
    """
    Print the model registry.

    Args:
        provider: Optional provider to filter by
        format: Output format ("table" or "json")
    """
    registry = get_all_models()

    if provider:
        if provider not in registry:
            print(f"Error: Unknown provider '{provider}'")
            print(f"Available providers: {', '.join(registry.keys())}")
            sys.exit(1)
        registry = {provider: registry[provider]}

    if format == "json":
        # Convert to JSON-serializable format
        output: dict[str, dict[str, dict[str, object]]] = {}
        for prov, tiers in registry.items():
            output[prov] = {}
            for tier, info in tiers.items():
                output[prov][tier] = {
                    "id": info.id,
                    "input_cost_per_million": info.input_cost_per_million,
                    "output_cost_per_million": info.output_cost_per_million,
                    "max_tokens": info.max_tokens,
                    "supports_vision": info.supports_vision,
                    "supports_tools": info.supports_tools,
                }
        print(json.dumps(output, indent=2))
    else:
        # Table format
        print("\n" + "=" * 80)
        print("MODEL REGISTRY")
        print("=" * 80)

        for prov, tiers in sorted(registry.items()):
            print(f"\n[{prov.upper()}]")
            print("-" * 60)
            print(f"{'Tier':<10} {'Model ID':<35} {'Input/M':<10} {'Output/M':<10}")
            print("-" * 60)

            for tier in ["cheap", "capable", "premium"]:
                if tier in tiers:
                    info = tiers[tier]
                    print(
                        f"{tier:<10} {info.id:<35} "
                        f"${info.input_cost_per_million:<9.2f} "
                        f"${info.output_cost_per_million:<9.2f}"
                    )

        print("\n" + "=" * 80)


def print_tasks(tier: str | None = None, format: str = "table") -> None:
    """
    Print task-to-tier mappings.

    Args:
        tier: Optional tier to filter by
        format: Output format ("table" or "json")
    """
    all_tasks = get_all_tasks()

    if tier:
        if tier not in all_tasks:
            print(f"Error: Unknown tier '{tier}'")
            print(f"Available tiers: {', '.join(all_tasks.keys())}")
            sys.exit(1)
        all_tasks = {tier: all_tasks[tier]}

    if format == "json":
        print(json.dumps(all_tasks, indent=2))
    else:
        print("\n" + "=" * 60)
        print("TASK-TO-TIER MAPPINGS")
        print("=" * 60)

        for tier_name, tasks in sorted(all_tasks.items()):
            print(f"\n[{tier_name.upper()}] - {len(tasks)} tasks")
            print("-" * 40)
            for task in sorted(tasks):
                print(f"  • {task}")

        print("\n" + "=" * 60)


def print_costs(
    input_tokens: int = 10000,
    output_tokens: int = 2000,
    provider: str | None = None,
    format: str = "table",
) -> None:
    """
    Print cost estimates for all tiers.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        provider: Optional provider to filter by
        format: Output format
    """
    registry = get_all_models()

    if provider:
        if provider not in registry:
            print(f"Error: Unknown provider '{provider}'")
            sys.exit(1)
        providers = [provider]
    else:
        providers = list(registry.keys())

    if format == "json":
        output: dict[str, dict[str, dict[str, object]]] = {}
        for prov in providers:
            output[prov] = {}
            for tier in ["cheap", "capable", "premium"]:
                if tier in registry[prov]:
                    info = registry[prov][tier]
                    input_cost = (input_tokens / 1_000_000) * info.input_cost_per_million
                    output_cost = (output_tokens / 1_000_000) * info.output_cost_per_million
                    output[prov][tier] = {
                        "input_cost": round(input_cost, 6),
                        "output_cost": round(output_cost, 6),
                        "total_cost": round(input_cost + output_cost, 6),
                    }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 70)
        print(f"COST ESTIMATES ({input_tokens:,} input / {output_tokens:,} output tokens)")
        print("=" * 70)

        for prov in sorted(providers):
            print(f"\n[{prov.upper()}]")
            print("-" * 50)
            print(f"{'Tier':<10} {'Input':<12} {'Output':<12} {'Total':<12}")
            print("-" * 50)

            for tier in ["cheap", "capable", "premium"]:
                if tier in registry[prov]:
                    info = registry[prov][tier]
                    input_cost = (input_tokens / 1_000_000) * info.input_cost_per_million
                    output_cost = (output_tokens / 1_000_000) * info.output_cost_per_million
                    total = input_cost + output_cost
                    print(f"{tier:<10} ${input_cost:<11.4f} ${output_cost:<11.4f} ${total:<11.4f}")

        print("\n" + "=" * 70)


def validate_file(file_path: str, format: str = "table") -> int:
    """
    Validate a configuration file.

    Args:
        file_path: Path to YAML config file
        format: Output format

    Returns:
        Exit code (0 = valid, 1 = errors)
    """
    result = validate_yaml_file(file_path)

    if format == "json":
        output = {
            "valid": result.valid,
            "errors": [{"path": e.path, "message": e.message} for e in result.errors],
            "warnings": [{"path": w.path, "message": w.message} for w in result.warnings],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nValidating: {file_path}")
        print("-" * 60)
        print(result)

    return 0 if result.valid else 1


def print_effective_config(provider: str = "anthropic") -> None:
    """
    Print the effective configuration for a provider.

    Args:
        provider: Provider to show config for
    """
    registry = get_all_models()

    if provider not in registry:
        print(f"Error: Unknown provider '{provider}'")
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"EFFECTIVE CONFIGURATION: {provider.upper()}")
    print("=" * 70)

    # Provider models
    print("\n[Models]")
    for tier in ["cheap", "capable", "premium"]:
        if tier in registry[provider]:
            info = registry[provider][tier]
            print(f"  {tier}: {info.id}")

    # Task routing
    print("\n[Task Routing Examples]")
    example_tasks = ["summarize", "fix_bug", "coordinate"]
    for task in example_tasks:
        task_tier = get_tier_for_task(task)
        model = registry[provider].get(task_tier.value)
        model_id = model.id if model else "N/A"
        print(f"  {task} → {task_tier.value} → {model_id}")

    # Default timeouts
    print("\n[Default Timeouts]")
    print("  cheap: 30,000 ms")
    print("  capable: 60,000 ms")
    print("  premium: 120,000 ms")

    print("\n" + "=" * 70)


def print_telemetry_summary(
    days: int = 7,
    format: str = "table",
    storage_dir: str = ".empathy",
) -> None:
    """
    Print telemetry summary.

    Args:
        days: Number of days to look back
        format: Output format
        storage_dir: Directory containing telemetry files
    """
    store = TelemetryStore(storage_dir)
    analytics = TelemetryAnalytics(store)

    since = datetime.now() - timedelta(days=days)
    calls = store.get_calls(since=since, limit=10000)
    workflows = store.get_workflows(since=since, limit=1000)

    if format == "json":
        output = {
            "period_days": days,
            "total_calls": len(calls),
            "total_workflows": len(workflows),
            "total_cost": sum(c.estimated_cost for c in calls),
            "success_rate": sum(1 for c in calls if c.success) / len(calls) * 100 if calls else 0,
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"TELEMETRY SUMMARY (Last {days} days)")
        print("=" * 60)

        print("\n[Overview]")
        print(f"  Total LLM calls: {len(calls):,}")
        print(f"  Total workflows: {len(workflows):,}")
        total_cost = sum(c.estimated_cost for c in calls)
        print(f"  Total cost: ${total_cost:.4f}")
        if calls:
            success_rate = sum(1 for c in calls if c.success) / len(calls) * 100
            print(f"  Success rate: {success_rate:.1f}%")

        # Tier breakdown
        tier_dist = analytics.tier_distribution(since)
        print("\n[Tier Distribution]")
        for tier, stats in tier_dist.items():
            print(f"  {tier}: {stats['count']} calls ({stats['percent']:.1f}%)")

        print("\n" + "=" * 60)


def print_telemetry_costs(
    days: int = 30,
    format: str = "table",
    storage_dir: str = ".empathy",
) -> None:
    """
    Print cost savings report.

    Args:
        days: Number of days to look back
        format: Output format
        storage_dir: Directory containing telemetry files
    """
    store = TelemetryStore(storage_dir)
    analytics = TelemetryAnalytics(store)

    since = datetime.now() - timedelta(days=days)
    report = analytics.cost_savings_report(since)

    if format == "json":
        print(json.dumps(report, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"COST SAVINGS REPORT (Last {days} days)")
        print("=" * 60)

        print("\n[Summary]")
        print(f"  Workflow runs: {report['workflow_count']}")
        print(f"  Actual cost: ${report['total_actual_cost']:.4f}")
        print(f"  Baseline cost (all premium): ${report['total_baseline_cost']:.4f}")
        print(f"  Total savings: ${report['total_savings']:.4f}")
        print(f"  Savings percent: {report['savings_percent']:.1f}%")
        print(f"  Avg cost per workflow: ${report['avg_cost_per_workflow']:.4f}")

        # Top expensive workflows
        top_wfs = analytics.top_expensive_workflows(n=5, since=since)
        if top_wfs:
            print("\n[Top Expensive Workflows]")
            for wf in top_wfs:
                print(f"  {wf['workflow_name']}: ${wf['total_cost']:.4f} ({wf['run_count']} runs)")

        print("\n" + "=" * 60)


def print_telemetry_providers(
    days: int = 30,
    format: str = "table",
    storage_dir: str = ".empathy",
) -> None:
    """
    Print provider usage summary.

    Args:
        days: Number of days to look back
        format: Output format
        storage_dir: Directory containing telemetry files
    """
    store = TelemetryStore(storage_dir)
    analytics = TelemetryAnalytics(store)

    since = datetime.now() - timedelta(days=days)
    summary = analytics.provider_usage_summary(since)

    if format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"PROVIDER USAGE (Last {days} days)")
        print("=" * 60)

        for provider, stats in sorted(summary.items()):
            print(f"\n[{provider.upper()}]")
            print(f"  Calls: {stats['call_count']:,}")
            print(f"  Tokens: {stats['total_tokens']:,}")
            print(f"  Cost: ${stats['total_cost']:.4f}")
            print(f"  Errors: {stats['error_count']}")
            print(f"  By tier: {stats['by_tier']}")

        print("\n" + "=" * 60)


def print_telemetry_fallbacks(
    days: int = 30,
    format: str = "table",
    storage_dir: str = ".empathy",
) -> None:
    """
    Print fallback statistics.

    Args:
        days: Number of days to look back
        format: Output format
        storage_dir: Directory containing telemetry files
    """
    store = TelemetryStore(storage_dir)
    analytics = TelemetryAnalytics(store)

    since = datetime.now() - timedelta(days=days)
    stats = analytics.fallback_stats(since)

    if format == "json":
        print(json.dumps(stats, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"FALLBACK STATISTICS (Last {days} days)")
        print("=" * 60)

        print("\n[Summary]")
        print(f"  Total calls: {stats['total_calls']:,}")
        print(f"  Fallback count: {stats['fallback_count']:,}")
        print(f"  Fallback rate: {stats['fallback_percent']:.2f}%")
        print(f"  Error count: {stats['error_count']:,}")
        print(f"  Error rate: {stats['error_rate']:.2f}%")

        if stats["by_original_provider"]:
            print("\n[Fallbacks by Original Provider]")
            for provider, count in stats["by_original_provider"].items():
                print(f"  {provider}: {count}")

        print("\n" + "=" * 60)


def print_provider_config(format: str = "table") -> None:
    """
    Print current provider configuration.

    Args:
        format: Output format ("table" or "json")
    """
    config = get_provider_config()

    if format == "json":
        output = config.to_dict()
        output["available_providers"] = config.available_providers
        output["effective_models"] = {
            tier: {"id": model.id, "provider": model.provider}
            for tier, model in config.get_effective_registry().items()
            if model
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 60)
        print("PROVIDER CONFIGURATION")
        print("=" * 60)

        print("\n[Current Settings]")
        print(f"  Mode: {config.mode.value}")
        print(f"  Primary provider: {config.primary_provider}")
        print(f"  Cost optimization: {config.cost_optimization}")
        print(f"  Prefer local (Ollama): {config.prefer_local}")

        print("\n[Available Providers]")
        if config.available_providers:
            for provider in config.available_providers:
                print(f"  - {provider}")
        else:
            print("  (No API keys detected)")

        print("\n[Effective Model Mapping]")
        effective = config.get_effective_registry()
        for tier in ["cheap", "capable", "premium"]:
            model = effective.get(tier)
            if model:
                print(f"  {tier:<10} -> {model.id} ({model.provider})")
            else:
                print(f"  {tier:<10} -> (not configured)")

        if config.tier_providers:
            print("\n[Custom Tier Providers]")
            for tier, provider in config.tier_providers.items():
                print(f"  {tier}: {provider}")

        print("\n" + "=" * 60)


def configure_provider(
    provider: str | None = None,
    mode: str | None = None,
    interactive: bool = False,
) -> int:
    """
    Configure provider settings.

    Args:
        provider: Provider to set (anthropic, openai, google, ollama, hybrid)
        mode: Mode to set (single, hybrid)
        interactive: Whether to run interactive configuration

    Returns:
        Exit code (0 for success)
    """
    if interactive:
        configure_provider_interactive()
        return 0

    if provider or mode:
        config = configure_provider_cli(provider=provider, mode=mode)
        config.save()
        print("Provider configuration updated:")
        print(f"  Mode: {config.mode.value}")
        print(f"  Provider: {config.primary_provider}")
        print("\nEffective models:")
        for tier, model in config.get_effective_registry().items():
            if model:
                print(f"  {tier}: {model.id}")
        return 0

    # Show current config
    print_provider_config()
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Model Configuration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s registry                     Show all models
  %(prog)s registry --provider anthropic  Show Anthropic models only
  %(prog)s tasks                        Show task-to-tier mappings
  %(prog)s costs --input 50000          Estimate costs for 50k input tokens
  %(prog)s validate config.yaml         Validate a config file
  %(prog)s effective --provider openai  Show effective config for OpenAI
  %(prog)s telemetry                    Show telemetry summary
  %(prog)s telemetry --costs            Show cost savings report
  %(prog)s telemetry --providers        Show provider usage
  %(prog)s telemetry --fallbacks        Show fallback stats
  %(prog)s provider                     Show current provider config
  %(prog)s provider --set anthropic     Set Anthropic as primary
  %(prog)s provider --set hybrid        Enable hybrid mode
  %(prog)s provider --interactive       Interactive setup wizard
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Registry command
    reg_parser = subparsers.add_parser("registry", help="Show model registry")
    reg_parser.add_argument("--provider", "-p", help="Filter by provider")
    reg_parser.add_argument("--format", "-f", choices=["table", "json"], default="table")

    # Tasks command
    tasks_parser = subparsers.add_parser("tasks", help="Show task-to-tier mappings")
    tasks_parser.add_argument("--tier", "-t", help="Filter by tier")
    tasks_parser.add_argument("--format", "-f", choices=["table", "json"], default="table")

    # Costs command
    costs_parser = subparsers.add_parser("costs", help="Estimate costs")
    costs_parser.add_argument("--input-tokens", "-i", type=int, default=10000, help="Input tokens")
    costs_parser.add_argument("--output-tokens", "-o", type=int, default=2000, help="Output tokens")
    costs_parser.add_argument("--provider", "-p", help="Filter by provider")
    costs_parser.add_argument("--format", "-f", choices=["table", "json"], default="table")

    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validate config file")
    val_parser.add_argument("file", help="Path to YAML config file")
    val_parser.add_argument("--format", "-f", choices=["table", "json"], default="table")

    # Effective command
    eff_parser = subparsers.add_parser("effective", help="Show effective config")
    eff_parser.add_argument("--provider", "-p", default="anthropic", help="Provider to show")

    # Telemetry command
    tel_parser = subparsers.add_parser("telemetry", help="Show telemetry data")
    tel_parser.add_argument("--days", "-d", type=int, default=7, help="Number of days to look back")
    tel_parser.add_argument("--costs", action="store_true", help="Show cost savings report")
    tel_parser.add_argument("--providers", action="store_true", help="Show provider usage")
    tel_parser.add_argument("--fallbacks", action="store_true", help="Show fallback statistics")
    tel_parser.add_argument("--storage-dir", default=".empathy", help="Telemetry storage directory")
    tel_parser.add_argument("--format", "-f", choices=["table", "json"], default="table")

    # Provider command
    prov_parser = subparsers.add_parser("provider", help="Configure provider settings")
    prov_parser.add_argument(
        "--set",
        "-s",
        dest="provider_set",
        help="Set provider (anthropic, openai, google, ollama, hybrid)",
    )
    prov_parser.add_argument(
        "--mode", "-m", choices=["single", "hybrid"], help="Set mode (single or hybrid)"
    )
    prov_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive configuration wizard"
    )
    prov_parser.add_argument("--format", "-f", choices=["table", "json"], default="table")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "registry":
        print_registry(args.provider, args.format)
        return 0

    elif args.command == "tasks":
        print_tasks(args.tier, args.format)
        return 0

    elif args.command == "costs":
        print_costs(args.input_tokens, args.output_tokens, args.provider, args.format)
        return 0

    elif args.command == "validate":
        return validate_file(args.file, args.format)

    elif args.command == "effective":
        print_effective_config(args.provider)
        return 0

    elif args.command == "telemetry":
        if args.costs:
            print_telemetry_costs(args.days, args.format, args.storage_dir)
        elif args.providers:
            print_telemetry_providers(args.days, args.format, args.storage_dir)
        elif args.fallbacks:
            print_telemetry_fallbacks(args.days, args.format, args.storage_dir)
        else:
            print_telemetry_summary(args.days, args.format, args.storage_dir)
        return 0

    elif args.command == "provider":
        if args.interactive:
            return configure_provider(interactive=True)
        elif args.provider_set or args.mode:
            return configure_provider(provider=args.provider_set, mode=args.mode)
        else:
            print_provider_config(args.format)
            return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
