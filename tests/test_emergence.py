"""
Tests for Emergence Detection

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from empathy_os.emergence import EmergenceDetector, EmergentProperty


class TestEmergentProperty:
    """Test EmergentProperty dataclass"""

    def test_emergent_property_creation(self):
        """Test creating an emergent property"""
        prop = EmergentProperty(
            property_type="norm",
            description="Quick response time norm",
            confidence=0.8,
            components_involved=["ai", "human"],
        )

        assert prop.property_type == "norm"
        assert prop.description == "Quick response time norm"
        assert prop.confidence == 0.8
        assert len(prop.components_involved) == 2
        assert len(prop.evidence) == 0  # Default

    def test_emergent_property_with_evidence(self):
        """Test creating emergent property with evidence"""
        evidence = [{"interaction": 1}, {"interaction": 2}]
        prop = EmergentProperty(
            property_type="pattern",
            description="Collaboration pattern",
            confidence=0.9,
            evidence=evidence,
        )

        assert len(prop.evidence) == 2
        assert prop.confidence == 0.9


class TestEmergenceDetector:
    """Test EmergenceDetector"""

    def test_initialization(self):
        """Test detector initializes correctly"""
        detector = EmergenceDetector()

        assert len(detector.detected_properties) == 0
        assert isinstance(detector.baseline_metrics, dict)
        assert len(detector.baseline_metrics) == 0

    def test_detect_emergent_norms_empty(self):
        """Test norm detection with empty interactions"""
        detector = EmergenceDetector()

        norms = detector.detect_emergent_norms([])

        assert len(norms) == 0

    def test_detect_emergent_norms_insufficient_data(self):
        """Test norm detection with insufficient data"""
        detector = EmergenceDetector()

        interactions = [{"response_time": 5}]

        norms = detector.detect_emergent_norms(interactions)

        # Need 3+ for norm detection
        assert len(norms) == 0

    def test_detect_response_time_norm(self):
        """Test detecting response time norm"""
        detector = EmergenceDetector()

        # Consistent response times (low variance)
        interactions = [
            {"response_time": 5.0},
            {"response_time": 5.2},
            {"response_time": 4.8},
            {"response_time": 5.1},
        ]

        norms = detector.detect_emergent_norms(interactions)

        assert len(norms) >= 1
        norm = norms[0]
        assert norm.property_type == "norm"
        assert "Response time norm" in norm.description
        assert norm.confidence > 0.7  # High consistency
        assert "ai_agent" in norm.components_involved

    def test_detect_response_time_norm_inconsistent(self):
        """Test response time norm with high variance (no norm)"""
        detector = EmergenceDetector()

        # Inconsistent response times (high variance)
        interactions = [
            {"response_time": 1.0},
            {"response_time": 10.0},
            {"response_time": 2.0},
            {"response_time": 15.0},
        ]

        norms = detector.detect_emergent_norms(interactions)

        # Should not detect norm with high variance
        assert len(norms) == 0

    def test_detect_communication_pattern_norm(self):
        """Test detecting communication pattern norm"""
        detector = EmergenceDetector()

        # Frequent clarifying questions
        interactions = [
            {"type": "clarifying_question", "content": "Q1"},
            {"type": "clarifying_question", "content": "Q2"},
            {"type": "response", "content": "R1"},
            {"type": "clarifying_question", "content": "Q3"},
        ]

        norms = detector.detect_emergent_norms(interactions)

        # Should detect clarifying questions pattern (3/4 = 75%)
        pattern_norms = [n for n in norms if "Communication pattern" in n.description]
        assert len(pattern_norms) >= 1
        assert pattern_norms[0].confidence > 0.6

    def test_measure_emergence_empty_baseline(self):
        """Test measuring emergence with empty states"""
        detector = EmergenceDetector()

        baseline = {}
        current = {}

        score = detector.measure_emergence(baseline, current)

        assert score == 0.0

    def test_measure_emergence_trust_growth(self):
        """Test measuring emergence with trust growth"""
        detector = EmergenceDetector()

        baseline = {"trust": 0.3, "interactions": 10}
        current = {"trust": 0.8, "interactions": 50}

        score = detector.measure_emergence(baseline, current)

        # Should detect emergence from trust growth and interaction increase
        assert score > 0.0
        assert score <= 1.0

    def test_measure_emergence_new_capabilities(self):
        """Test measuring emergence with new capabilities"""
        detector = EmergenceDetector()

        baseline = {"trust": 0.5, "interactions": 10}
        current = {
            "trust": 0.6,
            "interactions": 20,
            "shared_patterns": 3,  # New capability
            "collaboration_norms": 2,  # New capability
        }

        score = detector.measure_emergence(baseline, current)

        # Should detect emergence from new capabilities
        assert score > 0.0

    def test_measure_emergence_high_score(self):
        """Test measuring high emergence score"""
        detector = EmergenceDetector()

        baseline = {"trust": 0.2, "interactions": 5}
        current = {
            "trust": 0.9,  # Significant trust growth
            "interactions": 100,  # Many more interactions
            "shared_patterns": 8,  # Multiple patterns
            "custom_workflows": 3,  # New capabilities
            "team_norms": 5,
        }

        score = detector.measure_emergence(baseline, current)

        # High emergence expected
        assert score > 0.5
        assert score <= 1.0

    def test_detect_emergent_capabilities_insufficient_data(self):
        """Test capability detection with insufficient data"""
        detector = EmergenceDetector()

        history = [{"trust": 0.5}]

        capabilities = detector.detect_emergent_capabilities(history)

        assert len(capabilities) == 0

    def test_detect_emergent_capabilities_with_growth(self):
        """Test detecting emergent capabilities"""
        detector = EmergenceDetector()

        history = [
            {"trust": 0.3, "interactions": 5},
            {"trust": 0.5, "interactions": 15, "patterns": 2},
            {"trust": 0.7, "interactions": 30, "patterns": 5, "workflows": 3},
        ]

        capabilities = detector.detect_emergent_capabilities(history)

        # Should detect new capabilities: "patterns" and "workflows"
        assert len(capabilities) >= 2
        assert all(c.property_type == "capability" for c in capabilities)
        assert any("patterns" in c.description for c in capabilities)
        assert any("workflows" in c.description for c in capabilities)

    def test_calculate_consistency_high(self):
        """Test consistency calculation with consistent values"""
        detector = EmergenceDetector()

        values = [5.0, 5.1, 4.9, 5.0, 5.1]
        consistency = detector._calculate_consistency(values)

        assert consistency > 0.8  # High consistency

    def test_calculate_consistency_low(self):
        """Test consistency calculation with inconsistent values"""
        detector = EmergenceDetector()

        values = [1.0, 10.0, 2.0, 15.0, 3.0]
        consistency = detector._calculate_consistency(values)

        assert consistency < 0.5  # Low consistency

    def test_calculate_consistency_insufficient_data(self):
        """Test consistency with insufficient data"""
        detector = EmergenceDetector()

        values = [5.0]
        consistency = detector._calculate_consistency(values)

        assert consistency == 0.0

    def test_calculate_consistency_zero_mean(self):
        """Test consistency with zero mean"""
        detector = EmergenceDetector()

        values = [0.0, 0.0, 0.0]
        consistency = detector._calculate_consistency(values)

        assert consistency == 0.0

    def test_analyze_communication_patterns_empty(self):
        """Test analyzing patterns with empty interactions"""
        detector = EmergenceDetector()

        patterns = detector._analyze_communication_patterns([])

        assert len(patterns) == 0

    def test_analyze_communication_patterns_clarifying(self):
        """Test detecting clarifying questions pattern"""
        detector = EmergenceDetector()

        interactions = [
            {"type": "clarifying_question"},
            {"type": "clarifying_question"},
            {"type": "response"},
        ]

        patterns = detector._analyze_communication_patterns(interactions)

        assert "clarifying_questions" in patterns
        assert patterns["clarifying_questions"]["frequency"] > 0.6
        assert patterns["clarifying_questions"]["count"] == 2

    def test_analyze_communication_patterns_proactive(self):
        """Test detecting proactive suggestions pattern"""
        detector = EmergenceDetector()

        interactions = [
            {"type": "proactive_suggestion"},
            {"type": "proactive_suggestion"},
            {"type": "response"},
        ]

        patterns = detector._analyze_communication_patterns(interactions)

        assert "proactive_suggestions" in patterns
        assert patterns["proactive_suggestions"]["frequency"] > 0.6

    def test_get_detected_properties_all(self):
        """Test getting all detected properties"""
        detector = EmergenceDetector()

        # Add some properties
        prop1 = EmergentProperty(property_type="norm", description="Test norm")
        prop2 = EmergentProperty(property_type="capability", description="Test capability")

        detector.detected_properties = [prop1, prop2]

        properties = detector.get_detected_properties()

        assert len(properties) == 2

    def test_get_detected_properties_filtered(self):
        """Test getting filtered properties by type"""
        detector = EmergenceDetector()

        prop1 = EmergentProperty(property_type="norm", description="Norm 1")
        prop2 = EmergentProperty(property_type="norm", description="Norm 2")
        prop3 = EmergentProperty(property_type="capability", description="Cap 1")

        detector.detected_properties = [prop1, prop2, prop3]

        norms = detector.get_detected_properties(property_type="norm")

        assert len(norms) == 2
        assert all(p.property_type == "norm" for p in norms)

    def test_reset(self):
        """Test resetting detector"""
        detector = EmergenceDetector()

        # Add some data
        prop = EmergentProperty(property_type="norm", description="Test")
        detector.detected_properties = [prop]
        detector.baseline_metrics = {"trust": 0.5}

        assert len(detector.detected_properties) == 1
        assert len(detector.baseline_metrics) == 1

        # Reset
        detector.reset()

        assert len(detector.detected_properties) == 0
        assert len(detector.baseline_metrics) == 0

    def test_integration_full_workflow(self):
        """Test full workflow: detect norms, measure emergence, detect capabilities"""
        detector = EmergenceDetector()

        # Step 1: Detect norms from interactions
        interactions = [
            {"response_time": 5.0, "type": "clarifying_question"},
            {"response_time": 5.1, "type": "clarifying_question"},
            {"response_time": 4.9, "type": "response"},
            {"response_time": 5.0, "type": "clarifying_question"},
        ]

        norms = detector.detect_emergent_norms(interactions)
        assert len(norms) >= 1

        # Step 2: Measure emergence
        baseline = {"trust": 0.3, "interactions": 10}
        current = {"trust": 0.7, "interactions": 50, "patterns": 3}

        emergence_score = detector.measure_emergence(baseline, current)
        assert emergence_score > 0.0

        # Step 3: Detect capabilities
        history = [
            {"trust": 0.3},
            {"trust": 0.5, "workflows": 2},
            {"trust": 0.7, "workflows": 5, "patterns": 3},
        ]

        capabilities = detector.detect_emergent_capabilities(history)
        assert len(capabilities) >= 2

        # Verify all detected
        all_properties = detector.get_detected_properties()
        assert len(all_properties) > 0
