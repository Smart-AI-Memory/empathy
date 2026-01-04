"""Tests for empathy_software_plugin/wizards/security_learning_wizard.py

Tests the SecurityLearningWizard including:
- SecurityFinding, TeamDecision, LearningResult dataclasses
- Wizard initialization and properties
- Vulnerability pattern detection
- Learning and suppression
- Helper methods

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.security_learning_wizard import (
    LearningResult,
    SecurityFinding,
    SecurityLearningWizard,
    TeamDecision,
)


class TestSecurityFinding:
    """Tests for SecurityFinding dataclass."""

    def test_basic_creation(self):
        """Test basic creation of SecurityFinding."""
        finding = SecurityFinding(
            finding_id="sec_001",
            file_path="src/auth.py",
            line_number=42,
            vulnerability_type="sql_injection",
            severity="high",
            description="Potential SQL injection",
            code_snippet="cursor.execute(f'SELECT * FROM users WHERE id={id}')",
        )
        assert finding.finding_id == "sec_001"
        assert finding.file_path == "src/auth.py"
        assert finding.line_number == 42
        assert finding.vulnerability_type == "sql_injection"
        assert finding.severity == "high"

    def test_default_owasp_category(self):
        """Test default owasp_category is None."""
        finding = SecurityFinding(
            finding_id="id",
            file_path="f.py",
            line_number=1,
            vulnerability_type="xss",
            severity="high",
            description="desc",
            code_snippet="code",
        )
        assert finding.owasp_category is None

    def test_with_owasp_category(self):
        """Test with owasp_category."""
        finding = SecurityFinding(
            finding_id="id",
            file_path="f.py",
            line_number=1,
            vulnerability_type="sql_injection",
            severity="high",
            description="desc",
            code_snippet="code",
            owasp_category="A03:2021",
        )
        assert finding.owasp_category == "A03:2021"

    def test_various_severities(self):
        """Test various severity levels."""
        for severity in ["critical", "high", "medium", "low", "info"]:
            finding = SecurityFinding(
                finding_id="id",
                file_path="f.py",
                line_number=1,
                vulnerability_type="test",
                severity=severity,
                description="desc",
                code_snippet="code",
            )
            assert finding.severity == severity

    def test_various_vulnerability_types(self):
        """Test various vulnerability types."""
        vuln_types = [
            "sql_injection",
            "xss",
            "hardcoded_secret",
            "insecure_random",
            "path_traversal",
            "command_injection",
        ]
        for vuln_type in vuln_types:
            finding = SecurityFinding(
                finding_id="id",
                file_path="f.py",
                line_number=1,
                vulnerability_type=vuln_type,
                severity="high",
                description="desc",
                code_snippet="code",
            )
            assert finding.vulnerability_type == vuln_type


class TestTeamDecision:
    """Tests for TeamDecision dataclass."""

    def test_basic_creation(self):
        """Test basic creation of TeamDecision."""
        decision = TeamDecision(
            finding_hash="abc123",
            decision="false_positive",
            reason="React auto-escapes, no XSS risk",
            decided_by="@sarah",
            decided_at="2025-01-01",
            applies_to="pattern",
        )
        assert decision.finding_hash == "abc123"
        assert decision.decision == "false_positive"
        assert decision.reason == "React auto-escapes, no XSS risk"
        assert decision.decided_by == "@sarah"

    def test_default_expiration(self):
        """Test default expiration is None."""
        decision = TeamDecision(
            finding_hash="hash",
            decision="accepted",
            reason="reason",
            decided_by="@user",
            decided_at="2025-01-01",
            applies_to="all",
        )
        assert decision.expiration is None

    def test_with_expiration(self):
        """Test with expiration date."""
        decision = TeamDecision(
            finding_hash="hash",
            decision="deferred",
            reason="Will fix in Q2",
            decided_by="@team",
            decided_at="2025-01-01",
            applies_to="file",
            expiration="2025-06-30",
        )
        assert decision.expiration == "2025-06-30"

    def test_various_decisions(self):
        """Test various decision types."""
        for decision_type in ["accepted", "false_positive", "deferred", "fixed"]:
            decision = TeamDecision(
                finding_hash="hash",
                decision=decision_type,
                reason="reason",
                decided_by="@user",
                decided_at="2025-01-01",
                applies_to="all",
            )
            assert decision.decision == decision_type

    def test_various_applies_to(self):
        """Test various applies_to scopes."""
        for scope in ["all", "file", "pattern"]:
            decision = TeamDecision(
                finding_hash="hash",
                decision="accepted",
                reason="reason",
                decided_by="@user",
                decided_at="2025-01-01",
                applies_to=scope,
            )
            assert decision.applies_to == scope


class TestLearningResult:
    """Tests for LearningResult dataclass."""

    def test_basic_creation(self):
        """Test basic creation of LearningResult."""
        result = LearningResult(
            total_findings=10,
            suppressed_count=3,
            adjusted_count=2,
            new_findings=5,
        )
        assert result.total_findings == 10
        assert result.suppressed_count == 3
        assert result.adjusted_count == 2
        assert result.new_findings == 5

    def test_default_suppression_details(self):
        """Test default suppression_details is empty list."""
        result = LearningResult(
            total_findings=5,
            suppressed_count=0,
            adjusted_count=0,
            new_findings=5,
        )
        assert result.suppression_details == []

    def test_with_suppression_details(self):
        """Test with suppression_details."""
        details = [
            {"finding_id": "sec_001", "reason": "False positive"},
            {"finding_id": "sec_002", "reason": "Accepted risk"},
        ]
        result = LearningResult(
            total_findings=10,
            suppressed_count=2,
            adjusted_count=0,
            new_findings=8,
            suppression_details=details,
        )
        assert len(result.suppression_details) == 2
        assert result.suppression_details[0]["finding_id"] == "sec_001"


class TestSecurityLearningWizardInit:
    """Tests for SecurityLearningWizard initialization."""

    def test_name_property(self):
        """Test name property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            assert wizard.name == "Security Learning Wizard"

    def test_level_property(self):
        """Test level property is 4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            assert wizard.level == 4

    def test_default_pattern_storage_path(self):
        """Test default pattern storage path."""
        wizard = SecurityLearningWizard()
        assert wizard.pattern_storage_path == Path("./patterns/security")

    def test_custom_pattern_storage_path(self):
        """Test custom pattern storage path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            assert wizard.pattern_storage_path == Path(tmpdir)

    def test_creates_storage_directory(self):
        """Test storage directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "custom" / "security"
            SecurityLearningWizard(pattern_storage_path=str(storage_path))
            assert storage_path.exists()

    def test_vulnerability_patterns_loaded(self):
        """Test vulnerability patterns are loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            assert "sql_injection" in wizard.vulnerability_patterns
            assert "xss" in wizard.vulnerability_patterns
            assert "hardcoded_secret" in wizard.vulnerability_patterns
            assert "insecure_random" in wizard.vulnerability_patterns
            assert "path_traversal" in wizard.vulnerability_patterns
            assert "command_injection" in wizard.vulnerability_patterns


class TestVulnerabilityPatterns:
    """Tests for vulnerability pattern definitions."""

    def test_sql_injection_patterns(self):
        """Test SQL injection patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            pattern_def = wizard.vulnerability_patterns["sql_injection"]
            assert "patterns" in pattern_def
            assert len(pattern_def["patterns"]) > 0
            assert pattern_def["severity"] == "high"
            assert pattern_def["owasp"] == "A03:2021"

    def test_xss_patterns(self):
        """Test XSS patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            pattern_def = wizard.vulnerability_patterns["xss"]
            assert "innerHTML" in str(pattern_def["patterns"])
            assert pattern_def["severity"] == "high"

    def test_hardcoded_secret_patterns(self):
        """Test hardcoded secret patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            pattern_def = wizard.vulnerability_patterns["hardcoded_secret"]
            assert pattern_def["severity"] == "critical"
            assert "password" in str(pattern_def["patterns"])

    def test_insecure_random_patterns(self):
        """Test insecure random patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            pattern_def = wizard.vulnerability_patterns["insecure_random"]
            assert pattern_def["severity"] == "medium"

    def test_command_injection_patterns(self):
        """Test command injection patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            pattern_def = wizard.vulnerability_patterns["command_injection"]
            assert pattern_def["severity"] == "critical"
            assert "eval" in str(pattern_def["patterns"])


class TestSecurityLearningWizardAnalyze:
    """Tests for analyze method."""

    @pytest.mark.asyncio
    async def test_analyze_empty_project(self):
        """Test analyze on empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            assert result is not None
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_clean_project(self):
        """Test analyze on clean project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "clean.py").write_text("x = 1\ny = 2\n")

            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            assert result is not None

    @pytest.mark.asyncio
    async def test_analyze_with_apply_learning(self):
        """Test analyze with apply_learned_patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze(
                {
                    "project_path": tmpdir,
                    "apply_learned_patterns": True,
                },
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_analyze_returns_structure(self):
        """Test analyze returns expected structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            # Should have findings and learning info
            assert isinstance(result, dict)


class TestVulnerabilityDetection:
    """Tests for vulnerability detection."""

    def test_pattern_detects_sql_injection(self):
        """Test pattern detects SQL injection."""
        import re

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            code = "cursor.execute(f'SELECT * FROM users WHERE id={id}')"
            patterns = wizard.vulnerability_patterns["sql_injection"]["patterns"]
            matches = any(re.search(p, code) for p in patterns)
            assert matches

    def test_pattern_detects_xss(self):
        """Test pattern detects XSS."""
        import re

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            code = "element.innerHTML = userInput;"
            patterns = wizard.vulnerability_patterns["xss"]["patterns"]
            matches = any(re.search(p, code) for p in patterns)
            assert matches

    def test_pattern_detects_hardcoded_password(self):
        """Test pattern detects hardcoded password."""
        import re

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            code = "password = 'mysecretpassword123'"
            patterns = wizard.vulnerability_patterns["hardcoded_secret"]["patterns"]
            matches = any(re.search(p, code, re.IGNORECASE) for p in patterns)
            assert matches

    def test_pattern_detects_insecure_random(self):
        """Test pattern detects insecure random."""
        import re

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            code = "token = Math.random().toString(36)"
            patterns = wizard.vulnerability_patterns["insecure_random"]["patterns"]
            matches = any(re.search(p, code) for p in patterns)
            assert matches

    def test_pattern_detects_eval(self):
        """Test pattern detects eval usage."""
        import re

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            code = "result = eval(user_input)"
            patterns = wizard.vulnerability_patterns["command_injection"]["patterns"]
            matches = any(re.search(p, code) for p in patterns)
            assert matches


class TestSecurityLearningWizardIntegration:
    """Integration tests for SecurityLearningWizard."""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test full analysis workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with potential vulnerabilities
            (Path(tmpdir) / "auth.py").write_text("password = 'secret123'\nx = Math.random()\n")

            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})

            assert result is not None
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analysis_with_no_vulnerabilities(self):
        """Test analysis on secure project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "secure.py").write_text(
                "import os\nsecret = os.environ.get('SECRET')\n",
            )

            wizard = SecurityLearningWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})

            assert result is not None
