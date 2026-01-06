"""CI integration test for cross-platform compatibility.

Runs the platform compatibility checker as part of pytest to catch
cross-platform issues during regular test runs.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestPlatformCompatibility:
    """Tests for cross-platform compatibility in the codebase."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def test_no_critical_platform_issues(self, project_root: Path):
        """Ensure no critical cross-platform errors in src/ directory."""
        script = project_root / "scripts" / "check_platform_compat.py"

        if not script.exists():
            pytest.skip("Platform compatibility script not found")

        result = subprocess.run(
            [sys.executable, str(script), str(project_root / "src"), "--json"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        import json

        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Failed to parse compatibility report: {result.stdout}")

        errors = report["summary"]["errors"]
        assert errors == 0, (
            f"Found {errors} platform compatibility errors. Run: python scripts/check_platform_compat.py src/ --fix"
        )

    def test_platform_utils_available(self):
        """Ensure platform_utils module is importable."""
        try:
            from empathy_os.platform_utils import (
                get_default_data_dir,
                get_default_log_dir,
                is_linux,
                is_macos,
                is_windows,
                setup_asyncio_policy,
            )

            # Verify functions are callable
            assert callable(is_windows)
            assert callable(is_macos)
            assert callable(is_linux)
            assert callable(get_default_log_dir)
            assert callable(get_default_data_dir)
            assert callable(setup_asyncio_policy)
        except ImportError as e:
            pytest.fail(f"platform_utils module not importable: {e}")

    def test_platform_detection_consistent(self):
        """Ensure platform detection is consistent."""
        from empathy_os.platform_utils import is_linux, is_macos, is_windows

        # At most one should be True
        platforms = [is_windows(), is_macos(), is_linux()]
        true_count = sum(platforms)

        assert true_count <= 1, "Multiple platforms detected as True"

    def test_default_directories_are_paths(self):
        """Ensure directory functions return Path objects."""
        from empathy_os.platform_utils import (
            get_default_cache_dir,
            get_default_config_dir,
            get_default_data_dir,
            get_default_log_dir,
        )

        assert isinstance(get_default_log_dir(), Path)
        assert isinstance(get_default_data_dir(), Path)
        assert isinstance(get_default_config_dir(), Path)
        assert isinstance(get_default_cache_dir(), Path)

    def test_asyncio_policy_runs_without_error(self):
        """Ensure asyncio policy setup doesn't raise."""
        from empathy_os.platform_utils import setup_asyncio_policy

        # Should not raise on any platform
        setup_asyncio_policy()
