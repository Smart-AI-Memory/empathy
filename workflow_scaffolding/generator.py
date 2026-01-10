"""Workflow code generator.

Generates workflow code from patterns and templates.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from empathy_os.workflow_patterns import get_workflow_pattern_registry


class WorkflowGenerator:
    """Generates workflow code from patterns."""

    def __init__(self, templates_dir: Path | None = None):
        """Initialize generator.

        Args:
            templates_dir: Path to templates directory

        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.registry = get_workflow_pattern_registry()

    def _workflow_name_to_class_name(self, workflow_name: str) -> str:
        """Convert workflow-name to WorkflowName class name.

        Args:
            workflow_name: Workflow name (e.g., "bug-scanner")

        Returns:
            Class name (e.g., "BugScannerWorkflow")

        """
        parts = workflow_name.replace("-", "_").replace("_", " ").split()
        return "".join(p.capitalize() for p in parts) + "Workflow"

    def _workflow_name_to_file_name(self, workflow_name: str) -> str:
        """Convert workflow-name to file_name.

        Args:
            workflow_name: Workflow name (e.g., "bug-scanner")

        Returns:
            File name (e.g., "bug_scanner")

        """
        return workflow_name.replace("-", "_")

    def _merge_code_sections(self, sections_by_location: dict) -> dict[str, str]:
        """Merge code sections into single strings per location.

        Args:
            sections_by_location: Dict mapping location to list of CodeSection

        Returns:
            Dict mapping location to merged code string

        """
        merged = {}

        for location, sections in sections_by_location.items():
            # Sort by priority (highest first)
            sections = sorted(sections, key=lambda s: -s.priority)

            # Merge code
            code_parts = [s.code for s in sections]
            merged[location] = "\n\n".join(code_parts)

        return merged

    def generate_workflow(
        self,
        workflow_name: str,
        description: str,
        patterns: list[str],
        stages: list[str] | None = None,
        tier_map: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, str]:
        """Generate workflow code.

        Args:
            workflow_name: Workflow name (e.g., "bug-scanner")
            description: Workflow description
            patterns: List of pattern IDs to use
            stages: List of stage names (auto-generated if None)
            tier_map: Mapping of stage to tier (auto-generated if None)
            **kwargs: Additional context for code generation

        Returns:
            Dict with generated files:
                - "workflow": Main workflow file content
                - "test": Test file content
                - "readme": README content

        """
        # Validate patterns
        valid, error = self.registry.validate_pattern_combination(patterns)
        if not valid:
            raise ValueError(f"Invalid pattern combination: {error}")

        # Auto-generate stages if not provided
        if stages is None:
            if "single-stage" in patterns:
                stages = ["process"]
            elif "multi-stage" in patterns:
                stages = ["analyze", "process", "report"]
            elif "crew-based" in patterns:
                stages = ["diagnose", "fix"]
            else:
                stages = ["execute"]

        # Auto-generate tier map if not provided
        if tier_map is None:
            if len(stages) == 1:
                tier_map = {stages[0]: "CAPABLE"}
            elif len(stages) == 2:
                tier_map = {stages[0]: "CHEAP", stages[1]: "CAPABLE"}
            else:
                tier_map = {
                    stages[0]: "CHEAP",
                    **dict.fromkeys(stages[1:-1], "CAPABLE"),
                    stages[-1]: "PREMIUM",
                }

        # Generate class and file names
        class_name = self._workflow_name_to_class_name(workflow_name)
        workflow_file = self._workflow_name_to_file_name(workflow_name)

        # Build context
        context = {
            "workflow_name": workflow_name,
            "class_name": class_name,
            "workflow_file": workflow_file,
            "description": description,
            "stages": stages,
            "tier_map": tier_map,
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "complexity": self._determine_complexity(patterns),
            "patterns": [self.registry.get(p) for p in patterns if self.registry.get(p)],
            # Pattern flags
            "has_conditional_tier": "conditional-tier" in patterns,
            "has_config_driven": "config-driven" in patterns,
            "has_crew_based": "crew-based" in patterns,
            "has_result_dataclass": "result-dataclass" in patterns,
            "has_code_scanner": "code-scanner" in patterns,
            "has_imports": False,
            "has_step_config": False,
            **kwargs,
        }

        # Generate code sections from patterns
        sections_by_location = self.registry.generate_code_sections(patterns, context)
        merged_sections = self._merge_code_sections(sections_by_location)

        # Update context with merged sections
        context.update(
            {
                "imports": merged_sections.get("imports", ""),
                "helper_functions": merged_sections.get("helper_functions", ""),
                "dataclasses": merged_sections.get("dataclasses", ""),
                "class_attributes": merged_sections.get("class_attributes", ""),
                "init_method": merged_sections.get("init_method", ""),
                "methods": merged_sections.get("methods", ""),
            }
        )

        # Update flags
        context["has_imports"] = bool(context["imports"])
        context["has_step_config"] = "WorkflowStepConfig" in str(merged_sections)

        # Generate files
        workflow_template = self.env.get_template("workflow.py.j2")
        test_template = self.env.get_template("test.py.j2")
        readme_template = self.env.get_template("README.md.j2")

        return {
            "workflow": workflow_template.render(**context),
            "test": test_template.render(**context),
            "readme": readme_template.render(**context),
        }

    def _determine_complexity(self, patterns: list[str]) -> str:
        """Determine overall workflow complexity.

        Args:
            patterns: List of pattern IDs

        Returns:
            Complexity level string

        """
        if "crew-based" in patterns or "multi-stage" in patterns:
            return "COMPLEX"
        if "conditional-tier" in patterns or "config-driven" in patterns:
            return "MODERATE"
        return "SIMPLE"

    def write_workflow(
        self,
        output_dir: Path,
        workflow_name: str,
        description: str,
        patterns: list[str],
        **kwargs: Any,
    ) -> dict[str, Path]:
        """Generate and write workflow files.

        Args:
            output_dir: Base output directory
            workflow_name: Workflow name
            description: Workflow description
            patterns: List of pattern IDs
            **kwargs: Additional generation parameters

        Returns:
            Dict mapping file type to written path

        """
        # Generate code
        generated = self.generate_workflow(
            workflow_name,
            description,
            patterns,
            **kwargs,
        )

        # Determine file paths
        workflow_file = self._workflow_name_to_file_name(workflow_name)

        workflow_dir = output_dir / "src" / "empathy_os" / "workflows"
        test_dir = output_dir / "tests" / "unit" / "workflows"

        workflow_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)

        workflow_path = workflow_dir / f"{workflow_file}.py"
        test_path = test_dir / f"test_{workflow_file}.py"
        readme_path = workflow_dir / f"{workflow_file}_README.md"

        # Write files
        workflow_path.write_text(generated["workflow"])
        test_path.write_text(generated["test"])
        readme_path.write_text(generated["readme"])

        return {
            "workflow": workflow_path,
            "test": test_path,
            "readme": readme_path,
        }
