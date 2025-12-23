"""
Prompt Engineering Wizard

Helps developers craft better prompts for any AI task.
Can also optimize prompts used internally by other wizards.

Features:
1. Role & Context Setting - Define AI persona and background
2. Few-Shot Examples - Generate effective examples
3. Output Constraints - Format, length, structure
4. Token Optimization - Reduce costs while maintaining quality
5. Chain-of-Thought - Scaffolding for complex reasoning

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .base_wizard import BaseCoachWizard, WizardIssue, WizardPrediction


@dataclass
class PromptAnalysis:
    """Analysis of a prompt's quality and effectiveness."""

    overall_score: float  # 0.0 - 1.0
    clarity_score: float
    specificity_score: float
    structure_score: float
    token_count: int
    estimated_cost: float

    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    has_role: bool = False
    has_context: bool = False
    has_examples: bool = False
    has_constraints: bool = False
    has_output_format: bool = False


@dataclass
class OptimizedPrompt:
    """Result of prompt optimization."""

    original_prompt: str
    optimized_prompt: str
    original_tokens: int
    optimized_tokens: int
    token_reduction: float
    quality_preserved: bool
    changes_made: list[str] = field(default_factory=list)


class PromptEngineeringWizard(BaseCoachWizard):
    """
    Wizard for crafting and optimizing prompts.

    Provides tools for:
    - Analyzing existing prompts for improvements
    - Generating optimized prompts for tasks
    - Adding few-shot examples
    - Token optimization
    - Chain-of-thought scaffolding
    """

    # Keywords that indicate good prompt structure
    ROLE_INDICATORS = [
        "you are",
        "act as",
        "role:",
        "persona:",
        "as a",
        "expert",
        "specialist",
    ]

    CONTEXT_INDICATORS = [
        "context:",
        "background:",
        "situation:",
        "given that",
        "considering",
    ]

    EXAMPLE_INDICATORS = [
        "example:",
        "for example",
        "e.g.",
        "such as",
        "here is an example",
        "input:",
        "output:",
    ]

    CONSTRAINT_INDICATORS = [
        "must",
        "should",
        "don't",
        "do not",
        "avoid",
        "ensure",
        "never",
        "always",
        "constraint:",
        "rule:",
    ]

    OUTPUT_INDICATORS = [
        "format:",
        "output:",
        "respond in",
        "return as",
        "json",
        "markdown",
        "structured",
        "format your response",
    ]

    # Token estimation (rough approximation)
    CHARS_PER_TOKEN = 4

    def __init__(self):
        super().__init__(
            name="prompt-engineering",
            category="prompt_optimization",
            languages=["natural_language"],
        )
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None and self._api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                pass
        return self._client

    def analyze_code(self, code: str, file_path: str, language: str) -> list[WizardIssue]:
        """Analyze a prompt (passed as 'code') for issues."""
        return self._analyze_prompt_issues(code, file_path)

    def _analyze_prompt_issues(self, prompt: str, source: str = "") -> list[WizardIssue]:
        """Convert prompt analysis to WizardIssues."""
        analysis = self.analyze_prompt(prompt)
        issues = []

        if analysis.overall_score < 0.5:
            issues.append(
                WizardIssue(
                    severity="error",
                    message="Prompt has significant quality issues",
                    file_path=source,
                    line_number=None,
                    code_snippet=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                    fix_suggestion="Consider restructuring with role, context, and output format",
                    category="prompt_quality",
                    confidence=0.9,
                )
            )

        if not analysis.has_role:
            issues.append(
                WizardIssue(
                    severity="warning",
                    message="Prompt lacks a clear role definition",
                    file_path=source,
                    line_number=None,
                    code_snippet=None,
                    fix_suggestion="Add 'You are a...' or 'Act as a...' at the start",
                    category="prompt_structure",
                    confidence=0.8,
                )
            )

        if not analysis.has_output_format:
            issues.append(
                WizardIssue(
                    severity="warning",
                    message="Prompt doesn't specify output format",
                    file_path=source,
                    line_number=None,
                    code_snippet=None,
                    fix_suggestion="Add output format specification (JSON, markdown, etc.)",
                    category="prompt_structure",
                    confidence=0.7,
                )
            )

        for suggestion in analysis.suggestions:
            issues.append(
                WizardIssue(
                    severity="info",
                    message=suggestion,
                    file_path=source,
                    line_number=None,
                    code_snippet=None,
                    fix_suggestion=None,
                    category="prompt_improvement",
                    confidence=0.6,
                )
            )

        return issues

    def predict_future_issues(
        self,
        code: str,
        file_path: str,
        project_context: dict[str, Any],
        timeline_days: int = 90,
    ) -> list[WizardPrediction]:
        """Predict future prompt-related issues."""
        predictions = []
        analysis = self.analyze_prompt(code)

        # Predict maintenance issues for unclear prompts
        if analysis.clarity_score < 0.5:
            predictions.append(
                WizardPrediction(
                    predicted_date=datetime.now() + timedelta(days=30),
                    issue_type="prompt_drift",
                    probability=0.7,
                    impact="medium",
                    prevention_steps=[
                        "Document the prompt's purpose",
                        "Add version comments",
                        "Create test cases for expected outputs",
                    ],
                    reasoning="Low clarity prompts tend to drift from intended behavior over time",
                )
            )

        # Predict cost issues for verbose prompts
        if analysis.token_count > 1000:
            predictions.append(
                WizardPrediction(
                    predicted_date=datetime.now() + timedelta(days=14),
                    issue_type="cost_escalation",
                    probability=0.8,
                    impact="high",
                    prevention_steps=[
                        "Optimize prompt tokens",
                        "Use cheaper models for routing",
                        "Cache common responses",
                    ],
                    reasoning=f"Prompt uses {analysis.token_count} tokens - costs will escalate with scale",
                )
            )

        return predictions

    def suggest_fixes(self, issue: WizardIssue) -> str:
        """Suggest how to fix a prompt issue."""
        if issue.category == "prompt_quality":
            return """To improve overall prompt quality:

1. Start with a clear role:
   "You are an expert software engineer specializing in..."

2. Add relevant context:
   "Context: The user is working on a Python web application..."

3. Specify the output format:
   "Respond in JSON format with the following fields: ..."

4. Include constraints:
   "Important: Focus only on security-related issues. Do not suggest style changes."
"""

        elif issue.category == "prompt_structure":
            if "role" in issue.message.lower():
                return """Add a role definition at the start of your prompt:

Examples:
- "You are a senior code reviewer with expertise in Python best practices."
- "Act as a security auditor analyzing this code for vulnerabilities."
- "As an experienced technical writer, help document this API."
"""

            elif "output" in issue.message.lower():
                return """Specify the output format clearly:

Examples:
- "Respond in JSON format: {\"issues\": [], \"suggestions\": []}"
- "Format your response as a markdown checklist."
- "Return a numbered list of actionable recommendations."
"""

        return issue.fix_suggestion or "Review and improve the prompt structure."

    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """
        Analyze an existing prompt for improvements.

        Args:
            prompt: The prompt to analyze

        Returns:
            PromptAnalysis with scores and suggestions
        """
        prompt_lower = prompt.lower()
        token_count = len(prompt) // self.CHARS_PER_TOKEN

        # Check for structural elements
        has_role = any(ind in prompt_lower for ind in self.ROLE_INDICATORS)
        has_context = any(ind in prompt_lower for ind in self.CONTEXT_INDICATORS)
        has_examples = any(ind in prompt_lower for ind in self.EXAMPLE_INDICATORS)
        has_constraints = any(ind in prompt_lower for ind in self.CONSTRAINT_INDICATORS)
        has_output_format = any(ind in prompt_lower for ind in self.OUTPUT_INDICATORS)

        # Calculate scores
        clarity_score = self._calculate_clarity(prompt)
        specificity_score = self._calculate_specificity(prompt)
        structure_score = (
            sum([has_role, has_context, has_examples, has_constraints, has_output_format]) / 5
        )

        # Overall score
        overall_score = (clarity_score + specificity_score + structure_score) / 3

        # Generate issues and suggestions
        issues = []
        suggestions = []

        if not has_role:
            issues.append("Missing role definition")
            suggestions.append("Add 'You are a...' to define the AI's role")

        if not has_context and len(prompt) > 100:
            issues.append("Missing context section")
            suggestions.append("Add background context for better results")

        if not has_output_format:
            issues.append("No output format specified")
            suggestions.append("Specify the desired response format")

        if token_count > 500 and not has_examples:
            suggestions.append("Consider adding examples for clearer expectations")

        if clarity_score < 0.5:
            issues.append("Prompt clarity is low")
            suggestions.append("Use shorter sentences and clearer instructions")

        # Estimate cost (using Claude pricing approximation)
        estimated_cost = (token_count / 1_000_000) * 3.0  # ~$3/MTok for Sonnet

        return PromptAnalysis(
            overall_score=overall_score,
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            structure_score=structure_score,
            token_count=token_count,
            estimated_cost=estimated_cost,
            issues=issues,
            suggestions=suggestions,
            has_role=has_role,
            has_context=has_context,
            has_examples=has_examples,
            has_constraints=has_constraints,
            has_output_format=has_output_format,
        )

    def _calculate_clarity(self, prompt: str) -> float:
        """Calculate clarity score based on sentence structure."""
        sentences = re.split(r"[.!?]+", prompt)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.5

        # Average sentence length (shorter is clearer)
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # Optimal is 10-20 words per sentence
        if 10 <= avg_length <= 20:
            length_score = 1.0
        elif avg_length < 5 or avg_length > 40:
            length_score = 0.3
        else:
            length_score = 0.7

        # Check for clear instruction verbs
        instruction_verbs = [
            "analyze",
            "review",
            "generate",
            "create",
            "explain",
            "describe",
            "list",
            "identify",
            "compare",
            "summarize",
        ]
        has_verbs = any(v in prompt.lower() for v in instruction_verbs)
        verb_score = 1.0 if has_verbs else 0.5

        return (length_score + verb_score) / 2

    def _calculate_specificity(self, prompt: str) -> float:
        """Calculate how specific the prompt is."""
        # Check for specific terms
        specific_indicators = [
            r"\d+",  # Numbers
            r"\b(python|javascript|typescript|java|go|rust)\b",  # Languages
            r"\b(json|xml|yaml|csv|markdown)\b",  # Formats
            r"\b(api|function|class|method|variable)\b",  # Code terms
        ]

        specificity = 0.0
        for pattern in specific_indicators:
            if re.search(pattern, prompt.lower()):
                specificity += 0.25

        return min(specificity, 1.0)

    def generate_prompt(
        self,
        task: str,
        role: str | None = None,
        context: str | None = None,
        output_format: str | None = None,
        constraints: list[str] | None = None,
        examples: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Generate an optimized prompt for a task.

        Args:
            task: The main task to accomplish
            role: Optional role definition
            context: Optional context/background
            output_format: Desired output format
            constraints: List of constraints/rules
            examples: List of input/output examples

        Returns:
            Generated prompt string
        """
        parts = []

        # Role definition
        if role:
            parts.append(f"You are {role}.")
        else:
            parts.append("You are a helpful AI assistant.")

        # Context
        if context:
            parts.append(f"\n## Context\n{context}")

        # Main task
        parts.append(f"\n## Task\n{task}")

        # Constraints
        if constraints:
            parts.append("\n## Constraints")
            for c in constraints:
                parts.append(f"- {c}")

        # Examples
        if examples:
            parts.append("\n## Examples")
            for i, ex in enumerate(examples, 1):
                parts.append(f"\nExample {i}:")
                if "input" in ex:
                    parts.append(f"Input: {ex['input']}")
                if "output" in ex:
                    parts.append(f"Output: {ex['output']}")

        # Output format
        if output_format:
            parts.append(f"\n## Output Format\n{output_format}")

        return "\n".join(parts)

    def add_few_shot_examples(
        self,
        prompt: str,
        examples: list[dict[str, str]],
        position: str = "end",
    ) -> str:
        """
        Add few-shot examples to a prompt.

        Args:
            prompt: Original prompt
            examples: List of input/output example dicts
            position: Where to add examples ("start", "end", "after_context")

        Returns:
            Prompt with examples added
        """
        example_section = "\n## Examples\n"
        for i, ex in enumerate(examples, 1):
            example_section += f"\n### Example {i}\n"
            if "input" in ex:
                example_section += f"Input: {ex['input']}\n"
            if "output" in ex:
                example_section += f"Output: {ex['output']}\n"

        if position == "start":
            return example_section + "\n" + prompt
        elif position == "after_context" and "Context" in prompt:
            # Insert after context section
            parts = prompt.split("## Task")
            if len(parts) == 2:
                return parts[0] + example_section + "## Task" + parts[1]
        # Default: end
        return prompt + "\n" + example_section

    def optimize_tokens(
        self,
        prompt: str,
        target_reduction: float = 0.2,
    ) -> OptimizedPrompt:
        """
        Reduce token count while preserving intent.

        Args:
            prompt: Original prompt
            target_reduction: Target reduction percentage (0.0 - 1.0)

        Returns:
            OptimizedPrompt with original and optimized versions
        """
        original_tokens = len(prompt) // self.CHARS_PER_TOKEN
        changes = []

        optimized = prompt

        # Remove redundant whitespace
        optimized = re.sub(r"\n\n\n+", "\n\n", optimized)
        optimized = re.sub(r"  +", " ", optimized)
        if optimized != prompt:
            changes.append("Removed redundant whitespace")

        # Shorten common phrases
        shortenings = {
            "in order to": "to",
            "for the purpose of": "for",
            "in the event that": "if",
            "with respect to": "regarding",
            "prior to": "before",
            "subsequent to": "after",
            "in addition to": "also",
            "as a result of": "due to",
            "at this point in time": "now",
            "it is important to note that": "note:",
        }

        for long, short in shortenings.items():
            if long in optimized.lower():
                optimized = re.sub(re.escape(long), short, optimized, flags=re.IGNORECASE)
                changes.append(f"Shortened '{long}' to '{short}'")

        # Remove filler words
        fillers = ["basically", "essentially", "actually", "literally", "really", "just"]
        for filler in fillers:
            pattern = rf"\b{filler}\b\s*"
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, "", optimized, flags=re.IGNORECASE)
                changes.append(f"Removed filler word '{filler}'")

        optimized_tokens = len(optimized) // self.CHARS_PER_TOKEN
        reduction = (
            (original_tokens - optimized_tokens) / original_tokens if original_tokens > 0 else 0
        )

        return OptimizedPrompt(
            original_prompt=prompt,
            optimized_prompt=optimized.strip(),
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            token_reduction=reduction,
            quality_preserved=True,  # Basic optimization preserves quality
            changes_made=changes,
        )

    def add_chain_of_thought(
        self,
        prompt: str,
        reasoning_type: str = "step_by_step",
    ) -> str:
        """
        Add Chain-of-Thought scaffolding for complex reasoning.

        Args:
            prompt: Original prompt
            reasoning_type: Type of reasoning scaffold
                - "step_by_step": General step-by-step reasoning
                - "pros_cons": Evaluate options
                - "debug": Debugging thought process
                - "analysis": Analytical breakdown

        Returns:
            Prompt with CoT scaffolding
        """
        cot_scaffolds = {
            "step_by_step": """
Before providing your final answer, think through the problem step by step:

1. First, understand what is being asked
2. Identify the key components and constraints
3. Consider each requirement systematically
4. Formulate your approach
5. Execute and verify each step
6. Provide your final answer

Show your reasoning process clearly.""",
            "pros_cons": """
Analyze the options by considering:

For each option:
- List the advantages (pros)
- List the disadvantages (cons)
- Consider edge cases
- Evaluate trade-offs

Then make your recommendation based on the analysis.""",
            "debug": """
Follow this debugging process:

1. What is the expected behavior?
2. What is the actual behavior?
3. What are the possible causes?
4. How can we verify each hypothesis?
5. What is the root cause?
6. What is the fix?

Work through each step methodically.""",
            "analysis": """
Perform a structured analysis:

1. Define the scope and boundaries
2. Identify key components
3. Analyze relationships and dependencies
4. Evaluate current state
5. Identify patterns or anomalies
6. Draw conclusions
7. Make recommendations

Present your findings systematically.""",
        }

        scaffold = cot_scaffolds.get(reasoning_type, cot_scaffolds["step_by_step"])

        # Insert before the task or at the end
        if "## Task" in prompt:
            parts = prompt.split("## Task")
            return parts[0] + "\n## Reasoning Process" + scaffold + "\n\n## Task" + parts[1]
        else:
            return prompt + "\n\n## Reasoning Process" + scaffold
