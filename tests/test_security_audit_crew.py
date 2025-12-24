"""
Tests for Security Audit Crew

Tests the multi-agent security audit crew that demonstrates
CrewAI's hierarchical collaboration patterns.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path

import pytest


class TestSecurityFinding:
    """Test SecurityFinding data structure."""

    def test_finding_creation(self):
        """Test creating a security finding."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        finding = SecurityFinding(
            title="SQL Injection in user input",
            description="User input is not sanitized before SQL query",
            severity=Severity.CRITICAL,
            category=FindingCategory.INJECTION,
            file_path="src/api/users.py",
            line_number=42,
            code_snippet='query = f"SELECT * FROM users WHERE id = {user_id}"',
            remediation="Use parameterized queries",
            cwe_id="CWE-89",
            cvss_score=9.8,
        )

        assert finding.title == "SQL Injection in user input"
        assert finding.severity == Severity.CRITICAL
        assert finding.category == FindingCategory.INJECTION
        assert finding.cwe_id == "CWE-89"
        assert finding.cvss_score == 9.8

    def test_finding_to_dict(self):
        """Test converting finding to dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        finding = SecurityFinding(
            title="XSS Vulnerability",
            description="Reflected XSS in search parameter",
            severity=Severity.HIGH,
            category=FindingCategory.XSS,
        )

        data = finding.to_dict()

        assert data["title"] == "XSS Vulnerability"
        assert data["severity"] == "high"
        assert data["category"] == "cross_site_scripting"
        assert data["confidence"] == 1.0

    def test_finding_defaults(self):
        """Test finding default values."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        finding = SecurityFinding(
            title="Test",
            description="Test finding",
            severity=Severity.LOW,
            category=FindingCategory.OTHER,
        )

        assert finding.file_path is None
        assert finding.line_number is None
        assert finding.cwe_id is None
        assert finding.confidence == 1.0
        assert finding.metadata == {}


class TestSecurityReport:
    """Test SecurityReport data structure."""

    def test_report_creation(self):
        """Test creating a security report."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding, SecurityReport
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        findings = [
            SecurityFinding(
                title="Critical SQL Injection",
                description="...",
                severity=Severity.CRITICAL,
                category=FindingCategory.INJECTION,
            ),
            SecurityFinding(
                title="High XSS",
                description="...",
                severity=Severity.HIGH,
                category=FindingCategory.XSS,
            ),
            SecurityFinding(
                title="Medium misconfiguration",
                description="...",
                severity=Severity.MEDIUM,
                category=FindingCategory.MISCONFIGURATION,
            ),
        ]

        report = SecurityReport(
            target="./src",
            findings=findings,
            summary="Found 3 issues",
            audit_duration_seconds=10.5,
        )

        assert report.target == "./src"
        assert len(report.findings) == 3
        assert len(report.critical_findings) == 1
        assert len(report.high_findings) == 1

    def test_report_risk_score(self):
        """Test risk score calculation."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding, SecurityReport
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        # Empty report = 0 risk
        empty_report = SecurityReport(target="./src", findings=[])
        assert empty_report.risk_score == 0.0

        # Report with findings
        findings = [
            SecurityFinding(
                title="Critical",
                description="...",
                severity=Severity.CRITICAL,
                category=FindingCategory.OTHER,
                confidence=1.0,
            ),
            SecurityFinding(
                title="High",
                description="...",
                severity=Severity.HIGH,
                category=FindingCategory.OTHER,
                confidence=0.8,
            ),
        ]

        report = SecurityReport(target="./src", findings=findings)
        # Critical: 25 * 1.0 = 25, High: 15 * 0.8 = 12, Total = 37
        assert report.risk_score == 37.0

    def test_report_findings_by_category(self):
        """Test grouping findings by category."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding, SecurityReport
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        findings = [
            SecurityFinding(
                title="Injection 1",
                description="...",
                severity=Severity.HIGH,
                category=FindingCategory.INJECTION,
            ),
            SecurityFinding(
                title="Injection 2",
                description="...",
                severity=Severity.MEDIUM,
                category=FindingCategory.INJECTION,
            ),
            SecurityFinding(
                title="XSS 1",
                description="...",
                severity=Severity.HIGH,
                category=FindingCategory.XSS,
            ),
        ]

        report = SecurityReport(target="./src", findings=findings)
        by_cat = report.findings_by_category

        assert len(by_cat["injection"]) == 2
        assert len(by_cat["cross_site_scripting"]) == 1

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityFinding, SecurityReport
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        findings = [
            SecurityFinding(
                title="Test",
                description="...",
                severity=Severity.CRITICAL,
                category=FindingCategory.OTHER,
            ),
        ]

        report = SecurityReport(
            target="./src",
            findings=findings,
            summary="Found 1 issue",
            audit_duration_seconds=5.0,
            agents_used=["lead", "hunter"],
        )

        data = report.to_dict()

        assert data["target"] == "./src"
        assert data["finding_counts"]["critical"] == 1
        assert data["finding_counts"]["total"] == 1
        assert len(data["agents_used"]) == 2


class TestSecurityAuditConfig:
    """Test SecurityAuditConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditConfig

        config = SecurityAuditConfig()

        assert config.provider == "anthropic"
        assert config.scan_depth == "standard"
        assert config.memory_graph_enabled is True
        assert config.resilience_enabled is True
        assert config.lead_tier == "premium"
        assert config.hunter_tier == "capable"
        assert config.compliance_tier == "cheap"

    def test_custom_config(self):
        """Test custom configuration."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditConfig

        config = SecurityAuditConfig(
            provider="openai",
            scan_depth="thorough",
            memory_graph_enabled=False,
            timeout_seconds=600.0,
        )

        assert config.provider == "openai"
        assert config.scan_depth == "thorough"
        assert config.memory_graph_enabled is False
        assert config.timeout_seconds == 600.0


class TestSecurityAuditCrew:
    """Test SecurityAuditCrew creation and initialization."""

    def test_crew_creation_with_config(self):
        """Test creating crew with config object."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditConfig, SecurityAuditCrew

        config = SecurityAuditConfig(
            api_key="test-key",
            scan_depth="quick",
        )

        crew = SecurityAuditCrew(config=config)

        assert crew.config.api_key == "test-key"
        assert crew.config.scan_depth == "quick"
        assert crew.is_initialized is False

    def test_crew_creation_with_kwargs(self):
        """Test creating crew with keyword arguments."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        crew = SecurityAuditCrew(
            api_key="test-key",
            provider="openai",
            memory_graph_enabled=False,
        )

        assert crew.config.api_key == "test-key"
        assert crew.config.provider == "openai"
        assert crew.config.memory_graph_enabled is False

    @pytest.mark.asyncio
    async def test_crew_initialization(self):
        """Test lazy initialization of crew agents."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        with tempfile.TemporaryDirectory() as tmpdir:
            crew = SecurityAuditCrew(
                memory_graph_enabled=False,  # Disable to avoid file I/O
                memory_graph_path=str(Path(tmpdir) / "test.json"),
            )

            # Not initialized yet
            assert crew.is_initialized is False
            assert len(crew.agents) == 0

            # Initialize
            await crew._initialize()

            # Now initialized with 5 agents
            assert crew.is_initialized is True
            assert len(crew.agents) == 5
            assert "lead" in crew.agents
            assert "hunter" in crew.agents
            assert "assessor" in crew.agents
            assert "remediation" in crew.agents
            assert "compliance" in crew.agents

    @pytest.mark.asyncio
    async def test_crew_agent_stats(self):
        """Test getting agent statistics."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        with tempfile.TemporaryDirectory() as tmpdir:
            crew = SecurityAuditCrew(
                memory_graph_enabled=False,
                memory_graph_path=str(Path(tmpdir) / "test.json"),
            )

            stats = await crew.get_agent_stats()

            assert stats["agent_count"] == 5
            assert "lead" in stats["agents"]
            assert "memory_graph_enabled" in stats


class TestSecurityAuditCrewParsing:
    """Test SecurityAuditCrew parsing logic."""

    def test_generate_summary_no_findings(self):
        """Test summary generation with no findings."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        crew = SecurityAuditCrew()
        summary = crew._generate_summary([])

        assert "No security issues" in summary

    def test_generate_summary_with_findings(self):
        """Test summary generation with findings."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew, SecurityFinding
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        crew = SecurityAuditCrew()

        findings = [
            SecurityFinding(
                title="Critical",
                description="...",
                severity=Severity.CRITICAL,
                category=FindingCategory.INJECTION,
            ),
            SecurityFinding(
                title="High 1",
                description="...",
                severity=Severity.HIGH,
                category=FindingCategory.XSS,
            ),
            SecurityFinding(
                title="High 2",
                description="...",
                severity=Severity.HIGH,
                category=FindingCategory.XSS,
            ),
        ]

        summary = crew._generate_summary(findings)

        assert "3 findings" in summary
        assert "1 CRITICAL" in summary
        assert "2 HIGH" in summary

    def test_parse_text_findings(self):
        """Test parsing findings from text output."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        crew = SecurityAuditCrew()

        text = """
        CRITICAL: SQL Injection vulnerability detected in login form
        The user input is passed directly to database query.

        HIGH: XSS issue found in search results
        Search term is reflected without encoding.
        """

        findings = crew._parse_text_findings(text)

        assert len(findings) >= 1  # Should detect at least one finding

    def test_dict_to_finding(self):
        """Test converting dictionary to finding."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory, Severity

        crew = SecurityAuditCrew()

        data = {
            "title": "Test Finding",
            "description": "Description here",
            "severity": "high",
            "category": "injection",
            "cwe_id": "CWE-89",
            "cvss_score": 8.5,
        }

        finding = crew._dict_to_finding(data)

        assert finding.title == "Test Finding"
        assert finding.severity == Severity.HIGH
        assert finding.category == FindingCategory.INJECTION
        assert finding.cwe_id == "CWE-89"
        assert finding.cvss_score == 8.5


class TestSecurityAuditCrewWorkflow:
    """Test SecurityAuditCrew workflow execution."""

    def test_build_audit_task_standard(self):
        """Test building audit task description."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        crew = SecurityAuditCrew(scan_depth="standard")

        task = crew._build_audit_task("./src", {})

        assert "./src" in task
        assert "standard" in task.lower()
        assert "Vulnerability Hunter" in task
        assert "Security Lead" in task

    def test_build_audit_task_with_context(self):
        """Test building audit task with context."""
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew

        crew = SecurityAuditCrew(scan_depth="thorough")

        context = {
            "similar_audits": [{"name": "previous_audit", "risk_score": 45}],
            "focus_areas": ["authentication", "injection"],
        }

        task = crew._build_audit_task("./src", context)

        assert "Similar Audits Found: 1" in task
        assert "Focus Areas" in task

    @pytest.mark.asyncio
    async def test_audit_with_mocked_workflow(self):
        """Test audit execution with mocked workflow."""
        from unittest.mock import AsyncMock, MagicMock

        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditConfig, SecurityAuditCrew

        config = SecurityAuditConfig(
            memory_graph_enabled=False,
        )
        crew = SecurityAuditCrew(config=config)

        # Mock the initialization and workflow
        crew._initialized = True
        crew._factory = MagicMock()
        crew._agents = {
            "lead": MagicMock(),
            "hunter": MagicMock(),
            "assessor": MagicMock(),
            "remediation": MagicMock(),
            "compliance": MagicMock(),
        }

        # Mock workflow
        mock_workflow = MagicMock()
        mock_workflow.run = AsyncMock(
            return_value={
                "output": "Found SQL injection vulnerability",
                "metadata": {
                    "findings": [
                        {
                            "title": "SQL Injection",
                            "description": "...",
                            "severity": "critical",
                            "category": "injection",
                        }
                    ]
                },
            }
        )
        crew._workflow = mock_workflow

        report = await crew.audit("./src")

        assert report.target == "./src"
        assert len(report.findings) == 1
        assert report.findings[0].title == "SQL Injection"


class TestSeverityEnum:
    """Test Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        from empathy_llm_toolkit.agent_factory.crews.security_audit import Severity

        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestFindingCategoryEnum:
    """Test FindingCategory enum."""

    def test_category_values(self):
        """Test finding category enum values."""
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory

        assert FindingCategory.INJECTION.value == "injection"
        assert FindingCategory.XSS.value == "cross_site_scripting"
        assert FindingCategory.BROKEN_AUTH.value == "broken_authentication"
        assert FindingCategory.SENSITIVE_DATA.value == "sensitive_data_exposure"

    def test_all_owasp_categories(self):
        """Test all OWASP Top 10 categories are represented."""
        from empathy_llm_toolkit.agent_factory.crews.security_audit import FindingCategory

        # Should have at least 10 categories (OWASP Top 10 + OTHER)
        assert len(FindingCategory) >= 10


class TestCrewExports:
    """Test that crew module exports are correct."""

    def test_public_exports(self):
        """Test public exports from crews module."""
        from empathy_llm_toolkit.agent_factory.crews import (
            SecurityAuditConfig,
            SecurityAuditCrew,
            SecurityFinding,
            SecurityReport,
        )

        assert SecurityAuditCrew is not None
        assert SecurityAuditConfig is not None
        assert SecurityFinding is not None
        assert SecurityReport is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
