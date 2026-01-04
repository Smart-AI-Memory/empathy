"""Unit Tests for Coach Language Server

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from ..cache import ResultCache
from ..server import CoachLanguageServer


class TestCoachLanguageServer:
    """Test suite for CoachLanguageServer"""

    @pytest.fixture
    def server(self):
        """Create server instance for testing"""
        return CoachLanguageServer()

    @pytest.fixture
    def mock_coach(self):
        """Mock Coach engine"""
        mock = AsyncMock()
        mock.process.return_value = Mock(
            routing=["PerformanceWizard"],
            primary_output=Mock(
                wizard_name="PerformanceWizard",
                diagnosis="Test diagnosis",
                artifacts=[],
                confidence=0.85,
            ),
            secondary_outputs=[],
            synthesis="",
            overall_confidence=0.85,
        )
        return mock

    def test_server_initialization(self, server):
        """Test server initializes correctly"""
        assert server is not None
        assert server.coach is not None
        assert server.context_collector is not None
        assert server.cache is not None
        assert len(server.coach.wizards) == 16

    def test_server_version(self, server):
        """Test server version is set"""
        assert server.name == "coach-lsp"
        assert server.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_health_check_command(self, server):
        """Test health check custom command"""
        result = await server.command_handlers.get("coach/healthCheck")(server, [])

        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"
        assert result["wizards"] == 16
        assert len(result["wizard_names"]) == 16

    @pytest.mark.asyncio
    async def test_run_wizard_command(self, server, mock_coach):
        """Test run wizard custom command"""
        server.coach = mock_coach

        result = await server.command_handlers["coach/runWizard"](
            server,
            [
                "PerformanceWizard",
                {"role": "developer", "task": "Analyze performance", "context": "Test context"},
            ],
        )

        assert result["routing"] == ["PerformanceWizard"]
        assert result["primary_output"]["wizard_name"] == "PerformanceWizard"
        assert result["overall_confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_predict_command(self, server, mock_coach):
        """Test prediction custom command"""
        server.coach = mock_coach

        result = await server.command_handlers["coach/predict"](
            server,
            ["database_connection_pool", 10],
        )

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_cache_usage(self, server, mock_coach):
        """Test that results are cached"""
        server.coach = mock_coach

        # First call
        result1 = await server.command_handlers["coach/runWizard"](
            server,
            ["PerformanceWizard", {"role": "developer", "task": "Test"}],
        )

        # Second call (should use cache)
        result2 = await server.command_handlers["coach/runWizard"](
            server,
            ["PerformanceWizard", {"role": "developer", "task": "Test"}],
        )

        # Coach should only be called once (second call uses cache)
        assert mock_coach.process.call_count == 1
        assert result1 == result2

    def test_diagnostics_conversion(self, server):
        """Test converting wizard output to LSP diagnostics"""
        mock_output = Mock(
            routing=["SecurityWizard"],
            primary_output=Mock(
                wizard_name="SecurityWizard",
                diagnosis="Found SQL injection vulnerability",
                artifacts=[
                    Mock(
                        name="security_issue",
                        content="SQL injection vulnerability in user input",
                        format="markdown",
                    ),
                ],
                confidence=0.95,
            ),
            secondary_outputs=[],
            synthesis="",
            overall_confidence=0.95,
        )

        diagnostics = server._convert_to_diagnostics(mock_output)

        assert len(diagnostics) > 0
        assert diagnostics[0].source == "coach.security"
        assert "SQL injection" in diagnostics[0].message.lower()


class TestResultCache:
    """Test suite for ResultCache"""

    def test_cache_set_and_get(self):
        """Test basic cache operations"""
        cache = ResultCache(ttl=60)

        cache.set("test_key", {"data": "test"})
        result = cache.get("test_key")

        assert result == {"data": "test"}

    def test_cache_expiration(self):
        """Test cache TTL expiration"""
        import time

        cache = ResultCache(ttl=1)  # 1 second TTL

        cache.set("test_key", {"data": "test"})
        assert cache.get("test_key") is not None

        time.sleep(1.5)  # Wait for expiration
        assert cache.get("test_key") is None

    def test_cache_clear(self):
        """Test clearing cache"""
        cache = ResultCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_clear_file(self):
        """Test clearing cache for specific file"""
        cache = ResultCache()

        cache.set("file:///test.py:wizard1", "value1")
        cache.set("file:///test.py:wizard2", "value2")
        cache.set("file:///other.py:wizard1", "value3")

        cache.clear_file("file:///test.py")

        assert cache.get("file:///test.py:wizard1") is None
        assert cache.get("file:///test.py:wizard2") is None
        assert cache.get("file:///other.py:wizard1") == "value3"


class TestErrorHandling:
    """Test suite for error handling"""

    @pytest.mark.asyncio
    async def test_wizard_not_found_error(self, server):
        """Test handling of wizard not found error"""
        with pytest.raises((KeyError, ValueError)):  # Will be caught and converted to LSP error
            await server.command_handlers["coach/runWizard"](
                server,
                ["NonExistentWizard", {"role": "developer", "task": "Test"}],
            )

    @pytest.mark.asyncio
    async def test_invalid_params_error(self, server):
        """Test handling of invalid parameters"""
        with pytest.raises((IndexError, TypeError, ValueError)):
            await server.command_handlers["coach/runWizard"](
                server,
                ["PerformanceWizard"],  # Missing task dict
            )

    @pytest.mark.asyncio
    async def test_context_collection_error(self, server):
        """Test handling of context collection failures"""
        with patch.object(server.context_collector, "collect", side_effect=Exception("Test error")):
            # Should not crash, should handle gracefully
            await server._analyze_document("file:///test.py")
            # Server should handle error and continue


class TestContextCollector:
    """Test suite for ContextCollector"""

    @pytest.mark.asyncio
    async def test_collect_basic_context(self):
        """Test basic context collection"""
        from ..context_collector import ContextCollector

        collector = ContextCollector()

        # Create a test file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Test file\nprint('hello')")
            temp_path = f.name

        try:
            context = await collector.collect(f"file://{temp_path}")

            assert "Test file" in context
            assert "print('hello')" in context
            assert "Language:" in context
        finally:
            import os

            os.unlink(temp_path)

    def test_detect_language(self):
        """Test language detection from file extension"""
        from pathlib import Path

        from ..context_collector import ContextCollector

        collector = ContextCollector()

        assert collector._detect_language(Path("test.py")) == "Python"
        assert collector._detect_language(Path("test.js")) == "JavaScript"
        assert collector._detect_language(Path("test.ts")) == "TypeScript"
        assert collector._detect_language(Path("test.java")) == "Java"
        assert collector._detect_language(Path("test.go")) == "Go"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
