"""Feature discovery parsers for keyboard shortcut generation.

Supports multiple input sources:
- VSCode extension package.json
- Python pyproject.toml entry points
- Custom features.yaml manifest
- LLM-based code analysis
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path

import yaml

from .schema import Category, Feature, FeatureManifest, FrequencyTier


class FeatureParser(ABC):
    """Base class for feature parsers."""

    @abstractmethod
    def parse(self, path: Path) -> list[Feature]:
        """Extract features from source file."""

    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Check if this parser can handle the given path."""


class VSCodeCommandParser(FeatureParser):
    """Parse VSCode extension package.json for commands."""

    def can_parse(self, path: Path) -> bool:
        return path.name == "package.json" and path.exists()

    def parse(self, path: Path) -> list[Feature]:
        """Extract commands from VSCode package.json."""
        try:
            pkg = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return []

        commands = pkg.get("contributes", {}).get("commands", [])
        features = []

        for cmd in commands:
            command_id = cmd.get("command", "")
            title = cmd.get("title", "")

            # Skip internal/hidden commands
            if not title or command_id.startswith("_"):
                continue

            # Extract category from title (e.g., "Empathy: Quick → Morning")
            category = self._extract_category(title)
            name = self._extract_name(title)

            # Determine frequency tier based on category
            tier = self._infer_tier(category)

            features.append(
                Feature(
                    id=command_id.split(".")[-1],
                    name=name,
                    description=f"VSCode command: {command_id}",
                    command=command_id,
                    icon=cmd.get("icon", "$(symbol-misc)"),
                    frequency=tier,
                ),
            )

        return features

    def _extract_category(self, title: str) -> str:
        """Extract category from title like 'Empathy: Quick → Morning'."""
        if "→" in title:
            parts = title.split("→")
            if len(parts) >= 2:
                # Get the part before the arrow
                prefix = parts[0].strip()
                if ":" in prefix:
                    return prefix.split(":")[-1].strip()
                return prefix
        if ":" in title:
            return title.split(":")[0].strip()
        return "General"

    def _extract_name(self, title: str) -> str:
        """Extract feature name from title like 'Empathy: Quick → Morning'."""
        if "→" in title:
            return title.split("→")[-1].strip()
        if ":" in title:
            return title.split(":")[-1].strip()
        return title.strip()

    def _infer_tier(self, category: str) -> FrequencyTier:
        """Infer frequency tier from category name."""
        category_lower = category.lower()
        if "quick" in category_lower or "daily" in category_lower:
            return FrequencyTier.DAILY
        if "view" in category_lower or "workflow" in category_lower:
            return FrequencyTier.FREQUENT
        return FrequencyTier.ADVANCED


class PyProjectParser(FeatureParser):
    """Parse Python pyproject.toml for CLI entry points."""

    def can_parse(self, path: Path) -> bool:
        return path.name == "pyproject.toml" and path.exists()

    def parse(self, path: Path) -> list[Feature]:
        """Extract CLI scripts from pyproject.toml."""
        try:
            # Python 3.11+ has tomllib built-in
            import tomllib

            data = tomllib.loads(path.read_text())
        except ImportError:
            # Fallback for older Python
            try:
                import tomli as tomllib

                data = tomllib.loads(path.read_text())
            except ImportError:
                return []
        except (OSError, Exception):
            return []

        features = []

        # Parse [project.scripts] section
        scripts = data.get("project", {}).get("scripts", {})
        for name, _entry_point in scripts.items():
            features.append(
                Feature(
                    id=name.replace("-", "_"),
                    name=name.replace("-", " ").title(),
                    description=f"CLI command: {name}",
                    command=f"cli.{name}",
                    cli_alias=name,
                    frequency=FrequencyTier.FREQUENT,
                ),
            )

        # Parse [project.entry-points] section
        entry_points = data.get("project", {}).get("entry-points", {})
        for group, entries in entry_points.items():
            if isinstance(entries, dict):
                for name, entry_point in entries.items():
                    features.append(
                        Feature(
                            id=f"{group}_{name}".replace("-", "_"),
                            name=name.replace("-", " ").title(),
                            description=f"Entry point: {group}.{name}",
                            command=entry_point,
                            frequency=FrequencyTier.ADVANCED,
                        ),
                    )

        return features


class YAMLManifestParser(FeatureParser):
    """Parse custom features.yaml manifest."""

    def can_parse(self, path: Path) -> bool:
        return path.name in ("features.yaml", "features.yml") and path.exists()

    def parse(self, path: Path) -> list[Feature]:
        """Extract features from custom YAML manifest."""
        try:
            manifest = yaml.safe_load(path.read_text())
        except (yaml.YAMLError, OSError):
            return []

        if not manifest or not isinstance(manifest, dict):
            return []

        features = []
        categories = manifest.get("categories", [])

        for category in categories:
            if not isinstance(category, dict):
                continue

            category.get("name", "General")
            tier_str = category.get("tier", "frequent")
            tier = (
                FrequencyTier(tier_str)
                if tier_str in FrequencyTier._value2member_map_
                else FrequencyTier.FREQUENT
            )

            for feat in category.get("features", []):
                if not isinstance(feat, dict):
                    continue

                freq_str = feat.get("frequency", tier_str)
                freq = (
                    FrequencyTier(freq_str)
                    if freq_str in FrequencyTier._value2member_map_
                    else tier
                )

                features.append(
                    Feature(
                        id=feat.get("id", feat.get("name", "").lower().replace(" ", "_")),
                        name=feat.get("name", ""),
                        description=feat.get("description", ""),
                        command=feat.get("command", ""),
                        cli_alias=feat.get("cli_alias", ""),
                        frequency=freq,
                        context=feat.get("context", "global"),
                        icon=feat.get("icon", "$(symbol-misc)"),
                    ),
                )

        return features

    def parse_full_manifest(self, path: Path) -> FeatureManifest | None:
        """Parse complete manifest including project metadata."""
        try:
            data = yaml.safe_load(path.read_text())
        except (yaml.YAMLError, OSError):
            return None

        if not data:
            return None

        project = data.get("project", {})
        categories = []

        for cat_data in data.get("categories", []):
            features = []
            tier_str = cat_data.get("tier", "frequent")
            tier = (
                FrequencyTier(tier_str)
                if tier_str in FrequencyTier._value2member_map_
                else FrequencyTier.FREQUENT
            )

            for feat_data in cat_data.get("features", []):
                freq_str = feat_data.get("frequency", tier_str)
                freq = (
                    FrequencyTier(freq_str)
                    if freq_str in FrequencyTier._value2member_map_
                    else tier
                )

                features.append(
                    Feature(
                        id=feat_data.get("id", ""),
                        name=feat_data.get("name", ""),
                        description=feat_data.get("description", ""),
                        command=feat_data.get("command", ""),
                        cli_alias=feat_data.get("cli_alias", ""),
                        frequency=freq,
                        context=feat_data.get("context", "global"),
                        icon=feat_data.get("icon", "$(symbol-misc)"),
                    ),
                )

            categories.append(
                Category(
                    name=cat_data.get("name", "General"),
                    icon=cat_data.get("icon", "$(folder)"),
                    tier=tier,
                    features=features,
                ),
            )

        return FeatureManifest(
            project_name=project.get("name", "project"),
            project_type=project.get("type", "custom"),
            prefix=project.get("prefix", "ctrl+shift+e"),
            categories=categories,
        )


class LLMFeatureAnalyzer:
    """Use LLM to analyze codebase and discover features."""

    def __init__(self, llm_client=None):
        """Initialize with optional LLM client."""
        self.llm_client = llm_client

    async def analyze_codebase(self, project_path: Path) -> list[Feature]:
        """Analyze codebase using LLM to discover features.

        This is a placeholder for LLM-based feature discovery.
        The actual implementation would:
        1. Scan for function signatures, CLI decorators, etc.
        2. Send code snippets to LLM for analysis
        3. Extract feature descriptions and usage patterns
        """
        # TODO: Implement LLM-based feature discovery
        # For now, return empty list
        return []


class CompositeParser:
    """Combines multiple parsers for comprehensive feature discovery."""

    def __init__(self):
        self.parsers: list[FeatureParser] = [
            VSCodeCommandParser(),
            PyProjectParser(),
            YAMLManifestParser(),
        ]
        self.llm_analyzer = LLMFeatureAnalyzer()

    def discover_features(self, project_path: Path) -> FeatureManifest:
        """Discover all features from a project.

        Scans for:
        - VSCode package.json commands
        - Python pyproject.toml entry points
        - Custom features.yaml manifest
        """
        all_features: list[Feature] = []

        # Try each parser
        for parser in self.parsers:
            for file_pattern in self._get_patterns(parser):
                for found_path in project_path.rglob(file_pattern):
                    if parser.can_parse(found_path):
                        features = parser.parse(found_path)
                        all_features.extend(features)

        # Check for custom manifest with full metadata
        manifest_path = project_path / "features.yaml"
        if manifest_path.exists():
            yaml_parser = YAMLManifestParser()
            full_manifest = yaml_parser.parse_full_manifest(manifest_path)
            if full_manifest:
                return full_manifest

        # Create manifest from discovered features
        return self._create_manifest_from_features(project_path, all_features)

    def _get_patterns(self, parser: FeatureParser) -> list[str]:
        """Get file patterns for a parser."""
        if isinstance(parser, VSCodeCommandParser):
            return ["package.json"]
        if isinstance(parser, PyProjectParser):
            return ["pyproject.toml"]
        if isinstance(parser, YAMLManifestParser):
            return ["features.yaml", "features.yml"]
        return []

    def _create_manifest_from_features(
        self,
        project_path: Path,
        features: list[Feature],
    ) -> FeatureManifest:
        """Create a manifest from discovered features."""
        # Group features by inferred category
        categories_dict: dict[str, list[Feature]] = {}
        for feature in features:
            # Try to infer category from feature properties
            category = "General"
            if "quick" in feature.id.lower() or feature.frequency == FrequencyTier.DAILY:
                category = "Quick Actions"
            elif "view" in feature.id.lower() or "dashboard" in feature.id.lower():
                category = "Views"
            elif "workflow" in feature.id.lower() or "run" in feature.id.lower():
                category = "Workflows"
            elif "security" in feature.id.lower() or "audit" in feature.id.lower():
                category = "Security"

            if category not in categories_dict:
                categories_dict[category] = []
            categories_dict[category].append(feature)

        # Convert to Category objects
        categories = []
        for name, feats in categories_dict.items():
            # Determine tier based on most common tier in category
            tier = FrequencyTier.FREQUENT
            if feats:
                tier_counts: dict[FrequencyTier, int] = {}
                for f in feats:
                    tier_counts[f.frequency] = tier_counts.get(f.frequency, 0) + 1
                tier = max(tier_counts.keys(), key=lambda t: tier_counts[t])

            categories.append(
                Category(
                    name=name,
                    tier=tier,
                    features=feats,
                ),
            )

        # Infer project name
        project_name = project_path.name

        # Infer project type - use cast for Literal typing
        from typing import Literal, cast

        project_type_str = "custom"
        if (project_path / "package.json").exists():
            project_type_str = "vscode-extension"
        elif (project_path / "pyproject.toml").exists():
            project_type_str = "python-cli"

        project_type = cast("Literal['vscode-extension', 'python-cli', 'custom']", project_type_str)

        return FeatureManifest(
            project_name=project_name,
            project_type=project_type,
            categories=categories,
        )
