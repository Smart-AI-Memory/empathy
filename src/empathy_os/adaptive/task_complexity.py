"""Task complexity scoring for adaptive prompt selection.

Uses simple heuristics (token count, LOC) to classify tasks as
simple, moderate, complex, or very complex, enabling dynamic
model tier and compression level selection.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass
from enum import Enum

try:
    import tiktoken
except ImportError:
    tiktoken = None  # type: ignore[assignment]


class TaskComplexity(Enum):
    """Task complexity levels for adaptive prompting."""

    SIMPLE = "simple"  # <100 tokens, <50 LOC
    MODERATE = "moderate"  # 100-500 tokens, 50-200 LOC
    COMPLEX = "complex"  # 500-2000 tokens, 200-1000 LOC
    VERY_COMPLEX = "very_complex"  # >2000 tokens, >1000 LOC


@dataclass
class ComplexityScore:
    """Task complexity scoring result.

    Attributes:
        token_count: Estimated input tokens
        line_count: Lines of code in context
        file_count: Number of files involved
        complexity_level: Classified complexity
        confidence: Confidence in classification (0-1)
    """

    token_count: int
    line_count: int
    file_count: int
    complexity_level: TaskComplexity
    confidence: float


class TaskComplexityScorer:
    """Scores task complexity using simple heuristics.

    Uses token counting (via tiktoken if available) and line counting
    to estimate task complexity for adaptive prompt selection.

    Usage:
        scorer = TaskComplexityScorer()
        score = scorer.score_task(
            description="Refactor authentication module",
            context=source_code,
            files=["auth.py", "session.py"]
        )

        if score.complexity_level == TaskComplexity.VERY_COMPLEX:
            use_premium_model()
    """

    def __init__(self):
        """Initialize complexity scorer."""
        if tiktoken:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            self.tokenizer = None

    def score_task(
        self,
        description: str,
        context: str | None = None,
        files: list[str] | None = None,
    ) -> ComplexityScore:
        """Score task complexity.

        Args:
            description: Task description
            context: Optional context (code, docs, etc.)
            files: Optional list of file paths

        Returns:
            ComplexityScore with classification and metrics
        """
        # Count tokens
        if self.tokenizer:
            token_count = len(self.tokenizer.encode(description))
            if context:
                token_count += len(self.tokenizer.encode(context))
        else:
            # Fallback: rough estimate (4 chars per token)
            token_count = len(description) // 4
            if context:
                token_count += len(context) // 4

        # Count lines of code
        line_count = 0
        if context:
            line_count = len(context.split("\n"))

        # Count files
        file_count = len(files) if files else 0

        # Determine complexity level using thresholds
        if token_count < 100 and line_count < 50:
            complexity = TaskComplexity.SIMPLE
        elif token_count < 500 and line_count < 200:
            complexity = TaskComplexity.MODERATE
        elif token_count < 2000 and line_count < 1000:
            complexity = TaskComplexity.COMPLEX
        else:
            complexity = TaskComplexity.VERY_COMPLEX

        # Confidence is moderate for simple heuristics
        confidence = 0.8 if self.tokenizer else 0.6

        return ComplexityScore(
            token_count=token_count,
            line_count=line_count,
            file_count=file_count,
            complexity_level=complexity,
            confidence=confidence,
        )
