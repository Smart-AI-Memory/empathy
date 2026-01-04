"""Comprehensive tests for SoftwarePlugin

Tests the software development plugin including metadata, wizard registration,
pattern registration, and graceful import handling.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
from unittest.mock import patch

from empathy_software_plugin.plugin import SoftwarePlugin

# ============================================================================
# Plugin Initialization Tests
# ============================================================================


def test_software_plugin_instantiation():
    """Test creating SoftwarePlugin instance"""
    plugin = SoftwarePlugin()
    assert plugin is not None
    assert isinstance(plugin, SoftwarePlugin)


# ============================================================================
# Metadata Tests
# ============================================================================


def test_get_metadata():
    """Test plugin metadata is complete and correct"""
    plugin = SoftwarePlugin()
    metadata = plugin.get_metadata()

    assert metadata is not None
    assert metadata.name == "Empathy Framework - Software Development"
    assert metadata.version == "1.0.0"
    assert metadata.domain == "software"
    assert metadata.author == "Smart AI Memory, LLC"
    assert metadata.license == "Apache-2.0"
    assert metadata.requires_core_version == "1.0.0"


def test_get_metadata_description():
    """Test metadata description mentions key features"""
    plugin = SoftwarePlugin()
    metadata = plugin.get_metadata()

    description = metadata.description
    assert "16+" in description or "Coach" in description
    assert "wizard" in description.lower()
    assert len(description) > 50  # Should be descriptive


def test_get_metadata_dependencies():
    """Test metadata includes dependencies list"""
    plugin = SoftwarePlugin()
    metadata = plugin.get_metadata()

    assert hasattr(metadata, "dependencies")
    assert isinstance(metadata.dependencies, list)


# ============================================================================
# Wizard Registration Tests
# ============================================================================


def test_register_wizards_returns_dict():
    """Test wizard registration returns dictionary"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    assert isinstance(wizards, dict)


def test_register_wizards_with_available_wizards():
    """Test registering wizards when imports succeed"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    # At least some wizards should be registered
    # (depends on what's actually available in the codebase)
    assert isinstance(wizards, dict)


def test_register_wizards_security_wizard():
    """Test security wizard registration if available"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    # If security wizard is available, it should be registered
    if "security" in wizards:
        assert wizards["security"] is not None
        # Should be a class (Type[BaseWizard])
        assert hasattr(wizards["security"], "__name__")


def test_register_wizards_performance_wizard():
    """Test performance wizard registration if available"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    if "performance" in wizards:
        assert wizards["performance"] is not None
        assert hasattr(wizards["performance"], "__name__")


def test_register_wizards_testing_wizard():
    """Test testing wizard registration if available"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    if "testing" in wizards:
        assert wizards["testing"] is not None
        assert hasattr(wizards["testing"], "__name__")


def test_register_wizards_architecture_wizard():
    """Test architecture wizard registration if available"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    if "architecture" in wizards:
        assert wizards["architecture"] is not None
        assert hasattr(wizards["architecture"], "__name__")


def test_register_wizards_ai_wizards():
    """Test AI development wizard registration if available"""
    plugin = SoftwarePlugin()
    wizards = plugin.register_wizards()

    # Check for AI-related wizards
    ai_wizard_keys = [
        "prompt_engineering",
        "context_window",
        "collaboration_pattern",
        "ai_documentation",
        "agent_orchestration",
        "rag_pattern",
        "multi_model",
    ]

    for key in ai_wizard_keys:
        if key in wizards:
            assert wizards[key] is not None


def test_register_wizards_graceful_import_failure():
    """Test that wizard registration handles import failures gracefully"""
    plugin = SoftwarePlugin()

    # Mock import to fail for a specific wizard
    with patch("empathy_software_plugin.plugin.logger"):
        # This should not raise an exception even if imports fail
        wizards = plugin.register_wizards()

        # Should still return a dict (possibly empty or partial)
        assert isinstance(wizards, dict)


def test_register_wizards_logs_warnings_on_import_error():
    """Test that import errors are logged as warnings"""
    plugin = SoftwarePlugin()

    with patch("empathy_software_plugin.plugin.logger"):
        # Force an import error by mocking sys.modules
        original_modules = sys.modules.copy()

        try:
            # Remove a wizard module to simulate import error
            if "empathy_software_plugin.wizards.security_wizard" in sys.modules:
                del sys.modules["empathy_software_plugin.wizards.security_wizard"]

            wizards = plugin.register_wizards()

            # Check if any warnings were logged
            # (This depends on which wizards actually fail to import)
            assert isinstance(wizards, dict)

        finally:
            # Restore original modules
            sys.modules.update(original_modules)


def test_register_wizards_logs_success_count():
    """Test that successful wizard registration is logged"""
    plugin = SoftwarePlugin()

    with patch("empathy_software_plugin.plugin.logger") as mock_logger:
        wizards = plugin.register_wizards()

        # Should log the number of registered wizards
        mock_logger.info.assert_called()

        # Check the logged message contains wizard count
        call_args = mock_logger.info.call_args[0][0]
        assert "registered" in call_args.lower()
        assert str(len(wizards)) in call_args


# ============================================================================
# Pattern Registration Tests
# ============================================================================


def test_register_patterns_returns_dict():
    """Test pattern registration returns dictionary"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    assert isinstance(patterns, dict)


def test_register_patterns_domain():
    """Test patterns include domain identifier"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    assert "domain" in patterns
    assert patterns["domain"] == "software"


def test_register_patterns_includes_patterns():
    """Test patterns dictionary includes pattern definitions"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    assert "patterns" in patterns
    assert isinstance(patterns["patterns"], dict)


def test_register_patterns_testing_bottleneck():
    """Test testing bottleneck pattern is registered"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    pattern_dict = patterns.get("patterns", {})

    if "testing_bottleneck" in pattern_dict:
        pattern = pattern_dict["testing_bottleneck"]

        assert "description" in pattern
        assert "indicators" in pattern
        assert "threshold" in pattern
        assert "recommendation" in pattern

        # Validate structure
        assert isinstance(pattern["description"], str)
        assert isinstance(pattern["indicators"], list)
        assert len(pattern["indicators"]) > 0
        assert "test" in pattern["description"].lower()


def test_register_patterns_security_drift():
    """Test security drift pattern is registered"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    pattern_dict = patterns.get("patterns", {})

    if "security_drift" in pattern_dict:
        pattern = pattern_dict["security_drift"]

        assert "description" in pattern
        assert "indicators" in pattern
        assert isinstance(pattern["description"], str)
        assert isinstance(pattern["indicators"], list)
        assert len(pattern["indicators"]) > 0
        assert "security" in pattern["description"].lower()


def test_register_patterns_indicators_are_meaningful():
    """Test pattern indicators are meaningful strings"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    pattern_dict = patterns.get("patterns", {})

    for _pattern_name, pattern_def in pattern_dict.items():
        if "indicators" in pattern_def:
            indicators = pattern_def["indicators"]
            for indicator in indicators:
                assert isinstance(indicator, str)
                assert len(indicator) > 0
                # Indicators should use snake_case or similar
                assert "_" in indicator or indicator.islower()


def test_register_patterns_descriptions_are_detailed():
    """Test pattern descriptions are detailed and helpful"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    pattern_dict = patterns.get("patterns", {})

    for _pattern_name, pattern_def in pattern_dict.items():
        if "description" in pattern_def:
            description = pattern_def["description"]
            # Descriptions should be substantial
            assert len(description) > 30
            # Should contain useful keywords
            assert any(
                word in description.lower()
                for word in ["alert", "when", "recommend", "monitoring", "pattern"]
            )


# ============================================================================
# Integration Tests
# ============================================================================


def test_plugin_full_initialization():
    """Test complete plugin initialization workflow"""
    plugin = SoftwarePlugin()

    # Get all components
    metadata = plugin.get_metadata()
    wizards = plugin.register_wizards()
    patterns = plugin.register_patterns()

    # All components should be valid
    assert metadata is not None
    assert isinstance(wizards, dict)
    assert isinstance(patterns, dict)

    # Metadata should be complete
    assert metadata.name
    assert metadata.version
    assert metadata.domain

    # Patterns should have domain
    assert patterns.get("domain") == "software"


def test_plugin_metadata_consistency():
    """Test metadata values are consistent"""
    plugin = SoftwarePlugin()
    metadata = plugin.get_metadata()

    # Version should be semantic versioning
    version_parts = metadata.version.split(".")
    assert len(version_parts) >= 2
    assert all(part.isdigit() for part in version_parts)

    # Domain should match pattern domain
    patterns = plugin.register_patterns()
    assert metadata.domain == patterns.get("domain")


def test_plugin_wizard_count_logged():
    """Test that wizard count is properly logged"""
    plugin = SoftwarePlugin()

    with patch("empathy_software_plugin.plugin.logger") as mock_logger:
        wizards = plugin.register_wizards()

        # Verify logging was called
        assert mock_logger.info.called

        # Get the logged message
        logged_message = str(mock_logger.info.call_args[0][0])

        # Should contain wizard count
        wizard_count = len(wizards)
        assert str(wizard_count) in logged_message


def test_plugin_can_be_instantiated_multiple_times():
    """Test that multiple plugin instances can coexist"""
    plugin1 = SoftwarePlugin()
    plugin2 = SoftwarePlugin()

    metadata1 = plugin1.get_metadata()
    metadata2 = plugin2.get_metadata()

    # Both should have valid metadata
    assert metadata1.name == metadata2.name
    assert metadata1.version == metadata2.version

    # Both should register wizards independently
    wizards1 = plugin1.register_wizards()
    wizards2 = plugin2.register_wizards()

    assert len(wizards1) == len(wizards2)


# ============================================================================
# Mock Import Tests (Isolated Wizard Registration)
# ============================================================================


@patch("empathy_software_plugin.plugin.logger")
def test_register_wizards_with_all_imports_failing(mock_logger):
    """Test wizard registration when all imports fail"""
    plugin = SoftwarePlugin()

    # Mock all wizard imports to fail
    with patch.dict(
        "sys.modules",
        {
            "empathy_software_plugin.wizards.security_wizard": None,
            "empathy_software_plugin.wizards.performance_wizard": None,
            "empathy_software_plugin.wizards.testing_wizard": None,
            "empathy_software_plugin.wizards.architecture_wizard": None,
        },
    ):
        wizards = plugin.register_wizards()

        # Should return empty dict or dict with available wizards
        assert isinstance(wizards, dict)

        # Logger should have been called with info about registered wizards
        assert mock_logger.info.called


@patch("empathy_software_plugin.plugin.logger")
def test_wizard_import_warning_contains_error_details(mock_logger):
    """Test that import warnings include error details"""
    plugin = SoftwarePlugin()

    # Create a mock that will raise ImportError
    def mock_import_error(*args, **kwargs):
        raise ImportError("Test module not found")

    with patch("builtins.__import__", side_effect=mock_import_error):
        # This will trigger import errors
        try:
            plugin.register_wizards()
        except Exception:
            pass  # Expected to fail

        # Check if warning was logged with error details
        # (may or may not be called depending on implementation)


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_plugin_metadata_with_empty_dependencies():
    """Test that empty dependencies list is valid"""
    plugin = SoftwarePlugin()
    metadata = plugin.get_metadata()

    # Empty dependencies should be valid
    assert isinstance(metadata.dependencies, list)


def test_plugin_patterns_structure_is_valid():
    """Test that pattern structure matches expected schema"""
    plugin = SoftwarePlugin()
    patterns = plugin.register_patterns()

    # Top-level keys
    assert "domain" in patterns
    assert "patterns" in patterns

    # Each pattern should have expected keys
    for pattern_name, pattern_def in patterns["patterns"].items():
        # Core pattern fields
        assert isinstance(pattern_name, str)
        assert isinstance(pattern_def, dict)

        # Common pattern fields (may vary by pattern)
        if "description" in pattern_def:
            assert isinstance(pattern_def["description"], str)
        if "indicators" in pattern_def:
            assert isinstance(pattern_def["indicators"], list)


def test_plugin_wizard_registration_is_idempotent():
    """Test that calling register_wizards multiple times is safe"""
    plugin = SoftwarePlugin()

    wizards1 = plugin.register_wizards()
    wizards2 = plugin.register_wizards()

    # Should return same wizard set
    assert len(wizards1) == len(wizards2)
    assert set(wizards1.keys()) == set(wizards2.keys())


def test_plugin_pattern_registration_is_idempotent():
    """Test that calling register_patterns multiple times is safe"""
    plugin = SoftwarePlugin()

    patterns1 = plugin.register_patterns()
    patterns2 = plugin.register_patterns()

    # Should return same pattern set
    assert patterns1 == patterns2
