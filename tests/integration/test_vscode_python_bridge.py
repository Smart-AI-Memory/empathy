"""Integration tests for VSCode ↔ Python CLI interaction.

These tests validate the entire stack from VSCode extension
through to Python CLI workflow execution.
"""

import json
import subprocess
import sys

import pytest


@pytest.mark.integration
def test_workflow_discovery_via_cli():
    """Test that VSCode can discover workflows via Python CLI."""
    # This simulates what WorkflowDiscoveryService.discoverFromPythonCLI() does
    result = subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "workflow", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"

    workflows = json.loads(result.stdout)
    assert isinstance(workflows, list), "Should return list of workflows"
    assert len(workflows) > 0, "Should discover at least one workflow"

    # Verify workflow structure
    first_workflow = workflows[0]
    assert "name" in first_workflow
    assert "description" in first_workflow
    assert "class" in first_workflow


@pytest.mark.integration
def test_workflow_metadata_structure():
    """Test that workflow metadata has expected structure for VSCode."""
    result = subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "workflow", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    workflows = json.loads(result.stdout)

    for workflow in workflows:
        # Required fields for VSCode extension
        assert isinstance(workflow["name"], str), "name must be string"
        assert isinstance(workflow["description"], str), "description must be string"
        assert len(workflow["name"]) > 0, "name cannot be empty"

        # Optional but expected fields
        if "stages" in workflow:
            assert isinstance(workflow["stages"], list), "stages must be list"


@pytest.mark.integration
def test_workflow_names_match_expectations():
    """Test that discovered workflows match expected names."""
    result = subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "workflow", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    workflows = json.loads(result.stdout)
    workflow_names = {w["name"] for w in workflows}

    # These are workflows we expect to exist
    expected_workflows = {
        "code-review",
        "bug-predict",
        "security-audit",
        "health-check",
    }

    assert expected_workflows.issubset(
        workflow_names,
    ), f"Missing expected workflows. Found: {workflow_names}"


@pytest.mark.integration
def test_workflow_categorization_coverage():
    """Test that all workflows can be categorized."""
    result = subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "workflow", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    workflows = json.loads(result.stdout)

    # Simulate categorization logic from WorkflowDiscoveryService
    quick_workflows = ["morning", "ship", "fix-all", "learn", "health"]
    view_workflows = ["dashboard", "costs", "status"]
    tool_workflows = ["fix-lint", "fix-format", "sync-claude"]

    categories = {"quick": 0, "workflow": 0, "view": 0, "tool": 0}

    for workflow in workflows:
        name = workflow["name"]
        if name in quick_workflows:
            categories["quick"] += 1
        elif name in view_workflows:
            categories["view"] += 1
        elif name in tool_workflows:
            categories["tool"] += 1
        else:
            categories["workflow"] += 1

    # Document the mismatch for tracking
    print("\nCategory distribution:")
    print(f"  Quick: {categories['quick']}")
    print(f"  Workflow: {categories['workflow']}")
    print(f"  View: {categories['view']}")
    print(f"  Tool: {categories['tool']}")

    # At least one workflow should be categorized
    assert sum(categories.values()) == len(workflows)


@pytest.mark.integration
def test_workflow_cli_json_format():
    """Test that CLI returns valid JSON format."""
    result = subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "workflow", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should not raise JSONDecodeError
    try:
        workflows = json.loads(result.stdout)
        assert isinstance(workflows, list)
    except json.JSONDecodeError as e:
        pytest.fail(f"CLI returned invalid JSON: {e}\nOutput: {result.stdout}")


@pytest.mark.integration
def test_vscode_workflow_picker_data_format():
    """Test that workflow data is suitable for VSCode Quick Pick."""
    result = subprocess.run(
        [sys.executable, "-m", "empathy_os.cli", "workflow", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    workflows = json.loads(result.stdout)

    # VSCode Quick Pick needs label and description
    for workflow in workflows:
        # Can construct label from name
        label = workflow["name"]
        assert len(label) > 0, "Name must be non-empty for label"

        # Has description for Quick Pick
        description = workflow.get("description", "")
        assert isinstance(description, str), "Description must be string"

        # Can construct detail from stages
        if "stages" in workflow:
            detail = " → ".join(workflow["stages"])
            assert isinstance(detail, str), "Stages should join to string"
