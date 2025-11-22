"""
Tests for Trust-Building Behaviors

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from empathy_os.trust_building import TrustBuildingBehaviors, TrustSignal


class TestTrustSignal:
    """Test TrustSignal dataclass"""

    def test_trust_signal_creation(self):
        """Test creating a trust signal"""
        signal = TrustSignal(
            signal_type="building",
            behavior="pre_format_handoff",
            evidence="Formatted data for manager",
            impact=0.7,
        )

        assert signal.signal_type == "building"
        assert signal.behavior == "pre_format_handoff"
        assert signal.evidence == "Formatted data for manager"
        assert signal.impact == 0.7

    def test_trust_signal_defaults(self):
        """Test trust signal with default values"""
        signal = TrustSignal(signal_type="eroding", behavior="missed_deadline")

        assert signal.evidence is None
        assert signal.impact == 0.5  # Default


class TestTrustBuildingBehaviors:
    """Test TrustBuildingBehaviors"""

    def test_initialization(self):
        """Test behaviors initialize correctly"""
        behaviors = TrustBuildingBehaviors()

        assert len(behaviors.trust_signals) == 0

    def test_pre_format_for_handoff_executive(self):
        """Test pre-formatting for executive"""
        behaviors = TrustBuildingBehaviors()

        data = {"tasks": 10, "completed": 7, "metrics": {"speed": 0.8}}

        formatted = behaviors.pre_format_for_handoff(
            data=data, recipient_role="executive", context="board_meeting"
        )

        assert "original_data" in formatted
        assert "format" in formatted
        assert formatted["format"] == "executive_summary"
        assert "summary" in formatted
        assert formatted["summary"]["type"] == "executive_summary"

        # Should record trust signal
        assert len(behaviors.trust_signals) == 1
        assert behaviors.trust_signals[0].behavior == "pre_format_handoff"

    def test_pre_format_for_handoff_developer(self):
        """Test pre-formatting for developer"""
        behaviors = TrustBuildingBehaviors()

        data = {"code": "test", "lines": 100}

        formatted = behaviors.pre_format_for_handoff(
            data=data, recipient_role="developer", context="code_review"
        )

        assert formatted["format"] == "technical_detail"
        assert formatted["summary"]["type"] == "technical_detail"

    def test_pre_format_for_handoff_team_lead(self):
        """Test pre-formatting for team lead"""
        behaviors = TrustBuildingBehaviors()

        data = {"tasks": ["T1", "T2", "T3"]}

        formatted = behaviors.pre_format_for_handoff(
            data=data, recipient_role="team_lead", context="sprint_planning"
        )

        assert formatted["format"] == "action_oriented"
        assert formatted["summary"]["type"] == "action_oriented"

    def test_pre_format_for_handoff_unknown_role(self):
        """Test pre-formatting for unknown role"""
        behaviors = TrustBuildingBehaviors()

        data = {"info": "data"}

        formatted = behaviors.pre_format_for_handoff(
            data=data, recipient_role="unknown_role", context="general"
        )

        assert formatted["format"] == "general"
        assert formatted["summary"]["type"] == "general"

    def test_clarify_before_acting_basic(self):
        """Test clarifying ambiguous instruction"""
        behaviors = TrustBuildingBehaviors()

        instruction = "Deploy the changes"
        ambiguities = ["which environment?", "which changes?"]

        clarification = behaviors.clarify_before_acting(
            instruction=instruction, detected_ambiguities=ambiguities
        )

        assert clarification["original_instruction"] == instruction
        assert clarification["status"] == "needs_clarification"
        assert len(clarification["ambiguities_detected"]) == 2
        assert len(clarification["clarifying_questions"]) == 2

        # Should record trust signal
        assert len(behaviors.trust_signals) == 1
        assert behaviors.trust_signals[0].behavior == "clarify_ambiguity"

    def test_clarify_before_acting_with_context(self):
        """Test clarifying with additional context"""
        behaviors = TrustBuildingBehaviors()

        instruction = "Update the system"
        ambiguities = ["which system?"]
        context = {"project": "backend", "urgency": "high"}

        clarification = behaviors.clarify_before_acting(
            instruction=instruction, detected_ambiguities=ambiguities, context=context
        )

        assert len(clarification["clarifying_questions"]) == 1
        question = clarification["clarifying_questions"][0]
        assert "ambiguity" in question
        assert "question" in question

    def test_volunteer_structure_critical_stress(self):
        """Test volunteering structure during critical stress"""
        behaviors = TrustBuildingBehaviors()

        stress_indicators = {
            "task_count": 20,
            "deadline_proximity": "12h",
            "complexity": "high",
            "team_capacity": "low",
        }
        scaffolding = ["prioritization", "breakdown", "templates"]

        support = behaviors.volunteer_structure_during_stress(
            stress_indicators=stress_indicators, available_scaffolding=scaffolding
        )

        assert support["stress_assessment"]["level"] == "critical"
        assert len(support["offered_support"]) > 0

        # Should offer immediate help for critical stress
        immediate_support = [s for s in support["offered_support"] if s.get("immediate")]
        assert len(immediate_support) > 0

        # Should record trust signal
        assert len(behaviors.trust_signals) == 1
        assert behaviors.trust_signals[0].behavior == "volunteer_structure"

    def test_volunteer_structure_high_stress(self):
        """Test volunteering structure during high stress"""
        behaviors = TrustBuildingBehaviors()

        stress_indicators = {"task_count": 15, "deadline_proximity": "24h", "complexity": "medium"}
        scaffolding = ["prioritization", "templates"]

        support = behaviors.volunteer_structure_during_stress(
            stress_indicators=stress_indicators, available_scaffolding=scaffolding
        )

        assert support["stress_assessment"]["level"] == "high"
        assert len(support["offered_support"]) > 0

    def test_volunteer_structure_moderate_stress(self):
        """Test volunteering structure during moderate stress"""
        behaviors = TrustBuildingBehaviors()

        stress_indicators = {"task_count": 8, "deadline": "3d"}
        scaffolding = ["templates"]

        support = behaviors.volunteer_structure_during_stress(
            stress_indicators=stress_indicators, available_scaffolding=scaffolding
        )

        assert support["stress_assessment"]["level"] == "moderate"

    def test_offer_proactive_help_comprehension_struggle(self):
        """Test offering help for comprehension struggle"""
        behaviors = TrustBuildingBehaviors()

        struggle_indicators = {"time_on_task": 45, "confusion_signals": 3}
        available_help = ["explanation", "examples", "guidance"]

        offer = behaviors.offer_proactive_help(
            struggle_indicators=struggle_indicators, available_help=available_help
        )

        assert offer["struggle_assessment"]["type"] == "comprehension"
        assert len(offer["help_offered"]) > 0

        # Should offer explanation and examples for comprehension
        help_types = [h["type"] for h in offer["help_offered"]]
        assert "explanation" in help_types or "examples" in help_types

        # Should record trust signal
        assert len(behaviors.trust_signals) == 1
        assert behaviors.trust_signals[0].behavior == "proactive_help"

    def test_offer_proactive_help_execution_struggle(self):
        """Test offering help for execution struggle"""
        behaviors = TrustBuildingBehaviors()

        struggle_indicators = {"repeated_errors": 5, "failed_attempts": 3}
        available_help = ["debugging", "guidance", "examples"]

        offer = behaviors.offer_proactive_help(
            struggle_indicators=struggle_indicators, available_help=available_help
        )

        assert offer["struggle_assessment"]["type"] == "execution"

        # Should offer debugging help for execution struggles
        help_types = [h["type"] for h in offer["help_offered"]]
        assert "debugging" in help_types or "step_by_step" in help_types

    def test_get_trust_trajectory_insufficient_data(self):
        """Test trust trajectory with insufficient data"""
        behaviors = TrustBuildingBehaviors()

        trajectory = behaviors.get_trust_trajectory()

        assert trajectory["status"] == "insufficient_data"
        assert trajectory["trajectory"] == "unknown"
        assert trajectory["signal_count"] == 0

    def test_get_trust_trajectory_strongly_building(self):
        """Test trust trajectory that's strongly building"""
        behaviors = TrustBuildingBehaviors()

        # Add mostly building signals
        for i in range(8):
            behaviors._record_trust_signal("building", f"behavior_{i}")
        for i in range(2):
            behaviors._record_trust_signal("eroding", f"bad_{i}")

        trajectory = behaviors.get_trust_trajectory()

        assert trajectory["status"] == "active"
        assert trajectory["trajectory"] == "strongly_building"
        assert trajectory["building_ratio"] == 0.8
        assert trajectory["building_signals"] == 8
        assert trajectory["eroding_signals"] == 2

    def test_get_trust_trajectory_building(self):
        """Test trust trajectory that's building"""
        behaviors = TrustBuildingBehaviors()

        # Add 60% building signals
        for i in range(6):
            behaviors._record_trust_signal("building", f"behavior_{i}")
        for i in range(4):
            behaviors._record_trust_signal("eroding", f"bad_{i}")

        trajectory = behaviors.get_trust_trajectory()

        assert trajectory["trajectory"] == "building"
        assert trajectory["building_ratio"] == 0.6

    def test_get_trust_trajectory_mixed(self):
        """Test mixed trust trajectory"""
        behaviors = TrustBuildingBehaviors()

        # Add 50-50 mix
        for i in range(5):
            behaviors._record_trust_signal("building", f"behavior_{i}")
        for i in range(5):
            behaviors._record_trust_signal("eroding", f"bad_{i}")

        trajectory = behaviors.get_trust_trajectory()

        assert trajectory["trajectory"] == "mixed"
        assert trajectory["building_ratio"] == 0.5

    def test_get_trust_trajectory_eroding(self):
        """Test eroding trust trajectory"""
        behaviors = TrustBuildingBehaviors()

        # Add mostly eroding signals
        for i in range(2):
            behaviors._record_trust_signal("building", f"behavior_{i}")
        for i in range(8):
            behaviors._record_trust_signal("eroding", f"bad_{i}")

        trajectory = behaviors.get_trust_trajectory()

        assert trajectory["trajectory"] == "eroding"
        assert trajectory["building_ratio"] == 0.2

    def test_determine_format(self):
        """Test format determination"""
        behaviors = TrustBuildingBehaviors()

        assert behaviors._determine_format("executive", "meeting") == "executive_summary"
        assert behaviors._determine_format("developer", "review") == "technical_detail"
        assert behaviors._determine_format("team_lead", "planning") == "action_oriented"
        assert behaviors._determine_format("unknown", "context") == "general"

    def test_extract_key_metrics(self):
        """Test extracting key metrics"""
        behaviors = TrustBuildingBehaviors()

        data = {"count": 10, "score": 0.85, "name": "test", "value": 42.5}

        metrics = behaviors._extract_key_metrics(data)

        assert len(metrics) > 0
        assert any("count" in m for m in metrics)
        assert any("score" in m for m in metrics)

    def test_assess_stress_level(self):
        """Test stress level assessment"""
        behaviors = TrustBuildingBehaviors()

        critical = {"i1": 1, "i2": 2, "i3": 3, "i4": 4}
        assert behaviors._assess_stress_level(critical) == "critical"

        high = {"i1": 1, "i2": 2, "i3": 3}
        assert behaviors._assess_stress_level(high) == "high"

        moderate = {"i1": 1, "i2": 2}
        assert behaviors._assess_stress_level(moderate) == "moderate"

        low = {"i1": 1}
        assert behaviors._assess_stress_level(low) == "low"

    def test_classify_struggle(self):
        """Test struggle classification"""
        behaviors = TrustBuildingBehaviors()

        exec_struggle = {"repeated_errors": 5}
        assert behaviors._classify_struggle(exec_struggle) == "execution"

        comp_struggle = {"time_on_task": 60}
        assert behaviors._classify_struggle(comp_struggle) == "comprehension"

        general_struggle = {"unknown": "indicator"}
        assert behaviors._classify_struggle(general_struggle) == "general"

    def test_record_trust_signal(self):
        """Test recording trust signals"""
        behaviors = TrustBuildingBehaviors()

        assert len(behaviors.trust_signals) == 0

        behaviors._record_trust_signal(
            signal_type="building", behavior="helpful_action", evidence="Did something helpful"
        )

        assert len(behaviors.trust_signals) == 1
        signal = behaviors.trust_signals[0]
        assert signal.signal_type == "building"
        assert signal.behavior == "helpful_action"
        assert signal.evidence == "Did something helpful"

    def test_reset(self):
        """Test resetting behaviors"""
        behaviors = TrustBuildingBehaviors()

        # Add some signals
        behaviors._record_trust_signal("building", "test")
        assert len(behaviors.trust_signals) == 1

        # Reset
        behaviors.reset()

        assert len(behaviors.trust_signals) == 0

    def test_integration_full_workflow(self):
        """Test full trust-building workflow"""
        behaviors = TrustBuildingBehaviors()

        # 1. Pre-format data for handoff
        data = {"tasks": 10, "completed": 7}
        formatted = behaviors.pre_format_for_handoff(
            data=data, recipient_role="manager", context="status_update"
        )
        assert "summary" in formatted

        # 2. Clarify ambiguous instruction
        clarification = behaviors.clarify_before_acting(
            instruction="Update the report", detected_ambiguities=["which report?", "when?"]
        )
        assert clarification["status"] == "needs_clarification"

        # 3. Volunteer structure during stress
        support = behaviors.volunteer_structure_during_stress(
            stress_indicators={"task_count": 15, "deadline": "12h", "complexity": "high"},
            available_scaffolding=["prioritization", "breakdown"],
        )
        assert len(support["offered_support"]) > 0

        # 4. Offer proactive help
        help_offer = behaviors.offer_proactive_help(
            struggle_indicators={"repeated_errors": 3}, available_help=["debugging", "explanation"]
        )
        assert len(help_offer["help_offered"]) > 0

        # 5. Check trust trajectory
        trajectory = behaviors.get_trust_trajectory()
        assert trajectory["status"] == "active"
        assert trajectory["trajectory"] == "strongly_building"  # All building signals
        assert trajectory["signal_count"] == 4  # 4 behaviors recorded

    def test_create_summaries(self):
        """Test creating different summary formats"""
        behaviors = TrustBuildingBehaviors()

        data = {"metric1": 10, "metric2": 0.85, "info": "test"}

        # Executive summary
        exec_summary = behaviors._create_executive_summary(data, "meeting")
        assert exec_summary["type"] == "executive_summary"
        assert "key_metrics" in exec_summary

        # Technical summary
        tech_summary = behaviors._create_technical_summary(data, "review")
        assert tech_summary["type"] == "technical_detail"
        assert "details" in tech_summary

        # Action-oriented summary
        action_summary = behaviors._create_action_oriented_summary(data, "planning")
        assert action_summary["type"] == "action_oriented"
        assert "immediate_actions" in action_summary

        # Generic summary
        generic_summary = behaviors._create_generic_summary(data, "general")
        assert generic_summary["type"] == "general"

    def test_extract_immediate_actions(self):
        """Test extracting immediate actions"""
        behaviors = TrustBuildingBehaviors()

        data_with_actions = {"actions": ["A1", "A2", "A3", "A4", "A5", "A6"]}
        actions = behaviors._extract_immediate_actions(data_with_actions)
        assert len(actions) == 5  # Top 5

        data_without_actions = {"info": "test"}
        actions = behaviors._extract_immediate_actions(data_without_actions)
        assert len(actions) > 0  # Default action

    def test_generate_clarifying_question(self):
        """Test generating clarifying questions"""
        behaviors = TrustBuildingBehaviors()

        question = behaviors._generate_clarifying_question(
            instruction="Deploy changes",
            ambiguity="which environment?",
            context={"project": "backend"},
        )

        assert "ambiguity" in question
        assert question["ambiguity"] == "which environment?"
        assert "question" in question
        assert "Could you clarify" in question["question"]

    def test_extract_priorities_with_data(self):
        """Test extracting priorities when they exist in data"""
        behaviors = TrustBuildingBehaviors()

        # Data with priorities
        data_with_priorities = {"priorities": ["P1", "P2", "P3"]}
        priorities = behaviors._extract_priorities(data_with_priorities)
        assert priorities == ["P1", "P2", "P3"]

        # Data without priorities
        data_without_priorities = {"info": "test"}
        priorities_empty = behaviors._extract_priorities(data_without_priorities)
        assert priorities_empty == []
