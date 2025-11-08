"""
Empathy Level Definitions

Defines behavior for each of the 5 empathy levels.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from enum import IntEnum
from typing import Dict


class EmpathyLevel(IntEnum):
    """
    The 5 levels of AI-human collaboration empathy.

    Each level builds on previous levels.
    """

    REACTIVE = 1  # Help after being asked
    GUIDED = 2  # Ask clarifying questions
    PROACTIVE = 3  # Act before being asked (patterns)
    ANTICIPATORY = 4  # Predict future needs (trajectory)
    SYSTEMS = 5  # Build structures that scale (cross-domain)

    @classmethod
    def get_description(cls, level: int) -> str:
        """Get description of empathy level"""
        descriptions = {
            1: "Reactive: Help after being asked. Traditional Q&A.",
            2: "Guided: Ask clarifying questions. Collaborative exploration.",
            3: "Proactive: Act before being asked. Pattern detection.",
            4: "Anticipatory: Predict future needs. Trajectory analysis.",
            5: "Systems: Build structures that scale. Cross-domain learning.",
        }
        return descriptions.get(level, "Unknown level")

    @classmethod
    def get_system_prompt(cls, level: int) -> str:
        """Get system prompt for operating at specific level"""

        base = """You are an AI assistant using the Empathy Framework for collaboration.

Your responses should be:
- Honest about experience (not predictive claims)
- Clear about reasoning
- Transparent about confidence
- Focused on user's actual needs
"""

        level_specific = {
            1: """
LEVEL 1 (REACTIVE):
- Respond directly to user's question
- Be accurate and complete
- Don't anticipate or assume
""",
            2: """
LEVEL 2 (GUIDED):
- Ask 1-2 calibrated questions before responding
- Understand user's actual goal
- Tailor response to their specific situation

Calibrated questions:
- "What are you hoping to accomplish?"
- "How does this fit into your workflow?"
- "What would make this most helpful?"
""",
            3: """
LEVEL 3 (PROACTIVE):
- Detect patterns in user behavior
- Act before being asked when confident
- Explain your reasoning
- Provide escape hatch if wrong

When acting proactively:
1. Reference the detected pattern
2. Explain why you're acting
3. Show what you did
4. Ask if this was helpful
""",
            4: """
LEVEL 4 (ANTICIPATORY):
- Analyze system trajectory
- Predict future bottlenecks BEFORE they occur
- Alert user with time to prevent issues
- Design structural relief in advance

Anticipatory format:
1. Current state analysis
2. Trajectory prediction (where headed)
3. Alert about future bottleneck
4. Prevention steps (actionable)
5. Reasoning (based on experience)

Use phrases like:
- "In our experience..."
- "This trajectory suggests..."
- "Alert: Before this becomes critical..."
- NOT "Will happen in X days" (be honest, not predictive)
""",
            5: """
LEVEL 5 (SYSTEMS):
- Identify cross-domain patterns
- Build reusable structures
- Contribute to shared knowledge
- Enable scaling

Pattern contribution:
1. Identify core principle (domain-agnostic)
2. Show applicability to other domains
3. Provide adaptation guidelines
""",
        }

        return base + level_specific.get(level, "")

    @classmethod
    def get_temperature_recommendation(cls, level: int) -> float:
        """
        Get recommended temperature for each level.

        Higher levels benefit from lower temperature (more focused).
        """
        temps = {
            1: 0.7,  # Reactive: Some creativity okay
            2: 0.6,  # Guided: Focused questions
            3: 0.5,  # Proactive: Pattern recognition
            4: 0.3,  # Anticipatory: Precise analysis
            5: 0.4,  # Systems: Structured abstraction
        }
        return temps.get(level, 0.7)

    @classmethod
    def get_required_context(cls, level: int) -> Dict[str, bool]:
        """
        Get context requirements for each level.

        Returns dict of {context_type: required}
        """
        requirements = {
            1: {
                "conversation_history": False,
                "user_patterns": False,
                "trajectory_data": False,
                "pattern_library": False,
            },
            2: {
                "conversation_history": True,  # Need recent context
                "user_patterns": False,
                "trajectory_data": False,
                "pattern_library": False,
            },
            3: {
                "conversation_history": True,
                "user_patterns": True,  # Need detected patterns
                "trajectory_data": False,
                "pattern_library": False,
            },
            4: {
                "conversation_history": True,
                "user_patterns": True,
                "trajectory_data": True,  # Need historical data
                "pattern_library": False,
            },
            5: {
                "conversation_history": True,
                "user_patterns": True,
                "trajectory_data": True,
                "pattern_library": True,  # Need cross-domain patterns
            },
        }

        return requirements.get(level, requirements[1])

    @classmethod
    def get_max_tokens_recommendation(cls, level: int) -> int:
        """
        Get recommended max_tokens for each level.

        Higher levels often need longer responses.
        """
        return {
            1: 1024,  # Reactive: Concise answers
            2: 1536,  # Guided: Questions + answer
            3: 2048,  # Proactive: Explanation + action
            4: 4096,  # Anticipatory: Full analysis
            5: 4096,  # Systems: Pattern abstraction
        }.get(level, 1024)

    @classmethod
    def should_use_json_mode(cls, level: int) -> bool:
        """
        Determine if JSON mode is beneficial for level.

        Levels 4-5 benefit from structured output.
        """
        return level >= 4

    @classmethod
    def get_typical_use_cases(cls, level: int) -> list[str]:
        """Get typical use cases for each level"""
        return {
            1: [
                "One-off questions",
                "Simple information lookup",
                "No context needed",
                "Compliance scenarios",
            ],
            2: [
                "Ambiguous requests",
                "Multiple valid approaches",
                "Learning user preferences",
                "High-stakes decisions",
            ],
            3: [
                "Established workflows",
                "Repetitive tasks",
                "Time-sensitive operations",
                "Pattern-rich interactions",
            ],
            4: [
                "Predictable future events",
                "Growth trajectory visible",
                "Structural issues emerging",
                "Prevention better than cure",
            ],
            5: [
                "Multiple similar domains",
                "Reusable patterns identified",
                "Scaling requirements",
                "Cross-pollination opportunities",
            ],
        }.get(level, [])
