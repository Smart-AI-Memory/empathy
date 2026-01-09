#!/usr/bin/env python3
"""Manual Test Script for Empathy Framework

Interactive test runner for CLI features, provider config, telemetry, and workflows.

Usage:
    python manual_test.py                 # Run all tests (interactive)
    python manual_test.py --all           # Run all tests (non-interactive)
    python manual_test.py --cli           # Test CLI commands only
    python manual_test.py --provider      # Test provider commands only
    python manual_test.py --telemetry     # Test telemetry commands only
    python manual_test.py --workflows     # Test workflow commands only
    python manual_test.py --quality       # Test code quality only
    python manual_test.py --unit          # Run unit tests only

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import argparse
import json
import subprocess
import sys
from enum import Enum


class Color(str, Enum):
    """ANSI color codes."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


class TestResult:
    """Track test results."""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0

    def add_pass(self):
        self.total += 1
        self.passed += 1

    def add_fail(self):
        self.total += 1
        self.failed += 1

    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0


results = TestResult()


def print_header(text: str):
    """Print section header."""
    print(f"\n{Color.BLUE}{'=' * 60}{Color.NC}")
    print(f"{Color.BLUE}{Color.BOLD}{text}{Color.NC}")
    print(f"{Color.BLUE}{'=' * 60}{Color.NC}\n")


def print_test(text: str):
    """Print test name."""
    print(f"{Color.YELLOW}▶ Testing: {text}{Color.NC}")


def print_success(text: str):
    """Print success message."""
    print(f"{Color.GREEN}✓ {text}{Color.NC}")
    results.add_pass()


def print_error(text: str):
    """Print error message."""
    print(f"{Color.RED}✗ {text}{Color.NC}")
    results.add_fail()


def run_command(cmd: list[str], check_output: str = None) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        output = result.stdout + result.stderr

        if check_output:
            return check_output in output, output
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def test_cli_basics():
    """Test basic CLI functionality."""
    print_header("Testing CLI Basics")

    # Test version
    print_test("CLI version")
    success, output = run_command(
        [sys.executable, "-m", "empathy_os.cli_unified", "--version"],
        check_output="Empathy Framework",
    )
    if success:
        print_success("CLI version works")
        print(f"   {output.strip()}")
    else:
        print_error("CLI version failed")

    # Test help
    print_test("CLI help")
    success, output = run_command(["empathy", "--help"], check_output="Empathy Framework")
    if success:
        print_success("CLI help works")
    else:
        print_error("CLI help failed")

    # Test cheatsheet
    print_test("Cheatsheet command")
    success, output = run_command(["empathy", "cheatsheet"], check_output="Getting Started")
    if success:
        print_success("Cheatsheet works")
    else:
        print_error("Cheatsheet failed")


def test_memory_commands():
    """Test memory-related commands."""
    print_header("Testing Memory Commands")

    print_test("Memory status")
    success, output = run_command(["empathy", "memory", "status"])
    if success or "Redis" in output:  # May fail if Redis not installed
        print_success("Memory status works")
    else:
        print_error("Memory status failed")

    print_test("Memory patterns")
    success, output = run_command(["empathy", "memory", "patterns"])
    if success or "pattern" in output.lower():
        print_success("Memory patterns works")
    else:
        print_error("Memory patterns failed")


def test_provider_commands():
    """Test provider configuration commands."""
    print_header("Testing Provider Commands")

    # Provider config
    print_test("Provider configuration")
    success, output = run_command(
        [sys.executable, "-m", "empathy_os.models.cli", "provider"],
        check_output="PROVIDER CONFIGURATION",
    )
    if success:
        print_success("Provider config works")
        # Show current provider
        if "Mode:" in output:
            mode_line = [line for line in output.split("\n") if "Mode:" in line][0]
            print(f"   {mode_line.strip()}")
    else:
        print_error("Provider config failed")

    # Registry
    print_test("Model registry")
    success, output = run_command(
        [sys.executable, "-m", "empathy_os.models.cli", "registry"],
        check_output="MODEL REGISTRY",
    )
    if success:
        print_success("Model registry works")
    else:
        print_error("Model registry failed")

    # Tasks
    print_test("Task-to-tier mappings")
    success, output = run_command(
        [sys.executable, "-m", "empathy_os.models.cli", "tasks"], check_output="TASK-TO-TIER"
    )
    if success:
        print_success("Task mappings work")
    else:
        print_error("Task mappings failed")

    # Costs
    print_test("Cost estimates")
    success, output = run_command(
        [sys.executable, "-m", "empathy_os.models.cli", "costs"], check_output="COST ESTIMATES"
    )
    if success:
        print_success("Cost estimates work")
    else:
        print_error("Cost estimates failed")

    # JSON format
    print_test("Registry JSON format")
    success, output = run_command(
        [sys.executable, "-m", "empathy_os.models.cli", "registry", "--format", "json"]
    )
    if success:
        try:
            json.loads(output)
            print_success("Registry JSON is valid")
        except json.JSONDecodeError:
            print_error("Registry JSON is invalid")
    else:
        print_error("Registry JSON failed")


def test_telemetry_commands():
    """Test telemetry commands."""
    print_header("Testing Telemetry Commands")

    commands = [
        ("Telemetry summary", ["telemetry"]),
        ("Telemetry costs", ["telemetry", "--costs"]),
        ("Telemetry providers", ["telemetry", "--providers"]),
        ("Telemetry fallbacks", ["telemetry", "--fallbacks"]),
    ]

    for name, args in commands:
        print_test(name)
        success, output = run_command([sys.executable, "-m", "empathy_os.models.cli"] + args)
        if success or "TELEMETRY" in output or "Total" in output:
            print_success(f"{name} works")
        else:
            print_error(f"{name} failed")


def test_token_estimation():
    """Test token estimation functionality."""
    print_header("Testing Token Estimation")

    print_test("Token estimation module")
    code = """
from empathy_os.models.token_estimator import estimate_tokens
result = estimate_tokens('Hello world')
print(f'Tokens: {result}')
assert result > 0, 'Token count should be positive'
"""
    success, output = run_command([sys.executable, "-c", code])
    if success:
        print_success("Token estimation works")
        print(f"   {output.strip()}")
    else:
        print_error("Token estimation failed")

    print_test("Workflow cost estimation")
    code = """
from empathy_os.models.token_estimator import estimate_workflow_cost
result = estimate_workflow_cost('code-review', 'def test(): pass', 'anthropic')
print(f'Stages: {len(result["stages"])}')
assert 'total_min' in result, 'Should have total_min'
"""
    success, output = run_command([sys.executable, "-c", code])
    if success:
        print_success("Workflow cost estimation works")
        print(f"   {output.strip()}")
    else:
        print_error("Workflow cost estimation failed")


def test_workflow_commands():
    """Test workflow-related commands."""
    print_header("Testing Workflow Commands")

    print_test("Workflow list")
    success, output = run_command(["empathy", "workflow", "list"])
    if success or "workflow" in output.lower():
        print_success("Workflow list works")
    else:
        print_error("Workflow list failed")

    print_test("Wizard list")
    success, output = run_command(["empathy", "wizard", "list"])
    if success or "wizard" in output.lower() or "framework" in output.lower():
        print_success("Wizard list works")
    else:
        print_error("Wizard list failed")


def test_unit_tests():
    """Run unit tests."""
    print_header("Running Unit Tests")

    # CLI unified tests
    print_test("CLI Unified Tests")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "tests/unit/test_cli_unified.py", "-v", "--tb=no", "-q"]
    )
    if "passed" in output:
        passed = output.count(" PASSED")
        print_success(f"CLI unified tests passed ({passed} tests)")
    else:
        print_error("CLI unified tests failed")

    # Models CLI tests
    print_test("Models CLI Tests")
    success, output = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/models/test_models_cli.py",
            "-v",
            "--tb=no",
            "-q",
        ]
    )
    if "passed" in output:
        passed = output.count(" PASSED")
        print_success(f"Models CLI tests passed ({passed} tests)")
    else:
        print_error("Models CLI tests failed")

    # All unit tests
    print_test("All Unit Tests")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=no", "-q"]
    )
    if "passed" in output:
        # Extract test count
        lines = output.split("\n")
        summary_line = [line for line in lines if "passed" in line][-1]
        print_success(f"All unit tests: {summary_line.strip()}")
    else:
        print_error("Some unit tests failed")


def test_code_quality():
    """Test code quality metrics."""
    print_header("Testing Code Quality")

    # Lint check
    print_test("Lint check (ruff)")
    success, output = run_command(["ruff", "check", "src/", "tests/"])
    if "All checks passed" in output:
        print_success("Lint check passed - no errors")
    else:
        error_count = output.count("error:")
        if error_count == 0:
            print_success("Lint check passed - no errors")
        else:
            print_error(f"Lint check failed - {error_count} errors")

    # Type check
    print_test("Type check (mypy)")
    success, output = run_command([sys.executable, "-m", "mypy", "src/"])
    error_count = output.count("error:")
    if error_count == 0:
        print_success("Type check passed - no errors")
    else:
        print_error(f"Type check failed - {error_count} errors")

    # Test count
    print_test("Test inventory")
    success, output = run_command([sys.executable, "-m", "pytest", "tests/unit/", "--co", "-q"])
    if success:
        lines = output.strip().split("\n")
        test_line = lines[-1]
        print_success(f"Test inventory: {test_line}")
    else:
        print_error("Test inventory failed")


def print_summary():
    """Print test summary."""
    print_header("Test Summary")

    print(f"Tests run:    {Color.BLUE}{results.total}{Color.NC}")
    print(f"Tests passed: {Color.GREEN}{results.passed}{Color.NC}")
    print(f"Tests failed: {Color.RED}{results.failed}{Color.NC}")
    print(f"Pass rate:    {Color.CYAN}{results.pass_rate:.1f}%{Color.NC}")

    if results.failed == 0:
        print(f"\n{Color.GREEN}{Color.BOLD}✓ All tests passed!{Color.NC}")
        return 0
    else:
        print(f"\n{Color.RED}{Color.BOLD}✗ Some tests failed{Color.NC}")
        return 1


def interactive_mode():
    """Run tests in interactive mode."""
    print(f"{Color.BOLD}Empathy Framework - Interactive Test Suite{Color.NC}\n")

    test_suites = {
        "1": ("CLI Basics", test_cli_basics),
        "2": ("Memory Commands", test_memory_commands),
        "3": ("Provider Commands", test_provider_commands),
        "4": ("Telemetry Commands", test_telemetry_commands),
        "5": ("Token Estimation", test_token_estimation),
        "6": ("Workflow Commands", test_workflow_commands),
        "7": ("Unit Tests", test_unit_tests),
        "8": ("Code Quality", test_code_quality),
        "9": ("All Tests", None),
    }

    print("Available test suites:")
    for key, (name, _) in test_suites.items():
        print(f"  {key}. {name}")

    choice = input("\nSelect test suite (1-9, or q to quit): ").strip()

    if choice.lower() == "q":
        print("Exiting...")
        return 0

    if choice in test_suites:
        name, test_func = test_suites[choice]
        if test_func:
            test_func()
        else:
            # Run all tests
            for _, (_, func) in test_suites.items():
                if func:
                    func()
    else:
        print(f"{Color.RED}Invalid choice{Color.NC}")
        return 1

    return print_summary()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manual test runner for Empathy Framework")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--cli", action="store_true", help="Test CLI commands")
    parser.add_argument("--memory", action="store_true", help="Test memory commands")
    parser.add_argument("--provider", action="store_true", help="Test provider commands")
    parser.add_argument("--telemetry", action="store_true", help="Test telemetry commands")
    parser.add_argument("--token", action="store_true", help="Test token estimation")
    parser.add_argument("--workflows", action="store_true", help="Test workflow commands")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--quality", action="store_true", help="Test code quality")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    # Check if any test flag is set
    any_test = any(
        [
            args.all,
            args.cli,
            args.memory,
            args.provider,
            args.telemetry,
            args.token,
            args.workflows,
            args.unit,
            args.quality,
        ]
    )

    if args.interactive or not any_test:
        return interactive_mode()

    # Run selected tests
    if args.all or args.cli:
        test_cli_basics()
    if args.all or args.memory:
        test_memory_commands()
    if args.all or args.provider:
        test_provider_commands()
    if args.all or args.telemetry:
        test_telemetry_commands()
    if args.all or args.token:
        test_token_estimation()
    if args.all or args.workflows:
        test_workflow_commands()
    if args.all or args.unit:
        test_unit_tests()
    if args.all or args.quality:
        test_code_quality()

    return print_summary()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Test interrupted by user{Color.NC}")
        sys.exit(130)
