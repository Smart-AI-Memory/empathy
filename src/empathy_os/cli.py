"""
Command-Line Interface for Empathy Framework

Provides CLI commands for:
- Running interactive REPL (empathy run)
- Inspecting patterns, metrics, state (empathy inspect)
- Exporting/importing patterns (empathy export/import)
- Interactive setup wizard (empathy wizard)
- Configuration management
- Power user workflows: morning, ship, fix-all, learn (v2.4+)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import argparse
import sys
import time
from importlib.metadata import version as get_version

from empathy_os import EmpathyConfig, EmpathyOS, load_config
from empathy_os.cost_tracker import cmd_costs
from empathy_os.dashboard import cmd_dashboard
from empathy_os.logging_config import get_logger
from empathy_os.pattern_library import PatternLibrary
from empathy_os.persistence import MetricsCollector, PatternPersistence, StateManager
from empathy_os.templates import cmd_new
from empathy_os.workflows import cmd_fix_all, cmd_learn, cmd_morning, cmd_ship

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


def cmd_patterns_resolve(args):
    """Resolve investigating bug patterns with root cause and fix."""
    from empathy_llm_toolkit.pattern_resolver import PatternResolver

    resolver = PatternResolver(args.patterns_dir)

    # If no bug_id, list investigating bugs
    if not args.bug_id:
        investigating = resolver.list_investigating()
        if not investigating:
            print("No bugs with 'investigating' status found.")
            return

        print(f"\nBugs needing resolution ({len(investigating)}):\n")
        for bug in investigating:
            print(f"  {bug.get('bug_id', 'unknown')}")
            print(f"    Type: {bug.get('error_type', 'unknown')}")
            print(f"    File: {bug.get('file_path', 'unknown')}")
            msg = bug.get("error_message", "N/A")
            print(f"    Message: {msg[:60]}..." if len(msg) > 60 else f"    Message: {msg}")
            print()
        return

    # Validate required args
    if not args.root_cause or not args.fix:
        print("✗ --root-cause and --fix are required when resolving a bug")
        print(
            "  Example: empathy patterns resolve bug_123 --root-cause 'Null check' --fix 'Added ?.'"
        )
        sys.exit(1)

    # Resolve the specified bug
    success = resolver.resolve_bug(
        bug_id=args.bug_id,
        root_cause=args.root_cause,
        fix_applied=args.fix,
        fix_code=args.fix_code,
        resolution_time_minutes=args.time or 0,
        resolved_by=args.resolved_by or "@developer",
    )

    if success:
        print(f"✓ Resolved: {args.bug_id}")

        # Regenerate summary if requested
        if not args.no_regenerate:
            if resolver.regenerate_summary():
                print("✓ Regenerated patterns_summary.md")
            else:
                print("⚠ Failed to regenerate summary")
    else:
        print(f"✗ Failed to resolve: {args.bug_id}")
        print("  Use 'empathy patterns resolve' (no args) to list investigating bugs")
        sys.exit(1)


def cmd_status(args):
    """Session status assistant - prioritized project status report."""
    from empathy_llm_toolkit.session_status import SessionStatusCollector

    config = {"inactivity_minutes": args.inactivity}
    collector = SessionStatusCollector(
        patterns_dir=args.patterns_dir,
        project_root=args.project_root,
        config=config,
    )

    # Check if should show (unless forced)
    if not args.force and not collector.should_show():
        print("No status update needed (recent activity detected).")
        print("Use --force to show status anyway.")
        return

    # Collect status
    status = collector.collect()

    # Handle selection
    if args.select:
        prompt = collector.get_action_prompt(status, args.select)
        if prompt:
            print(f"\nAction prompt for selection {args.select}:\n")
            print(prompt)
        else:
            print(f"Invalid selection: {args.select}")
        return

    # Output
    if args.json:
        print(collector.format_json(status))
    else:
        max_items = None if args.full else 5
        print()
        print(collector.format_output(status, max_items=max_items))
        print()

    # Record interaction
    collector.record_interaction()


def cmd_review(args):
    """Pattern-based code review against historical bugs."""
    import asyncio

    from empathy_software_plugin.wizards.code_review_wizard import CodeReviewWizard

    wizard = CodeReviewWizard(patterns_dir=args.patterns_dir)

    # Run the async analysis
    result = asyncio.run(
        wizard.analyze(
            {
                "files": args.files,
                "staged_only": args.staged,
                "severity_threshold": args.severity,
            }
        )
    )

    # Output results
    if args.json:
        import json

        print(json.dumps(result, indent=2, default=str))
    else:
        print(wizard.format_terminal_output(result))

        # Show recommendations
        recommendations = result.get("recommendations", [])
        if recommendations and result.get("findings"):
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"  • {rec}")


def cmd_health(args):
    """Code health assistant - run health checks and auto-fix issues."""
    import asyncio

    from empathy_llm_toolkit.code_health import (
        AutoFixer,
        CheckCategory,
        HealthCheckRunner,
        HealthTrendTracker,
        format_health_output,
    )

    runner = HealthCheckRunner(
        project_root=args.project_root,
    )

    # Determine what checks to run
    if args.check:
        # Run specific check
        try:
            category = CheckCategory(args.check)
            report_future = runner.run_check(category)
            result = asyncio.run(report_future)
            # Create a minimal report with just this result
            from empathy_llm_toolkit.code_health import HealthReport

            report = HealthReport(project_root=args.project_root)
            report.add_result(result)
        except ValueError:
            print(f"Unknown check category: {args.check}")
            print(f"Available: {', '.join(c.value for c in CheckCategory)}")
            return
    elif args.deep:
        # Run all checks
        print("Running comprehensive health check...\n")
        report = asyncio.run(runner.run_all())
    else:
        # Run quick checks (default)
        report = asyncio.run(runner.run_quick())

    # Handle fix mode
    if args.fix:
        fixer = AutoFixer()

        if args.dry_run:
            # Preview only
            fixes = fixer.preview_fixes(report)
            if fixes:
                print("Would fix the following issues:\n")
                for fix in fixes:
                    safe_indicator = " (safe)" if fix["safe"] else " (needs confirmation)"
                    print(f"  [{fix['category']}] {fix['file']}")
                    print(f"    {fix['issue']}")
                    print(f"    Command: {fix['fix_command']}{safe_indicator}")
                    print()
            else:
                print("No auto-fixable issues found.")
            return

        # Apply fixes
        if args.check:
            try:
                category = CheckCategory(args.check)
                result = asyncio.run(fixer.fix_category(report, category))
            except ValueError:
                result = {"fixed": [], "skipped": [], "failed": []}
        else:
            result = asyncio.run(fixer.fix_all(report, interactive=args.interactive))

        # Report fix results
        if result["fixed"]:
            print(f"✓ Fixed {len(result['fixed'])} issue(s)")
            for fix in result["fixed"][:5]:
                print(f"  - {fix['file_path']}: {fix['message']}")
            if len(result["fixed"]) > 5:
                print(f"  ... and {len(result['fixed']) - 5} more")

        if result["skipped"]:
            if args.interactive:
                print(f"\n⚠ Skipped {len(result['skipped'])} issue(s) (could not auto-fix)")
            else:
                print(
                    f"\n⚠ Skipped {len(result['skipped'])} issue(s) (use --interactive to review)"
                )

        if result["failed"]:
            print(f"\n✗ Failed to fix {len(result['failed'])} issue(s)")

        return

    # Handle trends
    if args.trends:
        tracker = HealthTrendTracker(project_root=args.project_root)
        trends = tracker.get_trends(days=args.trends)

        print(f"📈 Health Trends ({trends['period_days']} days)\n")
        print(f"Average Score: {trends['average_score']}/100")
        print(f"Trend: {trends['trend_direction']} ({trends['score_change']:+d})")

        if trends["data_points"]:
            print("\nRecent scores:")
            for point in trends["data_points"][:7]:
                print(f"  {point['date']}: {point['score']}/100")

        hotspots = tracker.identify_hotspots()
        if hotspots:
            print("\n🔥 Hotspots (files with recurring issues):")
            for spot in hotspots[:5]:
                print(f"  {spot['file']}: {spot['issue_count']} issues")

        return

    # Output report
    if args.json:
        import json

        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        level = 3 if args.full else (2 if args.details else 1)
        print(format_health_output(report, level=level))

    # Record to trend history
    if not args.check:  # Only record full runs
        tracker = HealthTrendTracker(project_root=args.project_root)
        tracker.record_check(report)


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
user_id: "{config["user_id"]}"
target_level: {config["target_level"]}
confidence_threshold: {config["confidence_threshold"]}

# Use case
use_case: "{config["use_case"]}"

# Persistence
persistence_enabled: {str(config["persistence_enabled"]).lower()}
persistence_backend: "{config["persistence_backend"]}"
persistence_path: "{config["persistence_path"]}"

# Metrics
metrics_enabled: {str(config["metrics_enabled"]).lower()}
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


def cmd_frameworks(args):
    """List and manage agent frameworks."""
    import json as json_mod

    try:
        from empathy_llm_toolkit.agent_factory import AgentFactory
        from empathy_llm_toolkit.agent_factory.framework import (
            get_framework_info,
            get_recommended_framework,
        )
    except ImportError:
        print("Agent Factory not available. Install empathy-framework with all dependencies.")
        return 1

    show_all = getattr(args, "all", False)
    recommend_use_case = getattr(args, "recommend", None)
    output_json = getattr(args, "json", False)

    if recommend_use_case:
        # Recommend a framework
        recommended = get_recommended_framework(recommend_use_case)
        info = get_framework_info(recommended)

        if output_json:
            print(
                json_mod.dumps(
                    {"use_case": recommend_use_case, "recommended": recommended.value, **info},
                    indent=2,
                )
            )
        else:
            print(f"\nRecommended framework for '{recommend_use_case}': {info['name']}")
            print(f"  Best for: {', '.join(info['best_for'])}")
            if info.get("install_command"):
                print(f"  Install: {info['install_command']}")
            print()
        return 0

    # List frameworks
    frameworks = AgentFactory.list_frameworks(installed_only=not show_all)

    if output_json:
        print(
            json_mod.dumps(
                [
                    {
                        "id": f["framework"].value,
                        "name": f["name"],
                        "installed": f["installed"],
                        "best_for": f["best_for"],
                        "install_command": f.get("install_command"),
                    }
                    for f in frameworks
                ],
                indent=2,
            )
        )
    else:
        print("\n" + "=" * 60)
        print("  AGENT FRAMEWORKS")
        print("=" * 60 + "\n")

        for f in frameworks:
            status = "INSTALLED" if f["installed"] else "not installed"
            print(f"  {f['name']:20} [{status}]")
            print(f"    Best for: {', '.join(f['best_for'][:3])}")
            if not f["installed"] and f.get("install_command"):
                print(f"    Install:  {f['install_command']}")
            print()

        print("-" * 60)
        print("  Use: empathy frameworks --recommend <use_case>")
        print("  Use cases: general, rag, multi_agent, code_analysis")
        print("=" * 60 + "\n")

    return 0


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

    # Patterns resolve - mark investigating bugs as resolved
    parser_patterns_resolve = patterns_subparsers.add_parser(
        "resolve", help="Resolve investigating bug patterns"
    )
    parser_patterns_resolve.add_argument(
        "bug_id", nargs="?", help="Bug ID to resolve (omit to list investigating)"
    )
    parser_patterns_resolve.add_argument("--root-cause", help="Description of the root cause")
    parser_patterns_resolve.add_argument("--fix", help="Description of the fix applied")
    parser_patterns_resolve.add_argument("--fix-code", help="Code snippet of the fix")
    parser_patterns_resolve.add_argument("--time", type=int, help="Resolution time in minutes")
    parser_patterns_resolve.add_argument(
        "--resolved-by", default="@developer", help="Who resolved it"
    )
    parser_patterns_resolve.add_argument(
        "--patterns-dir", default="./patterns", help="Path to patterns directory"
    )
    parser_patterns_resolve.add_argument(
        "--no-regenerate", action="store_true", help="Skip regenerating summary"
    )
    parser_patterns_resolve.set_defaults(func=cmd_patterns_resolve)

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

    # Status command (Session status assistant)
    parser_status = subparsers.add_parser(
        "status", help="Session status - prioritized project status report"
    )
    parser_status.add_argument(
        "--patterns-dir", default="./patterns", help="Path to patterns directory"
    )
    parser_status.add_argument("--project-root", default=".", help="Project root directory")
    parser_status.add_argument(
        "--force", action="store_true", help="Force show status regardless of inactivity"
    )
    parser_status.add_argument("--full", action="store_true", help="Show all items (no limit)")
    parser_status.add_argument("--json", action="store_true", help="Output as JSON")
    parser_status.add_argument("--select", type=int, help="Select an item to get its action prompt")
    parser_status.add_argument(
        "--inactivity",
        type=int,
        default=60,
        help="Inactivity threshold in minutes (default: 60)",
    )
    parser_status.set_defaults(func=cmd_status)

    # Review command (Pattern-based code review)
    parser_review = subparsers.add_parser(
        "review", help="Pattern-based code review against historical bugs"
    )
    parser_review.add_argument("files", nargs="*", help="Files to review (default: recent changes)")
    parser_review.add_argument("--staged", action="store_true", help="Review staged changes only")
    parser_review.add_argument(
        "--severity",
        choices=["info", "warning", "error"],
        default="info",
        help="Minimum severity to report (default: info)",
    )
    parser_review.add_argument("--patterns-dir", default="./patterns", help="Patterns directory")
    parser_review.add_argument("--json", action="store_true", help="Output as JSON")
    parser_review.set_defaults(func=cmd_review)

    # Health command (Code Health Assistant)
    parser_health = subparsers.add_parser(
        "health", help="Code health assistant - run checks and auto-fix issues"
    )
    parser_health.add_argument(
        "--deep", action="store_true", help="Run comprehensive checks (slower)"
    )
    parser_health.add_argument(
        "--check",
        choices=["lint", "format", "types", "tests", "security", "deps"],
        help="Run specific check only",
    )
    parser_health.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    parser_health.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without applying"
    )
    parser_health.add_argument(
        "--interactive", action="store_true", help="Prompt before applying non-safe fixes"
    )
    parser_health.add_argument("--details", action="store_true", help="Show detailed issue list")
    parser_health.add_argument(
        "--full", action="store_true", help="Show full report with all details"
    )
    parser_health.add_argument(
        "--trends", type=int, metavar="DAYS", help="Show health trends over N days"
    )
    parser_health.add_argument(
        "--project-root", default=".", help="Project root directory (default: current)"
    )
    parser_health.add_argument("--json", action="store_true", help="Output as JSON")
    parser_health.set_defaults(func=cmd_health)

    # =========================================================================
    # POWER USER WORKFLOWS (v2.4+)
    # =========================================================================

    # Morning command (start-of-day briefing)
    parser_morning = subparsers.add_parser(
        "morning", help="Start-of-day briefing with patterns, debt, and focus areas"
    )
    parser_morning.add_argument(
        "--patterns-dir", default="./patterns", help="Path to patterns directory"
    )
    parser_morning.add_argument("--project-root", default=".", help="Project root directory")
    parser_morning.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser_morning.set_defaults(func=cmd_morning)

    # Ship command (pre-commit validation)
    parser_ship = subparsers.add_parser("ship", help="Pre-commit validation pipeline")
    parser_ship.add_argument(
        "--patterns-dir", default="./patterns", help="Path to patterns directory"
    )
    parser_ship.add_argument("--project-root", default=".", help="Project root directory")
    parser_ship.add_argument(
        "--skip-sync", action="store_true", help="Skip syncing patterns to Claude"
    )
    parser_ship.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser_ship.set_defaults(func=cmd_ship)

    # Fix-all command (auto-fix everything)
    parser_fix_all = subparsers.add_parser(
        "fix-all", help="Auto-fix all fixable lint and format issues"
    )
    parser_fix_all.add_argument("--project-root", default=".", help="Project root directory")
    parser_fix_all.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without applying"
    )
    parser_fix_all.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser_fix_all.set_defaults(func=cmd_fix_all)

    # Learn command (pattern learning from git history)
    parser_learn = subparsers.add_parser(
        "learn", help="Learn patterns from git history and bug fixes"
    )
    parser_learn.add_argument(
        "--patterns-dir", default="./patterns", help="Path to patterns directory"
    )
    parser_learn.add_argument(
        "--analyze", type=int, metavar="N", help="Analyze last N commits (default: 10)"
    )
    parser_learn.add_argument(
        "--watch", action="store_true", help="Watch for new commits (not yet implemented)"
    )
    parser_learn.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser_learn.set_defaults(func=cmd_learn)

    # Costs command (cost tracking dashboard)
    parser_costs = subparsers.add_parser(
        "costs", help="View API cost tracking and savings from model routing"
    )
    parser_costs.add_argument(
        "--days", type=int, default=7, help="Number of days to include (default: 7)"
    )
    parser_costs.add_argument("--empathy-dir", default=".empathy", help="Empathy data directory")
    parser_costs.add_argument("--json", action="store_true", help="Output as JSON")
    parser_costs.set_defaults(func=cmd_costs)

    # New command (project scaffolding)
    parser_new = subparsers.add_parser("new", help="Create a new project from a template")
    parser_new.add_argument(
        "template",
        nargs="?",
        help="Template name (minimal, python-cli, python-fastapi, python-agent)",
    )
    parser_new.add_argument("name", nargs="?", help="Project name")
    parser_new.add_argument("--output", "-o", help="Output directory (default: ./<project-name>)")
    parser_new.add_argument("--force", "-f", action="store_true", help="Overwrite existing files")
    parser_new.add_argument("--list", "-l", action="store_true", help="List available templates")
    parser_new.set_defaults(func=cmd_new)

    # Dashboard command (visual web interface)
    parser_dashboard = subparsers.add_parser("dashboard", help="Launch visual dashboard in browser")
    parser_dashboard.add_argument(
        "--port", type=int, default=8765, help="Port to run on (default: 8765)"
    )
    parser_dashboard.add_argument(
        "--patterns-dir", default="./patterns", help="Path to patterns directory"
    )
    parser_dashboard.add_argument(
        "--empathy-dir", default=".empathy", help="Empathy data directory"
    )
    parser_dashboard.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )
    parser_dashboard.set_defaults(func=cmd_dashboard)

    # Frameworks command (agent framework management)
    parser_frameworks = subparsers.add_parser(
        "frameworks",
        help="List and manage agent frameworks (LangChain, LangGraph, AutoGen, Haystack)",
    )
    parser_frameworks.add_argument(
        "--all", action="store_true", help="Show all frameworks including uninstalled"
    )
    parser_frameworks.add_argument(
        "--recommend",
        metavar="USE_CASE",
        help="Recommend framework for use case (general, rag, multi_agent, code_analysis)",
    )
    parser_frameworks.add_argument("--json", action="store_true", help="Output as JSON")
    parser_frameworks.set_defaults(func=cmd_frameworks)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
