"""Unit tests for EmpathyLLM core

Tests the core EmpathyLLM orchestrator with mocked providers,
focusing on level progression, state management, and interaction logic.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_llm_toolkit.core import EmpathyLLM
from empathy_llm_toolkit.state import CollaborationState, PatternType, UserPattern

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_provider_response():
    """Create mock provider response"""
    response = MagicMock()
    response.content = "Mock LLM response"
    response.model = "claude-test"
    response.tokens_used = 100
    return response


@pytest.fixture
def mock_provider(mock_provider_response):
    """Create mock LLM provider"""
    provider = AsyncMock()
    provider.generate = AsyncMock(return_value=mock_provider_response)
    return provider


# ============================================================================
# Initialization Tests
# ============================================================================


def test_empathy_llm_initialization_anthropic():
    """Test EmpathyLLM initialization with Anthropic provider"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider") as mock_anthropic:
        llm = EmpathyLLM(provider="anthropic", target_level=3, api_key="test-key")

        assert llm.target_level == 3
        assert llm.pattern_library == {}
        assert llm.states == {}
        mock_anthropic.assert_called_once()


def test_empathy_llm_initialization_openai():
    """Test EmpathyLLM initialization with OpenAI provider"""
    with patch("empathy_llm_toolkit.core.OpenAIProvider") as mock_openai:
        llm = EmpathyLLM(provider="openai", target_level=4, api_key="test-key")

        assert llm.target_level == 4
        mock_openai.assert_called_once()


def test_empathy_llm_initialization_local():
    """Test EmpathyLLM initialization with local provider"""
    with patch("empathy_llm_toolkit.core.LocalProvider") as mock_local:
        llm = EmpathyLLM(provider="local", target_level=2, model="llama2")

        assert llm.target_level == 2
        mock_local.assert_called_once()


def test_empathy_llm_initialization_invalid_provider():
    """Test initialization with invalid provider raises ValueError"""
    with pytest.raises(ValueError, match="Unknown provider"):
        EmpathyLLM(provider="invalid_provider")


def test_empathy_llm_initialization_with_pattern_library():
    """Test initialization with custom pattern library"""
    pattern_lib = {"pattern1": "data1", "pattern2": "data2"}

    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic", pattern_library=pattern_lib)

        assert llm.pattern_library == pattern_lib


def test_empathy_llm_initialization_custom_model():
    """Test initialization with custom model"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider") as mock_anthropic:
        EmpathyLLM(provider="anthropic", model="custom-model-123")

        # Should pass custom model to provider
        call_kwargs = mock_anthropic.call_args[1]
        assert call_kwargs["model"] == "custom-model-123"


# ============================================================================
# State Management Tests
# ============================================================================


def test_get_or_create_state_new_user():
    """Test creating new state for user"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        state = llm._get_or_create_state("user123")

        assert state is not None
        assert state.user_id == "user123"
        assert "user123" in llm.states


def test_get_or_create_state_existing_user():
    """Test retrieving existing state for user"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Create initial state
        state1 = llm._get_or_create_state("user123")

        # Retrieve same state
        state2 = llm._get_or_create_state("user123")

        assert state1 is state2


# ============================================================================
# Level Determination Tests
# ============================================================================


def test_determine_level_starts_at_level_2():
    """Test level determination starts at level 2 (guided)"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic", target_level=5)
        state = CollaborationState(user_id="test")

        level = llm._determine_level(state)

        # Should start at level 2 for new state (Level 2 always appropriate)
        assert level == 2


def test_determine_level_respects_target():
    """Test level determination respects target_level"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic", target_level=2)
        state = CollaborationState(user_id="test")

        # Even if state would allow progression, should cap at target
        level = llm._determine_level(state)

        assert level <= 2


# ============================================================================
# Interaction Tests (Async)
# ============================================================================


@pytest.mark.asyncio
async def test_interact_level_1_reactive(mock_provider):
    """Test Level 1 reactive interaction"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=1)

        result = await llm.interact(user_id="test_user", user_input="Hello", force_level=1)

        assert result["content"] == "Mock LLM response"
        assert result["level_used"] == 1
        assert result["proactive"] is False
        assert "tokens_used" in result["metadata"]
        mock_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_interact_level_2_guided(mock_provider):
    """Test Level 2 guided interaction"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=2)

        # First interaction to build history
        await llm.interact(user_id="test_user", user_input="First message", force_level=2)

        # Second interaction should have history
        result = await llm.interact(user_id="test_user", user_input="Second message", force_level=2)

        assert result["level_used"] == 2
        assert "history_turns" in result["metadata"]


@pytest.mark.asyncio
async def test_interact_level_3_proactive_no_pattern(mock_provider):
    """Test Level 3 proactive without matching pattern"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=3)

        result = await llm.interact(user_id="test_user", user_input="Test input", force_level=3)

        assert result["level_used"] == 3
        assert result["proactive"] is False  # No pattern matched
        assert result["metadata"]["pattern"] is None


@pytest.mark.asyncio
async def test_interact_level_3_proactive_with_pattern(mock_provider):
    """Test Level 3 proactive with matching pattern"""
    from datetime import datetime

    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=3)

        # Add a pattern
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="optimize code",
            action="run performance analysis",
            confidence=0.9,
            occurrences=5,
            last_seen=datetime.now(),
        )
        llm.add_pattern("test_user", pattern)

        result = await llm.interact(user_id="test_user", user_input="optimize code", force_level=3)

        assert result["level_used"] == 3
        # Should be proactive if pattern matched
        assert "pattern" in result["metadata"]


@pytest.mark.asyncio
async def test_interact_level_4_anticipatory(mock_provider):
    """Test Level 4 anticipatory interaction"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=4)

        result = await llm.interact(user_id="test_user", user_input="Test request", force_level=4)

        assert result["level_used"] == 4
        assert result["proactive"] is True  # Level 4 is inherently proactive
        assert "trajectory_analyzed" in result["metadata"]
        assert "trust_level" in result["metadata"]


@pytest.mark.asyncio
async def test_interact_level_5_systems(mock_provider):
    """Test Level 5 systems interaction"""
    pattern_lib = {"cross_domain_pattern": "test_data"}

    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=5, pattern_library=pattern_lib)

        result = await llm.interact(user_id="test_user", user_input="Test request", force_level=5)

        assert result["level_used"] == 5
        assert result["proactive"] is True
        assert "pattern_library_size" in result["metadata"]
        assert result["metadata"]["pattern_library_size"] == 1
        assert "systems_level" in result["metadata"]


@pytest.mark.asyncio
async def test_interact_invalid_level(mock_provider):
    """Test interaction with invalid level raises ValueError"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic")

        with pytest.raises(ValueError, match="Invalid level"):
            await llm.interact(user_id="test_user", user_input="Test", force_level=99)


@pytest.mark.asyncio
async def test_interact_with_context(mock_provider):
    """Test interaction with additional context"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=1)

        context = {"project_name": "test_project", "file_count": 42}

        result = await llm.interact(
            user_id="test_user",
            user_input="Help me",
            context=context,
            force_level=1,
        )

        assert result["content"] is not None


@pytest.mark.asyncio
async def test_interact_updates_state(mock_provider):
    """Test that interact updates collaboration state"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=1)

        # Perform interaction
        await llm.interact(user_id="test_user", user_input="Test input", force_level=1)

        # Check state was updated
        state = llm.states["test_user"]
        assert len(state.interactions) == 2  # User input + assistant response


# ============================================================================
# Trust Management Tests
# ============================================================================


def test_update_trust_success():
    """Test updating trust on successful interaction"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Create initial state
        llm._get_or_create_state("test_user")
        initial_trust = llm.states["test_user"].trust_level

        # Update trust
        llm.update_trust("test_user", "success", magnitude=1.0)

        # Trust should increase
        assert llm.states["test_user"].trust_level >= initial_trust


def test_update_trust_failure():
    """Test updating trust on failed interaction"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Create state with some trust
        llm._get_or_create_state("test_user")
        llm.update_trust("test_user", "success")  # Build trust first
        trust_after_success = llm.states["test_user"].trust_level

        # Now fail
        llm.update_trust("test_user", "failure", magnitude=1.0)

        # Trust should decrease
        assert llm.states["test_user"].trust_level < trust_after_success


def test_update_trust_creates_state_if_needed():
    """Test that update_trust creates state if it doesn't exist"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Update trust for non-existent user
        llm.update_trust("new_user", "success")

        # State should be created
        assert "new_user" in llm.states


# ============================================================================
# Pattern Management Tests
# ============================================================================


def test_add_pattern():
    """Test adding a pattern for user"""
    from datetime import datetime

    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="run tests",
            action="check coverage",
            confidence=0.85,
            occurrences=3,
            last_seen=datetime.now(),
        )

        llm.add_pattern("test_user", pattern)

        # Check pattern was added
        state = llm.states["test_user"]
        assert len(state.detected_patterns) == 1
        assert state.detected_patterns[0].trigger == "run tests"


def test_add_pattern_creates_state_if_needed():
    """Test that add_pattern creates state if it doesn't exist"""
    from datetime import datetime

    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        pattern = UserPattern(
            pattern_type=PatternType.CONDITIONAL,
            trigger="error occurs",
            action="check logs",
            confidence=0.75,
            occurrences=2,
            last_seen=datetime.now(),
        )

        llm.add_pattern("new_user", pattern)

        # State should be created
        assert "new_user" in llm.states
        assert len(llm.states["new_user"].detected_patterns) == 1


# ============================================================================
# Statistics Tests
# ============================================================================


def test_get_statistics():
    """Test getting collaboration statistics"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Create state and add some data
        llm._get_or_create_state("test_user")
        llm.update_trust("test_user", "success")

        stats = llm.get_statistics("test_user")

        assert stats is not None
        assert isinstance(stats, dict)
        assert "total_interactions" in stats
        assert "trust_level" in stats


def test_get_statistics_creates_state_if_needed():
    """Test that get_statistics creates state if needed"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        stats = llm.get_statistics("new_user")

        assert "new_user" in llm.states
        assert stats is not None


# ============================================================================
# Reset State Tests
# ============================================================================


def test_reset_state():
    """Test resetting user state"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Create state
        llm._get_or_create_state("test_user")
        assert "test_user" in llm.states

        # Reset state
        llm.reset_state("test_user")

        # State should be removed
        assert "test_user" not in llm.states


def test_reset_state_nonexistent_user():
    """Test resetting state for user that doesn't exist"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic")

        # Should not raise error
        llm.reset_state("nonexistent_user")

        # Should still not exist
        assert "nonexistent_user" not in llm.states


# ============================================================================
# Multiple Users Tests
# ============================================================================


@pytest.mark.asyncio
async def test_multiple_users_independent_states(mock_provider):
    """Test that multiple users have independent states"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=2)

        # Interact with user 1
        await llm.interact(user_id="user1", user_input="User 1 message", force_level=1)

        # Interact with user 2
        await llm.interact(user_id="user2", user_input="User 2 message", force_level=1)

        # Each should have their own state
        assert "user1" in llm.states
        assert "user2" in llm.states
        assert llm.states["user1"] is not llm.states["user2"]


# ============================================================================
# Level Description Tests
# ============================================================================


@pytest.mark.asyncio
async def test_interact_includes_level_description(mock_provider):
    """Test that interact result includes level description"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=3)

        result = await llm.interact(user_id="test_user", user_input="Test", force_level=2)

        assert "level_description" in result
        assert result["level_description"] is not None


# ============================================================================
# Level 3 Proactive Pattern Matching Tests - TARGETS MISSING LINES 234-248
# ============================================================================


@pytest.mark.asyncio
async def test_level_3_proactive_with_matching_pattern_builds_prompt(mock_provider):
    """Test Level 3 builds proactive prompt when pattern matches - COVERS 234-248"""
    from datetime import datetime

    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=3)

        # Increase trust level so pattern will trigger (needs > 0.6)
        llm.update_trust("test_user", "success", magnitude=1.0)
        llm.update_trust("test_user", "success", magnitude=1.0)

        # Add a high-confidence pattern that will match
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="run tests",
            action="check coverage report",
            confidence=0.92,
            occurrences=8,
            last_seen=datetime.now(),
        )
        llm.add_pattern("test_user", pattern)

        # Trigger the pattern with matching input
        result = await llm.interact(
            user_id="test_user",
            user_input="run tests",  # Matches the trigger
            force_level=3,
        )

        # Verify proactive behavior
        assert result["level_used"] == 3
        assert result["proactive"] is True
        assert result["metadata"]["pattern"] is not None
        assert result["metadata"]["pattern"]["trigger"] == "run tests"
        assert result["metadata"]["pattern"]["confidence"] == 0.92
        assert result["metadata"]["pattern"]["pattern_type"] == PatternType.SEQUENTIAL.value

        # Verify the provider was called (prompt was built and used)
        mock_provider.generate.assert_called()
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]

        # Should have the proactive prompt
        assert len(messages) == 1
        assert "pattern" in messages[0]["content"].lower()
        assert "run tests" in messages[0]["content"]
        assert "check coverage report" in messages[0]["content"]


@pytest.mark.asyncio
async def test_level_3_proactive_pattern_includes_confidence_in_prompt(mock_provider):
    """Test Level 3 includes confidence in proactive prompt"""
    from datetime import datetime

    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=3)

        # Increase trust level so pattern will trigger (needs > 0.6)
        llm.update_trust("test_user", "success", magnitude=1.0)
        llm.update_trust("test_user", "success", magnitude=1.0)

        pattern = UserPattern(
            pattern_type=PatternType.CONDITIONAL,
            trigger="error occurs",
            action="check logs",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
        )
        llm.add_pattern("test_user", pattern)

        result = await llm.interact(
            user_id="test_user",
            user_input="error occurs",
            force_level=3,
        )

        assert result["proactive"] is True
        assert result["metadata"]["pattern"]["confidence"] == 0.85

        # Check that confidence is in the prompt
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]
        prompt_content = messages[0]["content"]
        assert "85%" in prompt_content or "0.85" in prompt_content


# ============================================================================
# Level 5 Systems Empty Pattern Library Tests - TARGETS MISSING LINE 344->347
# ============================================================================


@pytest.mark.asyncio
async def test_level_5_systems_with_empty_pattern_library(mock_provider):
    """Test Level 5 with empty pattern library - COVERS 344->347"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        # Initialize with empty pattern library (default)
        llm = EmpathyLLM(provider="anthropic", target_level=5)

        result = await llm.interact(
            user_id="test_user",
            user_input="Analyze this system",
            force_level=5,
        )

        assert result["level_used"] == 5
        assert result["metadata"]["pattern_library_size"] == 0

        # Verify the prompt was built correctly
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]
        # The pattern context would be in the last message (the prompt we built)
        last_message = messages[-1]["content"]

        # Should NOT include pattern library section when empty
        assert "SHARED PATTERN LIBRARY:" not in last_message


@pytest.mark.asyncio
async def test_level_5_systems_with_populated_pattern_library(mock_provider):
    """Test Level 5 with populated pattern library"""
    pattern_lib = {
        "error_handling": {"pattern": "try-catch", "domains": ["backend", "frontend"]},
        "validation": {"pattern": "schema-based", "domains": ["api", "database"]},
    }

    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=5, pattern_library=pattern_lib)

        result = await llm.interact(
            user_id="test_user",
            user_input="Implement error handling",
            force_level=5,
        )

        assert result["level_used"] == 5
        assert result["metadata"]["pattern_library_size"] == 2

        # Verify the prompt includes pattern library
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]
        last_message = messages[-1]["content"]

        # Should include pattern library section
        assert "SHARED PATTERN LIBRARY:" in last_message
        assert "error_handling" in str(pattern_lib)


@pytest.mark.asyncio
async def test_level_5_systems_pattern_library_in_prompt(mock_provider):
    """Test Level 5 includes pattern library in prompt when available"""
    pattern_lib = {"test_pattern": "test_value"}

    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(provider="anthropic", target_level=5, pattern_library=pattern_lib)

        await llm.interact(
            user_id="test_user",
            user_input="Test request",
            force_level=5,
        )

        # Verify pattern library context was included
        call_args = mock_provider.generate.call_args
        messages = call_args[1]["messages"]
        last_message = messages[-1]["content"]

        # Pattern library should be in the prompt
        assert "test_pattern" in last_message or str(pattern_lib) in last_message


# ============================================================================
# Model Routing Integration Tests
# ============================================================================


def test_empathy_llm_initialization_with_model_routing():
    """Test EmpathyLLM initialization with model routing enabled"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            api_key="test-key",
            enable_model_routing=True,
        )

        assert llm.enable_model_routing is True
        assert llm.model_router is not None


def test_empathy_llm_initialization_without_model_routing():
    """Test EmpathyLLM initialization with model routing disabled (default)"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(provider="anthropic", target_level=3, api_key="test-key")

        assert llm.enable_model_routing is False
        assert llm.model_router is None


def test_empathy_llm_explicit_model_overrides_routing():
    """Test that explicit model parameter disables routing"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider"):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            api_key="test-key",
            model="claude-3-opus-20240229",  # Explicit model
            enable_model_routing=True,
        )

        # Routing is enabled but explicit model should override
        assert llm.enable_model_routing is True
        assert llm._explicit_model == "claude-3-opus-20240229"


@pytest.mark.asyncio
async def test_interact_with_task_type_routes_model(mock_provider):
    """Test that task_type parameter routes to appropriate model"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            enable_model_routing=True,
        )

        # Summarize task should route to cheap model (Haiku)
        result = await llm.interact(
            user_id="test_user",
            user_input="Summarize this code",
            task_type="summarize",
            force_level=1,
        )

        # Check routing metadata
        assert "model_routing_enabled" in result["metadata"]
        assert result["metadata"]["model_routing_enabled"] is True
        assert result["metadata"]["task_type"] == "summarize"
        assert result["metadata"]["routed_tier"] == "cheap"
        assert "haiku" in result["metadata"]["routed_model"].lower()


@pytest.mark.asyncio
async def test_interact_with_fix_bug_routes_to_capable(mock_provider):
    """Test that fix_bug task routes to capable tier (Sonnet)"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            enable_model_routing=True,
        )

        result = await llm.interact(
            user_id="test_user",
            user_input="Fix this bug",
            task_type="fix_bug",
            force_level=1,
        )

        assert result["metadata"]["routed_tier"] == "capable"
        assert "sonnet" in result["metadata"]["routed_model"].lower()


@pytest.mark.asyncio
async def test_interact_with_coordinate_routes_to_premium(mock_provider):
    """Test that coordinate task routes to premium tier (Opus)"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            enable_model_routing=True,
        )

        result = await llm.interact(
            user_id="test_user",
            user_input="Coordinate this complex task",
            task_type="coordinate",
            force_level=1,
        )

        assert result["metadata"]["routed_tier"] == "premium"
        assert "opus" in result["metadata"]["routed_model"].lower()


@pytest.mark.asyncio
async def test_interact_passes_routed_model_to_provider(mock_provider):
    """Test that routed model is passed to provider.generate()"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            enable_model_routing=True,
        )

        await llm.interact(
            user_id="test_user",
            user_input="Summarize this",
            task_type="summarize",
            force_level=1,
        )

        # Verify model was passed to generate()
        call_kwargs = mock_provider.generate.call_args[1]
        assert "model" in call_kwargs
        assert "haiku" in call_kwargs["model"].lower()


@pytest.mark.asyncio
async def test_interact_without_routing_no_metadata(mock_provider):
    """Test that without routing enabled, no routing metadata is added"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            enable_model_routing=False,  # Disabled
        )

        result = await llm.interact(
            user_id="test_user",
            user_input="Test",
            task_type="summarize",  # task_type is ignored when routing disabled
            force_level=1,
        )

        # No routing metadata should be present
        assert "model_routing_enabled" not in result["metadata"]
        assert "routed_tier" not in result["metadata"]


@pytest.mark.asyncio
async def test_interact_default_task_type(mock_provider):
    """Test that default task_type is used when not specified"""
    with patch("empathy_llm_toolkit.core.AnthropicProvider", return_value=mock_provider):
        llm = EmpathyLLM(
            provider="anthropic",
            target_level=3,
            enable_model_routing=True,
        )

        # No task_type specified - should default to "generate_code" (capable)
        result = await llm.interact(
            user_id="test_user",
            user_input="Help me with code",
            force_level=1,
        )

        assert result["metadata"]["task_type"] == "generate_code"
        assert result["metadata"]["routed_tier"] == "capable"
