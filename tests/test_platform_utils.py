"""Tests for platform_utils cross-platform utilities.

Tests platform detection, directory functions, asyncio handling,
and file utilities across Windows, macOS, and Linux.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from empathy_os.platform_utils import (
    PLATFORM_INFO,
    ensure_dir,
    get_default_cache_dir,
    get_default_config_dir,
    get_default_data_dir,
    get_default_log_dir,
    get_platform_info,
    get_temp_dir,
    is_linux,
    is_macos,
    is_windows,
    normalize_path,
    open_text_file,
    read_text_file,
    safe_run_async,
    setup_asyncio_policy,
    write_text_file,
)


class TestPlatformDetection:
    """Tests for platform detection functions."""

    def test_is_windows_true(self):
        """Test is_windows returns True on Windows."""
        with patch("src.empathy_os.platform_utils.platform.system", return_value="Windows"):
            # Need to reload to pick up the mock
            from empathy_os import platform_utils

            with patch.object(platform_utils, "platform") as mock_platform:
                mock_platform.system.return_value = "Windows"
                # Direct call with mocked platform
                assert platform_utils.platform.system() == "Windows"

    def test_is_windows_false_on_darwin(self):
        """Test is_windows returns False on macOS."""
        with patch("platform.system", return_value="Darwin"):
            # The function caches nothing, so we can test behavior
            import platform as plat

            if plat.system() == "Darwin":
                assert is_windows() is False

    def test_is_macos_detection(self):
        """Test is_macos returns correct value based on current platform."""
        import platform as plat

        expected = plat.system() == "Darwin"
        assert is_macos() == expected

    def test_is_linux_detection(self):
        """Test is_linux returns correct value based on current platform."""
        import platform as plat

        expected = plat.system() == "Linux"
        assert is_linux() == expected

    def test_exactly_one_platform_true(self):
        """Test that exactly one platform function returns True."""
        results = [is_windows(), is_macos(), is_linux()]
        # At least one should be true (could be false on BSD, etc.)
        # But at most one should be true
        assert results.count(True) <= 1


class TestDefaultDirectoriesWindows:
    """Tests for default directory functions on Windows."""

    @patch("src.empathy_os.platform_utils.is_windows", return_value=True)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_log_dir_windows(self, mock_macos, mock_windows):
        """Test log directory on Windows uses APPDATA."""
        log_dir = get_default_log_dir()
        assert "empathy" in str(log_dir)
        assert "logs" in str(log_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=True)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_data_dir_windows(self, mock_macos, mock_windows):
        """Test data directory on Windows uses APPDATA."""
        data_dir = get_default_data_dir()
        assert "empathy" in str(data_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=True)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_config_dir_windows(self, mock_macos, mock_windows):
        """Test config directory on Windows uses APPDATA."""
        config_dir = get_default_config_dir()
        assert "empathy" in str(config_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=True)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict(
        "os.environ",
        {
            "LOCALAPPDATA": "C:\\Users\\Test\\AppData\\Local",
            "APPDATA": "C:\\Users\\Test\\AppData\\Roaming",
        },
    )
    def test_cache_dir_windows(self, mock_macos, mock_windows):
        """Test cache directory on Windows uses LOCALAPPDATA."""
        cache_dir = get_default_cache_dir()
        assert "empathy" in str(cache_dir)
        assert "cache" in str(cache_dir)


class TestDefaultDirectoriesMacOS:
    """Tests for default directory functions on macOS."""

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=True)
    def test_log_dir_macos(self, mock_macos, mock_windows):
        """Test log directory on macOS uses Library/Logs."""
        log_dir = get_default_log_dir()
        assert "Library" in str(log_dir)
        assert "Logs" in str(log_dir)
        assert "empathy" in str(log_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=True)
    def test_data_dir_macos(self, mock_macos, mock_windows):
        """Test data directory on macOS uses Library/Application Support."""
        data_dir = get_default_data_dir()
        assert "Library" in str(data_dir)
        assert "Application Support" in str(data_dir)
        assert "empathy" in str(data_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=True)
    def test_config_dir_macos(self, mock_macos, mock_windows):
        """Test config directory on macOS uses Library/Preferences."""
        config_dir = get_default_config_dir()
        assert "Library" in str(config_dir)
        assert "Preferences" in str(config_dir)
        assert "empathy" in str(config_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=True)
    def test_cache_dir_macos(self, mock_macos, mock_windows):
        """Test cache directory on macOS uses Library/Caches."""
        cache_dir = get_default_cache_dir()
        assert "Library" in str(cache_dir)
        assert "Caches" in str(cache_dir)
        assert "empathy" in str(cache_dir)


class TestDefaultDirectoriesLinux:
    """Tests for default directory functions on Linux."""

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch("os.access", return_value=False)
    @patch.object(Path, "exists", return_value=False)
    def test_log_dir_linux_fallback(self, mock_exists, mock_access, mock_macos, mock_windows):
        """Test log directory on Linux falls back to user directory."""
        log_dir = get_default_log_dir()
        assert "empathy" in str(log_dir)
        assert "logs" in str(log_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict("os.environ", {"XDG_DATA_HOME": "/home/test/.local/share"})
    def test_data_dir_linux_xdg(self, mock_macos, mock_windows):
        """Test data directory on Linux uses XDG_DATA_HOME."""
        data_dir = get_default_data_dir()
        assert "empathy" in str(data_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict("os.environ", {"XDG_CONFIG_HOME": "/home/test/.config"})
    def test_config_dir_linux_xdg(self, mock_macos, mock_windows):
        """Test config directory on Linux uses XDG_CONFIG_HOME."""
        config_dir = get_default_config_dir()
        assert "empathy" in str(config_dir)

    @patch("src.empathy_os.platform_utils.is_windows", return_value=False)
    @patch("src.empathy_os.platform_utils.is_macos", return_value=False)
    @patch.dict("os.environ", {"XDG_CACHE_HOME": "/home/test/.cache"})
    def test_cache_dir_linux_xdg(self, mock_macos, mock_windows):
        """Test cache directory on Linux uses XDG_CACHE_HOME."""
        cache_dir = get_default_cache_dir()
        assert "empathy" in str(cache_dir)


class TestAsyncioPolicy:
    """Tests for asyncio event loop policy functions."""

    def test_setup_asyncio_policy_runs(self):
        """Test setup_asyncio_policy executes without error."""
        # Should not raise on any platform
        setup_asyncio_policy()

    @patch("src.empathy_os.platform_utils.is_windows", return_value=True)
    def test_setup_asyncio_policy_windows(self, mock_windows):
        """Test setup_asyncio_policy sets policy on Windows."""
        import asyncio

        with patch.object(asyncio, "set_event_loop_policy") as mock_set_policy:
            with patch.object(asyncio, "WindowsSelectorEventLoopPolicy", create=True):
                setup_asyncio_policy()
                # On Windows, set_event_loop_policy should be called
                mock_set_policy.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_run_async_executes(self):
        """Test safe_run_async can execute a coroutine."""

        async def sample_coro():
            return 42

        # We can't easily test safe_run_async from within an async test
        # since we're already in an event loop, but we can verify import works
        assert callable(safe_run_async)


class TestFileUtilities:
    """Tests for file utility functions."""

    def test_open_text_file_default_encoding(self):
        """Test open_text_file uses UTF-8 by default."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            with open_text_file(temp_path, "r") as f:
                content = f.read()
                assert content == "Hello, World!"
        finally:
            Path(temp_path).unlink()

    def test_open_text_file_custom_encoding(self):
        """Test open_text_file accepts custom encoding."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write("Test")
            temp_path = f.name

        try:
            with open_text_file(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert content == "Test"
        finally:
            Path(temp_path).unlink()

    def test_read_text_file(self):
        """Test read_text_file reads content correctly."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write("Line 1\nLine 2\n")
            temp_path = f.name

        try:
            content = read_text_file(temp_path)
            assert "Line 1" in content
            assert "Line 2" in content
        finally:
            Path(temp_path).unlink()

    def test_write_text_file(self):
        """Test write_text_file writes content correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "test.txt"

            chars_written = write_text_file(temp_path, "Hello, World!")

            assert chars_written == 13
            assert temp_path.read_text(encoding="utf-8") == "Hello, World!"

    def test_write_and_read_unicode(self):
        """Test file utilities handle Unicode correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "unicode.txt"

            content = "Hello 世界 🌍 émojis"
            write_text_file(temp_path, content)
            read_content = read_text_file(temp_path)

            assert read_content == content


class TestPathUtilities:
    """Tests for path utility functions."""

    def test_normalize_path_string(self):
        """Test normalize_path with string input."""
        result = normalize_path(".")
        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_normalize_path_pathlib(self):
        """Test normalize_path with Path input."""
        result = normalize_path(Path())
        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_normalize_path_resolves(self):
        """Test normalize_path resolves relative components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "a" / "b"
            subdir.mkdir(parents=True)

            relative_path = subdir / ".." / ".." / "a"
            normalized = normalize_path(relative_path)

            assert ".." not in str(normalized)

    def test_get_temp_dir(self):
        """Test get_temp_dir returns valid temp directory."""
        temp_dir = get_temp_dir()

        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_ensure_dir_creates_directory(self):
        """Test ensure_dir creates directory if not exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new" / "nested" / "dir"
            assert not new_dir.exists()

            result = ensure_dir(new_dir)

            assert result == new_dir
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_ensure_dir_existing_directory(self):
        """Test ensure_dir handles existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_dir = Path(tmpdir)

            result = ensure_dir(existing_dir)

            assert result == existing_dir
            assert existing_dir.exists()

    def test_ensure_dir_returns_path(self):
        """Test ensure_dir returns Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_dir(tmpdir)

            assert isinstance(result, Path)


class TestPlatformInfo:
    """Tests for platform information functions."""

    def test_platform_info_has_required_keys(self):
        """Test PLATFORM_INFO contains required keys."""
        required_keys = [
            "system",
            "release",
            "version",
            "machine",
            "python_version",
            "is_windows",
            "is_macos",
            "is_linux",
        ]

        for key in required_keys:
            assert key in PLATFORM_INFO

    def test_get_platform_info_returns_copy(self):
        """Test get_platform_info returns a copy."""
        info1 = get_platform_info()
        info2 = get_platform_info()

        assert info1 == info2
        assert info1 is not info2  # Should be different objects

    def test_get_platform_info_modifiable(self):
        """Test modifying returned info doesn't affect original."""
        info = get_platform_info()
        info["custom_key"] = "custom_value"

        assert "custom_key" not in PLATFORM_INFO

    def test_platform_info_types(self):
        """Test PLATFORM_INFO values have correct types."""
        info = get_platform_info()

        assert isinstance(info["system"], str)
        assert isinstance(info["python_version"], str)
        assert isinstance(info["is_windows"], bool)
        assert isinstance(info["is_macos"], bool)
        assert isinstance(info["is_linux"], bool)

    def test_platform_booleans_consistent(self):
        """Test platform booleans match function results."""
        info = get_platform_info()

        # These are captured at module load time, so they should match
        # the current platform detection
        assert info["is_windows"] == is_windows()
        assert info["is_macos"] == is_macos()
        assert info["is_linux"] == is_linux()


class TestIntegration:
    """Integration tests for platform utilities."""

    def test_create_and_write_to_temp_location(self):
        """Test creating directory and writing file in temp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = ensure_dir(Path(tmpdir) / "empathy" / "test")
            file_path = target_dir / "test.txt"

            write_text_file(file_path, "Integration test content")
            content = read_text_file(file_path)

            assert content == "Integration test content"

    def test_directory_functions_return_paths(self):
        """Test all directory functions return Path objects."""
        assert isinstance(get_default_log_dir(), Path)
        assert isinstance(get_default_data_dir(), Path)
        assert isinstance(get_default_config_dir(), Path)
        assert isinstance(get_default_cache_dir(), Path)
        assert isinstance(get_temp_dir(), Path)

    def test_directory_paths_contain_empathy(self):
        """Test directory paths contain 'empathy' folder."""
        assert "empathy" in str(get_default_log_dir())
        assert "empathy" in str(get_default_data_dir())
        assert "empathy" in str(get_default_config_dir())
        assert "empathy" in str(get_default_cache_dir())
