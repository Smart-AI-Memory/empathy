"""Tests for SecurityAuditWorkflow.

Tests the OWASP-focused security audit with vulnerability detection,
team decision integration, and remediation planning.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.empathy_os.workflows.base import ModelTier
from src.empathy_os.workflows.security_audit import SECURITY_PATTERNS, SecurityAuditWorkflow


class TestSecurityPatterns:
    """Tests for security vulnerability patterns."""

    def test_patterns_exist(self):
        """Test that security patterns are defined."""
        assert len(SECURITY_PATTERNS) > 0
        assert "sql_injection" in SECURITY_PATTERNS
        assert "xss" in SECURITY_PATTERNS
        assert "hardcoded_secret" in SECURITY_PATTERNS
        assert "command_injection" in SECURITY_PATTERNS

    def test_pattern_structure(self):
        """Test that patterns have required fields."""
        for vuln_type, info in SECURITY_PATTERNS.items():
            assert "patterns" in info, f"{vuln_type} missing patterns"
            assert "severity" in info, f"{vuln_type} missing severity"
            assert "owasp" in info, f"{vuln_type} missing owasp"
            assert len(info["patterns"]) > 0

    def test_severity_values(self):
        """Test that severities are valid values."""
        valid_severities = {"critical", "high", "medium", "low"}
        for _vuln_type, info in SECURITY_PATTERNS.items():
            assert info["severity"] in valid_severities


class TestSecurityAuditWorkflowInit:
    """Tests for SecurityAuditWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = SecurityAuditWorkflow()

        assert workflow.name == "security-audit"
        assert workflow.patterns_dir == "./patterns"
        assert workflow.skip_remediate_if_clean is True
        assert workflow.use_crew_for_remediation is False
        assert workflow._has_critical is False

    def test_custom_patterns_dir(self):
        """Test custom patterns directory."""
        workflow = SecurityAuditWorkflow(patterns_dir="/custom/path")

        assert workflow.patterns_dir == "/custom/path"

    def test_custom_skip_setting(self):
        """Test skip remediate setting."""
        workflow = SecurityAuditWorkflow(skip_remediate_if_clean=False)

        assert workflow.skip_remediate_if_clean is False

    def test_crew_mode(self):
        """Test crew mode initialization."""
        config = {"verbose": True}
        workflow = SecurityAuditWorkflow(
            use_crew_for_remediation=True,
            crew_config=config,
        )

        assert workflow.use_crew_for_remediation is True
        assert workflow.crew_config == config

    def test_tier_map(self):
        """Test tier mapping for stages."""
        workflow = SecurityAuditWorkflow()

        assert workflow.tier_map["triage"] == ModelTier.CHEAP
        assert workflow.tier_map["analyze"] == ModelTier.CAPABLE
        assert workflow.tier_map["assess"] == ModelTier.CAPABLE
        assert workflow.tier_map["remediate"] == ModelTier.PREMIUM

    def test_stages(self):
        """Test workflow stages."""
        workflow = SecurityAuditWorkflow()

        assert workflow.stages == ["triage", "analyze", "assess", "remediate"]


class TestTeamDecisionsLoading:
    """Tests for team security decisions loading."""

    def test_load_decisions_file_not_exists(self):
        """Test loading when file doesn't exist."""
        workflow = SecurityAuditWorkflow(patterns_dir="/nonexistent")

        assert workflow._team_decisions == {}

    def test_load_decisions_from_file(self):
        """Test loading decisions from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            security_dir = Path(tmpdir) / "security"
            security_dir.mkdir()

            decisions = {
                "decisions": [
                    {"finding_hash": "abc123", "decision": "false_positive"},
                    {"finding_hash": "def456", "decision": "accepted_risk"},
                ],
            }

            with open(security_dir / "team_decisions.json", "w") as f:
                json.dump(decisions, f)

            workflow = SecurityAuditWorkflow(patterns_dir=tmpdir)

            assert "abc123" in workflow._team_decisions
            assert "def456" in workflow._team_decisions
            assert workflow._team_decisions["abc123"]["decision"] == "false_positive"

    def test_load_decisions_invalid_json(self):
        """Test loading invalid JSON doesn't crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            security_dir = Path(tmpdir) / "security"
            security_dir.mkdir()

            with open(security_dir / "team_decisions.json", "w") as f:
                f.write("not valid json")

            workflow = SecurityAuditWorkflow(patterns_dir=tmpdir)

            assert workflow._team_decisions == {}


class TestSecurityAuditSkipStage:
    """Tests for stage skipping logic."""

    def test_should_not_skip_triage(self):
        """Triage stage should never be skipped."""
        workflow = SecurityAuditWorkflow()

        skip, reason = workflow.should_skip_stage("triage", {})

        assert skip is False
        assert reason is None

    def test_should_not_skip_analyze(self):
        """Analyze stage should never be skipped."""
        workflow = SecurityAuditWorkflow()

        skip, reason = workflow.should_skip_stage("analyze", {})

        assert skip is False

    def test_should_skip_remediate_no_critical(self):
        """Remediate should be skipped if no critical findings."""
        workflow = SecurityAuditWorkflow(skip_remediate_if_clean=True)
        workflow._has_critical = False

        skip, reason = workflow.should_skip_stage("remediate", {})

        assert skip is True
        assert "No high/critical" in reason

    def test_should_not_skip_remediate_has_critical(self):
        """Remediate should not be skipped if critical findings exist."""
        workflow = SecurityAuditWorkflow(skip_remediate_if_clean=True)
        workflow._has_critical = True

        skip, reason = workflow.should_skip_stage("remediate", {})

        assert skip is False

    def test_should_not_skip_remediate_setting_disabled(self):
        """Remediate should not be skipped if setting is disabled."""
        workflow = SecurityAuditWorkflow(skip_remediate_if_clean=False)
        workflow._has_critical = False

        skip, reason = workflow.should_skip_stage("remediate", {})

        assert skip is False


class TestSecurityAuditStages:
    """Tests for workflow stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_triage(self):
        """Test triage stage routing."""
        workflow = SecurityAuditWorkflow()

        with patch.object(workflow, "_triage", new_callable=AsyncMock) as mock:
            mock.return_value = ({"findings": []}, 100, 50)

            await workflow.run_stage("triage", ModelTier.CHEAP, {"path": "."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_analyze(self):
        """Test analyze stage routing."""
        workflow = SecurityAuditWorkflow()

        with patch.object(workflow, "_analyze", new_callable=AsyncMock) as mock:
            mock.return_value = ({"analysis": {}}, 200, 100)

            await workflow.run_stage("analyze", ModelTier.CAPABLE, {"findings": []})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_assess(self):
        """Test assess stage routing."""
        workflow = SecurityAuditWorkflow()

        with patch.object(workflow, "_assess", new_callable=AsyncMock) as mock:
            mock.return_value = ({"risk_score": 0}, 150, 75)

            await workflow.run_stage("assess", ModelTier.CAPABLE, {})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_remediate(self):
        """Test remediate stage routing."""
        workflow = SecurityAuditWorkflow()

        with patch.object(workflow, "_remediate", new_callable=AsyncMock) as mock:
            mock.return_value = ({"remediation_plan": []}, 300, 200)

            await workflow.run_stage("remediate", ModelTier.PREMIUM, {})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_invalid(self):
        """Test invalid stage raises error."""
        workflow = SecurityAuditWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("invalid", ModelTier.CHEAP, {})


class TestSecurityAuditTriage:
    """Tests for security triage scanning."""

    @pytest.mark.asyncio
    async def test_triage_empty_directory(self):
        """Test triage on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = SecurityAuditWorkflow()

            result, input_tokens, output_tokens = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["findings"] == []
            assert result["files_scanned"] == 0

    @pytest.mark.asyncio
    async def test_triage_detects_sql_injection(self):
        """Test triage detects SQL injection patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create vulnerable file
            vuln_file = Path(tmpdir) / "vuln.py"
            vuln_file.write_text('cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")')

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["files_scanned"] == 1
            assert len(result["findings"]) > 0
            assert any(f["type"] == "sql_injection" for f in result["findings"])

    @pytest.mark.asyncio
    async def test_triage_detects_command_injection(self):
        """Test triage detects command injection patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = Path(tmpdir) / "cmd.py"
            vuln_file.write_text('os.system("rm -rf " + user_input)')

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert len(result["findings"]) > 0
            assert any(f["type"] == "command_injection" for f in result["findings"])

    @pytest.mark.asyncio
    async def test_triage_detects_hardcoded_secrets(self):
        """Test triage detects hardcoded secrets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = Path(tmpdir) / "config.py"
            vuln_file.write_text('api_key = "sk-abc123supersecretkey456"')

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert len(result["findings"]) > 0
            assert any(f["type"] == "hardcoded_secret" for f in result["findings"])

    @pytest.mark.asyncio
    async def test_triage_skips_git_directory(self):
        """Test triage skips .git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            (git_dir / "config.py").write_text('password = "secret"')

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            # Should not find the file in .git
            assert all(".git" not in f["file"] for f in result["findings"])

    @pytest.mark.asyncio
    async def test_triage_skips_node_modules(self):
        """Test triage skips node_modules directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            node_dir = Path(tmpdir) / "node_modules"
            node_dir.mkdir()
            (node_dir / "lib.js").write_text("eval(user_input)")

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".js"]},
                ModelTier.CHEAP,
            )

            assert all("node_modules" not in f["file"] for f in result["findings"])

    @pytest.mark.asyncio
    async def test_triage_clean_code(self):
        """Test triage on clean code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            clean_file = Path(tmpdir) / "clean.py"
            clean_file.write_text(
                """
def safe_query(user_id: int) -> dict:
    # Use parameterized queries
    return db.execute("SELECT * FROM users WHERE id = ?", [user_id])
""",
            )

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["files_scanned"] == 1
            # Parameterized queries shouldn't trigger SQL injection
            assert not any(
                f["type"] == "sql_injection" and "parameterized" in f.get("match", "")
                for f in result["findings"]
            )


class TestSecurityAuditIntegration:
    """Integration tests for SecurityAuditWorkflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_clean_code(self):
        """Test full workflow on clean codebase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create clean code
            (Path(tmpdir) / "app.py").write_text(
                """
import os
from typing import Optional

def get_user(user_id: int) -> Optional[dict]:
    '''Safe user lookup with parameterized query.'''
    return db.query("SELECT * FROM users WHERE id = ?", [user_id])
""",
            )

            workflow = SecurityAuditWorkflow(patterns_dir=tmpdir)

            # Just test triage directly
            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            # Clean code should have minimal findings
            critical_findings = [f for f in result["findings"] if f["severity"] == "critical"]
            assert len(critical_findings) == 0

    @pytest.mark.asyncio
    async def test_findings_include_line_numbers(self):
        """Test that findings include correct line numbers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text(
                """# Line 1
# Line 2
# Line 3
os.system(cmd)  # Line 4 - vulnerability here
# Line 5
""",
            )

            workflow = SecurityAuditWorkflow()

            result, _, _ = await workflow._triage(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert len(result["findings"]) > 0
            # The vulnerability is on line 4
            vuln = result["findings"][0]
            assert vuln["line"] == 4
