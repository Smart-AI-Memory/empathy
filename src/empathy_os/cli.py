"""
Command-Line Interface for Empathy Framework

Provides CLI commands for:
- Running examples and demos
- Inspecting pattern libraries
- Viewing metrics and statistics
- Configuration management

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from empathy_os import (
    EmpathyOS,
    EmpathyConfig,
    load_config,
    PatternLibrary,
    Pattern,
)
from empathy_os.persistence import PatternPersistence, StateManager, MetricsCollector


def cmd_version(args):
    """Display version information"""
    print("Empathy Framework v1.0.0")
    print("Copyright 2025 Deep Study AI, LLC")
    print("Licensed under the Apache License, Version 2.0")


def cmd_init(args):
    """Initialize a new Empathy Framework project"""
    config_format = args.format
    output_path = args.output or f"empathy.config.{config_format}"

    # Create default config
    config = EmpathyConfig()

    # Save to file
    if config_format == "yaml":
        config.to_yaml(output_path)
        print(f"✓ Created YAML configuration: {output_path}")
    elif config_format == "json":
        config.to_json(output_path)
        print(f"✓ Created JSON configuration: {output_path}")

    print("\nNext steps:")
    print(f"  1. Edit {output_path} to customize settings")
    print("  2. Use 'empathy-framework run' to start using the framework")


def cmd_validate(args):
    """Validate a configuration file"""
    filepath = args.config

    try:
        config = load_config(filepath=filepath, use_env=False)
        config.validate()
        print(f"✓ Configuration valid: {filepath}")
        print(f"\n  User ID: {config.user_id}")
        print(f"  Target Level: {config.target_level}")
        print(f"  Confidence Threshold: {config.confidence_threshold}")
        print(f"  Persistence Backend: {config.persistence_backend}")
        print(f"  Metrics Enabled: {config.metrics_enabled}")
    except Exception as e:
        print(f"✗ Configuration invalid: {e}")
        sys.exit(1)


def cmd_info(args):
    """Display information about the framework"""
    config_file = args.config

    if config_file:
        config = load_config(filepath=config_file)
    else:
        config = load_config()

    print("=== Empathy Framework Info ===\n")
    print(f"Configuration:")
    print(f"  User ID: {config.user_id}")
    print(f"  Target Level: {config.target_level}")
    print(f"  Confidence Threshold: {config.confidence_threshold}")
    print(f"\nPersistence:")
    print(f"  Backend: {config.persistence_backend}")
    print(f"  Path: {config.persistence_path}")
    print(f"  Enabled: {config.persistence_enabled}")
    print(f"\nMetrics:")
    print(f"  Enabled: {config.metrics_enabled}")
    print(f"  Path: {config.metrics_path}")
    print(f"\nPattern Library:")
    print(f"  Enabled: {config.pattern_library_enabled}")
    print(f"  Pattern Sharing: {config.pattern_sharing}")
    print(f"  Confidence Threshold: {config.pattern_confidence_threshold}")


def cmd_patterns_list(args):
    """List patterns in a pattern library"""
    filepath = args.library
    format_type = args.format

    try:
        if format_type == "json":
            library = PatternPersistence.load_from_json(filepath)
        elif format_type == "sqlite":
            library = PatternPersistence.load_from_sqlite(filepath)
        else:
            print(f"✗ Unknown format: {format_type}")
            sys.exit(1)

        print(f"=== Pattern Library: {filepath} ===\n")
        print(f"Total patterns: {len(library.patterns)}")
        print(f"Total agents: {len(library.agent_contributions)}")

        if library.patterns:
            print("\nPatterns:")
            for pattern_id, pattern in library.patterns.items():
                print(f"\n  [{pattern_id}] {pattern.name}")
                print(f"    Agent: {pattern.agent_id}")
                print(f"    Type: {pattern.pattern_type}")
                print(f"    Confidence: {pattern.confidence:.2f}")
                print(f"    Usage: {pattern.usage_count}")
                print(f"    Success Rate: {pattern.success_rate:.2f}")
    except FileNotFoundError:
        print(f"✗ Pattern library not found: {filepath}")
        sys.exit(1)


def cmd_patterns_export(args):
    """Export patterns from one format to another"""
    input_file = args.input
    input_format = args.input_format
    output_file = args.output
    output_format = args.output_format

    # Load from input format
    try:
        if input_format == "json":
            library = PatternPersistence.load_from_json(input_file)
        elif input_format == "sqlite":
            library = PatternPersistence.load_from_sqlite(input_file)
        else:
            print(f"✗ Unknown input format: {input_format}")
            sys.exit(1)

        print(f"✓ Loaded {len(library.patterns)} patterns from {input_file}")
    except Exception as e:
        print(f"✗ Failed to load patterns: {e}")
        sys.exit(1)

    # Save to output format
    try:
        if output_format == "json":
            PatternPersistence.save_to_json(library, output_file)
        elif output_format == "sqlite":
            PatternPersistence.save_to_sqlite(library, output_file)

        print(f"✓ Saved {len(library.patterns)} patterns to {output_file}")
    except Exception as e:
        print(f"✗ Failed to save patterns: {e}")
        sys.exit(1)


def cmd_metrics_show(args):
    """Display metrics for a user"""
    db_path = args.db
    user_id = args.user

    collector = MetricsCollector(db_path)

    try:
        stats = collector.get_user_stats(user_id)

        print(f"=== Metrics for User: {user_id} ===\n")
        print(f"Total Operations: {stats['total_operations']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Average Response Time: {stats.get('avg_response_time_ms', 0):.0f} ms")
        print(f"\nFirst Use: {stats['first_use']}")
        print(f"Last Use: {stats['last_use']}")

        print(f"\nEmpathy Level Usage:")
        print(f"  Level 1: {stats.get('level_1_count', 0)} uses")
        print(f"  Level 2: {stats.get('level_2_count', 0)} uses")
        print(f"  Level 3: {stats.get('level_3_count', 0)} uses")
        print(f"  Level 4: {stats.get('level_4_count', 0)} uses")
        print(f"  Level 5: {stats.get('level_5_count', 0)} uses")
    except Exception as e:
        print(f"✗ Failed to retrieve metrics: {e}")
        sys.exit(1)


def cmd_state_list(args):
    """List saved user states"""
    state_dir = args.state_dir

    manager = StateManager(state_dir)
    users = manager.list_users()

    print(f"=== Saved User States: {state_dir} ===\n")
    print(f"Total users: {len(users)}")

    if users:
        print("\nUsers:")
        for user_id in users:
            print(f"  - {user_id}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="empathy-framework",
        description="Empathy Framework - Build AI systems with 5 levels of empathy"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    parser_version = subparsers.add_parser("version", help="Display version information")
    parser_version.set_defaults(func=cmd_version)

    # Init command
    parser_init = subparsers.add_parser("init", help="Initialize a new project")
    parser_init.add_argument("--format", choices=["yaml", "json"], default="yaml",
                            help="Configuration format (default: yaml)")
    parser_init.add_argument("--output", "-o", help="Output file path")
    parser_init.set_defaults(func=cmd_init)

    # Validate command
    parser_validate = subparsers.add_parser("validate", help="Validate configuration file")
    parser_validate.add_argument("config", help="Path to configuration file")
    parser_validate.set_defaults(func=cmd_validate)

    # Info command
    parser_info = subparsers.add_parser("info", help="Display framework information")
    parser_info.add_argument("--config", "-c", help="Configuration file")
    parser_info.set_defaults(func=cmd_info)

    # Patterns commands
    parser_patterns = subparsers.add_parser("patterns", help="Pattern library commands")
    patterns_subparsers = parser_patterns.add_subparsers(dest="patterns_command")

    # Patterns list
    parser_patterns_list = patterns_subparsers.add_parser("list", help="List patterns in library")
    parser_patterns_list.add_argument("library", help="Path to pattern library file")
    parser_patterns_list.add_argument("--format", choices=["json", "sqlite"], default="json",
                                     help="Library format (default: json)")
    parser_patterns_list.set_defaults(func=cmd_patterns_list)

    # Patterns export
    parser_patterns_export = patterns_subparsers.add_parser("export", help="Export patterns")
    parser_patterns_export.add_argument("input", help="Input file path")
    parser_patterns_export.add_argument("output", help="Output file path")
    parser_patterns_export.add_argument("--input-format", choices=["json", "sqlite"], default="json")
    parser_patterns_export.add_argument("--output-format", choices=["json", "sqlite"], default="json")
    parser_patterns_export.set_defaults(func=cmd_patterns_export)

    # Metrics commands
    parser_metrics = subparsers.add_parser("metrics", help="Metrics commands")
    metrics_subparsers = parser_metrics.add_subparsers(dest="metrics_command")

    # Metrics show
    parser_metrics_show = metrics_subparsers.add_parser("show", help="Show user metrics")
    parser_metrics_show.add_argument("user", help="User ID")
    parser_metrics_show.add_argument("--db", default="./metrics.db", help="Metrics database path")
    parser_metrics_show.set_defaults(func=cmd_metrics_show)

    # State commands
    parser_state = subparsers.add_parser("state", help="State management commands")
    state_subparsers = parser_state.add_subparsers(dest="state_command")

    # State list
    parser_state_list = state_subparsers.add_parser("list", help="List saved states")
    parser_state_list.add_argument("--state-dir", default="./empathy_state",
                                   help="State directory path")
    parser_state_list.set_defaults(func=cmd_state_list)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
