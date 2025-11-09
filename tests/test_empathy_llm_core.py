"""
Unit tests for EmpathyLLM core

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
