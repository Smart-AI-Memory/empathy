"""Input patterns for wizard data collection.

Input patterns define how wizards collect data from users:
- Structured Fields: Predefined fields with types
- Code Analysis: Code, file path, and language inputs
- Context-Based: Flexible dictionary-based input

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from .core import BasePattern, CodeGeneratorMixin, PatternCategory


class FieldDefinition(BaseModel):
    """Definition of a structured input field."""

    name: str = Field(..., description="Field name")
    field_type: str = Field(
        default="str",
        description="Python type (str, int, float, bool, list, dict)",
    )
    required: bool = Field(default=True, description="Whether field is required")
    description: str = Field(default="", description="Field description")
    default_value: Any = Field(default=None, description="Default value if not required")


class StructuredFieldsPattern(BasePattern, CodeGeneratorMixin):
    """Structured field input pattern.

    **Description:**
    Wizards that collect data through predefined, typed fields. Each step
    has a set of fields with validation rules.

    **Usage:** 16 wizards (SOAP Note, Care Plan, Admission Assessment)
    **Reusability:** 0.9

    **Key Features:**
    - Type-safe field definitions
    - Per-step field organization
    - Automatic validation
    - Pydantic request models

    **Example:**
    Step 1: chief_complaint, history_present_illness, pain_description
    Step 2: vital_signs, physical_exam_findings, lab_results
    """

    category: Literal[PatternCategory.INPUT] = PatternCategory.INPUT
    fields_by_step: dict[int, list[FieldDefinition]] = Field(
        ..., description="Fields organized by step number"
    )

    def generate_code(self) -> str:
        """Generate Pydantic request models for each step."""
        models = []

        for step_num, fields in sorted(self.fields_by_step.items()):
            model_name = f"Step{step_num}Request"
            field_defs = []

            for field in fields:
                field_line = f"    {field.name}: {field.field_type}"

                if not field.required:
                    field_line += f" = {repr(field.default_value)}"

                if field.description:
                    field_line += f"  # {field.description}"

                field_defs.append(field_line)

            model = f'''
class {model_name}(BaseModel):
    """Request model for step {step_num}"""
{chr(10).join(field_defs)}
'''
            models.append(model)

        return "\n".join(models)


class CodeAnalysisPattern(BasePattern):
    """Code analysis input pattern.

    **Description:**
    Wizards that analyze source code take three standard inputs:
    - code: Source code string
    - file_path: Path to the file being analyzed
    - language: Programming language

    **Usage:** 16 wizards (all coach wizards)
    **Reusability:** 0.9

    **Signature:**
    def analyze_code(
        self,
        code: str,
        file_path: str,
        language: str
    ) -> list[WizardIssue]
    """

    category: Literal[PatternCategory.INPUT] = PatternCategory.INPUT
    supported_languages: list[str] = Field(
        default_factory=lambda: [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
        ],
        description="Supported programming languages",
    )
    returns_issues: bool = Field(
        default=True,
        description="Whether this returns a list of issues",
    )


class ContextBasedPattern(BasePattern):
    """Context-based flexible input pattern.

    **Description:**
    Wizards that accept a flexible dictionary of context parameters,
    allowing for extensible input without rigid schemas.

    **Usage:** 12 wizards (AI wizards)
    **Reusability:** 0.8

    **Example Context:**
    {
        "project_path": ".",
        "linters": {"eslint": "output.json"},
        "configs": {"eslint": ".eslintrc.json"},
        "auto_fix": True,
        "verify": True,
    }

    **Signature:**
    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]
    """

    category: Literal[PatternCategory.INPUT] = PatternCategory.INPUT
    required_keys: list[str] = Field(
        default_factory=list,
        description="Required context keys",
    )
    optional_keys: list[str] = Field(
        default_factory=list,
        description="Optional context keys",
    )
    key_descriptions: dict[str, str] = Field(
        default_factory=dict,
        description="Descriptions of what each key means",
    )
