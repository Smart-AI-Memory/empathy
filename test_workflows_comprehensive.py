#!/usr/bin/env python3
"""Comprehensive Workflow Testing for Empathy Framework v3.7.0."""

import subprocess
import sys
from pathlib import Path


def test_workflow_listing():
    """Test workflow list command."""
    print("=" * 70)
    print("TEST 1: Workflow Listing")
    print("=" * 70)

    try:
        result = subprocess.run(
            ["python", "-m", "empathy_os.cli", "workflow", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            output = result.stdout
            expected_workflows = [
                "code-review",
                "doc-gen",
                "bug-predict",
                "security-audit",
                "perf-audit",
                "health-check",
                "refactor-plan",
                "test-gen",
                "manage-docs",
                "doc-orchestrator",
            ]

            found = []
            missing = []
            for wf in expected_workflows:
                if wf in output:
                    found.append(wf)
                    print(f"  ✅ {wf}")
                else:
                    missing.append(wf)
                    print(f"  ❌ {wf} - NOT FOUND")

            print(f"\n  Found: {len(found)}/{len(expected_workflows)}")
            return len(missing) == 0
        else:
            print(f"  ❌ Command failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_workflow_imports():
    """Test importing all workflow classes."""
    print("\n" + "=" * 70)
    print("TEST 2: Workflow Imports")
    print("=" * 70)

    workflows_to_test = [
        ("BaseWorkflow", "empathy_os.workflows", "BaseWorkflow"),
        ("CodeReviewWorkflow", "empathy_os.workflows.code_review", "CodeReviewWorkflow"),
        ("BugPredictionWorkflow", "empathy_os.workflows.bug_predict", "BugPredictionWorkflow"),
        ("SecurityAuditWorkflow", "empathy_os.workflows.security_audit", "SecurityAuditWorkflow"),
        ("HealthCheckWorkflow", "empathy_os.workflows.health_check", "HealthCheckWorkflow"),
        ("TestGenerationWorkflow", "empathy_os.workflows.test_gen", "TestGenerationWorkflow"),
    ]

    passed = 0
    failed = 0

    for name, module, class_name in workflows_to_test:
        try:
            exec(f"from {module} import {class_name}")
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1

    print(f"\n  Passed: {passed}/{len(workflows_to_test)}")
    return failed == 0


def test_workflow_structure():
    """Test workflow structure and methods."""
    print("\n" + "=" * 70)
    print("TEST 3: Workflow Structure & Methods")
    print("=" * 70)

    try:
        from empathy_os.workflows import BaseWorkflow

        # Check for XML methods
        xml_methods = ["_is_xml_enabled", "_render_xml_prompt", "_parse_xml_response"]

        found = []
        missing = []

        for method in xml_methods:
            if hasattr(BaseWorkflow, method):
                found.append(method)
                print(f"  ✅ {method} exists")
            else:
                missing.append(method)
                print(f"  ❌ {method} missing")

        # Check for standard methods
        standard_methods = [
            "execute",
            "run",
        ]

        for method in standard_methods:
            if hasattr(BaseWorkflow, method):
                found.append(method)
                print(f"  ✅ {method} exists")
            else:
                print(f"  ⚠️  {method} missing (optional)")

        print(f"\n  XML Methods: {len([m for m in xml_methods if m in found])}/{len(xml_methods)}")
        return len(missing) == 0

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_crewai_workflows():
    """Test CrewAI crew imports."""
    print("\n" + "=" * 70)
    print("TEST 4: CrewAI Workflow Integration")
    print("=" * 70)

    crews = [
        ("SecurityAuditCrew", "empathy_llm_toolkit.agent_factory.crews.security_audit"),
        ("CodeReviewCrew", "empathy_llm_toolkit.agent_factory.crews.code_review"),
        ("RefactoringCrew", "empathy_llm_toolkit.agent_factory.crews.refactoring"),
        ("HealthCheckCrew", "empathy_llm_toolkit.agent_factory.crews.health_check"),
    ]

    passed = 0
    failed = 0

    for crew_name, module in crews:
        try:
            exec(f"from {module} import {crew_name}")
            print(f"  ✅ {crew_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {crew_name}: {e}")
            failed += 1

    print(f"\n  Passed: {passed}/{len(crews)}")
    return failed == 0


def test_workflow_describe():
    """Test workflow describe command."""
    print("\n" + "=" * 70)
    print("TEST 5: Workflow Describe")
    print("=" * 70)

    try:
        result = subprocess.run(
            ["python", "-m", "empathy_os.cli", "workflow", "describe", "code-review"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            output = result.stdout
            if "code-review" in output.lower() or "Code Review" in output:
                print("  ✅ code-review description available")
                print(f"  Output preview: {output[:200]}...")
                return True
            else:
                print("  ❌ Description missing or incomplete")
                return False
        else:
            print(f"  ❌ Command failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_workflow_files_structure():
    """Test workflow files exist in package."""
    print("\n" + "=" * 70)
    print("TEST 6: Workflow Files Structure")
    print("=" * 70)

    workflow_files = [
        "src/empathy_os/workflows/__init__.py",
        "src/empathy_os/workflows/base.py",
        "src/empathy_os/workflows/code_review.py",
        "src/empathy_os/workflows/bug_predict.py",
        "src/empathy_os/workflows/security_audit.py",
        "src/empathy_os/workflows/health_check.py",
        "src/empathy_os/workflows/test_gen.py",
    ]

    found = 0
    missing = 0

    for file_path in workflow_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
            found += 1
        else:
            print(f"  ❌ {file_path} - NOT FOUND")
            missing += 1

    print(f"\n  Found: {found}/{len(workflow_files)}")
    return missing == 0


def test_workflow_config():
    """Test workflow configuration."""
    print("\n" + "=" * 70)
    print("TEST 7: Workflow Configuration")
    print("=" * 70)

    try:
        from empathy_os.workflows.config import ModelConfig

        print("  ✅ ModelConfig imports successfully")

        # Check ModelConfig has expected attributes
        expected_attrs = ["model_name", "provider"]
        found = []

        for attr in expected_attrs:
            if hasattr(ModelConfig, attr) or attr in ModelConfig.__annotations__:
                found.append(attr)
                print(f"  ✅ ModelConfig.{attr} exists")
            else:
                print(f"  ⚠️  ModelConfig.{attr} missing (checking annotations)")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_xml_enhanced_workflows():
    """Test XML-enhanced workflow features."""
    print("\n" + "=" * 70)
    print("TEST 8: XML-Enhanced Workflow Features")
    print("=" * 70)

    try:
        from empathy_os.workflows.code_review import CodeReviewWorkflow

        # Check if workflow has XML methods
        xml_features = [
            "_is_xml_enabled",
            "_render_xml_prompt",
        ]

        found = []
        for feature in xml_features:
            if hasattr(CodeReviewWorkflow, feature):
                found.append(feature)
                print(f"  ✅ CodeReviewWorkflow.{feature}")
            else:
                print(f"  ❌ CodeReviewWorkflow.{feature} missing")

        print(f"\n  XML Features: {len(found)}/{len(xml_features)}")
        return len(found) == len(xml_features)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all workflow tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE WORKFLOW TESTING - Empathy Framework v3.7.0")
    print("=" * 70)

    tests = [
        ("Workflow Listing", test_workflow_listing),
        ("Workflow Imports", test_workflow_imports),
        ("Workflow Structure", test_workflow_structure),
        ("CrewAI Integration", test_crewai_workflows),
        ("Workflow Describe", test_workflow_describe),
        ("Workflow Files", test_workflow_files_structure),
        ("Workflow Config", test_workflow_config),
        ("XML Features", test_xml_enhanced_workflows),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  ❌ Test {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")

    print("\n" + "-" * 70)
    print(f"  Total: {passed_count}/{total_count} tests passed")
    print(f"  Pass Rate: {(passed_count / total_count) * 100:.1f}%")

    if passed_count == total_count:
        print("\n  🎉 ALL WORKFLOW TESTS PASSED!")
        return 0
    else:
        print(f"\n  ⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
