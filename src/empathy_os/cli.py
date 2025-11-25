"""
Command-Line Interface for Empathy Framework

Provides CLI commands for:
- Running interactive REPL (empathy run)
- Inspecting patterns, metrics, state (empathy inspect)
- Exporting/importing patterns (empathy export/import)
- Interactive setup wizard (empathy wizard)
- Configuration management

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import argparse
import sys
import time
from importlib.metadata import version as get_version

from empathy_os import EmpathyConfig, EmpathyOS, load_config
from empathy_os.logging_config import get_logger
from empathy_os.pattern_library import PatternLibrary
from empathy_os.persistence import MetricsCollector, PatternPersistence, StateManager

logger = get_logger(__name__)


def cmd_version(args):
    """Display version information"""
    logger.info("Displaying version information")
    try:
        version = get_version("empathy")
    except Exception:
        version = "unknown"
    logger.info(f"Empathy v{version}")
    logger.info("Copyright 2025 Smart-AI-Memory")
    logger.info("Licensed under Fair Source License 0.9")
    logger.info("\n✨ Built with Claude Code + MemDocs + VS Code transformative stack")


def cmd_init(args):
    """Initialize a new Empathy Framework project"""
    config_format = args.format
    output_path = args.output or f"empathy.config.{config_format}"

    logger.info(f"Initializing new Empathy Framework project with format: {config_format}")

    # Create default config
    config = EmpathyConfig()

    # Save to file
    if config_format == "yaml":
        config.to_yaml(output_path)
        logger.info(f"Created YAML configuration file: {output_path}")
        logger.info(f"✓ Created YAML configuration: {output_path}")
    elif config_format == "json":
        config.to_json(output_path)
        logger.info(f"Created JSON configuration file: {output_path}")
        logger.info(f"✓ Created JSON configuration: {output_path}")

    logger.info("\nNext steps:")
    logger.info(f"  1. Edit {output_path} to customize settings")
    logger.info("  2. Use 'empathy run' to start using the framework")


def cmd_validate(args):
    """Validate a configuration file"""
    filepath = args.config
    logger.info(f"Validating configuration file: {filepath}")

    try:
        config = load_config(filepath=filepath, use_env=False)
        config.validate()
        logger.info(f"Configuration validation successful: {filepath}")
        logger.info(f"✓ Configuration valid: {filepath}")
        logger.info(f"\n  User ID: {config.user_id}")
        logger.info(f"  Target Level: {config.target_level}")
        logger.info(f"  Confidence Threshold: {config.confidence_threshold}")
        logger.info(f"  Persistence Backend: {config.persistence_backend}")
        logger.info(f"  Metrics Enabled: {config.metrics_enabled}")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        logger.error(f"✗ Configuration invalid: {e}")
        sys.exit(1)


def cmd_info(args):
    """Display information about the framework"""
    config_file = args.config
    logger.info("Displaying framework information")

    if config_file:
        logger.debug(f"Loading config from file: {config_file}")
        config = load_config(filepath=config_file)
    else:
        logger.debug("Loading default configuration")
        config = load_config()

    logger.info("=== Empathy Framework Info ===\n")
    logger.info("Configuration:")
    logger.info(f"  User ID: {config.user_id}")
    logger.info(f"  Target Level: {config.target_level}")
    logger.info(f"  Confidence Threshold: {config.confidence_threshold}")
    logger.info("\nPersistence:")
    logger.info(f"  Backend: {config.persistence_backend}")
    logger.info(f"  Path: {config.persistence_path}")
    logger.info(f"  Enabled: {config.persistence_enabled}")
    logger.info("\nMetrics:")
    logger.info(f"  Enabled: {config.metrics_enabled}")
    logger.info(f"  Path: {config.metrics_path}")
    logger.info("\nPattern Library:")
    logger.info(f"  Enabled: {config.pattern_library_enabled}")
    logger.info(f"  Pattern Sharing: {config.pattern_sharing}")
    logger.info(f"  Confidence Threshold: {config.pattern_confidence_threshold}")


def cmd_patterns_list(args):
    """List patterns in a pattern library"""
    filepath = args.library
    format_type = args.format
    logger.info(f"Listing patterns from library: {filepath} (format: {format_type})")

    try:
        if format_type == "json":
            library = PatternPersistence.load_from_json(filepath)
        elif format_type == "sqlite":
            library = PatternPersistence.load_from_sqlite(filepath)
        else:
            logger.error(f"Unknown pattern library format: {format_type}")
            logger.error(f"✗ Unknown format: {format_type}")
            sys.exit(1)

        logger.info(f"Loaded {len(library.patterns)} patterns from {filepath}")
        logger.info(f"=== Pattern Library: {filepath} ===\n")
        logger.info(f"Total patterns: {len(library.patterns)}")
        logger.info(f"Total agents: {len(library.agent_contributions)}")

        if library.patterns:
            logger.info("\nPatterns:")
            for pattern_id, pattern in library.patterns.items():
                logger.info(f"\n  [{pattern_id}] {pattern.name}")
                logger.info(f"    Agent: {pattern.agent_id}")
                logger.info(f"    Type: {pattern.pattern_type}")
                logger.info(f"    Confidence: {pattern.confidence:.2f}")
                logger.info(f"    Usage: {pattern.usage_count}")
                logger.info(f"    Success Rate: {pattern.success_rate:.2f}")
    except FileNotFoundError:
        logger.error(f"Pattern library not found: {filepath}")
        logger.error(f"✗ Pattern library not found: {filepath}")
        sys.exit(1)


def cmd_patterns_export(args):
    """Export patterns from one format to another"""
    input_file = args.input
    input_format = args.input_format
    output_file = args.output
    output_format = args.output_format

    logger.info(f"Exporting patterns from {input_format} to {output_format}")

    # Load from input format
    try:
        if input_format == "json":
            library = PatternPersistence.load_from_json(input_file)
        elif input_format == "sqlite":
            library = PatternPersistence.load_from_sqlite(input_file)
        else:
            logger.error(f"Unknown input format: {input_format}")
            logger.error(f"✗ Unknown input format: {input_format}")
            sys.exit(1)

        logger.info(f"Loaded {len(library.patterns)} patterns from {input_file}")
        logger.info(f"✓ Loaded {len(library.patterns)} patterns from {input_file}")
    except Exception as e:
        logger.error(f"Failed to load patterns: {e}")
        logger.error(f"✗ Failed to load patterns: {e}")
        sys.exit(1)

    # Save to output format
    try:
        if output_format == "json":
            PatternPersistence.save_to_json(library, output_file)
        elif output_format == "sqlite":
            PatternPersistence.save_to_sqlite(library, output_file)

        logger.info(f"Saved {len(library.patterns)} patterns to {output_file}")
        logger.info(f"✓ Saved {len(library.patterns)} patterns to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save patterns: {e}")
        logger.error(f"✗ Failed to save patterns: {e}")
        sys.exit(1)


def cmd_metrics_show(args):
    """Display metrics for a user"""
    db_path = args.db
    user_id = args.user

    logger.info(f"Retrieving metrics for user: {user_id} from {db_path}")

    collector = MetricsCollector(db_path)

    try:
        stats = collector.get_user_stats(user_id)

        logger.info(f"Successfully retrieved metrics for user: {user_id}")
        logger.info(f"=== Metrics for User: {user_id} ===\n")
        logger.info(f"Total Operations: {stats['total_operations']}")
        logger.info(f"Success Rate: {stats['success_rate']:.1%}")
        logger.info(f"Average Response Time: {stats.get('avg_response_time_ms', 0):.0f} ms")
        logger.info(f"\nFirst Use: {stats['first_use']}")
        logger.info(f"Last Use: {stats['last_use']}")

        logger.info("\nEmpathy Level Usage:")
        logger.info(f"  Level 1: {stats.get('level_1_count', 0)} uses")
        logger.info(f"  Level 2: {stats.get('level_2_count', 0)} uses")
        logger.info(f"  Level 3: {stats.get('level_3_count', 0)} uses")
        logger.info(f"  Level 4: {stats.get('level_4_count', 0)} uses")
        logger.info(f"  Level 5: {stats.get('level_5_count', 0)} uses")
    except Exception as e:
        logger.error(f"Failed to retrieve metrics for user {user_id}: {e}")
        logger.error(f"✗ Failed to retrieve metrics: {e}")
        sys.exit(1)


def cmd_state_list(args):
    """List saved user states"""
    state_dir = args.state_dir

    logger.info(f"Listing saved user states from: {state_dir}")

    manager = StateManager(state_dir)
    users = manager.list_users()

    logger.info(f"Found {len(users)} saved user states")
    logger.info(f"=== Saved User States: {state_dir} ===\n")
    logger.info(f"Total users: {len(users)}")

    if users:
        logger.info("\nUsers:")
        for user_id in users:
            logger.info(f"  - {user_id}")


def cmd_run(args):
    """Interactive REPL for testing empathy interactions"""
    config_file = args.config
    user_id = args.user_id or "cli_user"
    level = args.level

    print("🧠 Empathy Framework - Interactive Mode")
    print("=" * 50)

    # Load configuration
    if config_file:
        config = load_config(filepath=config_file)
        print(f"✓ Loaded config from: {config_file}")
    else:
        config = EmpathyConfig(user_id=user_id, target_level=level)
        print("✓ Using default configuration")

    print(f"\nUser ID: {config.user_id}")
    print(f"Target Level: {config.target_level}")
    print(f"Confidence Threshold: {config.confidence_threshold:.0%}")

    # Create EmpathyOS instance
    try:
        empathy = EmpathyOS(
            user_id=config.user_id,
            target_level=config.target_level,
            confidence_threshold=config.confidence_threshold,
            persistence_enabled=config.persistence_enabled,
        )
        print("✓ Empathy OS initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Empathy OS: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Type your input (or 'exit'/'quit' to stop)")
    print("Type 'help' for available commands")
    print("=" * 50 + "\n")

    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == "help":
                print("\nAvailable commands:")
                print("  exit, quit, q - Exit the program")
                print("  help - Show this help message")
                print("  trust - Show current trust level")
                print("  stats - Show session statistics")
                print("  level - Show current empathy level")
                print()
                continue

            if user_input.lower() == "trust":
                trust = empathy.collaboration_state.trust_level
                print(f"\n  Current trust level: {trust:.0%}\n")
                continue

            if user_input.lower() == "level":
                current_level = empathy.collaboration_state.current_level
                print(f"\n  Current empathy level: {current_level}\n")
                continue

            if user_input.lower() == "stats":
                print("\n  Session Statistics:")
                print(f"    Trust: {empathy.collaboration_state.trust_level:.0%}")
                print(f"    Current Level: {empathy.collaboration_state.current_level}")
                print(f"    Target Level: {config.target_level}")
                print()
                continue

            # Process interaction
            start_time = time.time()
            response = empathy.interact(user_id=config.user_id, user_input=user_input, context={})
            duration = (time.time() - start_time) * 1000

            # Display response with level indicator
            level_indicators = ["❌", "🔵", "🟢", "🟡", "🔮"]
            level_indicator = level_indicators[response.level]

            print(f"\nBot {level_indicator} [L{response.level}]: {response.response}")

            # Show predictions if Level 4
            if response.predictions:
                print("\n🔮 Predictions:")
                for pred in response.predictions:
                    print(f"   • {pred}")

            print(
                f"\n  Level: {response.level} | Confidence: {response.confidence:.0%} | Time: {duration:.0f}ms"
            )
            print()

            # Ask for feedback
            feedback = input("Was this helpful? (y/n/skip): ").strip().lower()
            if feedback == "y":
                empathy.record_success(success=True)
                trust = empathy.collaboration_state.trust_level
                print(f"  ✓ Trust increased to {trust:.0%}\n")
            elif feedback == "n":
                empathy.record_success(success=False)
                trust = empathy.collaboration_state.trust_level
                print(f"  ✗ Trust decreased to {trust:.0%}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n")


def cmd_inspect(args):
    """Unified inspection command for patterns, metrics, and state"""
    inspect_type = args.type
    user_id = args.user_id
    db_path = args.db or ".empathy/patterns.db"

    print(f"🔍 Inspecting: {inspect_type}")
    print("=" * 50)

    if inspect_type == "patterns":
        try:
            # Determine file format from extension
            if db_path.endswith(".json"):
                library = PatternPersistence.load_from_json(db_path)
            else:
                library = PatternPersistence.load_from_sqlite(db_path)

            patterns = list(library.patterns.values())

            # Filter by user_id if specified
            if user_id:
                patterns = [p for p in patterns if p.agent_id == user_id]

            print(f"\nPatterns for {'user ' + user_id if user_id else 'all users'}:")
            print(f"  Total patterns: {len(patterns)}")

            if patterns:
                print("\n  Top patterns:")
                # Sort by confidence
                sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)[:10]
                for i, pattern in enumerate(sorted_patterns, 1):
                    print(f"\n  {i}. {pattern.name}")
                    print(f"     Confidence: {pattern.confidence:.0%}")
                    print(f"     Used: {pattern.usage_count} times")
                    print(f"     Success rate: {pattern.success_rate:.0%}")
        except FileNotFoundError:
            print(f"✗ Pattern library not found: {db_path}")
            print("  Tip: Use 'empathy-framework wizard' to set up your first project")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Failed to load patterns: {e}")
            sys.exit(1)

    elif inspect_type == "metrics":
        if not user_id:
            print("✗ User ID required for metrics inspection")
            print("  Usage: empathy-framework inspect metrics --user-id USER_ID")
            sys.exit(1)

        try:
            collector = MetricsCollector(db_path=db_path)
            stats = collector.get_user_stats(user_id)

            print(f"\nMetrics for user: {user_id}")
            print(f"  Total operations: {stats.get('total_operations', 0)}")
            print(f"  Success rate: {stats.get('success_rate', 0):.0%}")
            print(f"  Average response time: {stats.get('avg_response_time_ms', 0):.0f}ms")
            print("\n  Empathy level usage:")
            for level in range(1, 6):
                count = stats.get(f"level_{level}_count", 0)
                print(f"    Level {level}: {count} times")
        except Exception as e:
            print(f"✗ Failed to load metrics: {e}")
            sys.exit(1)

    elif inspect_type == "state":
        state_dir = args.state_dir or ".empathy/state"
        try:
            manager = StateManager(state_dir)
            users = manager.list_users()

            print("\nSaved states:")
            print(f"  Total users: {len(users)}")

            if users:
                print("\n  Users:")
                for uid in users:
                    print(f"    • {uid}")
        except Exception as e:
            print(f"✗ Failed to load state: {e}")
            sys.exit(1)

    print()


def cmd_export(args):
    """Export patterns to file for sharing/backup"""
    output_file = args.output
    user_id = args.user_id
    db_path = args.db or ".empathy/patterns.db"
    format_type = args.format

    print(f"📦 Exporting patterns to: {output_file}")
    print("=" * 50)

    try:
        # Load pattern library from source file
        if db_path.endswith(".json"):
            library = PatternPersistence.load_from_json(db_path)
        else:
            library = PatternPersistence.load_from_sqlite(db_path)

        patterns = list(library.patterns.values())

        # Filter by user_id if specified
        if user_id:
            patterns = [p for p in patterns if p.agent_id == user_id]

        print(f"  Found {len(patterns)} patterns")

        if format_type == "json":
            # Create filtered library if user_id specified
            if user_id:
                filtered_library = PatternLibrary()
                for pattern in patterns:
                    filtered_library.contribute_pattern(pattern.agent_id, pattern)
            else:
                filtered_library = library

            # Export as JSON
            PatternPersistence.save_to_json(filtered_library, output_file)
            print(f"  ✓ Exported {len(patterns)} patterns to {output_file}")
        else:
            print(f"✗ Unsupported format: {format_type}")
            sys.exit(1)

    except FileNotFoundError:
        print(f"✗ Source file not found: {db_path}")
        print("  Tip: Patterns are saved automatically when using the framework")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Export failed: {e}")
        sys.exit(1)

    print()


def cmd_import(args):
    """Import patterns from file (local dev only - SQLite/JSON)"""
    input_file = args.input
    db_path = args.db or ".empathy/patterns.db"

    print(f"📥 Importing patterns from: {input_file}")
    print("=" * 50)

    try:
        # Load patterns from input file
        if input_file.endswith(".json"):
            imported_library = PatternPersistence.load_from_json(input_file)
        else:
            imported_library = PatternPersistence.load_from_sqlite(input_file)

        pattern_count = len(imported_library.patterns)
        print(f"  Found {pattern_count} patterns in file")

        # Load existing library if it exists, otherwise create new one
        try:
            if db_path.endswith(".json"):
                existing_library = PatternPersistence.load_from_json(db_path)
            else:
                existing_library = PatternPersistence.load_from_sqlite(db_path)

            print(f"  Existing library has {len(existing_library.patterns)} patterns")
        except FileNotFoundError:
            existing_library = PatternLibrary()
            print("  Creating new pattern library")

        # Merge imported patterns into existing library
        for pattern in imported_library.patterns.values():
            existing_library.contribute_pattern(pattern.agent_id, pattern)

        # Save merged library (SQLite for local dev)
        if db_path.endswith(".json"):
            PatternPersistence.save_to_json(existing_library, db_path)
        else:
            PatternPersistence.save_to_sqlite(existing_library, db_path)

        print(f"  ✓ Imported {pattern_count} patterns")
        print(f"  ✓ Total patterns in library: {len(existing_library.patterns)}")

    except FileNotFoundError:
        print(f"✗ Input file not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Import failed: {e}")
        sys.exit(1)

    print()


def cmd_wizard(args):
    """Interactive setup wizard"""
    print("🧙 Empathy Framework Setup Wizard")
    print("=" * 50)
    print("\nI'll help you set up your Empathy Framework configuration.\n")

    # Step 1: Use case
    print("1. What's your primary use case?")
    print("   [1] Software development")
    print("   [2] Healthcare applications")
    print("   [3] Customer support")
    print("   [4] Other")

    use_case_choice = input("\nYour choice (1-4): ").strip()
    use_case_map = {
        "1": "software_development",
        "2": "healthcare",
        "3": "customer_support",
        "4": "general",
    }
    use_case = use_case_map.get(use_case_choice, "general")

    # Step 2: Empathy level
    print("\n2. What empathy level do you want to target?")
    print("   [1] Level 1 - Reactive (basic Q&A)")
    print("   [2] Level 2 - Guided (asks clarifying questions)")
    print("   [3] Level 3 - Proactive (offers improvements)")
    print("   [4] Level 4 - Anticipatory (predicts problems) ⭐ Recommended")
    print("   [5] Level 5 - Transformative (reshapes workflows)")

    level_choice = input("\nYour choice (1-5) [4]: ").strip() or "4"
    target_level = int(level_choice) if level_choice in ["1", "2", "3", "4", "5"] else 4

    # Step 3: LLM provider
    print("\n3. Which LLM provider will you use?")
    print("   [1] Anthropic Claude ⭐ Recommended")
    print("   [2] OpenAI GPT-4")
    print("   [3] Local (Ollama)")
    print("   [4] Skip (configure later)")

    llm_choice = input("\nYour choice (1-4) [1]: ").strip() or "1"
    llm_map = {"1": "anthropic", "2": "openai", "3": "ollama", "4": None}
    llm_provider = llm_map.get(llm_choice, "anthropic")

    # Step 4: User ID
    print("\n4. What user ID should we use?")
    user_id = input("User ID [default_user]: ").strip() or "default_user"

    # Generate configuration
    config = {
        "user_id": user_id,
        "target_level": target_level,
        "confidence_threshold": 0.75,
        "persistence_enabled": True,
        "persistence_backend": "sqlite",
        "persistence_path": ".empathy",
        "metrics_enabled": True,
        "use_case": use_case,
    }

    if llm_provider:
        config["llm_provider"] = llm_provider

    # Save configuration
    output_file = "empathy.config.yml"
    print(f"\n5. Creating configuration file: {output_file}")

    # Write YAML config
    yaml_content = f"""# Empathy Framework Configuration
# Generated by setup wizard

# Core settings
user_id: "{config['user_id']}"
target_level: {config['target_level']}
confidence_threshold: {config['confidence_threshold']}

# Use case
use_case: "{config['use_case']}"

# Persistence
persistence_enabled: {str(config['persistence_enabled']).lower()}
persistence_backend: "{config['persistence_backend']}"
persistence_path: "{config['persistence_path']}"

# Metrics
metrics_enabled: {str(config['metrics_enabled']).lower()}
"""

    if llm_provider:
        yaml_content += f"""
# LLM Provider
llm_provider: "{llm_provider}"
"""

    with open(output_file, "w") as f:
        f.write(yaml_content)

    print(f"  ✓ Created {output_file}")

    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print(f"  1. Edit {output_file} to customize settings")

    if llm_provider in ["anthropic", "openai"]:
        env_var = "ANTHROPIC_API_KEY" if llm_provider == "anthropic" else "OPENAI_API_KEY"
        print(f"  2. Set {env_var} environment variable")

    print("  3. Run: empathy-framework run --config empathy.config.yml")
    print("\nHappy empathizing! 🧠✨\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="empathy",
        description="Empathy - Build AI systems with 5 levels of empathy",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    parser_version = subparsers.add_parser("version", help="Display version information")
    parser_version.set_defaults(func=cmd_version)

    # Init command
    parser_init = subparsers.add_parser("init", help="Initialize a new project")
    parser_init.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Configuration format (default: yaml)",
    )
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
    parser_patterns_list.add_argument(
        "--format",
        choices=["json", "sqlite"],
        default="json",
        help="Library format (default: json)",
    )
    parser_patterns_list.set_defaults(func=cmd_patterns_list)

    # Patterns export
    parser_patterns_export = patterns_subparsers.add_parser("export", help="Export patterns")
    parser_patterns_export.add_argument("input", help="Input file path")
    parser_patterns_export.add_argument("output", help="Output file path")
    parser_patterns_export.add_argument(
        "--input-format", choices=["json", "sqlite"], default="json"
    )
    parser_patterns_export.add_argument(
        "--output-format", choices=["json", "sqlite"], default="json"
    )
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
    parser_state_list.add_argument(
        "--state-dir", default="./empathy_state", help="State directory path"
    )
    parser_state_list.set_defaults(func=cmd_state_list)

    # Run command (Interactive REPL)
    parser_run = subparsers.add_parser("run", help="Interactive REPL mode")
    parser_run.add_argument("--config", "-c", help="Configuration file path")
    parser_run.add_argument("--user-id", help="User ID (default: cli_user)")
    parser_run.add_argument(
        "--level", type=int, default=4, help="Target empathy level (1-5, default: 4)"
    )
    parser_run.set_defaults(func=cmd_run)

    # Inspect command (Unified inspection)
    parser_inspect = subparsers.add_parser("inspect", help="Inspect patterns, metrics, or state")
    parser_inspect.add_argument(
        "type",
        choices=["patterns", "metrics", "state"],
        help="Type of inspection (patterns, metrics, or state)",
    )
    parser_inspect.add_argument("--user-id", help="User ID to filter by (optional)")
    parser_inspect.add_argument("--db", help="Database path (default: .empathy/patterns.db)")
    parser_inspect.add_argument(
        "--state-dir", help="State directory path (default: .empathy/state)"
    )
    parser_inspect.set_defaults(func=cmd_inspect)

    # Export command
    parser_export = subparsers.add_parser(
        "export", help="Export patterns to file for sharing/backup"
    )
    parser_export.add_argument("output", help="Output file path")
    parser_export.add_argument(
        "--user-id", help="User ID to export (optional, exports all if not specified)"
    )
    parser_export.add_argument("--db", help="Database path (default: .empathy/patterns.db)")
    parser_export.add_argument(
        "--format", default="json", choices=["json"], help="Export format (default: json)"
    )
    parser_export.set_defaults(func=cmd_export)

    # Import command
    parser_import = subparsers.add_parser("import", help="Import patterns from file")
    parser_import.add_argument("input", help="Input file path")
    parser_import.add_argument("--db", help="Database path (default: .empathy/patterns.db)")
    parser_import.set_defaults(func=cmd_import)

    # Wizard command (Interactive setup)
    parser_wizard = subparsers.add_parser(
        "wizard", help="Interactive setup wizard for creating configuration"
    )
    parser_wizard.set_defaults(func=cmd_wizard)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
