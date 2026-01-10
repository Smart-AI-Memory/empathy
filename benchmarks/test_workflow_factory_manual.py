"""Manual test for Workflow Factory.

Quick test to verify the workflow factory works correctly.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from pathlib import Path

from empathy_os.workflow_patterns import get_workflow_pattern_registry

from workflow_scaffolding.generator import WorkflowGenerator


def test_pattern_registry():
    """Test pattern registry loads correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Pattern Registry")
    print("=" * 70)

    registry = get_workflow_pattern_registry()
    patterns = registry.list_all()

    print(f"\n✓ Loaded {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"  - {pattern.id:20} ({pattern.category.value:12}) - {pattern.name}")

    assert len(patterns) >= 7, f"Expected at least 7 patterns, got {len(patterns)}"
    print("\n✓ Pattern registry test PASSED")


def test_pattern_validation():
    """Test pattern validation."""
    print("\n" + "=" * 70)
    print("TEST 2: Pattern Validation")
    print("=" * 70)

    registry = get_workflow_pattern_registry()

    # Valid combination
    valid, error = registry.validate_pattern_combination(["multi-stage", "conditional-tier"])
    print(f"\n✓ Valid combination (multi-stage + conditional-tier): {valid}")
    assert valid, f"Should be valid: {error}"

    # Invalid - conditional-tier requires multi-stage
    valid, error = registry.validate_pattern_combination(["conditional-tier"])
    print(f"✓ Invalid combination (conditional-tier alone): {not valid}")
    assert not valid, "Should be invalid - missing requirement"
    print(f"  Error: {error}")

    # Conflicting patterns
    valid, error = registry.validate_pattern_combination(["single-stage", "crew-based"])
    print(f"✓ Conflicting combination (single-stage + crew-based): {not valid}")
    assert not valid, "Should be invalid - conflict"
    print(f"  Error: {error}")

    print("\n✓ Pattern validation test PASSED")


def test_workflow_generation():
    """Test workflow generation."""
    print("\n" + "=" * 70)
    print("TEST 3: Workflow Generation")
    print("=" * 70)

    generator = WorkflowGenerator()

    # Generate a simple workflow
    print("\nGenerating single-stage workflow...")
    generated = generator.generate_workflow(
        workflow_name="test-simple",
        description="Simple test workflow",
        patterns=["single-stage"],
    )

    print("✓ Generated files:")
    for file_type in ["workflow", "test", "readme"]:
        content = generated[file_type]
        lines = content.count("\n") + 1
        print(f"  - {file_type:10}: {lines:4} lines, {len(content):6} bytes")
        assert len(content) > 100, f"{file_type} too short"

    # Verify workflow content
    workflow_content = generated["workflow"]
    assert "class TestSimpleWorkflow(BaseWorkflow):" in workflow_content
    assert 'name = "test-simple"' in workflow_content
    assert "async def run_stage" in workflow_content
    print("\n✓ Workflow content validated")

    # Generate a multi-stage workflow
    print("\nGenerating multi-stage workflow...")
    generated = generator.generate_workflow(
        workflow_name="test-complex",
        description="Complex test workflow",
        patterns=["multi-stage", "conditional-tier", "config-driven"],
        stages=["analyze", "process", "report"],
    )

    workflow_content = generated["workflow"]
    assert "class TestComplexWorkflow(BaseWorkflow):" in workflow_content
    assert "analyze" in workflow_content
    assert "process" in workflow_content
    assert "report" in workflow_content
    assert "should_skip_stage" in workflow_content
    print("✓ Multi-stage workflow validated")

    print("\n✓ Workflow generation test PASSED")


def test_file_writing():
    """Test writing workflow files."""
    print("\n" + "=" * 70)
    print("TEST 4: File Writing")
    print("=" * 70)

    generator = WorkflowGenerator()
    output_dir = Path("test_output")

    # Clean up any existing test output
    import shutil

    if output_dir.exists():
        shutil.rmtree(output_dir)

    print("\nCreating test workflow...")
    written = generator.write_workflow(
        output_dir=output_dir,
        workflow_name="test-file-writing",
        description="Test file writing",
        patterns=["multi-stage", "result-dataclass"],
        stages=["scan", "analyze"],
    )

    print("✓ Written files:")
    for file_type, path in written.items():
        assert path.exists(), f"File not created: {path}"
        size = path.stat().st_size
        print(f"  - {file_type:10}: {path} ({size} bytes)")

    # Verify file contents
    workflow_path = written["workflow"]
    content = workflow_path.read_text()
    assert "class TestFileWritingWorkflow" in content
    assert "scan" in content
    assert "analyze" in content

    print("\n✓ File writing test PASSED")

    # Cleanup
    print("\nCleaning up test files...")
    shutil.rmtree(output_dir)
    print("✓ Cleanup complete")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("WORKFLOW FACTORY - MANUAL TEST SUITE")
    print("=" * 70)

    try:
        test_pattern_registry()
        test_pattern_validation()
        test_workflow_generation()
        test_file_writing()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\n✓ Workflow Factory is ready to use!")
        print("\nNext steps:")
        print("  1. Try creating a workflow:")
        print("     empathy workflow create my-workflow --patterns multi-stage")
        print("  2. List available patterns:")
        print("     empathy workflow list-patterns")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        print("=" * 70 + "\n")
        raise
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        print("=" * 70 + "\n")
        raise


if __name__ == "__main__":
    run_all_tests()
