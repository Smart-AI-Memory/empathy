"""
Debugging Assistant - Level 3 Proactive Empathy Example

Demonstrates how to use the Empathy Framework to build an AI debugging
assistant that proactively helps developers debug code.

**Empathy Level**: Level 3 (Proactive)
- Detects common debugging patterns
- Offers help before being asked
- Suggests fixes based on error patterns
- Reduces debugging frustration

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from typing import Any, Dict, List

from empathy_os import (
    EmpathyOS,
    FeedbackLoopDetector,
    Level3Proactive,
    Pattern,
    PatternLibrary,
    TrustBuildingBehaviors,
)


class DebuggingAssistant:
    """
    AI debugging assistant using Level 3 Proactive Empathy

    Proactively detects debugging struggles and offers targeted help
    without waiting to be asked.
    """

    def __init__(self, developer_id: str):
        """Initialize debugging assistant"""
        self.developer_id = developer_id
        self.empathy = EmpathyOS(user_id=developer_id, target_level=3)
        self.level3 = Level3Proactive()
        self.trust_builder = TrustBuildingBehaviors()
        self.pattern_library = PatternLibrary()
        self.feedback_detector = FeedbackLoopDetector()

        # Load common debugging patterns
        self._initialize_debugging_patterns()

        # Track debugging session
        self.session_history: List[Dict[str, Any]] = []

    def _initialize_debugging_patterns(self):
        """Initialize common debugging patterns"""

        # Pattern 1: Repeated syntax errors
        pattern1 = Pattern(
            id="pat_syntax_errors",
            agent_id="debug_assistant",
            pattern_type="sequential",
            name="Repeated syntax errors pattern",
            description="Developer making repeated syntax errors suggests IDE/linter not configured",
            confidence=0.9,
            tags=["syntax", "tooling", "beginner"]
        )
        self.pattern_library.contribute_pattern("debug_assistant", pattern1)

        # Pattern 2: Import errors
        pattern2 = Pattern(
            id="pat_import_errors",
            agent_id="debug_assistant",
            pattern_type="conditional",
            name="Import/dependency errors",
            description="ImportError or ModuleNotFoundError suggests environment issue",
            confidence=0.95,
            tags=["imports", "dependencies", "environment"]
        )
        self.pattern_library.contribute_pattern("debug_assistant", pattern2)

        # Pattern 3: Logic errors with no print debugging
        pattern3 = Pattern(
            id="pat_blind_debugging",
            agent_id="debug_assistant",
            pattern_type="behavioral",
            name="Logic errors without debugging output",
            description="Developer struggling with logic but not using print/debugger",
            confidence=0.85,
            tags=["logic", "debugging_strategy", "intermediate"]
        )
        self.pattern_library.contribute_pattern("debug_assistant", pattern3)

    def observe_debugging_session(
        self,
        error_type: str,
        error_message: str,
        code_snippet: str,
        attempt_number: int,
        time_spent_minutes: int
    ) -> dict:
        """
        Observe a debugging attempt and proactively offer help

        Args:
            error_type: Type of error (e.g., "SyntaxError", "ImportError")
            error_message: The actual error message
            code_snippet: Relevant code snippet
            attempt_number: How many times developer has tried to fix this
            time_spent_minutes: Time spent on this issue

        Returns:
            Proactive assistance response
        """

        # Record observation
        observation = {
            "error_type": error_type,
            "error_message": error_message,
            "attempt_number": attempt_number,
            "time_spent": time_spent_minutes,
            "timestamp": "now"
        }
        self.session_history.append(observation)

        # Detect struggle indicators
        struggle_indicators = {}

        if attempt_number >= 3:
            struggle_indicators["repeated_errors"] = attempt_number

        if time_spent_minutes >= 10:
            struggle_indicators["time_on_task"] = time_spent_minutes

        if error_type == error_type and attempt_number > 1:
            struggle_indicators["same_error_type"] = True

        # Calculate confidence for proactive action
        confidence = self._calculate_intervention_confidence(
            error_type,
            attempt_number,
            time_spent_minutes
        )

        # Query pattern library for relevant patterns
        context = {
            "error_type": error_type,
            "tags": [error_type.lower(), "debugging"]
        }
        relevant_patterns = self.pattern_library.query_patterns(
            "debug_assistant",
            context,
            min_confidence=0.7
        )

        # Level 3: Proactively offer help
        proactive_response = self.level3.respond({
            "observed_need": f"debugging_{error_type.lower()}",
            "confidence": confidence
        })

        # If confidence is high enough, offer specific help
        if confidence >= 0.7:
            specific_help = self._generate_specific_help(
                error_type,
                error_message,
                code_snippet,
                relevant_patterns
            )
            proactive_response["specific_help"] = specific_help

            # Check if we should clarify before acting
            if self._has_ambiguity(error_message, code_snippet):
                clarification = self.trust_builder.clarify_before_acting(
                    instruction=f"Fix {error_type}",
                    detected_ambiguities=self._detect_ambiguities(error_message),
                    context={"error": error_message}
                )
                proactive_response["clarification_needed"] = clarification

        # If developer is struggling, offer structural support
        if struggle_indicators:
            structural_support = self.trust_builder.offer_proactive_help(
                struggle_indicators=struggle_indicators,
                available_help=[
                    "debugging_strategy",
                    "step_by_step",
                    "examples",
                    "explanation"
                ]
            )
            proactive_response["structural_support"] = structural_support

        # Update collaboration state
        return proactive_response

    def _calculate_intervention_confidence(
        self,
        error_type: str,
        attempt_number: int,
        time_spent: int
    ) -> float:
        """Calculate confidence for proactive intervention"""

        confidence = 0.5  # Base confidence

        # High confidence for well-known errors
        if error_type in ["ImportError", "ModuleNotFoundError", "SyntaxError"]:
            confidence += 0.2

        # Increase confidence with repeated attempts
        if attempt_number >= 3:
            confidence += 0.2
        elif attempt_number >= 2:
            confidence += 0.1

        # Increase confidence with time spent
        if time_spent >= 15:
            confidence += 0.2
        elif time_spent >= 10:
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_specific_help(
        self,
        error_type: str,
        error_message: str,
        code_snippet: str,
        patterns: list
    ) -> dict:
        """Generate specific debugging help"""

        help_response = {
            "error_type": error_type,
            "diagnosis": "",
            "suggested_fixes": [],
            "prevention_tips": [],
            "relevant_patterns": len(patterns)
        }

        # Type-specific help
        if error_type == "ImportError" or error_type == "ModuleNotFoundError":
            help_response["diagnosis"] = "Module import issue - likely missing dependency or environment problem"
            help_response["suggested_fixes"] = [
                "Check if package is installed: pip list | grep <package>",
                "Install missing package: pip install <package>",
                "Verify virtual environment is activated",
                "Check Python path: sys.path"
            ]
            help_response["prevention_tips"] = [
                "Use requirements.txt to track dependencies",
                "Always work in virtual environments",
                "Add import checks at top of file"
            ]

        elif error_type == "SyntaxError":
            help_response["diagnosis"] = "Syntax error in code structure"
            help_response["suggested_fixes"] = [
                "Check for missing/extra parentheses, brackets, or quotes",
                "Verify indentation (Python uses spaces consistently)",
                "Look for invalid characters or typos",
                "Enable syntax highlighting in your editor"
            ]
            help_response["prevention_tips"] = [
                "Use a linter (pylint, flake8) to catch syntax errors early",
                "Enable real-time syntax checking in IDE",
                "Use formatter like black to standardize code"
            ]

        elif error_type == "AttributeError":
            help_response["diagnosis"] = "Accessing non-existent attribute or method"
            help_response["suggested_fixes"] = [
                "Check object type: print(type(obj))",
                "List available attributes: dir(obj)",
                "Verify object initialization",
                "Check for None values: if obj is not None"
            ]
            help_response["prevention_tips"] = [
                "Use type hints to catch errors early",
                "Add attribute existence checks",
                "Use hasattr() for safer attribute access"
            ]

        elif error_type == "KeyError":
            help_response["diagnosis"] = "Accessing non-existent dictionary key"
            help_response["suggested_fixes"] = [
                "Check available keys: dict.keys()",
                "Use dict.get(key, default) for safe access",
                "Add key existence check: if key in dict",
                "Print dictionary structure to debug"
            ]
            help_response["prevention_tips"] = [
                "Always use .get() for optional keys",
                "Validate input data structure",
                "Use dataclasses or Pydantic for structured data"
            ]

        else:
            help_response["diagnosis"] = f"General {error_type} detected"
            help_response["suggested_fixes"] = [
                "Read the full error traceback carefully",
                "Add print statements to trace execution",
                "Use debugger to step through code",
                "Search for similar errors online"
            ]

        return help_response

    def _has_ambiguity(self, error_message: str, code_snippet: str) -> bool:
        """Check if error context has ambiguity"""
        # Simple heuristic: check if we need more context
        return len(code_snippet) < 10 or "..." in code_snippet

    def _detect_ambiguities(self, error_message: str) -> list:
        """Detect specific ambiguities in error context"""
        ambiguities = []

        if "line" not in error_message.lower():
            ambiguities.append("Which line is causing the error?")

        ambiguities.append("Can you share more of the surrounding code context?")
        ambiguities.append("What were you trying to accomplish when this error occurred?")

        return ambiguities

    def detect_feedback_loops(self) -> dict:
        """Detect if developer is in virtuous or vicious debugging cycle"""

        if len(self.session_history) < 3:
            return {"status": "insufficient_data"}

        # Analyze debugging session for feedback loops
        history_for_analysis = []
        for session in self.session_history:
            # Simulate trust/success based on attempt number
            success = session["attempt_number"] <= 2
            trust = 0.8 if success else 0.4

            history_for_analysis.append({
                "trust": trust,
                "success": success
            })

        result = self.feedback_detector.detect_active_loop(history_for_analysis)

        is_vicious = self.feedback_detector.detect_vicious_cycle(history_for_analysis)
        if is_vicious:
            result["warning"] = "⚠️  VICIOUS CYCLE DETECTED: Developer stuck in frustration loop"
            result["intervention"] = "Suggest taking a break, pair programming, or different approach"

        return result


def main():
    """Demonstrate debugging assistant with realistic scenarios"""

    try:
        print("=" * 70)
        print("Debugging Assistant - Level 3 Proactive Empathy")
        print("=" * 70)

        # Initialize assistant
        assistant = DebuggingAssistant(developer_id="dev_alice")

    print(f"\n✓ Debugging assistant initialized for developer: dev_alice")
    print(f"  Empathy Level: {assistant.empathy.target_level} (Proactive)")
    print(f"  Patterns loaded: {len(assistant.pattern_library.patterns)}")

    # ========================================
    # Scenario 1: Import Error (High Confidence)
    # ========================================
    print("\n" + "=" * 70)
    print("Scenario 1: Developer struggling with ImportError")
    print("=" * 70)

    print("\nDeveloper attempts:")
    print("  Attempt 1: ImportError: No module named 'requests'")
    print("  Attempt 2: Still getting same error...")
    print("  Attempt 3: Tried pip install, still not working")

    response1 = assistant.observe_debugging_session(
        error_type="ImportError",
        error_message="No module named 'requests'",
        code_snippet="import requests",
        attempt_number=3,
        time_spent_minutes=12
    )

    print(f"\n🤖 Assistant (Proactive - Confidence {response1['confidence']:.2f}):")
    print(f"   {response1['description']}")

    if "specific_help" in response1:
        help_info = response1["specific_help"]
        print(f"\n   📋 Diagnosis: {help_info['diagnosis']}")
        print(f"\n   🔧 Suggested fixes:")
        for i, fix in enumerate(help_info['suggested_fixes'][:3], 1):
            print(f"      {i}. {fix}")

        print(f"\n   💡 Prevention tips:")
        for tip in help_info['prevention_tips'][:2]:
            print(f"      - {tip}")

    if "structural_support" in response1:
        support = response1["structural_support"]
        print(f"\n   🆘 Proactive help offered:")
        if "offered_support" in support and support["offered_support"]:
            for offer in support["offered_support"]:
                print(f"      - {offer['description']}")
        else:
            print(f"      Assessment: {support['struggle_assessment']['type']} struggle detected")

    # Record successful resolution
    assistant.empathy.collaboration_state.update_trust("success")
    assistant.pattern_library.record_pattern_outcome("pat_import_errors", success=True)

    # ========================================
    # Scenario 2: Syntax Error (Medium Confidence)
    # ========================================
    print("\n" + "=" * 70)
    print("Scenario 2: Developer with syntax error")
    print("=" * 70)

    print("\nDeveloper attempts:")
    print("  Attempt 1: SyntaxError: invalid syntax")
    print("  Attempt 2: Still not finding the issue...")

    response2 = assistant.observe_debugging_session(
        error_type="SyntaxError",
        error_message="SyntaxError: invalid syntax at line 42",
        code_snippet="def calculate_total(items):\n    return sum([item['price'] for item in items]",
        attempt_number=2,
        time_spent_minutes=5
    )

    print(f"\n🤖 Assistant (Proactive - Confidence {response2['confidence']:.2f}):")

    if "specific_help" in response2:
        help_info = response2["specific_help"]
        print(f"   📋 Diagnosis: {help_info['diagnosis']}")
        print(f"\n   🔧 Top suggestions:")
        for i, fix in enumerate(help_info['suggested_fixes'][:3], 1):
            print(f"      {i}. {fix}")

    # ========================================
    # Scenario 3: Repeated AttributeError (Vicious Cycle)
    # ========================================
    print("\n" + "=" * 70)
    print("Scenario 3: Developer stuck in debugging loop")
    print("=" * 70)

    print("\nDeveloper attempts:")
    print("  Attempt 1: AttributeError: 'NoneType' object has no attribute 'name'")
    print("  Attempt 2: Same error...")
    print("  Attempt 3: Still stuck...")
    print("  Attempt 4: Getting frustrated...")

    response3 = assistant.observe_debugging_session(
        error_type="AttributeError",
        error_message="'NoneType' object has no attribute 'name'",
        code_snippet="user.name",
        attempt_number=4,
        time_spent_minutes=20
    )

    print(f"\n🤖 Assistant (Proactive - Confidence {response3['confidence']:.2f}):")
    print(f"   ⚠️  HIGH CONFIDENCE - Taking initiative!")

    if "specific_help" in response3:
        help_info = response3["specific_help"]
        print(f"\n   📋 Diagnosis: {help_info['diagnosis']}")
        print(f"\n   🔧 Immediate fixes to try:")
        for i, fix in enumerate(help_info['suggested_fixes'], 1):
            print(f"      {i}. {fix}")

    if "structural_support" in response3:
        support = response3["structural_support"]
        print(f"\n   🆘 Structural support offered:")
        if "struggle_assessment" in support:
            print(f"      Struggle type: {support['struggle_assessment']['type']}")
        if "help_offered" in support and support["help_offered"]:
            for offer in support["help_offered"]:
                print(f"      - {offer['type']}: {offer['description']}")
        else:
            print(f"      Assessment: Developer needs assistance")

    # ========================================
    # Feedback Loop Analysis
    # ========================================
    print("\n" + "=" * 70)
    print("Feedback Loop Analysis")
    print("=" * 70)

    loop_result = assistant.detect_feedback_loops()

    print(f"\nDebugging session analysis:")
    print(f"  Total attempts: {len(assistant.session_history)}")
    print(f"  Dominant loop: {loop_result.get('dominant_loop', 'N/A')}")
    print(f"  Trend: {loop_result.get('trend', 'N/A')}")

    if "warning" in loop_result:
        print(f"\n  {loop_result['warning']}")
        print(f"  Recommendation: {loop_result['intervention']}")
    else:
        print(f"  Recommendation: {loop_result.get('recommendation', 'Continue')}")

    # ========================================
    # Trust Trajectory
    # ========================================
    print("\n" + "=" * 70)
    print("Trust Building Analysis")
    print("=" * 70)

    trust_trajectory = assistant.trust_builder.get_trust_trajectory()

    print(f"\nTrust evolution:")
    print(f"  Current trust: {assistant.empathy.collaboration_state.trust_level:.2f}")
    print(f"  Trajectory: {trust_trajectory['trajectory']}")
    print(f"  Building signals: {trust_trajectory['building_signals']}")
    print(f"  Recent behaviors: {', '.join(trust_trajectory['recent_behaviors'][-3:])}")

    # ========================================
    # Pattern Library Stats
    # ========================================
    print("\n" + "=" * 70)
    print("Pattern Library Statistics")
    print("=" * 70)

    stats = assistant.pattern_library.get_library_stats()
    print(f"\nShared debugging patterns:")
    print(f"  Total patterns: {stats['total_patterns']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")
    print(f"  Total usage: {stats['total_usage']}")

    # Get top patterns
    top_patterns = assistant.pattern_library.get_top_patterns(n=3, sort_by="confidence")
    print(f"\n  Top patterns by confidence:")
    for i, pattern in enumerate(top_patterns, 1):
        print(f"    {i}. {pattern.name} (confidence: {pattern.confidence:.2f})")

    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 70)
    print("Summary: Level 3 Proactive Debugging")
    print("=" * 70)

    print("\nKey Behaviors Demonstrated:")
    print("  ✓ Proactive detection of debugging struggles")
    print("  ✓ Confidence-based intervention (higher confidence = more proactive)")
    print("  ✓ Pattern-based suggestions from shared library")
    print("  ✓ Structural support when developer is stuck")
    print("  ✓ Feedback loop detection (virtuous vs vicious cycles)")
    print("  ✓ Trust building through helpful, non-intrusive assistance")

    print("\nLevel 3 Proactive Empathy means:")
    print("  • Don't wait to be asked - act when need is clear")
    print("  • Higher confidence = more initiative")
    print("  • Learn from patterns to improve over time")
    print("  • Detect frustration loops and intervene")
    print("  • Build trust through consistent, helpful actions")

        print("\n" + "=" * 70)

    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        print("Please check your input parameters and try again.")
        return 1
    except KeyError as e:
        print(f"\n❌ Missing Required Field: {e}")
        print("Check that all required fields are present in the data.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {type(e).__name__}: {e}")
        print("Please check the documentation or file an issue.")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
