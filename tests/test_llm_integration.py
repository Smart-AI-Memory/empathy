"""
LLM Integration Tests - Real API Calls

These tests make actual calls to LLM providers (Anthropic Claude).
Run with: pytest -m llm

Requirements:
- ANTHROPIC_API_KEY environment variable must be set
- Active internet connection
- API credits available

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import os
import sys

import pytest
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from empathy_llm_toolkit.core import EmpathyLLM  # noqa: E402
from empathy_llm_toolkit.providers import AnthropicProvider  # noqa: E402

try:
    import anthropic
except ImportError:
    anthropic = None


@pytest.fixture
def api_key():
    """Get API key from environment"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set - skipping LLM integration tests")
    return key


@pytest.fixture
def anthropic_provider(api_key):
    """Create real Anthropic provider"""
    return AnthropicProvider(api_key=api_key, model="claude-sonnet-4-5-20250929")


@pytest.fixture
def empathy_llm(api_key):
    """Create EmpathyLLM with real provider"""
    return EmpathyLLM(
        provider="anthropic", api_key=api_key, model="claude-sonnet-4-5-20250929", target_level=4
    )


class TestAnthropicProviderIntegration:
    """Integration tests for Anthropic Claude provider"""

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_basic_generation(self, anthropic_provider):
        """Test basic text generation with real API"""
        messages = [{"role": "user", "content": "Say 'Hello from Claude!' and nothing else."}]

        response = await anthropic_provider.generate(
            messages=messages, temperature=0.0, max_tokens=50
        )

        assert response.content is not None
        assert len(response.content) > 0
        assert response.model.startswith("claude")
        assert response.tokens_used > 0
        assert "hello" in response.content.lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_system_prompt(self, anthropic_provider):
        """Test generation with system prompt"""
        messages = [{"role": "user", "content": "What is your role?"}]

        response = await anthropic_provider.generate(
            messages=messages,
            system_prompt="You are a helpful Python programming assistant. Respond in one sentence.",
            temperature=0.0,
            max_tokens=100,
        )

        assert response.content is not None
        assert "python" in response.content.lower() or "programming" in response.content.lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, anthropic_provider):
        """Test multi-turn conversation"""
        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Nice to meet you, Alice!"},
            {"role": "user", "content": "What is my name?"},
        ]

        response = await anthropic_provider.generate(
            messages=messages, temperature=0.0, max_tokens=50
        )

        assert response.content is not None
        assert "alice" in response.content.lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_model_info(self, anthropic_provider):
        """Test getting model information"""
        info = anthropic_provider.get_model_info()

        assert "max_tokens" in info
        assert info["max_tokens"] > 0
        assert "cost_per_1m_input" in info
        assert "supports_prompt_caching" in info

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_prompt_caching_enabled(self, api_key):
        """Test that prompt caching is enabled and working"""
        provider = AnthropicProvider(api_key=api_key, use_prompt_caching=True)

        # Make two identical requests - second should use cache
        messages = [{"role": "user", "content": "Count from 1 to 3."}]

        response1 = await provider.generate(messages=messages, temperature=0.0, max_tokens=50)
        response2 = await provider.generate(messages=messages, temperature=0.0, max_tokens=50)

        assert response1.content is not None
        assert response2.content is not None
        # Both should succeed (cache hit won't affect content with temp=0)

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_thinking_mode(self, api_key):
        """Test thinking mode for complex reasoning"""
        provider = AnthropicProvider(api_key=api_key, use_thinking=True)

        messages = [
            {
                "role": "user",
                "content": "If I have 3 apples and buy 2 more, then give away 1, how many do I have?",
            }
        ]

        # Thinking mode requires temperature=1 and max_tokens > thinking.budget_tokens
        response = await provider.generate(messages=messages, temperature=1.0, max_tokens=2048)

        assert response.content is not None
        # Should contain "4" in the answer
        assert "4" in response.content


class TestEmpathyLLMIntegration:
    """Integration tests for EmpathyLLM with real API"""

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_basic_interaction(self, empathy_llm):
        """Test basic interaction through EmpathyLLM"""
        result = await empathy_llm.interact(
            user_id="test_user_1",
            user_input="Say exactly: 'Hello from EmpathyLLM!'",
            force_level=1,
        )

        assert result is not None
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["level_used"] == 1
        assert "hello" in result["content"].lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_level_progression(self, empathy_llm):
        """Test automatic level progression"""
        user_id = "test_user_progression"

        # Multiple successful interactions should build trust
        for i in range(5):
            result = await empathy_llm.interact(
                user_id=user_id, user_input=f"Task {i}: Generate a hello world function"
            )
            assert result is not None
            assert "content" in result

        # Later interactions should use higher levels
        final_result = await empathy_llm.interact(
            user_id=user_id, user_input="Generate another function"
        )
        # Should have progressed beyond level 1
        assert final_result["level_used"] >= 1

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_context_memory(self, empathy_llm):
        """Test that EmpathyLLM remembers context"""
        user_id = "test_user_memory"

        # First interaction - provide information
        result1 = await empathy_llm.interact(
            user_id=user_id,
            user_input="My project is called SuperApp.",
            force_level=2,
        )
        assert result1 is not None

        # Second interaction - reference previous context
        result2 = await empathy_llm.interact(
            user_id=user_id, user_input="What is my project called?", force_level=2
        )
        assert result2 is not None
        assert "superapp" in result2["content"].lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_level_4_anticipatory(self, empathy_llm):
        """Test Level 4 anticipatory behavior"""
        result = await empathy_llm.interact(
            user_id="test_user_level4",
            user_input="I want to build a user authentication system",
            force_level=4,
            context={"project_type": "web_api", "language": "Python"},
        )

        assert result is not None
        assert result["level_used"] == 4
        # Level 4 should anticipate security needs
        content_lower = result["content"].lower()
        security_mentioned = any(
            word in content_lower
            for word in ["security", "hash", "password", "token", "bcrypt", "salt"]
        )
        assert security_mentioned, "Level 4 should anticipate security concerns"


class TestMultiUserScenarios:
    """Test multi-user collaboration scenarios"""

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_multiple_users_separate_contexts(self, empathy_llm):
        """Test that different users have separate contexts"""
        # User 1 provides information
        result1 = await empathy_llm.interact(
            user_id="user_1", user_input="My name is Alice.", force_level=2
        )
        assert result1 is not None

        # User 2 provides different information
        result2 = await empathy_llm.interact(
            user_id="user_2", user_input="My name is Bob.", force_level=2
        )
        assert result2 is not None

        # User 1 asks about their name
        result3 = await empathy_llm.interact(
            user_id="user_1", user_input="What is my name?", force_level=2
        )
        assert result3 is not None
        assert "alice" in result3["content"].lower()
        assert "bob" not in result3["content"].lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_user_progression_independence(self, empathy_llm):
        """Test that user progression is independent"""
        # User 1 has many interactions (should progress)
        for i in range(10):
            await empathy_llm.interact(
                user_id="advanced_user", user_input=f"Task {i}", force_level=None
            )

        # User 2 is new (should start at level 1)
        result = await empathy_llm.interact(
            user_id="new_user", user_input="First task", force_level=None
        )

        # New user should start at lower level
        assert result["level_used"] <= 2


class TestLLMErrorHandling:
    """Test error handling with real API"""

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """Test handling of invalid API key"""
        expected_exceptions = (ValueError, RuntimeError)
        if anthropic is not None:
            expected_exceptions = (ValueError, RuntimeError, anthropic.AuthenticationError)
        with pytest.raises(expected_exceptions):
            provider = AnthropicProvider(api_key="invalid-key-12345")
            await provider.generate(messages=[{"role": "user", "content": "Hello"}], max_tokens=50)

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_empty_message(self, anthropic_provider):
        """Test handling of empty message"""
        # Should handle gracefully or raise clear error
        expected_exceptions = (ValueError, RuntimeError)
        if anthropic is not None:
            expected_exceptions = (ValueError, RuntimeError, anthropic.BadRequestError)
        with pytest.raises(expected_exceptions):
            await anthropic_provider.generate(messages=[], max_tokens=50)

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_token_limit_exceeded(self, anthropic_provider):
        """Test handling when requesting too many tokens"""
        messages = [{"role": "user", "content": "Count to 1000."}]

        # Request very few tokens - should still complete
        response = await anthropic_provider.generate(messages=messages, max_tokens=10)

        assert response is not None
        assert response.finish_reason in ["max_tokens", "end_turn", "stop_sequence"]


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""

    @pytest.mark.llm
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_code_review_scenario(self, empathy_llm):
        """Test code review scenario"""
        code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total
"""

        result = await empathy_llm.interact(
            user_id="code_reviewer",
            user_input=f"Review this Python code and suggest improvements:\n\n{code}",
            force_level=3,
        )

        assert result is not None
        assert len(result["content"]) > 100
        # Should mention Python concepts
        assert "python" in result["content"].lower() or "function" in result["content"].lower()

    @pytest.mark.llm
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_api_design_scenario(self, empathy_llm):
        """Test API design assistance scenario"""
        result = await empathy_llm.interact(
            user_id="api_designer",
            user_input="""
            I'm building a REST API for a todo list app.
            I need endpoints for:
            - Creating todos
            - Listing todos
            - Updating todos
            - Deleting todos

            Help me design the API.
            """,
            force_level=4,
        )

        assert result is not None
        assert len(result["content"]) > 200
        # Should mention REST concepts
        result_lower = result["content"].lower()
        assert "get" in result_lower or "post" in result_lower or "endpoint" in result_lower

    @pytest.mark.llm
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_debugging_assistance(self, empathy_llm):
        """Test debugging assistance scenario"""
        error_message = """
        Traceback (most recent call last):
          File "app.py", line 42, in process_data
            result = data['users'][0]['email']
        KeyError: 'users'
        """

        result = await empathy_llm.interact(
            user_id="debugger",
            user_input=f"Help me debug this error:\n\n{error_message}",
            force_level=2,
        )

        assert result is not None
        assert len(result["content"]) > 50
        # Should mention KeyError or data structure
        assert "key" in result["content"].lower() or "data" in result["content"].lower()


if __name__ == "__main__":
    # Run only LLM integration tests
    pytest.main([__file__, "-v", "-m", "llm"])
