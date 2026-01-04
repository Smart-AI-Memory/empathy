"""Empathy Framework - Plugin Registry

Auto-discovery and management of domain plugins.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from importlib.metadata import entry_points

from .base import BasePlugin, BaseWizard, PluginValidationError

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for managing domain plugins.

    Features:
    - Auto-discovery via entry points
    - Manual registration
    - Lazy initialization
    - Graceful degradation (missing plugins don't crash)
    """

    def __init__(self):
        self._plugins: dict[str, BasePlugin] = {}
        self._auto_discovered = False
        self.logger = logging.getLogger("empathy.plugins.registry")

    def auto_discover(self) -> None:
        """Automatically discover plugins via entry points.

        Plugins register themselves in setup.py/pyproject.toml:

        [project.entry-points."empathy_framework.plugins"]
        software = "empathy_software.plugin:SoftwarePlugin"
        healthcare = "empathy_healthcare.plugin:HealthcarePlugin"
        """
        if self._auto_discovered:
            return

        self.logger.info("Auto-discovering plugins...")

        # Python 3.10+ has modern entry_points API with group parameter
        discovered = entry_points(group="empathy_framework.plugins")

        for ep in discovered:
            try:
                self.logger.info(f"Loading plugin '{ep.name}' from entry point")
                plugin_class = ep.load()
                plugin_instance = plugin_class()
                self.register_plugin(ep.name, plugin_instance)
                self.logger.info(f"Successfully loaded plugin: {ep.name}")
            except Exception as e:
                # Graceful degradation: log but don't crash
                self.logger.warning(f"Failed to load plugin '{ep.name}': {e}", exc_info=True)

        self._auto_discovered = True
        self.logger.info(f"Auto-discovery complete. {len(self._plugins)} plugins loaded.")

    def register_plugin(self, name: str, plugin: BasePlugin) -> None:
        """Manually register a plugin.

        Args:
            name: Plugin identifier (e.g., 'software', 'healthcare')
            plugin: Plugin instance

        Raises:
            PluginValidationError: If plugin is invalid

        """
        # Validate plugin
        try:
            metadata = plugin.get_metadata()
            if not metadata.name:
                raise PluginValidationError("Plugin metadata missing 'name'")
            if not metadata.domain:
                raise PluginValidationError("Plugin metadata missing 'domain'")
        except Exception as e:
            raise PluginValidationError(f"Invalid plugin metadata: {e}") from e

        # Register
        self._plugins[name] = plugin
        self.logger.info(
            f"Registered plugin '{name}' (domain: {metadata.domain}, version: {metadata.version})",
        )

    def get_plugin(self, name: str) -> BasePlugin | None:
        """Get a plugin by name.

        Args:
            name: Plugin identifier

        Returns:
            Plugin instance or None if not found

        """
        if not self._auto_discovered:
            self.auto_discover()

        plugin = self._plugins.get(name)
        if plugin and not plugin._initialized:
            plugin.initialize()

        return plugin

    def list_plugins(self) -> list[str]:
        """List all registered plugin names.

        Returns:
            List of plugin identifiers

        """
        if not self._auto_discovered:
            self.auto_discover()

        return list(self._plugins.keys())

    def list_all_wizards(self) -> dict[str, list[str]]:
        """List all wizards from all plugins.

        Returns:
            Dictionary mapping plugin_name -> list of wizard_ids

        """
        if not self._auto_discovered:
            self.auto_discover()

        result = {}
        for plugin_name, plugin in self._plugins.items():
            result[plugin_name] = plugin.list_wizards()

        return result

    def get_wizard(self, plugin_name: str, wizard_id: str) -> type[BaseWizard] | None:
        """Get a wizard from a specific plugin.

        Args:
            plugin_name: Plugin identifier
            wizard_id: Wizard identifier within plugin

        Returns:
            Wizard class or None if not found

        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return None

        return plugin.get_wizard(wizard_id)

    def get_wizard_info(self, plugin_name: str, wizard_id: str) -> dict | None:
        """Get information about a wizard.

        Args:
            plugin_name: Plugin identifier
            wizard_id: Wizard identifier

        Returns:
            Dictionary with wizard metadata or None

        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return None

        return plugin.get_wizard_info(wizard_id)

    def find_wizards_by_level(self, empathy_level: int) -> list[dict]:
        """Find all wizards operating at a specific empathy level.

        Args:
            empathy_level: Target empathy level (1-5)

        Returns:
            List of wizard info dictionaries

        """
        if not self._auto_discovered:
            self.auto_discover()

        results = []
        for plugin_name, plugin in self._plugins.items():
            for wizard_id in plugin.list_wizards():
                info = plugin.get_wizard_info(wizard_id)
                if info and info.get("empathy_level") == empathy_level:
                    info["plugin"] = plugin_name
                    results.append(info)

        return results

    def find_wizards_by_domain(self, domain: str) -> list[dict]:
        """Find all wizards for a specific domain.

        Args:
            domain: Domain identifier (e.g., 'software', 'healthcare')

        Returns:
            List of wizard info dictionaries

        """
        if not self._auto_discovered:
            self.auto_discover()

        results = []
        for plugin_name, plugin in self._plugins.items():
            metadata = plugin.get_metadata()
            if metadata.domain == domain:
                for wizard_id in plugin.list_wizards():
                    info = plugin.get_wizard_info(wizard_id)
                    if info:
                        info["plugin"] = plugin_name
                        results.append(info)

        return results

    def get_statistics(self) -> dict:
        """Get registry statistics.

        Returns:
            Dictionary with counts and metadata

        """
        if not self._auto_discovered:
            self.auto_discover()

        total_wizards = sum(len(plugin.list_wizards()) for plugin in self._plugins.values())

        # Count wizards by level
        wizards_by_level = {}
        for level in range(1, 6):
            wizards_by_level[f"level_{level}"] = len(self.find_wizards_by_level(level))

        return {
            "total_plugins": len(self._plugins),
            "total_wizards": total_wizards,
            "plugins": [
                {
                    "name": name,
                    "domain": plugin.get_metadata().domain,
                    "version": plugin.get_metadata().version,
                    "wizard_count": len(plugin.list_wizards()),
                }
                for name, plugin in self._plugins.items()
            ],
            "wizards_by_level": wizards_by_level,
        }


# Global registry instance
_global_registry: PluginRegistry | None = None


def get_global_registry() -> PluginRegistry:
    """Get the global plugin registry instance (singleton).

    Returns:
        Global PluginRegistry instance

    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
        _global_registry.auto_discover()
    return _global_registry
