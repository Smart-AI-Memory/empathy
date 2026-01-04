"""Software Development Wizards

Production-ready wizards for software development with memory enhancement.

Memory-Enhanced Wizards (Level 4+):
- MemoryEnhancedDebuggingWizard: Bug correlation with historical patterns
- TechDebtWizard: Tech debt trajectory tracking and prediction
- SecurityLearningWizard: Security scanning with false positive learning

Utility Wizards:
- PatternRetrieverWizard: Pattern search and retrieval (Level 3)
- PatternExtractionWizard: Auto-detect fixes and suggest patterns (Level 3)
- CodeReviewWizard: Pattern-based code review (Level 4)

Core Wizards:
- SecurityAnalysisWizard: OWASP vulnerability detection
- AdvancedDebuggingWizard: Protocol-based debugging
- PerformanceProfilingWizard: Performance analysis
- TestingWizard: Test coverage and quality
- AIDocumentationWizard: Documentation generation

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .base_wizard import BaseWizard
from .code_review_wizard import CodeReviewWizard
from .memory_enhanced_debugging_wizard import MemoryEnhancedDebuggingWizard
from .pattern_extraction_wizard import PatternExtractionWizard
from .pattern_retriever_wizard import PatternRetrieverWizard
from .security_learning_wizard import SecurityLearningWizard
from .tech_debt_wizard import TechDebtWizard

__all__ = [
    "BaseWizard",
    "CodeReviewWizard",
    "MemoryEnhancedDebuggingWizard",
    "PatternExtractionWizard",
    "PatternRetrieverWizard",
    "SecurityLearningWizard",
    "TechDebtWizard",
]
