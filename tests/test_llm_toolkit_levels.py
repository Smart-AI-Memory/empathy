"""Unit tests for empathy_llm_toolkit.levels module

Tests EmpathyLevel enum and class methods to achieve 95%+ coverage.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from empathy_llm_toolkit.levels import EmpathyLevel


class TestEmpathyLevelDescriptions:
    """Test EmpathyLevel description methods"""

    def test_get_description_level_1(self):
        """Test get_description for Level 1"""
        desc = EmpathyLevel.get_description(1)
        assert "Reactive" in desc
        assert desc == "Reactive: Help after being asked. Traditional Q&A."

    def test_get_description_level_2(self):
        """Test get_description for Level 2"""
        desc = EmpathyLevel.get_description(2)
        assert "Guided" in desc

    def test_get_description_level_3(self):
        """Test get_description for Level 3"""
        desc = EmpathyLevel.get_description(3)
        assert "Proactive" in desc

    def test_get_description_level_4(self):
        """Test get_description for Level 4"""
        desc = EmpathyLevel.get_description(4)
        assert "Anticipatory" in desc

    def test_get_description_level_5(self):
        """Test get_description for Level 5"""
        desc = EmpathyLevel.get_description(5)
        assert "Systems" in desc

    def test_get_description_unknown_level(self):
        """Test get_description for unknown level"""
        desc = EmpathyLevel.get_description(99)
        assert desc == "Unknown level"


class TestEmpathyLevelSystemPrompts:
    """Test EmpathyLevel system prompt generation"""

    def test_get_system_prompt_level_1(self):
        """Test system prompt for Level 1"""
        prompt = EmpathyLevel.get_system_prompt(1)
        assert "LEVEL 1 (REACTIVE)" in prompt
        assert "Empathy Framework" in prompt

    def test_get_system_prompt_level_2(self):
        """Test system prompt for Level 2"""
        prompt = EmpathyLevel.get_system_prompt(2)
        assert "LEVEL 2 (GUIDED)" in prompt
        assert "calibrated questions" in prompt.lower()

    def test_get_system_prompt_level_3(self):
        """Test system prompt for Level 3"""
        prompt = EmpathyLevel.get_system_prompt(3)
        assert "LEVEL 3 (PROACTIVE)" in prompt
        assert "pattern" in prompt.lower()

    def test_get_system_prompt_level_4(self):
        """Test system prompt for Level 4"""
        prompt = EmpathyLevel.get_system_prompt(4)
        assert "LEVEL 4 (ANTICIPATORY)" in prompt
        assert "trajectory" in prompt.lower()

    def test_get_system_prompt_level_5(self):
        """Test system prompt for Level 5"""
        prompt = EmpathyLevel.get_system_prompt(5)
        assert "LEVEL 5 (SYSTEMS)" in prompt
        assert "cross-domain" in prompt.lower()

    def test_get_system_prompt_unknown_level(self):
        """Test system prompt for unknown level returns base prompt only"""
        prompt = EmpathyLevel.get_system_prompt(99)
        assert "Empathy Framework" in prompt
        # Should not include level-specific content
        assert "LEVEL" not in prompt


class TestEmpathyLevelTemperature:
    """Test temperature recommendations"""

    def test_get_temperature_level_1(self):
        """Test temperature for Level 1"""
        temp = EmpathyLevel.get_temperature_recommendation(1)
        assert temp == 0.7

    def test_get_temperature_level_2(self):
        """Test temperature for Level 2"""
        temp = EmpathyLevel.get_temperature_recommendation(2)
        assert temp == 0.6

    def test_get_temperature_level_3(self):
        """Test temperature for Level 3"""
        temp = EmpathyLevel.get_temperature_recommendation(3)
        assert temp == 0.5

    def test_get_temperature_level_4(self):
        """Test temperature for Level 4"""
        temp = EmpathyLevel.get_temperature_recommendation(4)
        assert temp == 0.3

    def test_get_temperature_level_5(self):
        """Test temperature for Level 5"""
        temp = EmpathyLevel.get_temperature_recommendation(5)
        assert temp == 0.4

    def test_get_temperature_unknown_level(self):
        """Test temperature for unknown level returns default"""
        temp = EmpathyLevel.get_temperature_recommendation(99)
        assert temp == 0.7


class TestEmpathyLevelContextRequirements:
    """Test context requirements for each level - TARGETS MISSING LINES 142-175"""

    def test_get_required_context_level_1(self):
        """Test context requirements for Level 1"""
        context = EmpathyLevel.get_required_context(1)
        assert context["conversation_history"] is False
        assert context["user_patterns"] is False
        assert context["trajectory_data"] is False
        assert context["pattern_library"] is False

    def test_get_required_context_level_2(self):
        """Test context requirements for Level 2"""
        context = EmpathyLevel.get_required_context(2)
        assert context["conversation_history"] is True
        assert context["user_patterns"] is False
        assert context["trajectory_data"] is False
        assert context["pattern_library"] is False

    def test_get_required_context_level_3(self):
        """Test context requirements for Level 3"""
        context = EmpathyLevel.get_required_context(3)
        assert context["conversation_history"] is True
        assert context["user_patterns"] is True
        assert context["trajectory_data"] is False
        assert context["pattern_library"] is False

    def test_get_required_context_level_4(self):
        """Test context requirements for Level 4"""
        context = EmpathyLevel.get_required_context(4)
        assert context["conversation_history"] is True
        assert context["user_patterns"] is True
        assert context["trajectory_data"] is True
        assert context["pattern_library"] is False

    def test_get_required_context_level_5(self):
        """Test context requirements for Level 5"""
        context = EmpathyLevel.get_required_context(5)
        assert context["conversation_history"] is True
        assert context["user_patterns"] is True
        assert context["trajectory_data"] is True
        assert context["pattern_library"] is True

    def test_get_required_context_unknown_level(self):
        """Test context requirements for unknown level defaults to Level 1"""
        context = EmpathyLevel.get_required_context(99)
        # Should return Level 1 requirements as default
        assert context["conversation_history"] is False
        assert context["user_patterns"] is False
        assert context["trajectory_data"] is False
        assert context["pattern_library"] is False

    def test_get_required_context_returns_dict(self):
        """Test that get_required_context returns a dictionary"""
        for level in range(1, 6):
            context = EmpathyLevel.get_required_context(level)
            assert isinstance(context, dict)
            assert len(context) == 4


class TestEmpathyLevelMaxTokens:
    """Test max tokens recommendations"""

    def test_get_max_tokens_level_1(self):
        """Test max tokens for Level 1"""
        tokens = EmpathyLevel.get_max_tokens_recommendation(1)
        assert tokens == 1024

    def test_get_max_tokens_level_2(self):
        """Test max tokens for Level 2"""
        tokens = EmpathyLevel.get_max_tokens_recommendation(2)
        assert tokens == 1536

    def test_get_max_tokens_level_3(self):
        """Test max tokens for Level 3"""
        tokens = EmpathyLevel.get_max_tokens_recommendation(3)
        assert tokens == 2048

    def test_get_max_tokens_level_4(self):
        """Test max tokens for Level 4"""
        tokens = EmpathyLevel.get_max_tokens_recommendation(4)
        assert tokens == 4096

    def test_get_max_tokens_level_5(self):
        """Test max tokens for Level 5"""
        tokens = EmpathyLevel.get_max_tokens_recommendation(5)
        assert tokens == 4096

    def test_get_max_tokens_unknown_level(self):
        """Test max tokens for unknown level returns default"""
        tokens = EmpathyLevel.get_max_tokens_recommendation(99)
        assert tokens == 1024


class TestEmpathyLevelJSONMode:
    """Test JSON mode recommendations - TARGETS MISSING LINE 199"""

    def test_should_use_json_mode_level_1(self):
        """Test JSON mode for Level 1"""
        assert EmpathyLevel.should_use_json_mode(1) is False

    def test_should_use_json_mode_level_2(self):
        """Test JSON mode for Level 2"""
        assert EmpathyLevel.should_use_json_mode(2) is False

    def test_should_use_json_mode_level_3(self):
        """Test JSON mode for Level 3"""
        assert EmpathyLevel.should_use_json_mode(3) is False

    def test_should_use_json_mode_level_4(self):
        """Test JSON mode for Level 4 - should return True"""
        assert EmpathyLevel.should_use_json_mode(4) is True

    def test_should_use_json_mode_level_5(self):
        """Test JSON mode for Level 5 - should return True"""
        assert EmpathyLevel.should_use_json_mode(5) is True

    def test_should_use_json_mode_boundary(self):
        """Test JSON mode at boundary (level 4)"""
        # Test just below boundary
        assert EmpathyLevel.should_use_json_mode(3) is False
        # Test at boundary
        assert EmpathyLevel.should_use_json_mode(4) is True
        # Test above boundary
        assert EmpathyLevel.should_use_json_mode(5) is True


class TestEmpathyLevelUseCases:
    """Test typical use cases - TARGETS MISSING LINE 204"""

    def test_get_typical_use_cases_level_1(self):
        """Test use cases for Level 1"""
        cases = EmpathyLevel.get_typical_use_cases(1)
        assert isinstance(cases, list)
        assert len(cases) == 4
        assert "One-off questions" in cases

    def test_get_typical_use_cases_level_2(self):
        """Test use cases for Level 2"""
        cases = EmpathyLevel.get_typical_use_cases(2)
        assert isinstance(cases, list)
        assert len(cases) == 4
        assert any("Ambiguous" in case for case in cases)

    def test_get_typical_use_cases_level_3(self):
        """Test use cases for Level 3"""
        cases = EmpathyLevel.get_typical_use_cases(3)
        assert isinstance(cases, list)
        assert len(cases) == 4
        assert any("workflow" in case for case in cases)

    def test_get_typical_use_cases_level_4(self):
        """Test use cases for Level 4"""
        cases = EmpathyLevel.get_typical_use_cases(4)
        assert isinstance(cases, list)
        assert len(cases) == 4
        assert any("trajectory" in case for case in cases)

    def test_get_typical_use_cases_level_5(self):
        """Test use cases for Level 5"""
        cases = EmpathyLevel.get_typical_use_cases(5)
        assert isinstance(cases, list)
        assert len(cases) == 4
        assert any("domain" in case for case in cases)

    def test_get_typical_use_cases_unknown_level(self):
        """Test use cases for unknown level returns empty list"""
        cases = EmpathyLevel.get_typical_use_cases(99)
        assert cases == []

    def test_get_typical_use_cases_all_levels_unique(self):
        """Test that each level has different use cases"""
        all_cases = []
        for level in range(1, 6):
            cases = EmpathyLevel.get_typical_use_cases(level)
            all_cases.append(cases)

        # Each level should have unique primary use case
        first_items = [cases[0] for cases in all_cases]
        assert len(set(first_items)) == 5


class TestEmpathyLevelEnum:
    """Test EmpathyLevel enum values"""

    def test_level_values(self):
        """Test that levels have correct integer values"""
        assert EmpathyLevel.REACTIVE == 1
        assert EmpathyLevel.GUIDED == 2
        assert EmpathyLevel.PROACTIVE == 3
        assert EmpathyLevel.ANTICIPATORY == 4
        assert EmpathyLevel.SYSTEMS == 5

    def test_level_ordering(self):
        """Test that levels are ordered correctly"""
        assert EmpathyLevel.REACTIVE < EmpathyLevel.GUIDED
        assert EmpathyLevel.GUIDED < EmpathyLevel.PROACTIVE
        assert EmpathyLevel.PROACTIVE < EmpathyLevel.ANTICIPATORY
        assert EmpathyLevel.ANTICIPATORY < EmpathyLevel.SYSTEMS
