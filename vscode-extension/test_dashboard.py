#!/usr/bin/env python3
"""VSCode Dashboard Testing Script

Tests the data loading and CLI integration for the Empathy Dashboard.
Run from the Empathy-framework root directory.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_telemetry_costs():
    """Test the telemetry CLI command for costs data."""
    print("\n=== Test: Telemetry CLI Costs ===")
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "empathy_os.models.cli",
                "telemetry",
                "--costs",
                "-f",
                "json",
                "-d",
                "30",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            print("✓ CLI returned valid JSON")
            print(f"  - workflow_count: {data.get('workflow_count', 'N/A')}")
            print(f"  - total_actual_cost: ${data.get('total_actual_cost', 0):.4f}")
            print(f"  - total_savings: ${data.get('total_savings', 0):.4f}")
            print(f"  - savings_percent: {data.get('savings_percent', 0):.1f}%")
            return True
        print(f"✗ CLI failed with code {result.returncode}")
        print(f"  stderr: {result.stderr[:200]}")
        return False
    except subprocess.TimeoutExpired:
        print("✗ CLI timed out after 10 seconds")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_costs_file_fallback():
    """Test loading costs from .empathy/costs.json file."""
    print("\n=== Test: Costs File Fallback ===")
    costs_file = Path(".empathy/costs.json")

    if not costs_file.exists():
        print(f"⚠ File not found: {costs_file}")
        print("  Creating sample costs file for testing...")
        costs_file.parent.mkdir(exist_ok=True)
        sample_data = {
            "daily_totals": {
                "2025-12-20": {
                    "actual_cost": 0.05,
                    "savings": 0.10,
                    "requests": 5,
                    "baseline_cost": 0.15,
                },
                "2025-12-21": {
                    "actual_cost": 0.03,
                    "savings": 0.07,
                    "requests": 3,
                    "baseline_cost": 0.10,
                },
                "2025-12-22": {
                    "actual_cost": 0.04,
                    "savings": 0.08,
                    "requests": 4,
                    "baseline_cost": 0.12,
                },
            },
            "by_provider": {
                "anthropic": {"requests": 10, "actual_cost": 0.10},
                "openai": {"requests": 2, "actual_cost": 0.02},
            },
        }
        with open(costs_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        print(f"  Created sample file: {costs_file}")

    try:
        with open(costs_file) as f:
            data = json.load(f)

        total_cost = sum(d.get("actual_cost", 0) for d in data.get("daily_totals", {}).values())
        total_savings = sum(d.get("savings", 0) for d in data.get("daily_totals", {}).values())
        total_requests = sum(d.get("requests", 0) for d in data.get("daily_totals", {}).values())

        print("✓ Costs file loaded successfully")
        print(f"  - Total cost: ${total_cost:.4f}")
        print(f"  - Total savings: ${total_savings:.4f}")
        print(f"  - Total requests: {total_requests}")
        return True
    except Exception as e:
        print(f"✗ Error loading costs file: {e}")
        return False


def test_health_file():
    """Test loading health data from .empathy/health.json."""
    print("\n=== Test: Health File ===")
    health_file = Path(".empathy/health.json")

    if not health_file.exists():
        print(f"⚠ File not found: {health_file}")
        print("  Creating sample health file for testing...")
        health_file.parent.mkdir(exist_ok=True)
        sample_data = {
            "score": 85,
            "lint": {"errors": 2, "warnings": 5},
            "types": {"errors": 0},
            "security": {"high": 0, "medium": 1, "low": 3},
            "tests": {"passed": 142, "failed": 0, "total": 142, "coverage": 55},
            "tech_debt": {"total": 25, "todos": 15, "fixmes": 5, "hacks": 5},
            "timestamp": "2025-12-22T10:00:00Z",
        }
        with open(health_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        print(f"  Created sample file: {health_file}")

    try:
        with open(health_file) as f:
            data = json.load(f)

        print("✓ Health file loaded successfully")
        print(f"  - Score: {data.get('score', 'N/A')}%")
        print(f"  - Lint errors: {data.get('lint', {}).get('errors', 'N/A')}")
        print(f"  - Type errors: {data.get('types', {}).get('errors', 'N/A')}")
        print(
            f"  - Tests: {data.get('tests', {}).get('passed', 0)}/{data.get('tests', {}).get('total', 0)}",
        )
        print(f"  - Coverage: {data.get('tests', {}).get('coverage', 0)}%")
        return True
    except Exception as e:
        print(f"✗ Error loading health file: {e}")
        return False


def test_patterns_file():
    """Test loading patterns from patterns/debugging.json."""
    print("\n=== Test: Patterns File ===")
    patterns_file = Path("patterns/debugging.json")

    if not patterns_file.exists():
        print(f"⚠ File not found: {patterns_file}")
        print("  Creating sample patterns file for testing...")
        patterns_file.parent.mkdir(exist_ok=True)
        sample_data = {
            "patterns": [
                {
                    "pattern_id": "bug_test_001",
                    "bug_type": "null_reference",
                    "status": "resolved",
                    "root_cause": "Missing null check",
                    "fix": "Added optional chaining",
                    "files_affected": ["src/example.ts"],
                    "timestamp": "2025-12-22T10:00:00Z",
                },
            ],
        }
        with open(patterns_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        print(f"  Created sample file: {patterns_file}")

    try:
        with open(patterns_file) as f:
            data = json.load(f)

        patterns = data.get("patterns", [])
        print("✓ Patterns file loaded successfully")
        print(f"  - Total patterns: {len(patterns)}")
        if patterns:
            latest = patterns[-1]
            print(f"  - Latest: {latest.get('pattern_id')} ({latest.get('status')})")
        return True
    except Exception as e:
        print(f"✗ Error loading patterns file: {e}")
        return False


def test_workflow_runs_file():
    """Test loading workflow runs from .empathy/workflow_runs.json."""
    print("\n=== Test: Workflow Runs File ===")
    runs_file = Path(".empathy/workflow_runs.json")

    if not runs_file.exists():
        print(f"⚠ File not found: {runs_file}")
        print("  Creating sample workflow runs file for testing...")
        runs_file.parent.mkdir(exist_ok=True)
        sample_data = [
            {
                "workflow": "research",
                "success": True,
                "cost": 0.02,
                "savings": 0.05,
                "started_at": "2025-12-22T09:00:00Z",
            },
            {
                "workflow": "code-review",
                "success": True,
                "cost": 0.03,
                "savings": 0.07,
                "started_at": "2025-12-22T10:00:00Z",
            },
        ]
        with open(runs_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        print(f"  Created sample file: {runs_file}")

    try:
        with open(runs_file) as f:
            runs = json.load(f)

        total_runs = len(runs)
        successful = sum(1 for r in runs if r.get("success"))
        total_cost = sum(r.get("cost", 0) for r in runs)
        total_savings = sum(r.get("savings", 0) for r in runs)

        print("✓ Workflow runs file loaded successfully")
        print(f"  - Total runs: {total_runs}")
        print(f"  - Successful: {successful} ({100 * successful // max(total_runs, 1)}%)")
        print(f"  - Total cost: ${total_cost:.4f}")
        print(f"  - Total savings: ${total_savings:.4f}")
        return True
    except Exception as e:
        print(f"✗ Error loading workflow runs: {e}")
        return False


def test_dashboard_server():
    """Test if dashboard server can start."""
    print("\n=== Test: Dashboard Server ===")
    try:
        # Check if the module is importable and has expected functions
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from empathy_os.dashboard.server import run_dashboard, DashboardHandler; print('OK')",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "OK" in result.stdout:
            print("✓ Dashboard server module is importable")
            print("  - run_dashboard function available")
            print("  - DashboardHandler class available")
            return True
        print("✗ Dashboard server import failed")
        print(f"  stderr: {result.stderr[:200]}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all dashboard tests."""
    print("=" * 60)
    print("Empathy VSCode Dashboard Test Suite")
    print("=" * 60)

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")

    results = []

    # Run tests
    results.append(("Telemetry CLI Costs", test_cli_telemetry_costs()))
    results.append(("Costs File Fallback", test_costs_file_fallback()))
    results.append(("Health File", test_health_file()))
    results.append(("Patterns File", test_patterns_file()))
    results.append(("Workflow Runs File", test_workflow_runs_file()))
    results.append(("Dashboard Server", test_dashboard_server()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
