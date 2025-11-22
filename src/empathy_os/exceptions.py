"""
Custom exceptions for the Empathy Framework

Provides domain-specific exceptions for better error handling and debugging.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""


class EmpathyFrameworkError(Exception):
    """
    Base exception for all Empathy Framework errors

    All custom exceptions in the framework inherit from this class,
    making it easy to catch any framework-specific error.
    """

    pass


class ValidationError(EmpathyFrameworkError):
    """
    Raised when input validation fails

    Examples:
        - Empty strings when non-empty required
        - Wrong type provided
        - Invalid value ranges
    """

    pass


class PatternNotFoundError(EmpathyFrameworkError):
    """
    Raised when a pattern lookup fails

    Examples:
        - Pattern ID doesn't exist in library
        - No patterns match query criteria
    """

    def __init__(self, pattern_id: str, message: str = None):
        self.pattern_id = pattern_id
        if message is None:
            message = f"Pattern not found: {pattern_id}"
        super().__init__(message)


class TrustThresholdError(EmpathyFrameworkError):
    """
    Raised when trust level is insufficient for an operation

    Examples:
        - Trust too low for proactive actions
        - Erosion loop detected
    """

    def __init__(self, current_trust: float, required_trust: float, message: str = None):
        self.current_trust = current_trust
        self.required_trust = required_trust
        if message is None:
            message = f"Trust level {current_trust:.2f} is below required {required_trust:.2f}"
        super().__init__(message)


class ConfidenceThresholdError(EmpathyFrameworkError):
    """
    Raised when confidence is too low for proactive action

    Examples:
        - Pattern confidence below threshold
        - Prediction uncertainty too high
    """

    def __init__(self, confidence: float, threshold: float, message: str = None):
        self.confidence = confidence
        self.threshold = threshold
        if message is None:
            message = f"Confidence {confidence:.2f} is below threshold {threshold:.2f}"
        super().__init__(message)


class EmpathyLevelError(EmpathyFrameworkError):
    """
    Raised when empathy level operations fail

    Examples:
        - Invalid level number
        - Level not yet achieved
        - Cannot regress to lower level
    """

    def __init__(self, level: int, message: str = None):
        self.level = level
        if message is None:
            message = f"Invalid empathy level: {level}"
        super().__init__(message)


class LeveragePointError(EmpathyFrameworkError):
    """
    Raised when leverage point analysis fails

    Examples:
        - No leverage points found
        - Intervention feasibility too low
    """

    pass


class FeedbackLoopError(EmpathyFrameworkError):
    """
    Raised when feedback loop detection or management fails

    Examples:
        - Vicious cycle detected but cannot break
        - Insufficient history for loop detection
    """

    pass


class CollaborationStateError(EmpathyFrameworkError):
    """
    Raised when collaboration state operations fail

    Examples:
        - Invalid state transition
        - State corruption detected
    """

    pass
