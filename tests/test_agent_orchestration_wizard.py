"""Tests for empathy_software_plugin/wizards/agent_orchestration_wizard.py

Tests the AgentOrchestrationWizard including:
- Initialization and properties
- Agent parsing from text
- Orchestration pattern analysis
- Complexity prediction
- Recommendation generation
- Helper methods

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.agent_orchestration_wizard import AgentOrchestrationWizard


class TestAgentOrchestrationWizardInit:
    """Tests for AgentOrchestrationWizard initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        wizard = AgentOrchestrationWizard()
        assert wizard.name == "Agent Orchestration Wizard"
        assert wizard.domain == "software"
        assert wizard.empathy_level == 4
        assert wizard.category == "ai_development"

    def test_inherits_base_wizard(self):
        """Test wizard inherits from BaseWizard."""
        from empathy_os.plugins import BaseWizard

        wizard = AgentOrchestrationWizard()
        assert isinstance(wizard, BaseWizard)


class TestGetRequiredContext:
    """Tests for get_required_context method."""

    def test_required_context_keys(self):
        """Test required context includes expected keys."""
        wizard = AgentOrchestrationWizard()
        context = wizard.get_required_context()
        assert "agent_definitions" in context
        assert "orchestration_code" in context
        assert "project_path" in context

    def test_required_context_returns_list(self):
        """Test required context returns list."""
        wizard = AgentOrchestrationWizard()
        context = wizard.get_required_context()
        assert isinstance(context, list)
        assert len(context) == 3


class TestParseAgentsFromText:
    """Tests for _parse_agents_from_text method."""

    def test_parse_numeric_agent_count(self):
        """Test parsing '5 agents' pattern."""
        wizard = AgentOrchestrationWizard()
        agents = wizard._parse_agents_from_text("We have 5 agents in our system")
        assert len(agents) == 5
        assert all(a["type"] == "specialized" for a in agents)

    def test_parse_specialized_agents(self):
        """Test parsing 'specialized agents' pattern."""
        wizard = AgentOrchestrationWizard()
        agents = wizard._parse_agents_from_text("Using 3 specialized agents")
        assert len(agents) == 3

    def test_parse_named_agents_colon_list(self):
        """Test parsing named agents from colon-separated list."""
        wizard = AgentOrchestrationWizard()
        text = "3 agents: ingestion, validation, output"
        agents = wizard._parse_agents_from_text(text)
        assert len(agents) == 3
        names = [a["name"] for a in agents]
        assert "ingestion" in names
        assert "validation" in names
        assert "output" in names

    def test_parse_agent_keywords(self):
        """Test parsing agent-like keywords."""
        wizard = AgentOrchestrationWizard()
        text = "We use ingestion, validation, and processing"
        agents = wizard._parse_agents_from_text(text)
        names = [a["name"].lower() for a in agents]
        assert "ingestion" in names
        assert "validation" in names
        assert "processing" in names

    def test_empty_input_returns_default_agent(self):
        """Test empty input returns default agent."""
        wizard = AgentOrchestrationWizard()
        agents = wizard._parse_agents_from_text("")
        assert len(agents) == 1
        assert agents[0]["name"] == "DefaultAgent"
        assert agents[0]["type"] == "generic"

    def test_no_matches_returns_default(self):
        """Test no matches returns default agent."""
        wizard = AgentOrchestrationWizard()
        agents = wizard._parse_agents_from_text("some random text without agent info")
        assert len(agents) == 1
        assert agents[0]["name"] == "DefaultAgent"

    def test_parse_various_keywords(self):
        """Test parsing various agent keywords."""
        wizard = AgentOrchestrationWizard()
        keywords = [
            "ingestion",
            "validation",
            "transformation",
            "analysis",
            "reporting",
            "extraction",
            "processing",
            "routing",
            "aggregation",
            "monitoring",
            "scheduler",
            "executor",
            "coordinator",
            "supervisor",
            "worker",
        ]
        for kw in keywords:
            agents = wizard._parse_agents_from_text(f"Using {kw} component")
            assert any(a["name"].lower() == kw for a in agents), f"Failed for {kw}"


class TestAnalyze:
    """Tests for analyze method."""

    @pytest.mark.asyncio
    async def test_analyze_text_input_mode(self):
        """Test analyze with user_input text."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze({"user_input": "5 agents: a, b, c, d, e"})
        assert "issues" in result
        assert "predictions" in result
        assert "recommendations" in result
        assert "patterns" in result
        assert "confidence" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_analyze_structured_mode(self):
        """Test analyze with structured input."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze(
            {
                "agent_definitions": [
                    {"name": "Agent1"},
                    {"name": "Agent2"},
                ],
                "orchestration_code": [],
                "project_path": ".",
            },
        )
        assert "issues" in result
        assert result["metadata"]["agent_count"] == 2

    @pytest.mark.asyncio
    async def test_analyze_returns_metadata(self):
        """Test analyze returns metadata."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze({"user_input": "3 agents"})
        metadata = result["metadata"]
        assert metadata["wizard"] == "Agent Orchestration Wizard"
        assert metadata["empathy_level"] == 4
        assert "agent_count" in metadata
        assert "orchestration_complexity" in metadata

    @pytest.mark.asyncio
    async def test_analyze_confidence(self):
        """Test analyze returns confidence."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze({"user_input": "3 agents"})
        assert result["confidence"] == 0.85


class TestAnalyzeOrchestrationPatterns:
    """Tests for _analyze_orchestration_patterns method."""

    @pytest.mark.asyncio
    async def test_missing_state_management_issue(self):
        """Test issues raised for >3 agents without state management."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(5)]
        issues = await wizard._analyze_orchestration_patterns(agents, [])
        assert any(i["type"] == "missing_state_management" for i in issues)

    @pytest.mark.asyncio
    async def test_no_state_management_with_few_agents(self):
        """Test no state management issue with 3 or fewer agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(3)]
        issues = await wizard._analyze_orchestration_patterns(agents, [])
        assert not any(i["type"] == "missing_state_management" for i in issues)

    @pytest.mark.asyncio
    async def test_missing_error_handling_issue(self):
        """Test issues raised for missing error handling."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1"}]
        issues = await wizard._analyze_orchestration_patterns(agents, [])
        assert any(i["type"] == "missing_error_handling" for i in issues)

    @pytest.mark.asyncio
    async def test_circular_dependencies_detected(self):
        """Test circular dependencies detection."""
        wizard = AgentOrchestrationWizard()
        agents = [
            {"name": "Agent1", "dependencies": ["Agent1"]},  # Self-dependency
        ]
        issues = await wizard._analyze_orchestration_patterns(agents, [])
        assert any(i["type"] == "circular_dependencies" for i in issues)

    @pytest.mark.asyncio
    async def test_ad_hoc_communication_issue(self):
        """Test ad-hoc communication issue for >5 agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(6)]
        issues = await wizard._analyze_orchestration_patterns(agents, [])
        assert any(i["type"] == "ad_hoc_communication" for i in issues)

    @pytest.mark.asyncio
    async def test_no_ad_hoc_communication_with_protocol(self):
        """Test no ad-hoc communication issue when protocol exists."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}", "message_schema": {"type": "object"}} for i in range(6)]
        issues = await wizard._analyze_orchestration_patterns(agents, [])
        assert not any(i["type"] == "ad_hoc_communication" for i in issues)


class TestPredictOrchestrationComplexity:
    """Tests for _predict_orchestration_complexity method."""

    @pytest.mark.asyncio
    async def test_complexity_threshold_7_agents(self):
        """Test complexity threshold prediction for 7 agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(7)]
        predictions = await wizard._predict_orchestration_complexity(agents, [], {})
        assert any(p["type"] == "orchestration_complexity_threshold" for p in predictions)

    @pytest.mark.asyncio
    async def test_complexity_threshold_12_agents(self):
        """Test complexity threshold prediction for 12 agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(12)]
        predictions = await wizard._predict_orchestration_complexity(agents, [], {})
        assert any(p["type"] == "orchestration_complexity_threshold" for p in predictions)

    @pytest.mark.asyncio
    async def test_no_complexity_threshold_6_agents(self):
        """Test no complexity threshold prediction for 6 agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(6)]
        predictions = await wizard._predict_orchestration_complexity(agents, [], {})
        assert not any(p["type"] == "orchestration_complexity_threshold" for p in predictions)

    @pytest.mark.asyncio
    async def test_communication_overhead_prediction(self):
        """Test communication overhead prediction for >6 agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(7)]
        predictions = await wizard._predict_orchestration_complexity(agents, [], {})
        assert any(p["type"] == "communication_overhead" for p in predictions)

    @pytest.mark.asyncio
    async def test_agent_versioning_prediction(self):
        """Test agent versioning prediction for >4 agents."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}"} for i in range(5)]
        predictions = await wizard._predict_orchestration_complexity(agents, [], {})
        assert any(p["type"] == "agent_version_chaos" for p in predictions)

    @pytest.mark.asyncio
    async def test_no_versioning_prediction_with_versions(self):
        """Test no versioning prediction when agents have versions."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": f"Agent{i}", "version": "1.0.0"} for i in range(5)]
        predictions = await wizard._predict_orchestration_complexity(agents, [], {})
        assert not any(p["type"] == "agent_version_chaos" for p in predictions)


class TestGenerateRecommendations:
    """Tests for _generate_recommendations method."""

    def test_critical_issues_first(self):
        """Test critical issues are prioritized."""
        wizard = AgentOrchestrationWizard()
        issues = [{"severity": "error", "type": "critical_issue"}]
        predictions = []
        recommendations = wizard._generate_recommendations(issues, predictions)
        assert any("CRITICAL" in r for r in recommendations)

    def test_high_impact_predictions(self):
        """Test high impact predictions are included."""
        wizard = AgentOrchestrationWizard()
        issues = []
        predictions = [
            {
                "type": "complexity_threshold",
                "alert": "Alert message",
                "impact": "high",
                "prevention_steps": ["Step 1", "Step 2"],
            },
        ]
        recommendations = wizard._generate_recommendations(issues, predictions)
        assert any("ALERT" in r for r in recommendations)

    def test_personal_experience_included(self):
        """Test personal experience is included."""
        wizard = AgentOrchestrationWizard()
        issues = []
        predictions = [
            {
                "type": "test",
                "alert": "Alert",
                "impact": "high",
                "prevention_steps": ["Step 1"],
                "personal_experience": "We learned this the hard way",
            },
        ]
        recommendations = wizard._generate_recommendations(issues, predictions)
        assert any("Experience:" in r for r in recommendations)


class TestExtractPatterns:
    """Tests for _extract_patterns method."""

    def test_pattern_type(self):
        """Test extracted pattern type."""
        wizard = AgentOrchestrationWizard()
        patterns = wizard._extract_patterns([], [])
        assert len(patterns) == 1
        assert patterns[0]["pattern_type"] == "coordination_complexity_threshold"

    def test_pattern_domain_agnostic(self):
        """Test pattern is domain agnostic."""
        wizard = AgentOrchestrationWizard()
        patterns = wizard._extract_patterns([], [])
        assert patterns[0]["domain_agnostic"] is True

    def test_pattern_applicable_to(self):
        """Test pattern applicable domains."""
        wizard = AgentOrchestrationWizard()
        patterns = wizard._extract_patterns([], [])
        applicable = patterns[0]["applicable_to"]
        assert "Multi-agent AI systems" in applicable
        assert "Microservices architecture" in applicable
        assert "Distributed systems" in applicable


class TestHelperMethods:
    """Tests for helper methods."""

    def test_has_state_management_true(self):
        """Test has_state_management returns True for StateGraph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "orchestration.py"
            file_path.write_text("from langgraph import StateGraph\n")
            wizard = AgentOrchestrationWizard()
            assert wizard._has_state_management([str(file_path)]) is True

    def test_has_state_management_false(self):
        """Test has_state_management returns False without patterns."""
        wizard = AgentOrchestrationWizard()
        assert wizard._has_state_management([]) is False

    def test_has_agent_error_handling_true(self):
        """Test has_agent_error_handling returns True for try/except."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "orchestration.py"
            file_path.write_text("try:\n    agent.run()\nexcept:\n    pass")
            wizard = AgentOrchestrationWizard()
            assert wizard._has_agent_error_handling([str(file_path)]) is True

    def test_has_agent_error_handling_false(self):
        """Test has_agent_error_handling returns False without try."""
        wizard = AgentOrchestrationWizard()
        assert wizard._has_agent_error_handling([]) is False

    def test_detect_circular_dependencies_self(self):
        """Test detect_circular_dependencies for self-dependency."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1", "dependencies": ["Agent1"]}]
        assert wizard._detect_circular_dependencies(agents) is True

    def test_detect_circular_dependencies_none(self):
        """Test detect_circular_dependencies returns False."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1", "dependencies": ["Agent2"]}]
        assert wizard._detect_circular_dependencies(agents) is False

    def test_has_communication_protocol_true(self):
        """Test has_communication_protocol with message_schema."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1", "message_schema": {}}]
        assert wizard._has_communication_protocol(agents) is True

    def test_has_communication_protocol_false(self):
        """Test has_communication_protocol without schema."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1"}]
        assert wizard._has_communication_protocol(agents) is False

    def test_assess_complexity_none(self):
        """Test assess_complexity returns 'none'."""
        wizard = AgentOrchestrationWizard()
        assert wizard._assess_complexity([]) == "none"

    def test_assess_complexity_low(self):
        """Test assess_complexity returns 'low'."""
        wizard = AgentOrchestrationWizard()
        assert wizard._assess_complexity(["file1.py"]) == "low"

    def test_assess_complexity_medium(self):
        """Test assess_complexity returns 'medium'."""
        wizard = AgentOrchestrationWizard()
        files = ["f1.py", "f2.py", "f3.py"]
        assert wizard._assess_complexity(files) == "medium"

    def test_assess_complexity_high(self):
        """Test assess_complexity returns 'high'."""
        wizard = AgentOrchestrationWizard()
        files = ["f1.py", "f2.py", "f3.py", "f4.py", "f5.py", "f6.py"]
        assert wizard._assess_complexity(files) == "high"

    def test_all_sequential_true(self):
        """Test all_sequential returns True without parallel patterns."""
        wizard = AgentOrchestrationWizard()
        assert wizard._all_sequential([]) is True

    def test_all_sequential_false(self):
        """Test all_sequential returns False with asyncio.gather."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "orchestration.py"
            file_path.write_text("await asyncio.gather(*tasks)")
            wizard = AgentOrchestrationWizard()
            assert wizard._all_sequential([str(file_path)]) is False

    def test_has_agent_versioning_true(self):
        """Test has_agent_versioning with version field."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1", "version": "1.0.0"}]
        assert wizard._has_agent_versioning(agents) is True

    def test_has_agent_versioning_false(self):
        """Test has_agent_versioning without version."""
        wizard = AgentOrchestrationWizard()
        agents = [{"name": "Agent1"}]
        assert wizard._has_agent_versioning(agents) is False

    def test_has_observability_true(self):
        """Test has_observability with logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "orchestration.py"
            file_path.write_text("import logger\nlogger.info('test')")
            wizard = AgentOrchestrationWizard()
            assert wizard._has_observability([str(file_path)]) is True

    def test_has_observability_false(self):
        """Test has_observability without observability."""
        wizard = AgentOrchestrationWizard()
        assert wizard._has_observability([]) is False


class TestIntegration:
    """Integration tests for AgentOrchestrationWizard."""

    @pytest.mark.asyncio
    async def test_full_analysis_simple(self):
        """Test full analysis with simple input."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze({"user_input": "3 agents: ingestion, validation, output"})
        assert result["confidence"] == 0.85
        assert result["metadata"]["agent_count"] >= 3

    @pytest.mark.asyncio
    async def test_full_analysis_complex(self):
        """Test full analysis with complex input."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze({"user_input": "10 specialized agents for data processing"})
        # Should have complexity threshold prediction
        predictions = result["predictions"]
        assert any(p["type"] == "orchestration_complexity_threshold" for p in predictions)

    @pytest.mark.asyncio
    async def test_analysis_with_valid_context(self):
        """Test analysis with valid structured context."""
        wizard = AgentOrchestrationWizard()
        result = await wizard.analyze(
            {
                "agent_definitions": [
                    {"name": "Ingestion", "version": "1.0"},
                    {"name": "Processing", "version": "1.0"},
                    {"name": "Output", "version": "1.0"},
                ],
                "orchestration_code": [],
                "project_path": ".",
            },
        )
        assert "issues" in result
        assert "predictions" in result
