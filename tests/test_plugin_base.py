"""Comprehensive tests for Plugin System Base Classes

Tests cover:
- PluginMetadata dataclass
- BaseWizard abstract class and methods
- BasePlugin abstract class and lifecycle
- Plugin exception classes
"""

import pytest

from src.empathy_os.plugins.base import (
    BasePlugin,
    BaseWizard,
    PluginError,
    PluginLoadError,
    PluginMetadata,
    PluginValidationError,
)


class TestPluginMetadata:
    """Test PluginMetadata dataclass"""

    def test_plugin_metadata_creation(self):
        """Test PluginMetadata creation with all fields"""
        metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0",
            domain="test",
            description="A test plugin",
            author="Test Author",
            license="Apache-2.0",
            requires_core_version="1.0.0",
            dependencies=["numpy", "pandas"],
        )

        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"
        assert metadata.domain == "test"
        assert metadata.description == "A test plugin"
        assert metadata.author == "Test Author"
        assert metadata.license == "Apache-2.0"
        assert metadata.requires_core_version == "1.0.0"
        assert metadata.dependencies == ["numpy", "pandas"]

    def test_plugin_metadata_no_dependencies(self):
        """Test PluginMetadata without dependencies"""
        metadata = PluginMetadata(
            name="Simple Plugin",
            version="0.1.0",
            domain="simple",
            description="Simple",
            author="Author",
            license="MIT",
            requires_core_version="0.1.0",
        )

        assert metadata.dependencies is None


class TestBaseWizard:
    """Test BaseWizard abstract class"""

    def test_base_wizard_initialization(self):
        """Test BaseWizard initialization"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {
                    "issues": [],
                    "predictions": [],
                    "recommendations": [],
                    "patterns": [],
                    "confidence": 1.0,
                }

            def get_required_context(self):
                return ["input_data"]

        wizard = ConcreteWizard(
            name="Test Wizard",
            domain="test",
            empathy_level=3,
            category="testing",
        )

        assert wizard.name == "Test Wizard"
        assert wizard.domain == "test"
        assert wizard.empathy_level == 3
        assert wizard.category == "testing"

    def test_base_wizard_no_category(self):
        """Test BaseWizard without category"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {"issues": []}

            def get_required_context(self):
                return []

        wizard = ConcreteWizard(name="Simple", domain="test", empathy_level=1)

        assert wizard.category is None

    def test_wizard_validate_context_valid(self):
        """Test validate_context with valid context"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return ["code", "file_path"]

        wizard = ConcreteWizard(name="Test", domain="test", empathy_level=1)

        context = {"code": "def test(): pass", "file_path": "test.py"}

        assert wizard.validate_context(context) is True

    def test_wizard_validate_context_missing_fields(self):
        """Test validate_context with missing fields"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return ["code", "file_path", "language"]

        wizard = ConcreteWizard(name="Test", domain="test", empathy_level=1)

        context = {"code": "test"}

        with pytest.raises(
            ValueError,
            match="missing required context: \\['file_path', 'language'\\]",
        ):
            wizard.validate_context(context)

    def test_wizard_get_empathy_level(self):
        """Test get_empathy_level method"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        wizard = ConcreteWizard(name="Test", domain="test", empathy_level=4)

        assert wizard.get_empathy_level() == 4

    def test_wizard_contribute_patterns_default(self):
        """Test default contribute_patterns implementation"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        wizard = ConcreteWizard(name="PatternWizard", domain="patterns", empathy_level=5)

        analysis_result = {"patterns": ["pattern1", "pattern2"], "confidence": 0.9}

        patterns = wizard.contribute_patterns(analysis_result)

        assert patterns["wizard"] == "PatternWizard"
        assert patterns["domain"] == "patterns"
        assert "timestamp" in patterns
        assert patterns["patterns"] == ["pattern1", "pattern2"]

    def test_wizard_contribute_patterns_no_patterns(self):
        """Test contribute_patterns with no patterns in result"""

        class ConcreteWizard(BaseWizard):
            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        wizard = ConcreteWizard(name="Test", domain="test", empathy_level=1)

        patterns = wizard.contribute_patterns({"confidence": 1.0})

        assert patterns["patterns"] == []


class TestBasePlugin:
    """Test BasePlugin abstract class"""

    def test_base_plugin_initialization(self):
        """Test BasePlugin initialization"""

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test Plugin",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="Apache-2.0",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {}

        plugin = ConcretePlugin()

        assert plugin._initialized is False
        assert plugin._wizards == {}

    def test_plugin_initialize(self):
        """Test plugin initialization"""

        class TestWizard(BaseWizard):
            def __init__(self):
                super().__init__(name="Test", domain="test", empathy_level=1)

            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test Plugin",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="Apache-2.0",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {"test_wizard": TestWizard}

        plugin = ConcretePlugin()
        plugin.initialize()

        assert plugin._initialized is True
        assert len(plugin._wizards) == 1
        assert "test_wizard" in plugin._wizards

    def test_plugin_initialize_idempotent(self):
        """Test that initialize can be called multiple times safely"""

        class ConcretePlugin(BasePlugin):
            def __init__(self):
                super().__init__()
                self.init_count = 0

            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                self.init_count += 1
                return {}

        plugin = ConcretePlugin()

        plugin.initialize()
        plugin.initialize()
        plugin.initialize()

        assert plugin.init_count == 1  # Should only register once

    def test_plugin_get_wizard(self):
        """Test get_wizard method"""

        class TestWizard(BaseWizard):
            def __init__(self):
                super().__init__(name="Test", domain="test", empathy_level=1)

            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {"test": TestWizard}

        plugin = ConcretePlugin()
        wizard_class = plugin.get_wizard("test")

        assert wizard_class == TestWizard

    def test_plugin_get_wizard_not_found(self):
        """Test get_wizard with non-existent wizard"""

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {}

        plugin = ConcretePlugin()
        wizard_class = plugin.get_wizard("nonexistent")

        assert wizard_class is None

    def test_plugin_list_wizards(self):
        """Test list_wizards method"""

        class Wizard1(BaseWizard):
            def __init__(self):
                super().__init__(name="W1", domain="test", empathy_level=1)

            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        class Wizard2(BaseWizard):
            def __init__(self):
                super().__init__(name="W2", domain="test", empathy_level=2)

            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return []

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {"wizard1": Wizard1, "wizard2": Wizard2}

        plugin = ConcretePlugin()
        wizard_list = plugin.list_wizards()

        assert len(wizard_list) == 2
        assert "wizard1" in wizard_list
        assert "wizard2" in wizard_list

    def test_plugin_get_wizard_info(self):
        """Test get_wizard_info method"""

        class TestWizard(BaseWizard):
            def __init__(self):
                super().__init__(
                    name="Info Wizard",
                    domain="test",
                    empathy_level=3,
                    category="info",
                )

            async def analyze(self, context):
                return {}

            def get_required_context(self):
                return ["data1", "data2"]

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {"test": TestWizard}

        plugin = ConcretePlugin()
        info = plugin.get_wizard_info("test")

        assert info is not None
        assert info["id"] == "test"
        assert info["name"] == "Info Wizard"
        assert info["domain"] == "test"
        assert info["empathy_level"] == 3
        assert info["category"] == "info"
        assert info["required_context"] == ["data1", "data2"]

    def test_plugin_get_wizard_info_not_found(self):
        """Test get_wizard_info for non-existent wizard"""

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {}

        plugin = ConcretePlugin()
        info = plugin.get_wizard_info("nonexistent")

        assert info is None

    def test_plugin_register_patterns_default(self):
        """Test default register_patterns implementation"""

        class ConcretePlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="Test",
                    version="1.0.0",
                    domain="test",
                    description="Test",
                    author="Test",
                    license="MIT",
                    requires_core_version="1.0.0",
                )

            def register_wizards(self):
                return {}

        plugin = ConcretePlugin()
        patterns = plugin.register_patterns()

        assert patterns == {}


class TestPluginExceptions:
    """Test plugin exception classes"""

    def test_plugin_error(self):
        """Test PluginError base exception"""
        with pytest.raises(PluginError, match="Test error"):
            raise PluginError("Test error")

    def test_plugin_load_error(self):
        """Test PluginLoadError exception"""
        with pytest.raises(PluginLoadError, match="Failed to load"):
            raise PluginLoadError("Failed to load")

    def test_plugin_validation_error(self):
        """Test PluginValidationError exception"""
        with pytest.raises(PluginValidationError, match="Validation failed"):
            raise PluginValidationError("Validation failed")

    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy"""
        assert issubclass(PluginLoadError, PluginError)
        assert issubclass(PluginValidationError, PluginError)
        assert issubclass(PluginError, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
