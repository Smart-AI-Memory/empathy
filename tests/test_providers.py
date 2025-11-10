"""
Comprehensive tests for LLM Provider Adapters

Tests cover:
- LLMResponse dataclass
- BaseLLMProvider abstract class and methods
- AnthropicProvider initialization and validation
- OpenAIProvider initialization and validation
- LocalProvider initialization and validation
- Provider factory patterns
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from empathy_llm_toolkit.providers import (
    LLMResponse,
    BaseLLMProvider,
    AnthropicProvider,
    OpenAIProvider,
    LocalProvider,
)


class TestLLMResponse:
    """Test LLMResponse dataclass"""

    def test_llm_response_creation(self):
        """Test LLMResponse dataclass creation"""
        response = LLMResponse(
            content="Test response",
            model="claude-3-sonnet",
            tokens_used=150,
            finish_reason="stop",
            metadata={"input_tokens": 100, "output_tokens": 50},
        )

        assert response.content == "Test response"
        assert response.model == "claude-3-sonnet"
        assert response.tokens_used == 150
        assert response.finish_reason == "stop"
        assert response.metadata["input_tokens"] == 100
        assert response.metadata["output_tokens"] == 50

    def test_llm_response_with_empty_metadata(self):
        """Test LLMResponse with empty metadata"""
        response = LLMResponse(
            content="Hello", model="gpt-4", tokens_used=10, finish_reason="stop", metadata={}
        )

        assert response.content == "Hello"
        assert response.metadata == {}


class TestBaseLLMProvider:
    """Test BaseLLMProvider abstract base class"""

    def test_base_provider_initialization(self):
        """Test BaseLLMProvider can be initialized with api_key and kwargs"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider(api_key="test-key", custom_param="value")

        assert provider.api_key == "test-key"
        assert provider.config["custom_param"] == "value"

    def test_base_provider_no_api_key(self):
        """Test BaseLLMProvider can be initialized without api_key"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider()
        assert provider.api_key is None

    def test_estimate_tokens_short_text(self):
        """Test token estimation for short text"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider()
        text = "Hello world"  # 11 characters
        tokens = provider.estimate_tokens(text)

        assert tokens == 2  # 11 // 4 = 2

    def test_estimate_tokens_long_text(self):
        """Test token estimation for longer text"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider()
        text = "a" * 400  # 400 characters
        tokens = provider.estimate_tokens(text)

        assert tokens == 100  # 400 // 4 = 100

    def test_estimate_tokens_empty_text(self):
        """Test token estimation for empty text"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider()
        tokens = provider.estimate_tokens("")

        assert tokens == 0


class TestAnthropicProvider:
    """Test Anthropic provider initialization and validation"""

    def test_anthropic_provider_requires_api_key(self):
        """Test that AnthropicProvider requires API key"""
        with pytest.raises(ValueError, match="API key is required"):
            AnthropicProvider(api_key=None)

    def test_anthropic_provider_requires_non_empty_api_key(self):
        """Test that AnthropicProvider requires non-empty API key"""
        with pytest.raises(ValueError, match="API key is required"):
            AnthropicProvider(api_key="   ")

    def test_anthropic_provider_missing_package(self):
        """Test error when anthropic package not installed"""
        with patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(ImportError, match="anthropic package required"):
                AnthropicProvider(api_key="test-key")

    def test_anthropic_provider_initialization_success(self):
        """Test successful AnthropicProvider initialization"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(
                api_key="test-key",
                model="claude-3-opus",
                use_prompt_caching=True,
                use_thinking=True,
            )

            assert provider.api_key == "test-key"
            assert provider.model == "claude-3-opus"
            assert provider.use_prompt_caching is True
            assert provider.use_thinking is True

    def test_anthropic_provider_default_model(self):
        """Test AnthropicProvider default model"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key")

            assert provider.model == "claude-sonnet-4-5-20250929"

    def test_anthropic_get_model_info_opus(self):
        """Test get_model_info for Claude Opus"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", model="claude-3-opus-20240229")

            info = provider.get_model_info()

            assert info["max_tokens"] == 200000
            assert info["supports_prompt_caching"] is True
            assert info["supports_thinking"] is True
            assert "ideal_for" in info

    def test_anthropic_get_model_info_unknown_model(self):
        """Test get_model_info for unknown model returns defaults"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", model="unknown-model")

            info = provider.get_model_info()

            assert info["max_tokens"] == 200000
            assert info["supports_prompt_caching"] is True


class TestOpenAIProvider:
    """Test OpenAI provider initialization and validation"""

    def test_openai_provider_requires_api_key(self):
        """Test that OpenAIProvider requires API key"""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIProvider(api_key=None)

    def test_openai_provider_requires_non_empty_api_key(self):
        """Test that OpenAIProvider requires non-empty API key"""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIProvider(api_key="   ")

    def test_openai_provider_missing_package(self):
        """Test error when openai package not installed"""
        with patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(ImportError, match="openai package required"):
                OpenAIProvider(api_key="test-key")

    def test_openai_provider_initialization_success(self):
        """Test successful OpenAIProvider initialization"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key", model="gpt-4")

            assert provider.api_key == "test-key"
            assert provider.model == "gpt-4"

    def test_openai_provider_default_model(self):
        """Test OpenAIProvider default model"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key")

            assert provider.model == "gpt-4-turbo-preview"

    def test_openai_get_model_info_gpt4(self):
        """Test get_model_info for GPT-4"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key", model="gpt-4")

            info = provider.get_model_info()

            assert info["max_tokens"] == 8192
            assert info["cost_per_1m_input"] == 30.00
            assert info["cost_per_1m_output"] == 60.00

    def test_openai_get_model_info_gpt35_turbo(self):
        """Test get_model_info for GPT-3.5 Turbo"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")

            info = provider.get_model_info()

            assert info["max_tokens"] == 16385
            assert info["cost_per_1m_input"] == 0.50

    def test_openai_get_model_info_unknown_model(self):
        """Test get_model_info for unknown model returns defaults"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key", model="unknown-model")

            info = provider.get_model_info()

            assert info["max_tokens"] == 128000


class TestLocalProvider:
    """Test Local provider initialization"""

    def test_local_provider_default_initialization(self):
        """Test LocalProvider with default values"""
        provider = LocalProvider()

        assert provider.endpoint == "http://localhost:11434"
        assert provider.model == "llama2"
        assert provider.api_key is None

    def test_local_provider_custom_endpoint(self):
        """Test LocalProvider with custom endpoint"""
        provider = LocalProvider(endpoint="http://custom:8080", model="mistral")

        assert provider.endpoint == "http://custom:8080"
        assert provider.model == "mistral"

    def test_local_provider_get_model_info(self):
        """Test get_model_info for local provider"""
        provider = LocalProvider(endpoint="http://localhost:11434")

        info = provider.get_model_info()

        assert info["max_tokens"] == 4096
        assert info["cost_per_1m_input"] == 0.0
        assert info["cost_per_1m_output"] == 0.0
        assert info["endpoint"] == "http://localhost:11434"

    def test_local_provider_with_kwargs(self):
        """Test LocalProvider accepts additional kwargs"""
        provider = LocalProvider(custom_param="value", another="param")

        assert provider.config["custom_param"] == "value"
        assert provider.config["another"] == "param"


class TestProviderComparison:
    """Test comparing different providers"""

    def test_all_providers_implement_base_interface(self):
        """Test that all providers implement required abstract methods"""
        # This test verifies the class hierarchy is correct
        assert issubclass(AnthropicProvider, BaseLLMProvider)
        assert issubclass(OpenAIProvider, BaseLLMProvider)
        assert issubclass(LocalProvider, BaseLLMProvider)

    def test_all_providers_have_get_model_info(self):
        """Test all providers implement get_model_info"""
        mock_anthropic = MagicMock()
        mock_openai = MagicMock()
        mock_anthropic.Anthropic.return_value = MagicMock()
        mock_openai.AsyncOpenAI.return_value = MagicMock()

        with patch.dict("sys.modules", {"anthropic": mock_anthropic, "openai": mock_openai}):
            anthropic = AnthropicProvider(api_key="key1")
            openai = OpenAIProvider(api_key="key2")
            local = LocalProvider()

            assert hasattr(anthropic, "get_model_info")
            assert hasattr(openai, "get_model_info")
            assert hasattr(local, "get_model_info")

            # All should return dicts
            assert isinstance(anthropic.get_model_info(), dict)
            assert isinstance(openai.get_model_info(), dict)
            assert isinstance(local.get_model_info(), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
