"""Tests for DependencyCheckWorkflow.

Tests the dependency vulnerability and update checking workflow
with inventory, assess, and report stages.
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.empathy_os.workflows.base import ModelTier
from src.empathy_os.workflows.dependency_check import KNOWN_VULNERABILITIES, DependencyCheckWorkflow


class TestKnownVulnerabilities:
    """Tests for known vulnerability patterns."""

    def test_vulnerabilities_defined(self):
        """Test that known vulnerabilities are defined."""
        assert len(KNOWN_VULNERABILITIES) > 0
        assert "requests" in KNOWN_VULNERABILITIES
        assert "pyyaml" in KNOWN_VULNERABILITIES
        assert "lodash" in KNOWN_VULNERABILITIES

    def test_vulnerability_structure(self):
        """Test vulnerability entry structure."""
        for package, info in KNOWN_VULNERABILITIES.items():
            assert "affected_versions" in info, f"{package} missing affected_versions"
            assert "severity" in info, f"{package} missing severity"
            assert "cve" in info, f"{package} missing cve"
            assert isinstance(info["affected_versions"], list)

    def test_severity_values(self):
        """Test that severities are valid."""
        valid_severities = {"critical", "high", "medium", "low"}
        for info in KNOWN_VULNERABILITIES.values():
            assert info["severity"] in valid_severities


class TestDependencyCheckWorkflowInit:
    """Tests for DependencyCheckWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = DependencyCheckWorkflow()

        assert workflow.name == "dependency-check"
        assert workflow.description == "Audit dependencies for vulnerabilities and updates"
        assert workflow.stages == ["inventory", "assess", "report"]

    def test_tier_map(self):
        """Test tier mapping for stages."""
        workflow = DependencyCheckWorkflow()

        assert workflow.tier_map["inventory"] == ModelTier.CHEAP
        assert workflow.tier_map["assess"] == ModelTier.CAPABLE
        assert workflow.tier_map["report"] == ModelTier.CAPABLE


class TestDependencyParsing:
    """Tests for dependency file parsing."""

    def test_parse_requirements_txt(self):
        """Test parsing requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text(
                """
# Core dependencies
requests>=2.25.0
flask==2.0.0
django<4.0.0
pyyaml
# Comment
-r other-requirements.txt
""",
            )
            workflow = DependencyCheckWorkflow()
            deps = workflow._parse_requirements(req_file)

            assert len(deps) == 4
            assert deps[0]["name"] == "requests"
            assert deps[0]["version"] == ">=2.25.0"
            assert deps[1]["name"] == "flask"
            assert deps[2]["name"] == "django"
            assert deps[3]["name"] == "pyyaml"

    def test_parse_requirements_empty(self):
        """Test parsing empty requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("")

            workflow = DependencyCheckWorkflow()
            deps = workflow._parse_requirements(req_file)

            assert deps == []

    def test_parse_package_json(self):
        """Test parsing package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(
                json.dumps(
                    {
                        "name": "test-project",
                        "dependencies": {
                            "lodash": "^4.17.21",
                            "axios": "0.21.1",
                        },
                        "devDependencies": {
                            "jest": "^27.0.0",
                        },
                    },
                ),
            )

            workflow = DependencyCheckWorkflow()
            deps = workflow._parse_package_json(pkg_file)

            assert len(deps) == 3
            assert any(d["name"] == "lodash" for d in deps)
            assert any(d["name"] == "axios" for d in deps)
            assert any(d["name"] == "jest" and d["dev"] is True for d in deps)

    def test_parse_package_json_no_deps(self):
        """Test parsing package.json without dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(
                json.dumps(
                    {
                        "name": "empty-project",
                    },
                ),
            )

            workflow = DependencyCheckWorkflow()
            deps = workflow._parse_package_json(pkg_file)

            assert deps == []

    def test_parse_pyproject_toml(self):
        """Test parsing pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                """
[project]
name = "test"
dependencies = [
    "requests>=2.25.0",
    "flask",
    "pyyaml>=5.4",
]
""",
            )

            workflow = DependencyCheckWorkflow()
            deps = workflow._parse_pyproject(pyproject)

            # Should parse at least some dependencies
            assert isinstance(deps, list)


class TestDependencyCheckStages:
    """Tests for workflow stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_inventory(self):
        """Test inventory stage routing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a requirements file
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("requests>=2.25.0\nflask==2.0.0")

            workflow = DependencyCheckWorkflow()

            result, input_tokens, output_tokens = await workflow.run_stage(
                "inventory",
                ModelTier.CHEAP,
                {"path": tmpdir},
            )

            assert "dependencies" in result
            assert result["total_dependencies"] >= 0
            assert "python_count" in result

    @pytest.mark.asyncio
    async def test_run_stage_assess(self):
        """Test assess stage routing."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "dependencies": {
                "python": [
                    {"name": "requests", "version": "<2.25.0", "ecosystem": "python"},
                    {"name": "pyyaml", "version": "5.3", "ecosystem": "python"},
                ],
                "node": [],
            },
        }

        result, _, _ = await workflow.run_stage(
            "assess",
            ModelTier.CAPABLE,
            input_data,
        )

        assert "assessment" in result
        assert "vulnerabilities" in result["assessment"]
        assert result["assessment"]["vulnerability_count"] >= 0

    @pytest.mark.asyncio
    async def test_run_stage_report(self):
        """Test report stage routing."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "assessment": {
                "vulnerabilities": [
                    {"package": "pyyaml", "severity": "critical", "cve": "CVE-2020-XXXX"},
                ],
                "outdated": [],
                "critical_count": 1,
                "high_count": 0,
                "medium_count": 0,
            },
            "total_dependencies": 5,
        }

        result, _, _ = await workflow.run_stage(
            "report",
            ModelTier.CAPABLE,
            input_data,
        )

        assert "risk_score" in result
        assert "risk_level" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_run_stage_invalid(self):
        """Test invalid stage raises error."""
        workflow = DependencyCheckWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("invalid", ModelTier.CHEAP, {})


class TestDependencyInventory:
    """Tests for inventory stage."""

    @pytest.mark.asyncio
    async def test_inventory_empty_directory(self):
        """Test inventory on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = DependencyCheckWorkflow()

            result, _, _ = await workflow._inventory(
                {"path": tmpdir},
                ModelTier.CHEAP,
            )

            assert result["total_dependencies"] == 0
            assert result["python_count"] == 0
            assert result["node_count"] == 0

    @pytest.mark.asyncio
    async def test_inventory_deduplicates(self):
        """Test that inventory deduplicates dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple files with same dependency
            req = Path(tmpdir) / "requirements.txt"
            req.write_text("requests>=2.25.0")
            req_dev = Path(tmpdir) / "requirements-dev.txt"
            req_dev.write_text("requests>=2.25.0\npytest")

            workflow = DependencyCheckWorkflow()

            result, _, _ = await workflow._inventory(
                {"path": tmpdir},
                ModelTier.CHEAP,
            )

            # requests should only appear once
            python_deps = result["dependencies"]["python"]
            requests_deps = [d for d in python_deps if d["name"] == "requests"]
            assert len(requests_deps) == 1


class TestDependencyAssess:
    """Tests for assess stage."""

    @pytest.mark.asyncio
    async def test_assess_finds_vulnerabilities(self):
        """Test assess finds known vulnerabilities."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "dependencies": {
                "python": [
                    {"name": "pyyaml", "version": "<5.4", "ecosystem": "python"},
                    {"name": "urllib3", "version": "<1.26.5", "ecosystem": "python"},
                ],
                "node": [],
            },
        }

        result, _, _ = await workflow._assess(input_data, ModelTier.CAPABLE)

        assert result["assessment"]["vulnerability_count"] == 2
        assert result["assessment"]["critical_count"] >= 1  # pyyaml is critical

    @pytest.mark.asyncio
    async def test_assess_clean_dependencies(self):
        """Test assess on clean dependencies."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "dependencies": {
                "python": [
                    {"name": "safe-package", "version": "1.0.0", "ecosystem": "python"},
                ],
                "node": [],
            },
        }

        result, _, _ = await workflow._assess(input_data, ModelTier.CAPABLE)

        assert result["assessment"]["vulnerability_count"] == 0

    @pytest.mark.asyncio
    async def test_assess_categorizes_severity(self):
        """Test that assess categorizes by severity."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "dependencies": {
                "python": [
                    {"name": "pyyaml", "version": "<5.4", "ecosystem": "python"},  # critical
                    {"name": "django", "version": "<3.2.4", "ecosystem": "python"},  # high
                    {"name": "requests", "version": "<2.25.0", "ecosystem": "python"},  # medium
                ],
                "node": [],
            },
        }

        result, _, _ = await workflow._assess(input_data, ModelTier.CAPABLE)

        assert result["assessment"]["critical_count"] == 1
        assert result["assessment"]["high_count"] == 1
        assert result["assessment"]["medium_count"] == 1


class TestDependencyReport:
    """Tests for report stage."""

    @pytest.mark.asyncio
    async def test_report_calculates_risk_score(self):
        """Test risk score calculation."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "assessment": {
                "vulnerabilities": [],
                "outdated": [],
                "critical_count": 2,  # 2 * 25 = 50
                "high_count": 1,  # 1 * 10 = 10
                "medium_count": 3,  # 3 * 3 = 9
                "outdated_count": 2,  # 2 * 1 = 2
            },
            "total_dependencies": 10,
        }

        result, _, _ = await workflow._report(input_data, ModelTier.CAPABLE)

        # Expected: 50 + 10 + 9 + 2 = 71
        assert result["risk_score"] == 71
        assert result["risk_level"] == "high"  # 50-74 is high

    @pytest.mark.asyncio
    async def test_report_risk_levels(self):
        """Test different risk level thresholds."""
        workflow = DependencyCheckWorkflow()

        # Critical: >= 75
        result, _, _ = await workflow._report(
            {
                "assessment": {
                    "vulnerabilities": [],
                    "outdated": [],
                    "critical_count": 4,  # 100
                    "high_count": 0,
                    "medium_count": 0,
                    "outdated_count": 0,
                },
            },
            ModelTier.CAPABLE,
        )
        assert result["risk_level"] == "critical"

        # Low: < 25
        result, _, _ = await workflow._report(
            {
                "assessment": {
                    "vulnerabilities": [],
                    "outdated": [],
                    "critical_count": 0,
                    "high_count": 0,
                    "medium_count": 2,  # 6
                    "outdated_count": 5,  # 5
                },
            },
            ModelTier.CAPABLE,
        )
        assert result["risk_level"] == "low"

    @pytest.mark.asyncio
    async def test_report_generates_recommendations(self):
        """Test recommendation generation."""
        workflow = DependencyCheckWorkflow()

        input_data = {
            "assessment": {
                "vulnerabilities": [
                    {"package": "pyyaml", "severity": "critical", "cve": "CVE-2020-XXXX"},
                ],
                "outdated": [
                    {
                        "package": "flask",
                        "current_version": "1.0",
                        "status": "potentially_outdated",
                    },
                ],
                "critical_count": 1,
                "high_count": 0,
                "medium_count": 0,
                "outdated_count": 1,
            },
        }

        result, _, _ = await workflow._report(input_data, ModelTier.CAPABLE)

        assert len(result["recommendations"]) >= 2
        # Check priority ordering
        priorities = [r["priority"] for r in result["recommendations"]]
        assert priorities == sorted(priorities)


class TestDependencyCheckIntegration:
    """Integration tests for DependencyCheckWorkflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_clean_project(self):
        """Test full workflow on clean project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create clean requirements
            req = Path(tmpdir) / "requirements.txt"
            req.write_text("safe-package==1.0.0\nanother-safe==2.0.0")

            workflow = DependencyCheckWorkflow()

            # Run inventory stage
            inventory_result, _, _ = await workflow._inventory(
                {"path": tmpdir},
                ModelTier.CHEAP,
            )

            assert inventory_result["total_dependencies"] == 2

            # Run assess stage
            assess_result, _, _ = await workflow._assess(
                inventory_result,
                ModelTier.CAPABLE,
            )

            assert assess_result["assessment"]["vulnerability_count"] == 0

    @pytest.mark.asyncio
    async def test_full_workflow_vulnerable_project(self):
        """Test full workflow on vulnerable project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements with known vulnerabilities
            req = Path(tmpdir) / "requirements.txt"
            req.write_text("pyyaml<5.4\nurllib3<1.26.5\ndjango<3.2.4")

            workflow = DependencyCheckWorkflow()

            # Run inventory
            inventory_result, _, _ = await workflow._inventory(
                {"path": tmpdir},
                ModelTier.CHEAP,
            )

            # Run assess
            assess_result, _, _ = await workflow._assess(
                inventory_result,
                ModelTier.CAPABLE,
            )

            # Run report
            report_result, _, _ = await workflow._report(
                assess_result,
                ModelTier.CAPABLE,
            )

            assert assess_result["assessment"]["vulnerability_count"] >= 1
            assert report_result["risk_level"] in ["medium", "high", "critical"]
            assert len(report_result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_mixed_ecosystems(self):
        """Test workflow with Python and Node dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python requirements
            req = Path(tmpdir) / "requirements.txt"
            req.write_text("flask==2.0.0\nrequests>=2.25.0")

            # Create package.json
            pkg = Path(tmpdir) / "package.json"
            pkg.write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "lodash": "^4.17.21",
                            "axios": "0.21.1",
                        },
                    },
                ),
            )

            workflow = DependencyCheckWorkflow()

            result, _, _ = await workflow._inventory(
                {"path": tmpdir},
                ModelTier.CHEAP,
            )

            assert result["python_count"] == 2
            assert result["node_count"] == 2
            assert result["total_dependencies"] == 4
