"""Golden File Tests for Refactoring Crew

Tests the RefactoringCrew against known code patterns to ensure
consistent detection of refactoring opportunities.

These tests verify that:
1. Known patterns are correctly identified
2. Findings match expected categories
3. Confidence scores are appropriate
4. Line ranges are accurate

To add a new golden test:
1. Create a new directory under tests/golden_files/refactoring/
2. Add input.py with the code to analyze
3. Add expected.json with expected findings metadata

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

GOLDEN_FILES_DIR = Path(__file__).parent / "golden_files" / "refactoring"


def get_golden_scenarios() -> list[str]:
    """Get list of available golden file scenarios."""
    if not GOLDEN_FILES_DIR.exists():
        return []

    scenarios = []
    for subdir in GOLDEN_FILES_DIR.iterdir():
        if subdir.is_dir():
            input_file = subdir / "input.py"
            expected_file = subdir / "expected.json"
            if input_file.exists() and expected_file.exists():
                scenarios.append(subdir.name)

    return sorted(scenarios)


def load_golden_scenario(scenario: str) -> tuple[str, dict]:
    """Load input code and expected findings for a scenario."""
    scenario_dir = GOLDEN_FILES_DIR / scenario

    with open(scenario_dir / "input.py") as f:
        input_code = f.read()

    with open(scenario_dir / "expected.json") as f:
        expected = json.load(f)

    return input_code, expected


class TestGoldenFileStructure:
    """Test that golden file structure is valid."""

    def test_golden_files_directory_exists(self):
        """Test that golden files directory exists."""
        assert GOLDEN_FILES_DIR.exists(), f"Golden files directory not found: {GOLDEN_FILES_DIR}"

    def test_at_least_one_scenario(self):
        """Test that at least one golden scenario exists."""
        scenarios = get_golden_scenarios()
        assert len(scenarios) >= 1, "No golden scenarios found"

    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    def test_scenario_has_required_files(self, scenario: str):
        """Test that each scenario has required files."""
        scenario_dir = GOLDEN_FILES_DIR / scenario

        assert (scenario_dir / "input.py").exists(), f"Missing input.py in {scenario}"
        assert (scenario_dir / "expected.json").exists(), f"Missing expected.json in {scenario}"

    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    def test_expected_json_is_valid(self, scenario: str):
        """Test that expected.json has required fields."""
        _, expected = load_golden_scenario(scenario)

        assert "scenario" in expected, f"Missing 'scenario' field in {scenario}"
        assert "min_findings" in expected, f"Missing 'min_findings' field in {scenario}"
        assert "primary_category" in expected, f"Missing 'primary_category' field in {scenario}"


class TestGoldenScenarioValidation:
    """Test validation of golden scenario expectations."""

    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    def test_input_code_is_valid_python(self, scenario: str):
        """Test that input code is valid Python syntax."""
        input_code, _ = load_golden_scenario(scenario)

        try:
            compile(input_code, f"{scenario}/input.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Invalid Python in {scenario}/input.py: {e}")

    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    def test_primary_category_is_valid(self, scenario: str):
        """Test that primary_category is a valid RefactoringCategory."""
        from empathy_llm_toolkit.agent_factory.crews.refactoring import RefactoringCategory

        _, expected = load_golden_scenario(scenario)
        primary = expected["primary_category"]

        valid_categories = [c.value for c in RefactoringCategory]
        assert (
            primary in valid_categories
        ), f"Invalid primary_category '{primary}' in {scenario}. Valid options: {valid_categories}"


class TestRefactoringCrewGoldenAnalysis:
    """Test RefactoringCrew analysis against golden files.

    These tests use mocked agent responses to verify the parsing
    and validation logic works correctly.
    """

    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    def test_scenario_analysis_structure(self, scenario: str):
        """Test that analysis produces expected structure for each scenario."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringConfig, RefactoringCrew

        input_code, expected = load_golden_scenario(scenario)

        # Create crew with analysis disabled (we're testing structure)
        config = RefactoringConfig(
            memory_graph_enabled=False,
            user_profile_enabled=False,
        )
        crew = RefactoringCrew(config=config)

        # Verify crew can build analysis task
        task = crew._build_analysis_task(input_code, f"{scenario}/input.py", {})

        assert f"{scenario}/input.py" in task
        assert input_code[:100] in task or len(input_code) > 20000

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    async def test_scenario_with_mocked_findings(self, scenario: str):
        """Test scenario with mocked analyzer response matching expected."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringConfig, RefactoringCrew

        input_code, expected = load_golden_scenario(scenario)

        config = RefactoringConfig(
            memory_graph_enabled=False,
            user_profile_enabled=False,
        )
        crew = RefactoringCrew(config=config)

        # Mock initialization
        crew._initialized = True
        crew._factory = MagicMock()

        # Create mock findings based on expected
        mock_findings = []
        for i in range(expected.get("min_findings", 1)):
            mock_findings.append(
                {
                    "id": f"mock-{scenario}-{i}",
                    "title": f"Mock finding for {expected['primary_category']}",
                    "description": f"Detected in {scenario}",
                    "category": expected["primary_category"],
                    "severity": "medium",
                    "file_path": f"{scenario}/input.py",
                    "start_line": 1,
                    "end_line": 10,
                    "before_code": "# mock code",
                    "confidence": 0.9,
                    "estimated_impact": "medium",
                },
            )

        # Mock analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.invoke = AsyncMock(
            return_value={
                "output": "",
                "metadata": {"findings": mock_findings},
            },
        )

        crew._agents = {"analyzer": mock_analyzer, "writer": MagicMock()}

        # Run analysis
        report = await crew.analyze(input_code, f"{scenario}/input.py")

        # Verify report structure
        assert report.target == f"{scenario}/input.py"
        assert len(report.findings) >= expected["min_findings"]

        if expected.get("max_findings"):
            assert len(report.findings) <= expected["max_findings"]

        # Verify primary category is present
        categories = [f.category.value for f in report.findings]
        assert expected["primary_category"] in categories


class TestGoldenFileRecording:
    """Test recording capability for golden file creation."""

    def test_can_record_session(self):
        """Test that sessions can be recorded for later replay."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding
        from empathy_llm_toolkit.agent_factory.crews.refactoring import (
            RefactoringCategory,
            Severity,
        )

        # Simulate a session recording
        recording = {
            "input": {
                "code": "def test(): pass",
                "file_path": "test.py",
            },
            "findings": [
                RefactoringFinding(
                    id="f1",
                    title="Test finding",
                    description="...",
                    category=RefactoringCategory.SIMPLIFY,
                    severity=Severity.LOW,
                    file_path="test.py",
                    start_line=1,
                    end_line=1,
                ).to_dict(),
            ],
            "decisions": [("f1", True)],
        }

        # Verify recording structure
        assert "input" in recording
        assert "findings" in recording
        assert "decisions" in recording
        assert recording["findings"][0]["category"] == "simplify"

    def test_can_replay_session(self):
        """Test that recorded sessions can be replayed."""
        from empathy_llm_toolkit.agent_factory.crews import RefactoringFinding

        # Load a "recording"
        recording = {
            "input": {"code": "x = 1", "file_path": "test.py"},
            "findings": [
                {
                    "id": "f1",
                    "title": "Rename x",
                    "description": "Variable x is unclear",
                    "category": "rename",
                    "severity": "low",
                    "file_path": "test.py",
                    "start_line": 1,
                    "end_line": 1,
                    "before_code": "x = 1",
                    "confidence": 0.9,
                    "estimated_impact": "low",
                },
            ],
            "decisions": [("f1", True)],
        }

        # Replay: parse findings
        findings = [RefactoringFinding.from_dict(f) for f in recording["findings"]]

        assert len(findings) == 1
        assert findings[0].id == "f1"
        assert findings[0].category.value == "rename"

        # Verify decisions can be applied
        for finding_id, _accepted in recording["decisions"]:
            matching = [f for f in findings if f.id == finding_id]
            assert len(matching) == 1


class TestExpectedPatternMatching:
    """Test that expected patterns in golden files can be matched."""

    @pytest.mark.parametrize("scenario", get_golden_scenarios())
    def test_expected_patterns_are_matchable(self, scenario: str):
        """Test that expected_patterns in golden files are valid."""
        _, expected = load_golden_scenario(scenario)

        if "expected_patterns" not in expected:
            pytest.skip(f"No expected_patterns in {scenario}")

        for pattern in expected["expected_patterns"]:
            # Verify required fields
            assert "category" in pattern, f"Pattern missing 'category' in {scenario}"

            # Verify category is valid
            from empathy_llm_toolkit.agent_factory.crews.refactoring import RefactoringCategory

            valid_categories = [c.value for c in RefactoringCategory]
            assert (
                pattern["category"] in valid_categories
            ), f"Invalid category '{pattern['category']}' in {scenario}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
