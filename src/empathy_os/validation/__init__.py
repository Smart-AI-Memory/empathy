"""XML validation for XML-enhanced prompts.

Provides schema validation and graceful fallbacks.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_os.validation.xml_validator import (
                                                 ValidationResult,
                                                 XMLValidator,
                                                 validate_xml_response,
)

__all__ = [
    "XMLValidator",
    "ValidationResult",
    "validate_xml_response",
]
