"""You are an expert in the creating wide many types of documents. You use program libraries, systems, style guide, and industry best practices, to efficiently create and update documentation for the empathy-framework.

Stages:
1. process - Process

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
from pathlib import Path
from typing import Any

from empathy_os.workflows.base import BaseWorkflow, ModelTier

logger = logging.getLogger(__name__)


class DocumentManagerWorkflow(BaseWorkflow):
    """You are an expert in the creating wide many types of documents. You use program libraries, systems, style guide, and industry best practices, to efficiently create and update documentation for the empathy-framework.


    Usage:
        workflow = DocumentManagerWorkflow()
        result = await workflow.execute(
            # Add parameters here
        )
    """

    name = "document-manager"
    description = "You are an expert in the creating wide many types of documents. You use program libraries, systems, style guide, and industry best practices, to efficiently create and update documentation for the empathy-framework."
    stages = ["process"]
    tier_map = {
        "process": ModelTier.CAPABLE,
    }

    def __init__(
        self,
        **kwargs: Any,
    ):
        """Initialize document-manager workflow.

        Args:
            **kwargs: Additional arguments passed to BaseWorkflow

        """
        super().__init__(**kwargs)

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: Any,
    ) -> tuple[Any, int, int]:
        """Execute the single processing stage."""
        if stage_name == "process":
            return await self._process(input_data, tier)
        raise ValueError(f"Unknown stage: {stage_name}")

    async def _process(
        self,
        input_data: Any,
        tier: ModelTier,
    ) -> tuple[Any, int, int]:
        """Process the input data.

        Args:
            input_data: Input data to process
            tier: Model tier to use

        Returns:
            Tuple of (result, input_tokens, output_tokens)

        """
        # Extract path from input
        path = input_data.get("path", ".") if isinstance(input_data, dict) else "."
        target_path = Path(path).resolve()

        # Scan the codebase structure
        code_context = self._scan_codebase(target_path)

        system_prompt = """You are an expert technical writer specializing in API documentation.
You create clear, comprehensive documentation for Python frameworks and libraries.
DO NOT ask questions or request clarification - use the information provided to create
complete, professional documentation immediately."""

        user_prompt = f"""Create comprehensive API documentation for the Empathy Framework based on this codebase analysis.

**Project Path:** {target_path}

**Codebase Information:**
{code_context}

**Generate the following documentation sections:**

# Empathy Framework API Documentation

## Overview
[Analyze the project structure and write a clear overview of what the framework does]

## Installation
[Based on pyproject.toml, provide installation instructions]

## Quick Start
[Create a simple getting-started example]

## Architecture
[Describe the key modules and how they interact]

## Core Components
[Document the main classes, methods, and their purposes based on the module structure]

## Workflows
[Document available workflows and how to use them]

## Usage Examples
[Provide practical code examples]

## Configuration
[Explain configuration options if apparent from the code]

Write the documentation now in complete Markdown format. Be specific and technical."""

        # Call LLM using the workflow's built-in method
        response, input_tokens, output_tokens = await self._call_llm(
            tier=tier,
            system=system_prompt,
            user_message=user_prompt,
            max_tokens=4000,
        )

        return response, input_tokens, output_tokens

    def _scan_codebase(self, path: Path) -> str:
        """Scan the codebase and return a summary of the structure.

        Args:
            path: Path to scan

        Returns:
            String representation of the codebase structure

        """
        if not path.exists():
            return f"Path does not exist: {path}"

        if path.is_file():
            # If it's a single file, read it
            try:
                content = path.read_text()[:5000]  # First 5000 chars
                return f"File: {path.name}\n\n```\n{content}\n```"
            except Exception as e:
                return f"Error reading file: {e}"

        # If it's a directory, scan the structure
        structure = []
        try:
            # Read README if it exists
            readme_path = path / "README.md"
            if readme_path.exists():
                try:
                    readme_content = readme_path.read_text()[:3000]
                    structure.append("**README.md (excerpt):**\n```markdown")
                    structure.append(readme_content)
                    structure.append("```\n")
                except Exception:
                    pass

            # Read pyproject.toml if it exists
            pyproject_path = path / "pyproject.toml"
            if pyproject_path.exists():
                try:
                    pyproject_content = pyproject_path.read_text()[:2000]
                    structure.append("**pyproject.toml (excerpt):**\n```toml")
                    structure.append(pyproject_content)
                    structure.append("```\n")
                except Exception:
                    pass

            # Get Python files in src directory with sample content
            src_dir = path / "src"
            if src_dir.exists():
                py_files = list(src_dir.rglob("*.py"))[:10]  # Limit to 10 files
                structure.append("**Key Python Modules:**")
                for py_file in py_files:
                    rel_path = py_file.relative_to(path)
                    structure.append(f"\n- {rel_path}")
                    # Read docstring from file
                    try:
                        content = py_file.read_text()[:1000]
                        # Extract first docstring
                        if '"""' in content:
                            start = content.find('"""')
                            end = content.find('"""', start + 3)
                            if end != -1:
                                docstring = content[start + 3 : end].strip()
                                structure.append(f"  {docstring[:200]}")
                    except Exception:
                        pass

            # Get directory structure
            structure.append("\n**Directory Structure:**")
            for item in sorted(path.iterdir())[:15]:  # Limit to 15 items
                if item.name.startswith("."):
                    continue
                if item.is_dir():
                    structure.append(f"- {item.name}/ (directory)")
                else:
                    structure.append(f"- {item.name}")

            return "\n".join(structure)
        except Exception as e:
            return f"Error scanning directory: {e}"
