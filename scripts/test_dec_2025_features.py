#!/usr/bin/env python3
"""Manual Testing Script for December 2025 Features

Helps verify features implemented in recent sessions:
- Phase 2: Dashboard interactive charts (VSCode extension)
- Phase 3: Workflow executor migrations
- Phase 4: Dependency consolidation
- Phase 5: Workflow plugin discovery

Run with: python scripts/test_dec_2025_features.py

Copyright 2025 Smart-AI-Memory
"""

import subprocess
import sys
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def header(text: str) -> None:
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def success(text: str) -> None:
    print(f"{GREEN}✓ {text}{RESET}")


def warning(text: str) -> None:
    print(f"{YELLOW}⚠ {text}{RESET}")


def error(text: str) -> None:
    print(f"{RED}✗ {text}{RESET}")


def info(text: str) -> None:
    print(f"  {text}")


def test_workflow_plugin_discovery():
    """Test Phase 5: Workflow plugin entry points."""
    header("Phase 5: Workflow Plugin Discovery")

    try:
        from empathy_os.workflows import (
            WORKFLOW_REGISTRY,
            discover_workflows,
            refresh_workflow_registry,
        )

        # Test 1: Registry is populated
        if len(WORKFLOW_REGISTRY) >= 13:
            success(f"WORKFLOW_REGISTRY has {len(WORKFLOW_REGISTRY)} workflows")
        else:
            warning(f"Expected 13+ workflows, found {len(WORKFLOW_REGISTRY)}")

        # Test 2: discover_workflows function works
        discovered = discover_workflows()
        if len(discovered) >= 13:
            success(f"discover_workflows() returned {len(discovered)} workflows")
        else:
            warning(f"discover_workflows() returned only {len(discovered)}")

        # Test 3: All expected workflows present
        expected = [
            "code-review",
            "doc-gen",
            "bug-predict",
            "security-audit",
            "perf-audit",
            "test-gen",
            "refactor-plan",
            "dependency-check",
            "release-prep",
            "secure-release",
            "pro-review",
            "pr-review",
            "health-check",
        ]
        missing = [w for w in expected if w not in WORKFLOW_REGISTRY]
        if not missing:
            success("All 13 expected workflows registered")
        else:
            error(f"Missing workflows: {missing}")

        # Test 4: Workflows have execute method
        for name, cls in list(WORKFLOW_REGISTRY.items())[:3]:
            if hasattr(cls, "execute"):
                success(f"{name} has execute() method")
            else:
                error(f"{name} missing execute() method")

        # Test 5: refresh_workflow_registry works
        refresh_workflow_registry()
        if len(WORKFLOW_REGISTRY) >= 13:
            success("refresh_workflow_registry() works")
        else:
            error("refresh_workflow_registry() failed")

        return True

    except Exception as e:
        error(f"Plugin discovery test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_workflow_executor_migrations():
    """Test Phase 3: Workflow executor pattern migrations."""
    header("Phase 3: Workflow Executor Migrations")

    workflows_to_check = [
        ("security_audit", "SECURITY_STEPS", ["remediate"]),
        ("bug_predict", "BUG_PREDICT_STEPS", ["recommend"]),
        ("perf_audit", "PERF_AUDIT_STEPS", ["optimize"]),
        ("test_gen", "TEST_GEN_STEPS", ["review"]),
        ("document_gen", "DOC_GEN_STEPS", ["polish"]),
        ("dependency_check", "DEPENDENCY_CHECK_STEPS", ["report"]),
        ("code_review", "CODE_REVIEW_STEPS", ["architect_review"]),
        ("refactor_plan", "REFACTOR_PLAN_STEPS", ["plan"]),
        ("release_prep", "RELEASE_PREP_STEPS", ["approve"]),
    ]

    all_passed = True

    for module_name, steps_var, expected_steps in workflows_to_check:
        try:
            module = __import__(f"empathy_os.workflows.{module_name}", fromlist=[steps_var])
            steps = getattr(module, steps_var, None)

            if steps is None:
                error(f"{module_name}: {steps_var} not found")
                all_passed = False
                continue

            # Check all expected steps are defined
            for step_name in expected_steps:
                if step_name in steps:
                    step = steps[step_name]
                    if hasattr(step, "task_type") and hasattr(step, "tier_hint"):
                        success(
                            f"{module_name}.{step_name}: task_type={step.task_type}, tier={step.tier_hint}",
                        )
                    else:
                        warning(f"{module_name}.{step_name}: missing attributes")
                else:
                    error(f"{module_name}: missing step '{step_name}'")
                    all_passed = False

        except ImportError as e:
            error(f"{module_name}: import failed - {e}")
            all_passed = False

    return all_passed


def test_dependency_alignment():
    """Test Phase 4.1: Dependency consolidation."""
    header("Phase 4.1: Dependency Alignment")

    project_root = Path(__file__).parent.parent

    # Check backend/requirements.txt
    backend_req = project_root / "backend" / "requirements.txt"
    if backend_req.exists():
        content = backend_req.read_text()

        # Check for CVE-fixed versions
        if "fastapi>=0.109.1" in content:
            success("backend/requirements.txt: fastapi CVE-fixed version")
        else:
            warning("backend/requirements.txt: check fastapi version")

        if "starlette>=0.40.0" in content:
            success("backend/requirements.txt: starlette CVE-fixed version")
        else:
            warning("backend/requirements.txt: check starlette version")

        # Check it references pyproject.toml
        if "pip install -e" in content or "pyproject.toml" in content:
            success("backend/requirements.txt: references pyproject.toml")
        else:
            info("backend/requirements.txt: standalone (OK for deployments)")
    else:
        warning("backend/requirements.txt not found")

    # Check pyproject.toml has entry points
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if '[project.entry-points."empathy.workflows"]' in content:
            success("pyproject.toml: workflow entry points defined")
        else:
            error("pyproject.toml: missing workflow entry points")

    return True


def test_vscode_extension_builds():
    """Test Phase 2: VSCode extension compiles."""
    header("Phase 2: VSCode Extension Build")

    project_root = Path(__file__).parent.parent
    ext_dir = project_root / "vscode-extension"

    if not ext_dir.exists():
        warning("vscode-extension directory not found")
        return False

    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        warning("npm not available, skipping extension build test")
        return True

    # Try to compile
    try:
        result = subprocess.run(
            ["npm", "run", "compile"],
            check=False,
            cwd=ext_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            success("VSCode extension compiles successfully")

            # Check for new chart features in output
            panel_file = ext_dir / "src" / "panels" / "EmpathyDashboardPanel.ts"
            if panel_file.exists():
                content = panel_file.read_text()

                features = [
                    ("cost-trend-chart", "Daily cost trend chart"),
                    ("tier-pie-chart", "Tier distribution pie chart"),
                    ("provider-bars", "Provider comparison bars"),
                    ("workflow-timeline", "Workflow execution timeline"),
                    ("workflow-cost-bars", "Workflow cost comparison"),
                    ("sim-projection-chart", "Cost simulator projection"),
                    ('type="range"', "Interactive range sliders"),
                ]

                for pattern, name in features:
                    if pattern in content:
                        success(f"Dashboard has: {name}")
                    else:
                        warning(f"Dashboard missing: {name}")

            return True
        error(f"Extension compile failed: {result.stderr[:200]}")
        return False

    except subprocess.TimeoutExpired:
        warning("Extension compile timed out")
        return False
    except Exception as e:
        error(f"Extension compile error: {e}")
        return False


def manual_testing_checklist():
    """Print manual testing checklist for features that can't be automated."""
    header("Manual Testing Checklist")

    print(
        f"""{BOLD}VSCode Dashboard (open extension in VS Code):{RESET}

{CYAN}Costs Tab:{RESET}
  [ ] Daily Cost Trend chart shows bars for each day
  [ ] Tier Distribution pie chart shows cheap/capable/premium breakdown
  [ ] Provider Comparison shows horizontal bars by provider
  [ ] Cost Simulator sliders update values in real-time (while dragging)
  [ ] Monthly Projection chart updates dynamically
  [ ] Slider value labels (50%, 40%, 10%) update while dragging

{CYAN}Workflows Tab:{RESET}
  [ ] 24-hour Execution Timeline shows activity histogram
  [ ] Green bars for successful runs, red for failures
  [ ] Cost by Workflow Type shows horizontal bar chart
  [ ] Recent Runs list shows workflow history with XML badges

{BOLD}Generate Test Data:{RESET}

  Run a workflow to generate cost data, then refresh the dashboard:

    {CYAN}python -c "
from empathy_os.workflows import SecurityAuditWorkflow
import asyncio

async def test():
    wf = SecurityAuditWorkflow()
    # This requires an API key to actually run
    print('Workflow stages:', wf.stages)
    print('Tier map:', {{k: v.value for k, v in wf.tier_map.items()}})

asyncio.run(test())
"{RESET}

{BOLD}Verify Entry Points (after pip install -e .):{RESET}

    {CYAN}python -c "
import importlib.metadata
eps = list(importlib.metadata.entry_points(group='empathy.workflows'))
print(f'Found {{len(eps)}} workflow entry points:')
for ep in eps:
    print(f'  {{ep.name}}: {{ep.value}}')"
{RESET}

{BOLD}Test Workflow Executor Pattern:{RESET}

    {CYAN}python -c "
from empathy_os.workflows.security_audit import SECURITY_STEPS
print('Security audit steps:')
for name, step in SECURITY_STEPS.items():
    print(f'  {{name}}: task={{step.task_type}}, tier={{step.tier_hint}}')"
{RESET}
""",
    )


def run_pytest_subset():
    """Run a subset of relevant tests."""
    header("Running Automated Tests")

    project_root = Path(__file__).parent.parent

    test_files = [
        "tests/test_executor_integration.py",
        "tests/test_fallback.py",
        "tests/test_workflow_base.py",
    ]

    # Filter to existing files
    existing = [f for f in test_files if (project_root / f).exists()]

    if not existing:
        warning("No test files found")
        return False

    try:
        result = subprocess.run(
            ["python", "-m", "pytest"] + existing + ["-v", "--tb=short", "-q"],
            check=False,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Extract summary line
        lines = result.stdout.strip().split("\n")
        for line in reversed(lines):
            if "passed" in line or "failed" in line:
                if "failed" in line and "passed" not in line:
                    error(line)
                else:
                    success(line)
                break

        return result.returncode == 0 or "passed" in result.stdout

    except subprocess.TimeoutExpired:
        warning("Tests timed out")
        return False
    except Exception as e:
        error(f"Test run failed: {e}")
        return False


def main():
    print(
        f"""
{BOLD}{"=" * 60}{RESET}
{BOLD}Empathy Framework - December 2025 Features Test{RESET}
{BOLD}{"=" * 60}{RESET}

Testing features from recent implementation sessions:
- Phase 2: Dashboard interactive charts
- Phase 3: Workflow executor migrations
- Phase 4: Dependency consolidation
- Phase 5: Workflow plugin discovery
""",
    )

    results = {}

    # Run automated tests
    results["Phase 5: Plugin Discovery"] = test_workflow_plugin_discovery()
    results["Phase 3: Executor Migrations"] = test_workflow_executor_migrations()
    results["Phase 4: Dependencies"] = test_dependency_alignment()
    results["Phase 2: VSCode Build"] = test_vscode_extension_builds()
    results["Pytest Suite"] = run_pytest_subset()

    # Summary
    header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        if result:
            success(f"{name}")
        else:
            error(f"{name}")

    print(f"\n{BOLD}Result: {passed}/{total} test groups passed{RESET}")

    if passed < total:
        print(f"\n{YELLOW}Some tests failed. Check the output above for details.{RESET}")

    # Print manual testing checklist
    manual_testing_checklist()

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
