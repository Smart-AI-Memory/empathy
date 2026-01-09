"""Tests for Custom Exceptions

Tests all custom exception classes in the Empathy Framework.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_os.exceptions import (
    CollaborationStateError,
    ConfidenceThresholdError,
    EmpathyFrameworkError,
    EmpathyLevelError,
    FeedbackLoopError,
    LeveragePointError,
    PatternNotFoundError,
    TrustThresholdError,
    ValidationError,
)


class TestBaseException:
    """Test base exception class"""

    def test_base_exception_can_be_raised(self):
        """Test EmpathyFrameworkError can be raised"""
        with pytest.raises(EmpathyFrameworkError):
            raise EmpathyFrameworkError("Test error")

    def test_base_exception_message(self):
        """Test error message is preserved"""
        message = "This is a test error"
        with pytest.raises(EmpathyFrameworkError, match=message):
            raise EmpathyFrameworkError(message)

    def test_base_exception_inheritance(self):
        """Test base exception inherits from Exception"""
        assert issubclass(EmpathyFrameworkError, Exception)

    def test_base_exception_without_message(self):
        """Test EmpathyFrameworkError can be raised without message"""
        with pytest.raises(EmpathyFrameworkError):
            raise EmpathyFrameworkError()


class TestValidationError:
    """Test validation error"""

    def test_validation_error_can_be_raised(self):
        """Test ValidationError can be raised"""
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")

    def test_validation_error_inherits_from_base(self):
        """Test ValidationError inherits from EmpathyFrameworkError"""
        assert issubclass(ValidationError, EmpathyFrameworkError)

    def test_validation_error_can_be_caught_as_base(self):
        """Test ValidationError can be caught as base exception"""
        with pytest.raises(EmpathyFrameworkError):
            raise ValidationError("Validation failed")

    def test_validation_error_message(self):
        """Test validation error with custom message"""
        message = "Invalid input: expected string, got int"
        with pytest.raises(ValidationError, match=message):
            raise ValidationError(message)

    def test_validation_error_without_message(self):
        """Test ValidationError can be raised without message"""
        with pytest.raises(ValidationError):
            raise ValidationError()


class TestPatternNotFoundError:
    """Test pattern not found error"""

    def test_pattern_not_found_with_pattern_id(self):
        """Test PatternNotFoundError with pattern ID"""
        pattern_id = "test_pattern_123"

        try:
            raise PatternNotFoundError(pattern_id)
        except PatternNotFoundError as e:
            assert e.pattern_id == pattern_id
            assert "Pattern not found" in str(e)
            assert pattern_id in str(e)

    def test_pattern_not_found_with_custom_message(self):
        """Test PatternNotFoundError with custom message"""
        pattern_id = "test_pattern"
        message = "Custom error message"

        try:
            raise PatternNotFoundError(pattern_id, message)
        except PatternNotFoundError as e:
            assert e.pattern_id == pattern_id
            assert str(e) == message

    def test_pattern_not_found_inherits_from_base(self):
        """Test PatternNotFoundError inherits from base"""
        assert issubclass(PatternNotFoundError, EmpathyFrameworkError)

    def test_pattern_not_found_stores_pattern_id(self):
        """Test pattern_id is stored as attribute"""
        pattern_id = "missing_pattern"
        error = PatternNotFoundError(pattern_id)
        assert hasattr(error, "pattern_id")
        assert error.pattern_id == pattern_id


class TestTrustThresholdError:
    """Test trust threshold error"""

    def test_trust_threshold_error_with_values(self):
        """Test TrustThresholdError stores trust values"""
        current = 0.5
        required = 0.8

        try:
            raise TrustThresholdError(current, required)
        except TrustThresholdError as e:
            assert e.current_trust == current
            assert e.required_trust == required
            assert "0.50" in str(e)
            assert "0.80" in str(e)

    def test_trust_threshold_error_with_custom_message(self):
        """Test TrustThresholdError with custom message"""
        message = "Trust erosion detected"

        try:
            raise TrustThresholdError(0.3, 0.7, message)
        except TrustThresholdError as e:
            assert str(e) == message
            assert e.current_trust == 0.3
            assert e.required_trust == 0.7

    def test_trust_threshold_error_inherits_from_base(self):
        """Test TrustThresholdError inherits from base"""
        assert issubclass(TrustThresholdError, EmpathyFrameworkError)

    def test_trust_threshold_error_formatting(self):
        """Test default message formatting"""
        error = TrustThresholdError(0.45, 0.75)
        message = str(error)
        assert "Trust level" in message
        assert "0.45" in message
        assert "0.75" in message
        assert "below required" in message

    def test_trust_threshold_edge_cases(self):
        """Test with edge case values"""
        error = TrustThresholdError(0.0, 1.0)
        assert error.current_trust == 0.0
        assert error.required_trust == 1.0


class TestConfidenceThresholdError:
    """Test confidence threshold error"""

    def test_confidence_threshold_error_with_values(self):
        """Test ConfidenceThresholdError stores confidence values"""
        confidence = 0.6
        threshold = 0.9

        try:
            raise ConfidenceThresholdError(confidence, threshold)
        except ConfidenceThresholdError as e:
            assert e.confidence == confidence
            assert e.threshold == threshold
            assert "0.60" in str(e)
            assert "0.90" in str(e)

    def test_confidence_threshold_error_with_custom_message(self):
        """Test ConfidenceThresholdError with custom message"""
        message = "Prediction uncertainty too high"

        try:
            raise ConfidenceThresholdError(0.5, 0.8, message)
        except ConfidenceThresholdError as e:
            assert str(e) == message
            assert e.confidence == 0.5
            assert e.threshold == 0.8

    def test_confidence_threshold_error_inherits_from_base(self):
        """Test ConfidenceThresholdError inherits from base"""
        assert issubclass(ConfidenceThresholdError, EmpathyFrameworkError)

    def test_confidence_threshold_error_formatting(self):
        """Test default message formatting"""
        error = ConfidenceThresholdError(0.55, 0.85)
        message = str(error)
        assert "Confidence" in message
        assert "0.55" in message
        assert "0.85" in message
        assert "below threshold" in message


class TestEmpathyLevelError:
    """Test empathy level error"""

    def test_empathy_level_error_with_level(self):
        """Test EmpathyLevelError stores level"""
        level = 7

        try:
            raise EmpathyLevelError(level)
        except EmpathyLevelError as e:
            assert e.level == level
            assert str(level) in str(e)
            assert "Invalid empathy level" in str(e)

    def test_empathy_level_error_with_custom_message(self):
        """Test EmpathyLevelError with custom message"""
        message = "Cannot regress to level 2"

        try:
            raise EmpathyLevelError(2, message)
        except EmpathyLevelError as e:
            assert str(e) == message
            assert e.level == 2

    def test_empathy_level_error_inherits_from_base(self):
        """Test EmpathyLevelError inherits from base"""
        assert issubclass(EmpathyLevelError, EmpathyFrameworkError)

    def test_empathy_level_error_with_negative_level(self):
        """Test with negative level"""
        error = EmpathyLevelError(-1)
        assert error.level == -1

    def test_empathy_level_error_with_zero_level(self):
        """Test with zero level"""
        error = EmpathyLevelError(0)
        assert error.level == 0


class TestLeveragePointError:
    """Test leverage point error"""

    def test_leverage_point_error_can_be_raised(self):
        """Test LeveragePointError can be raised"""
        with pytest.raises(LeveragePointError):
            raise LeveragePointError("No leverage points found")

    def test_leverage_point_error_inherits_from_base(self):
        """Test LeveragePointError inherits from base"""
        assert issubclass(LeveragePointError, EmpathyFrameworkError)

    def test_leverage_point_error_message(self):
        """Test error message"""
        message = "Intervention feasibility too low"
        with pytest.raises(LeveragePointError, match=message):
            raise LeveragePointError(message)

    def test_leverage_point_error_without_message(self):
        """Test LeveragePointError can be raised without message"""
        with pytest.raises(LeveragePointError):
            raise LeveragePointError()


class TestFeedbackLoopError:
    """Test feedback loop error"""

    def test_feedback_loop_error_can_be_raised(self):
        """Test FeedbackLoopError can be raised"""
        with pytest.raises(FeedbackLoopError):
            raise FeedbackLoopError("Vicious cycle detected")

    def test_feedback_loop_error_inherits_from_base(self):
        """Test FeedbackLoopError inherits from base"""
        assert issubclass(FeedbackLoopError, EmpathyFrameworkError)

    def test_feedback_loop_error_message(self):
        """Test error message"""
        message = "Insufficient history for loop detection"
        with pytest.raises(FeedbackLoopError, match=message):
            raise FeedbackLoopError(message)

    def test_feedback_loop_error_without_message(self):
        """Test FeedbackLoopError can be raised without message"""
        with pytest.raises(FeedbackLoopError):
            raise FeedbackLoopError()


class TestCollaborationStateError:
    """Test collaboration state error"""

    def test_collaboration_state_error_can_be_raised(self):
        """Test CollaborationStateError can be raised"""
        with pytest.raises(CollaborationStateError):
            raise CollaborationStateError("Invalid state transition")

    def test_collaboration_state_error_inherits_from_base(self):
        """Test CollaborationStateError inherits from base"""
        assert issubclass(CollaborationStateError, EmpathyFrameworkError)

    def test_collaboration_state_error_message(self):
        """Test error message"""
        message = "State corruption detected"
        with pytest.raises(CollaborationStateError, match=message):
            raise CollaborationStateError(message)

    def test_collaboration_state_error_without_message(self):
        """Test CollaborationStateError can be raised without message"""
        with pytest.raises(CollaborationStateError):
            raise CollaborationStateError()


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy"""

    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from EmpathyFrameworkError"""
        exceptions = [
            ValidationError,
            PatternNotFoundError,
            TrustThresholdError,
            ConfidenceThresholdError,
            EmpathyLevelError,
            LeveragePointError,
            FeedbackLoopError,
            CollaborationStateError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, EmpathyFrameworkError)

    def test_catch_all_framework_errors(self):
        """Test catching any framework error with base class"""
        errors_to_test = [
            ValidationError("test"),
            PatternNotFoundError("pattern"),
            TrustThresholdError(0.5, 0.8),
            ConfidenceThresholdError(0.6, 0.9),
            EmpathyLevelError(7),
            LeveragePointError("test"),
            FeedbackLoopError("test"),
            CollaborationStateError("test"),
        ]

        for error in errors_to_test:
            with pytest.raises(EmpathyFrameworkError):
                raise error


class TestExceptionUsagePatterns:
    """Test common usage patterns"""

    def test_exception_with_context(self):
        """Test raising exception with context"""
        try:
            pattern_id = "missing_pattern"
            raise PatternNotFoundError(pattern_id, f"Pattern {pattern_id} not in library")
        except PatternNotFoundError as e:
            assert e.pattern_id == pattern_id
            assert "not in library" in str(e)

    def test_exception_reraising(self):
        """Test catching and re-raising exceptions"""
        with pytest.raises(ValidationError):
            try:
                raise ValidationError("Original error")
            except EmpathyFrameworkError:
                raise ValidationError("Re-raised with new message") from None

    def test_multiple_exception_types(self):
        """Test handling multiple exception types"""

        def risky_operation(scenario: str):
            if scenario == "validation":
                raise ValidationError("Bad input")
            if scenario == "trust":
                raise TrustThresholdError(0.3, 0.7)
            if scenario == "pattern":
                raise PatternNotFoundError("test_pattern")

        # Test each scenario
        with pytest.raises(ValidationError):
            risky_operation("validation")

        with pytest.raises(TrustThresholdError):
            risky_operation("trust")

        with pytest.raises(PatternNotFoundError):
            risky_operation("pattern")

    def test_exception_chaining(self):
        """Test exception chaining with 'from' clause"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ValidationError("Validation failed") from e
        except ValidationError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)


class TestExceptionEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_string_messages(self):
        """Test exceptions with empty string messages"""
        with pytest.raises(ValidationError):
            raise ValidationError("")

    def test_none_pattern_id(self):
        """Test PatternNotFoundError with None in pattern_id"""
        # While not ideal, the code should handle it
        error = PatternNotFoundError(None)
        assert error.pattern_id is None
        assert "None" in str(error)

    def test_negative_trust_values(self):
        """Test TrustThresholdError with negative values"""
        error = TrustThresholdError(-0.5, 0.5)
        assert error.current_trust == -0.5
        assert error.required_trust == 0.5
        assert "-0.50" in str(error)

    def test_very_large_confidence_values(self):
        """Test ConfidenceThresholdError with values > 1.0"""
        error = ConfidenceThresholdError(0.95, 1.5)
        assert error.confidence == 0.95
        assert error.threshold == 1.5
        assert "0.95" in str(error)
        assert "1.50" in str(error)

    def test_very_large_empathy_level(self):
        """Test EmpathyLevelError with very large level"""
        error = EmpathyLevelError(999)
        assert error.level == 999
        assert "999" in str(error)

    def test_exception_str_representation(self):
        """Test string representation of exceptions"""
        error1 = ValidationError("test message")
        assert str(error1) == "test message"

        error2 = PatternNotFoundError("pattern_123")
        assert "pattern_123" in str(error2)

        error3 = TrustThresholdError(0.3, 0.7)
        assert "0.30" in str(error3)

    def test_exception_repr(self):
        """Test repr of exceptions"""
        error = ValidationError("test")
        repr_str = repr(error)
        assert "ValidationError" in repr_str

    def test_exception_args(self):
        """Test exception args tuple"""
        message = "test error message"
        error = ValidationError(message)
        assert error.args[0] == message

    def test_pattern_error_with_empty_message(self):
        """Test PatternNotFoundError with empty custom message"""
        error = PatternNotFoundError("pattern_id", "")
        assert error.pattern_id == "pattern_id"
        assert str(error) == ""

    def test_trust_error_with_equal_values(self):
        """Test TrustThresholdError when current equals required"""
        error = TrustThresholdError(0.5, 0.5)
        assert error.current_trust == 0.5
        assert error.required_trust == 0.5

    def test_confidence_error_with_zero_values(self):
        """Test ConfidenceThresholdError with zero values"""
        error = ConfidenceThresholdError(0.0, 0.0)
        assert error.confidence == 0.0
        assert error.threshold == 0.0
        assert "0.00" in str(error)

    def test_multiline_error_messages(self):
        """Test exceptions with multiline messages"""
        multiline_msg = "Error occurred:\nLine 1\nLine 2\nLine 3"
        error = ValidationError(multiline_msg)
        assert str(error) == multiline_msg
        assert "\n" in str(error)

    def test_unicode_in_error_messages(self):
        """Test exceptions with unicode characters"""
        unicode_msg = "Error: \u2713 check failed \u2717"
        error = ValidationError(unicode_msg)
        assert str(error) == unicode_msg

    def test_special_characters_in_pattern_id(self):
        """Test PatternNotFoundError with special characters in pattern_id"""
        pattern_id = "pattern-with-special_chars.123"
        error = PatternNotFoundError(pattern_id)
        assert error.pattern_id == pattern_id
        assert pattern_id in str(error)
