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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_llm_toolkit.providers import (
    AnthropicProvider,
    BaseLLMProvider,
    LLMResponse,
    LocalProvider,
    OpenAIProvider,
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
            async def generate(
                self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs
            ):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider(api_key="test-key", custom_param="value")

        assert provider.api_key == "test-key"
        assert provider.config["custom_param"] == "value"

    def test_base_provider_no_api_key(self):
        """Test BaseLLMProvider can be initialized without api_key"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(
                self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs
            ):
                return LLMResponse("test", "model", 10, "stop", {})

            def get_model_info(self):
                return {"model": "test"}

        provider = ConcreteProvider()
        assert provider.api_key is None

    def test_estimate_tokens_short_text(self):
        """Test token estimation for short text"""

        class ConcreteProvider(BaseLLMProvider):
            async def generate(
                self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs
            ):
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
            async def generate(
                self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs
            ):
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
            async def generate(
                self, messages, system_prompt=None, temperature=0.7, max_tokens=1024, **kwargs
            ):
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


class TestAnthropicProviderGenerate:
    """Test Anthropic provider generate method and response handling"""

    @pytest.mark.asyncio
    async def test_anthropic_generate_basic(self):
        """Test basic Anthropic generate call"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        # Mock content block (text type)
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Test response"
        mock_response.content = [mock_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key")

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages)

            assert result.content == "Test response"
            assert result.model == "claude-3-sonnet"
            assert result.tokens_used == 150
            assert result.finish_reason == "end_turn"
            assert result.metadata["provider"] == "anthropic"

    @pytest.mark.asyncio
    async def test_anthropic_generate_with_system_prompt_and_caching(self):
        """Test Anthropic generate with system prompt and prompt caching"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        mock_response.usage.cache_creation_input_tokens = 200
        mock_response.usage.cache_read_input_tokens = 150

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Cached response"
        mock_response.content = [mock_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", use_prompt_caching=True)

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages, system_prompt="You are helpful")

            assert result.content == "Cached response"
            assert result.metadata["cache_creation_tokens"] == 200
            assert result.metadata["cache_read_tokens"] == 150

    @pytest.mark.asyncio
    async def test_anthropic_generate_without_caching(self):
        """Test Anthropic generate with system prompt but no caching"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Regular response"
        mock_response.content = [mock_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", use_prompt_caching=False)

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages, system_prompt="You are helpful")

            assert result.content == "Regular response"

    @pytest.mark.asyncio
    async def test_anthropic_generate_with_thinking_mode(self):
        """Test Anthropic generate with thinking mode enabled"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        # Mock thinking block
        mock_thinking_block = MagicMock()
        mock_thinking_block.type = "thinking"
        mock_thinking_block.thinking = "Let me think about this..."

        # Mock text block
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Based on my thinking..."

        mock_response.content = [mock_thinking_block, mock_text_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", use_thinking=True)

            messages = [{"role": "user", "content": "Complex question"}]
            result = await provider.generate(messages)

            assert result.content == "Based on my thinking..."
            assert result.metadata["thinking"] == "Let me think about this..."

    @pytest.mark.asyncio
    async def test_anthropic_generate_with_legacy_content_block(self):
        """Test Anthropic generate with content block without type attribute"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        # Mock content block without type attribute (legacy format)
        mock_block = MagicMock()
        del mock_block.type  # Remove type attribute
        mock_block.text = "Legacy response"
        mock_response.content = [mock_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key")

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages)

            assert result.content == "Legacy response"

    @pytest.mark.asyncio
    async def test_anthropic_generate_with_unknown_block_type(self):
        """Test Anthropic generate with unknown block type (skip it)"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        # Mock block with unknown type
        mock_unknown_block = MagicMock()
        mock_unknown_block.type = "unknown_type"

        # Mock text block
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Text response"

        mock_response.content = [mock_unknown_block, mock_text_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key")

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages)

            # Should get text from the text block, unknown block skipped
            assert result.content == "Text response"

    @pytest.mark.asyncio
    async def test_anthropic_generate_without_cache_metrics(self):
        """Test Anthropic generate without cache metrics in response"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"

        # Create usage object without cache attributes
        mock_usage = type("obj", (object,), {"input_tokens": 100, "output_tokens": 50})()
        mock_response.usage = mock_usage

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Response without cache"
        mock_response.content = [mock_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", use_prompt_caching=True)

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages, system_prompt="You are helpful")

            assert result.content == "Response without cache"
            # Should not have cache metrics
            assert "cache_creation_tokens" not in result.metadata
            assert "cache_read_tokens" not in result.metadata

    @pytest.mark.asyncio
    async def test_anthropic_generate_without_thinking_content(self):
        """Test Anthropic generate without thinking content"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        # Only text block, no thinking
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Simple response"
        mock_response.content = [mock_text_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", use_thinking=True)

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages)

            assert result.content == "Simple response"
            # Should not have thinking metadata
            assert "thinking" not in result.metadata

    @pytest.mark.asyncio
    async def test_anthropic_generate_with_thinking_no_cache(self):
        """Test Anthropic generate with thinking but no cache metrics"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"

        # Create usage object without cache attributes
        mock_usage = type("obj", (object,), {"input_tokens": 100, "output_tokens": 50})()
        mock_response.usage = mock_usage

        # Mock thinking block
        mock_thinking_block = MagicMock()
        mock_thinking_block.type = "thinking"
        mock_thinking_block.thinking = "Reasoning..."

        # Mock text block
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Response with thinking"

        mock_response.content = [mock_thinking_block, mock_text_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key", use_thinking=True)

            messages = [{"role": "user", "content": "Complex task"}]
            result = await provider.generate(messages)

            assert result.content == "Response with thinking"
            assert result.metadata["thinking"] == "Reasoning..."
            # Should not have cache metrics
            assert "cache_creation_tokens" not in result.metadata

    @pytest.mark.asyncio
    async def test_anthropic_analyze_large_codebase(self):
        """Test Anthropic analyze_large_codebase method"""
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "claude-3-sonnet"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Analysis complete"
        mock_response.content = [mock_block]

        mock_client.messages.create.return_value = mock_response

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider(api_key="test-key")

            codebase_files = [
                {"path": "main.py", "content": "print('hello')"},
                {"path": "utils.py", "content": "def helper(): pass"},
            ]
            result = await provider.analyze_large_codebase(codebase_files, "Analyze this code")

            assert result.content == "Analysis complete"
            assert result.tokens_used == 1500


class TestOpenAIProviderGenerate:
    """Test OpenAI provider generate method"""

    @pytest.mark.asyncio
    async def test_openai_generate_basic(self):
        """Test basic OpenAI generate call"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.model = "gpt-4"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        mock_choice = MagicMock()
        mock_choice.message.content = "OpenAI response"
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]

        # Mock async create method
        async def mock_create(*args, **kwargs):
            return mock_response

        mock_client.chat.completions.create = mock_create

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key")

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages)

            assert result.content == "OpenAI response"
            assert result.model == "gpt-4"
            assert result.tokens_used == 150
            assert result.finish_reason == "stop"
            assert result.metadata["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_openai_generate_with_system_prompt(self):
        """Test OpenAI generate with system prompt"""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.AsyncOpenAI.return_value = mock_client

        mock_response = MagicMock()
        mock_response.model = "gpt-4"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 75
        mock_response.usage.total_tokens = 225

        mock_choice = MagicMock()
        mock_choice.message.content = "System-aware response"
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]

        async def mock_create(*args, **kwargs):
            # Verify system prompt was added
            assert kwargs["messages"][0]["role"] == "system"
            assert kwargs["messages"][0]["content"] == "You are helpful"
            return mock_response

        mock_client.chat.completions.create = mock_create

        with patch.dict("sys.modules", {"openai": mock_openai}):
            provider = OpenAIProvider(api_key="test-key")

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.generate(messages, system_prompt="You are helpful")

            assert result.content == "System-aware response"


class AsyncContextManagerMock:
    """Helper class for mocking async context managers"""

    def __init__(self, return_value):
        self._return_value = return_value

    async def __aenter__(self):
        return self._return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class TestLocalProviderGenerate:
    """Test Local provider generate method"""

    @pytest.mark.asyncio
    async def test_local_provider_generate_basic(self):
        """Test basic Local provider generate call"""
        pytest.importorskip("aiohttp")  # Skip if aiohttp not installed

        provider = LocalProvider(endpoint="http://localhost:11434", model="llama2")

        messages = [{"role": "user", "content": "Hello"}]

        # Mock aiohttp response
        mock_response_data = {
            "message": {"content": "Local response"},
            "eval_count": 50,
            "prompt_eval_count": 100,
        }

        mock_resp = MagicMock()
        mock_resp.json = AsyncMock(return_value=mock_response_data)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=AsyncContextManagerMock(mock_resp))

        with patch("aiohttp.ClientSession") as mock_client:
            mock_client.return_value = AsyncContextManagerMock(mock_session)
            result = await provider.generate(messages)

            assert result.content == "Local response"
            assert result.model == "llama2"
            assert result.tokens_used == 150
            assert result.finish_reason == "stop"
            assert result.metadata["provider"] == "local"

    @pytest.mark.asyncio
    async def test_local_provider_generate_with_system_prompt(self):
        """Test Local provider generate with system prompt"""
        pytest.importorskip("aiohttp")  # Skip if aiohttp not installed

        provider = LocalProvider(endpoint="http://localhost:11434", model="llama2")

        messages = [{"role": "user", "content": "Hello"}]

        mock_response_data = {
            "message": {"content": "System-aware local response"},
            "eval_count": 50,
            "prompt_eval_count": 100,
        }

        mock_resp = MagicMock()
        mock_resp.json = AsyncMock(return_value=mock_response_data)

        mock_session = MagicMock()

        def mock_post(*args, **kwargs):
            # Verify system prompt in payload
            assert "system" in kwargs["json"]
            assert kwargs["json"]["system"] == "You are helpful"
            return AsyncContextManagerMock(mock_resp)

        mock_session.post = mock_post

        with patch("aiohttp.ClientSession") as mock_client:
            mock_client.return_value = AsyncContextManagerMock(mock_session)
            result = await provider.generate(messages, system_prompt="You are helpful")

            assert result.content == "System-aware local response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
