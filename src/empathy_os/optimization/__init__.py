"""Context window optimization for XML-enhanced prompts.

Provides compression and optimization to reduce token usage by 20-30%.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_os.optimization.context_optimizer import (
                                                       CompressionLevel,
                                                       ContextOptimizer,
                                                       optimize_xml_prompt,
)

__all__ = [
    "CompressionLevel",
    "ContextOptimizer",
    "optimize_xml_prompt",
]
