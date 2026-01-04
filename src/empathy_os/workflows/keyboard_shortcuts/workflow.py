"""Keyboard Shortcuts Workflow

Generates optimized keyboard shortcuts for any project following
the "Keyboard Conductor" musical scale pattern.

Stages:
1. DISCOVER - Parse features from project sources
2. ANALYZE - Categorize features and suggest mnemonics (LLM)
3. GENERATE - Create shortcuts for all layouts (LLM)
4. VALIDATE - Check for conflicts and ergonomic issues (LLM)
5. EXPORT - Generate output files (local)
"""

import json
from pathlib import Path
from typing import Any

import yaml

from empathy_os.workflows.base import BaseWorkflow, ModelTier

from .generators import ComprehensiveGenerator
from .parsers import CompositeParser
from .prompts import format_analyze_prompt, format_generate_prompt, format_validate_prompt
from .schema import (
    FeatureManifest,
    FrequencyTier,
    GeneratedShortcuts,
    KeyboardLayout,
    LayoutShortcuts,
    ScaleAssignments,
    ShortcutAssignment,
)


class KeyboardShortcutWorkflow(BaseWorkflow):
    """Generate optimized keyboard shortcuts for any project.

    Uses the "Keyboard Conductor" pattern:
    - Scale 1 (Daily): 4 most-used features on home row
    - Scale 2 (Frequent): Next 4 features on adjacent keys
    - Scale 3 (Advanced): Remaining features logically placed
    """

    name = "keyboard-shortcuts"
    description = "Generate ergonomic keyboard shortcuts with multi-layout support"
    stages = ["discover", "analyze", "generate", "validate", "export"]
    tier_map = {
        "discover": ModelTier.CHEAP,  # Parse files, no LLM
        "analyze": ModelTier.CAPABLE,  # Categorize features
        "generate": ModelTier.CAPABLE,  # Generate shortcuts
        "validate": ModelTier.CHEAP,  # Check conflicts
        "export": ModelTier.CHEAP,  # Write files, no LLM
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = CompositeParser()
        self.generator = ComprehensiveGenerator()

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: dict[str, Any],
    ) -> tuple[Any, int, int]:
        """Execute a single workflow stage."""
        if stage_name == "discover":
            return await self._discover_features(input_data)
        if stage_name == "analyze":
            return await self._analyze_features(input_data, tier)
        if stage_name == "generate":
            return await self._generate_shortcuts(input_data, tier)
        if stage_name == "validate":
            return await self._validate_shortcuts(input_data, tier)
        if stage_name == "export":
            return await self._export_outputs(input_data)
        raise ValueError(f"Unknown stage: {stage_name}")

    def should_skip_stage(
        self,
        stage_name: str,
        input_data: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Check if a stage should be skipped."""
        if stage_name == "analyze":
            # Skip LLM analysis if features already have frequencies set
            manifest = input_data.get("manifest")
            if manifest and all(f.frequency for f in manifest.all_features()):
                return True, "Features already categorized"

        if stage_name == "validate":
            # Skip validation if user explicitly requests it
            if input_data.get("skip_validation", False):
                return True, "Validation skipped by user request"

        return False, None

    # ========================================================================
    # Stage 1: Discover Features
    # ========================================================================

    async def _discover_features(
        self,
        input_data: dict[str, Any],
    ) -> tuple[dict[str, Any], int, int]:
        """Parse features from project sources.

        Supports:
        - VSCode package.json commands
        - Python pyproject.toml entry points
        - Custom features.yaml manifest
        """
        project_path = Path(input_data.get("path", "."))

        # Use the composite parser to discover features
        manifest = self.parser.discover_features(project_path)

        # If no features found, return early
        if not manifest.all_features():
            return (
                {
                    "manifest": manifest,
                    "feature_count": 0,
                    "error": "No features found in project",
                },
                0,
                0,
            )

        return (
            {
                "manifest": manifest,
                "feature_count": len(manifest.all_features()),
                "categories": len(manifest.categories),
            },
            0,
            0,
        )

    # ========================================================================
    # Stage 2: Analyze Features (LLM)
    # ========================================================================

    async def _analyze_features(
        self,
        input_data: dict[str, Any],
        tier: ModelTier,
    ) -> tuple[dict[str, Any], int, int]:
        """Use LLM to categorize features and suggest mnemonics.

        Input: FeatureManifest with discovered features
        Output: Enhanced manifest with frequency tiers and mnemonic suggestions
        """
        manifest: FeatureManifest = input_data["manifest"]

        # Convert features to YAML for the prompt
        features_yaml = self._features_to_yaml(manifest)

        # Format the analysis prompt
        prompt = format_analyze_prompt(
            project_name=manifest.project_name,
            project_type=manifest.project_type,
            feature_count=len(manifest.all_features()),
            features_yaml=features_yaml,
        )

        # Call LLM (using inherited method from BaseWorkflow)
        response, in_tokens, out_tokens = await self._invoke_llm(
            prompt=prompt,
            tier=tier,
            system="You are a UX expert specializing in keyboard ergonomics.",
        )

        # Parse the response
        analysis = self._parse_yaml_response(response)

        # Update manifest with analysis results
        if analysis and "analyzed_features" in analysis:
            self._update_manifest_from_analysis(manifest, analysis)

        return (
            {
                "manifest": manifest,
                "analysis": analysis,
                "phrase_mnemonic": analysis.get("phrase_mnemonic", "") if analysis else "",
            },
            in_tokens,
            out_tokens,
        )

    # ========================================================================
    # Stage 3: Generate Shortcuts (LLM)
    # ========================================================================

    async def _generate_shortcuts(
        self,
        input_data: dict[str, Any],
        tier: ModelTier,
    ) -> tuple[dict[str, Any], int, int]:
        """Use LLM to generate optimal shortcuts for each layout.

        Input: Analyzed manifest
        Output: GeneratedShortcuts with shortcuts for all layouts
        """
        manifest: FeatureManifest = input_data["manifest"]
        analysis = input_data.get("analysis", {})

        # Format the generation prompt
        prompt = format_generate_prompt(
            analyzed_yaml=yaml.dump(analysis) if analysis else self._features_to_yaml(manifest),
            existing_shortcuts="[]",
            reserved_keys='["q", "w", "s", "z", "x"]',
        )

        # Call LLM
        response, in_tokens, out_tokens = await self._invoke_llm(
            prompt=prompt,
            tier=tier,
            system="You are a keyboard layout specialist.",
        )

        # Parse the response
        shortcuts_data = self._parse_json_response(response)

        # Build GeneratedShortcuts from response
        generated = self._build_generated_shortcuts(manifest, shortcuts_data)

        return (
            {
                "manifest": manifest,
                "generated": generated,
            },
            in_tokens,
            out_tokens,
        )

    # ========================================================================
    # Stage 4: Validate Shortcuts (LLM)
    # ========================================================================

    async def _validate_shortcuts(
        self,
        input_data: dict[str, Any],
        tier: ModelTier,
    ) -> tuple[dict[str, Any], int, int]:
        """Validate generated shortcuts for conflicts and issues.

        Input: GeneratedShortcuts
        Output: Validated shortcuts with any warnings/conflicts
        """
        generated: GeneratedShortcuts = input_data["generated"]

        # Format the validation prompt
        shortcuts_json = json.dumps(
            {
                layout.value: {
                    "shortcuts": [
                        {"key": s.key, "feature_id": s.feature_id, "mnemonic": s.mnemonic}
                        for s in layout_shortcuts.shortcuts
                    ],
                }
                for layout, layout_shortcuts in generated.layouts.items()
            },
            indent=2,
        )

        prompt = format_validate_prompt(shortcuts_json)

        # Call LLM
        response, in_tokens, out_tokens = await self._invoke_llm(
            prompt=prompt,
            tier=tier,
            system="You are a keyboard shortcut validator.",
        )

        # Parse the response
        validation = self._parse_json_response(response)

        # Update generated shortcuts with validation results
        if validation:
            generated.validation_passed = validation.get("valid", True)
            generated.conflicts = validation.get("conflicts", [])
            generated.warnings = validation.get("warnings", [])

        return (
            {
                "manifest": input_data["manifest"],
                "generated": generated,
                "validation": validation,
            },
            in_tokens,
            out_tokens,
        )

    # ========================================================================
    # Stage 5: Export Outputs
    # ========================================================================

    async def _export_outputs(
        self,
        input_data: dict[str, Any],
    ) -> tuple[dict[str, Any], int, int]:
        """Generate output files in all formats.

        Output:
        - VSCode keybindings (per layout)
        - CLI aliases script
        - Markdown documentation
        """
        generated: GeneratedShortcuts = input_data["generated"]
        output_dir = Path(input_data.get("output_dir", "."))

        # Generate all outputs
        generated_files = self.generator.generate_all(generated, output_dir)

        return (
            {
                "generated": generated,
                "output_files": generated_files,
                "output_dir": str(output_dir),
            },
            0,
            0,
        )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _features_to_yaml(self, manifest: FeatureManifest) -> str:
        """Convert features to YAML for LLM prompts."""
        features_list = []
        for feature in manifest.all_features():
            features_list.append(
                {
                    "id": feature.id,
                    "name": feature.name,
                    "description": feature.description,
                    "frequency": feature.frequency.value,
                    "context": feature.context,
                },
            )
        return yaml.dump({"features": features_list}, default_flow_style=False)

    def _parse_yaml_response(self, response: str) -> dict[str, Any] | None:
        """Parse YAML from LLM response."""
        try:
            # Try to extract YAML from code blocks
            if "```yaml" in response:
                yaml_content = response.split("```yaml")[1].split("```")[0]
            elif "```" in response:
                yaml_content = response.split("```")[1].split("```")[0]
            else:
                yaml_content = response

            result = yaml.safe_load(yaml_content.strip())
            if isinstance(result, dict):
                return result
            return None
        except Exception:
            return None

    def _parse_json_response(self, response: str) -> dict[str, Any] | None:
        """Parse JSON from LLM response."""
        try:
            # Try to extract JSON from code blocks
            if "```json" in response:
                json_content = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_content = response.split("```")[1].split("```")[0]
            else:
                json_content = response

            result = json.loads(json_content.strip())
            if isinstance(result, dict):
                return result
            return None
        except Exception:
            return None

    def _update_manifest_from_analysis(
        self,
        manifest: FeatureManifest,
        analysis: dict,
    ) -> None:
        """Update manifest features with analysis results."""
        analyzed = {f["id"]: f for f in analysis.get("analyzed_features", [])}

        for feature in manifest.all_features():
            if feature.id in analyzed:
                af = analyzed[feature.id]
                freq_str = af.get("frequency", "frequent")
                if freq_str in FrequencyTier._value2member_map_:
                    feature.frequency = FrequencyTier(freq_str)

    def _build_generated_shortcuts(
        self,
        manifest: FeatureManifest,
        shortcuts_data: dict | None,
    ) -> GeneratedShortcuts:
        """Build GeneratedShortcuts from LLM response."""
        generated = GeneratedShortcuts(manifest=manifest)

        if not shortcuts_data:
            # Fallback: generate basic shortcuts
            generated = self._generate_fallback_shortcuts(manifest)
            return generated

        # Process each layout
        for layout_str in ["qwerty", "dvorak", "colemak"]:
            if layout_str not in shortcuts_data:
                continue

            layout = KeyboardLayout(layout_str)
            layout_data = shortcuts_data[layout_str]

            shortcuts = []
            for s in layout_data.get("shortcuts", []):
                shortcuts.append(
                    ShortcutAssignment(
                        feature_id=s["feature_id"],
                        key=s["key"],
                        mnemonic=s.get("mnemonic", f"{s['key'].upper()} = {s['feature_id']}"),
                        layout=layout,
                    ),
                )

            scales = layout_data.get("scale_assignments", {})
            scale_assignments = ScaleAssignments(
                daily=scales.get("daily", []),
                frequent=scales.get("frequent", []),
                advanced=scales.get("advanced", []),
            )

            generated.layouts[layout] = LayoutShortcuts(
                layout=layout,
                shortcuts=shortcuts,
                scale_assignments=scale_assignments,
                phrase_mnemonic=layout_data.get("phrase_mnemonic", ""),
            )

        return generated

    def _generate_fallback_shortcuts(self, manifest: FeatureManifest) -> GeneratedShortcuts:
        """Generate basic shortcuts without LLM."""
        generated = GeneratedShortcuts(manifest=manifest)
        features = manifest.all_features()

        # Simple assignment: use first letter of feature ID
        used_keys: set[str] = set()
        shortcuts = []

        for feature in features:
            # Try first letter
            key = feature.id[0].lower()
            if key in used_keys:
                # Find next available letter
                for c in feature.id.lower():
                    if c.isalpha() and c not in used_keys:
                        key = c
                        break
                else:
                    # Use any available letter
                    for c in "abcdefghijklmnopqrstuvwxyz":
                        if c not in used_keys:
                            key = c
                            break

            used_keys.add(key)
            shortcuts.append(
                ShortcutAssignment(
                    feature_id=feature.id,
                    key=key,
                    mnemonic=f"{key.upper()} = {feature.name}",
                ),
            )

        # Assign to QWERTY layout
        generated.layouts[KeyboardLayout.QWERTY] = LayoutShortcuts(
            layout=KeyboardLayout.QWERTY,
            shortcuts=shortcuts,
            phrase_mnemonic="First letter of each command",
        )

        return generated

    async def _invoke_llm(
        self,
        prompt: str,
        tier: ModelTier,
        system: str = "",
    ) -> tuple[str, int, int]:
        """Call LLM with the given prompt.

        Uses the inherited _call_llm method from BaseWorkflow
        which handles provider selection and telemetry.
        """
        # Use inherited _call_llm from BaseWorkflow
        return await self._call_llm(
            tier=tier,
            system=system,
            user_message=prompt,
            max_tokens=4096,
        )
