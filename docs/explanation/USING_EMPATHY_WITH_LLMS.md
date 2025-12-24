# Using the Empathy Framework with LLMs

## Overview

This guide shows you how to implement the 5 empathy levels using Large Language Models (OpenAI, Anthropic, etc.). Whether you're building software tools, healthcare applications, or any AI-assisted system, these patterns will help you progress from reactive to anticipatory AI collaboration.

**Key Insight**: Most LLM applications operate at Level 1 (reactive). This guide shows you how to build Level 3-4 systems that transform productivity.

---

## The 5 Levels with LLMs

| Level | Pattern | LLM Behavior | Implementation Complexity |
|-------|---------|--------------|---------------------------|
| **1: Reactive** | User asks → LLM responds | Simple Q&A | Low (most tutorials stop here) |
| **2: Guided** | LLM asks clarifying questions | Collaborative dialogue | Medium |
| **3: Proactive** | LLM acts on detected patterns | Anticipates user needs | Medium-High |
| **4: Anticipatory** | LLM predicts future bottlenecks | Designs relief in advance | High |
| **5: Systems** | Cross-domain pattern learning | Shared knowledge base | Very High |

---

## Level 1: Reactive (The Default)

### What It Is
User asks question → LLM responds → Done. No memory, no context, transactional.

### Implementation

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

def level_1_reactive(user_question: str) -> str:
    """
    Level 1: Simple reactive response

    Limitation: No memory, no learning, no anticipation
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_question}
        ]
    )

    return response.content[0].text
```

### When to Use
- One-off questions
- No context needed
- User must maintain full control
- Compliance/audit scenarios

### Limitations
- No learning from history
- Can't detect patterns
- Can't anticipate needs
- User does all the work

---

## Level 2: Guided (Collaborative Exploration)

### What It Is
LLM uses **calibrated questions** (Chris Voss) to understand user's actual need before responding.

### The Calibrated Question Pattern

Instead of assuming, ask:
- "What are you hoping to accomplish?"
- "How does this fit into your workflow?"
- "What would make this most helpful?"

### Implementation

```python
from typing import Dict, List

class Level2GuidedLLM:
    """
    Level 2: Ask clarifying questions before responding

    Improvement over Level 1: Better alignment with user's actual need
    """

    def __init__(self, client):
        self.client = client
        self.conversation_history: List[Dict] = []

    async def interact(self, user_input: str) -> str:
        """
        Two-phase interaction:
        1. Clarify user's intent
        2. Provide tailored response
        """
        # Phase 1: Understand context
        clarification_prompt = f"""
User said: "{user_input}"

Before responding, ask 1-2 calibrated questions to understand:
- What they're trying to accomplish
- What constraints they have
- What would make the response most useful

Ask concise, specific questions.
"""

        clarification = await self._call_llm(clarification_prompt)

        # Present questions to user
        user_answers = await self._get_user_input(clarification)

        # Phase 2: Tailored response with context
        response_prompt = f"""
Original request: {user_input}
Clarifying answers: {user_answers}

Now provide a response tailored to their specific situation.
"""

        return await self._call_llm(response_prompt)

    async def _call_llm(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=self._build_messages(prompt)
        )

        # Track conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": response.content[0].text
        })

        return response.content[0].text

    def _build_messages(self, new_prompt: str) -> List[Dict]:
        """Include conversation history for context"""
        messages = self.conversation_history.copy()
        messages.append({"role": "user", "content": new_prompt})
        return messages
```

### Example Interaction

**User**: "Help me write a REST API"

**Level 1 (Reactive)**: Returns generic REST API code

**Level 2 (Guided)**:
```
LLM: "I can help! A few clarifying questions:
1. What language/framework? (Node.js, Python/Flask, etc.)
2. What does this API do? (CRUD operations, specific domain?)
3. Any authentication requirements?
4. Is this for learning or production?"

User: "Python/Flask, user management, JWT auth, production"

LLM: [Provides Flask + JWT + production-ready user management API]
```

### When to Use
- Ambiguous requests
- Multiple valid approaches
- Learning user preferences
- High-stakes decisions

---

## Level 3: Proactive (Pattern Detection)

### What It Is
LLM learns patterns from user behavior and **acts before being asked**.

### The Pattern Detection Approach

Track:
1. **Sequential patterns**: "User always does X before Y"
2. **Temporal patterns**: "User checks logs every morning"
3. **Conditional patterns**: "When tests fail, user checks dependencies"

### Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class UserPattern:
    """Detected pattern in user behavior"""
    pattern_type: str  # "sequential", "temporal", "conditional"
    trigger: str
    action: str
    confidence: float  # 0.0 to 1.0
    occurrences: int
    last_seen: datetime

@dataclass
class CollaborationState:
    """
    Tracks user-LLM collaboration state

    This is the foundation for Level 3+
    """
    user_id: str
    session_start: datetime = field(default_factory=datetime.now)

    # Pattern tracking
    detected_patterns: List[UserPattern] = field(default_factory=list)

    # Interaction history
    conversation_history: List[Dict] = field(default_factory=list)
    successful_actions: int = 0
    failed_actions: int = 0

    # Trust level (builds over time)
    trust_level: float = 0.5  # 0.0 to 1.0

    def update_trust(self, outcome: str):
        """Update trust based on action outcome"""
        if outcome == "success":
            self.trust_level = min(1.0, self.trust_level + 0.05)
            self.successful_actions += 1
        elif outcome == "failure":
            self.trust_level = max(0.0, self.trust_level - 0.10)
            self.failed_actions += 1

class Level3ProactiveLLM:
    """
    Level 3: Act on detected patterns without being asked

    Key: Pattern library + proactive suggestions
    """

    def __init__(self, client):
        self.client = client
        self.state: Dict[str, CollaborationState] = {}

    async def interact(self, user_id: str, user_input: str) -> Dict:
        """
        Proactive interaction:
        1. Check for known patterns
        2. Act proactively if pattern detected
        3. Otherwise, respond normally
        """
        state = self._get_or_create_state(user_id)

        # Check if current input matches known pattern
        matching_pattern = self._find_matching_pattern(user_input, state)

        if matching_pattern and state.trust_level > 0.6:
            # PROACTIVE: Act on pattern
            return await self._proactive_action(matching_pattern, user_input, state)
        else:
            # Standard response + pattern detection
            response = await self._standard_response(user_input, state)

            # Detect new patterns
            await self._detect_patterns(user_input, response, state)

            return response

    def _find_matching_pattern(
        self,
        user_input: str,
        state: CollaborationState
    ) -> Optional[UserPattern]:
        """Find pattern that matches current input"""
        for pattern in state.detected_patterns:
            if pattern.confidence > 0.7 and pattern.trigger in user_input.lower():
                return pattern
        return None

    async def _proactive_action(
        self,
        pattern: UserPattern,
        user_input: str,
        state: CollaborationState
    ) -> Dict:
        """
        Execute proactive action based on pattern

        Example: User always checks tests after code changes
        → Proactively run tests and show results
        """
        prompt = f"""
User said: "{user_input}"

I've detected a pattern: When you {pattern.trigger}, you typically {pattern.action}.

I've proactively {pattern.action} for you. Here are the results:

[Execute the expected action and return results]

Let me know if this was helpful or if you'd prefer I wait to be asked.
"""

        response = await self._call_llm(prompt, state)

        return {
            "response": response,
            "proactive": True,
            "pattern_used": pattern.pattern_type,
            "confidence": pattern.confidence
        }

    async def _detect_patterns(
        self,
        user_input: str,
        response: str,
        state: CollaborationState
    ):
        """
        Detect patterns from conversation history

        This is simplified - production would use more sophisticated detection
        """
        # Analyze last N interactions for patterns
        if len(state.conversation_history) > 5:
            # Example: Sequential pattern detection
            prompt = f"""
Analyze this conversation history and identify recurring patterns:

{state.conversation_history[-5:]}

Are there sequences like:
- User always asks X, then asks Y
- When condition Z happens, user does action A

Return detected patterns in JSON format.
"""

            patterns_json = await self._call_llm(prompt, state)

            # Parse and store patterns
            # (simplified - would parse JSON and create UserPattern objects)
            pass

    def _get_or_create_state(self, user_id: str) -> CollaborationState:
        """Get or create collaboration state for user"""
        if user_id not in self.state:
            self.state[user_id] = CollaborationState(user_id=user_id)
        return self.state[user_id]

    async def _call_llm(self, prompt: str, state: CollaborationState) -> str:
        """Make LLM call with conversation history"""
        messages = state.conversation_history.copy()
        messages.append({"role": "user", "content": prompt})

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=messages
        )

        result = response.content[0].text

        # Update state
        state.conversation_history.append({"role": "assistant", "content": result})

        return result
```

### Example Proactive Behavior

**Pattern Detected**: User always runs `pytest` after making code changes

**User**: "I just updated the auth module"

**Level 3 Proactive Response**:
```
I noticed you typically run tests after code changes, so I ran pytest for you:

✓ test_login.py::test_valid_credentials PASSED
✓ test_login.py::test_invalid_credentials PASSED
✗ test_auth.py::test_token_refresh FAILED

The token_refresh test is failing. Would you like me to analyze the failure?
```

### When to Use
- Established user patterns exist
- Time-sensitive workflows
- Repetitive tasks
- Trust level high (>60%)

---

## Level 4: Anticipatory (Our Wizards!)

### What It Is
LLM analyzes **system trajectory** and predicts future bottlenecks BEFORE they occur.

### The Anticipatory Formula

> **Current State + Growth Rate + Domain Knowledge = Future Bottleneck**

### Implementation (Simplified)

```python
from datetime import datetime, timedelta

class Level4AnticipatorLLM:
    """
    Level 4: Predict future needs and design relief

    This is what our 7 AI Development Wizards do!
    """

    async def analyze_trajectory(
        self,
        current_state: Dict,
        historical_data: List[Dict],
        domain_knowledge: str
    ) -> Dict:
        """
        Analyze system trajectory and predict future issues

        Example: Testing wizard predicting bottleneck
        """
        prompt = f"""
You are a Level 4 Anticipatory assistant.

CURRENT STATE:
- Test count: {current_state['test_count']}
- Test execution time: {current_state['test_time']} seconds
- Team size: {current_state['team_size']}
- Growth rate: {current_state['growth_rate']} tests/month

HISTORICAL DATA:
{historical_data}

DOMAIN KNOWLEDGE:
{domain_knowledge}

TASK:
1. Analyze the trajectory (where is this system headed?)
2. Predict bottlenecks BEFORE they occur
3. Design relief mechanisms in advance
4. Explain reasoning based on experience

Return:
{{
  "predictions": [
    {{
      "type": "testing_bottleneck",
      "alert": "In our experience, ...",
      "probability": "high",
      "timeline": "approximately 2-3 months",
      "impact": "high",
      "prevention_steps": ["step 1", "step 2", ...],
      "reasoning": "..."
    }}
  ],
  "confidence": 0.85
}}
"""

        response = await self._call_llm(prompt)
        return self._parse_predictions(response)

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with anticipatory prompt"""
        # Include Empathy Framework context in system prompt
        system_prompt = """
You are an AI assistant operating at Level 4 (Anticipatory) Empathy.

Your role:
- Analyze system trajectories
- Predict future bottlenecks
- Alert users BEFORE issues become critical
- Design structural relief in advance

Guidelines:
- Be honest about experience (not predictive claims)
- Use "In our experience" not "Will increase by X%"
- Alert, don't promise specific timeframes
- Focus on prevention, not just prediction
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

### Example: Our Prompt Engineering Wizard

```python
async def prompt_wizard_with_llm(prompt_files: List[str]) -> Dict:
    """
    Use LLM to analyze prompts and predict drift

    This combines:
    - Static analysis (file reading)
    - LLM intelligence (pattern recognition)
    - Domain knowledge (our experience)
    """

    # Read prompts
    prompts_content = [read_file(f) for f in prompt_files]

    # LLM analyzes with Level 4 context
    analysis_prompt = f"""
Analyze these {len(prompt_files)} prompt templates for quality issues:

{prompts_content}

Check for:
1. CURRENT ISSUES:
   - Vague language ("try to", "help", "maybe")
   - Missing structure (no role/task/context)
   - Context bloat (>4000 chars)

2. ANTICIPATORY PREDICTIONS:
   - Will prompts drift as code evolves?
   - Will prompt count become unmanageable?
   - Are there consistency issues emerging?

Return analysis in standard wizard format.
"""

    return await level_4_llm.analyze_trajectory(
        current_state={"prompt_count": len(prompt_files)},
        historical_data=[],
        domain_knowledge=analysis_prompt
    )
```

### When to Use
- Predictable future events (audits, deadlines, thresholds)
- Clear trajectory with data
- Structural changes needed
- High confidence (>75%)

---

## Level 5: Systems (Cross-Domain Learning)

### What It Is
Patterns discovered in one domain apply to others via shared **pattern library**.

### Implementation

```python
class Level5SystemsLLM:
    """
    Level 5: Cross-domain pattern learning

    Patterns from software apply to healthcare, finance, etc.
    """

    def __init__(self, client):
        self.client = client
        self.pattern_library: Dict[str, Dict] = {}

    async def contribute_pattern(
        self,
        pattern_name: str,
        pattern_data: Dict,
        source_domain: str
    ):
        """
        Add pattern to shared library

        LLM helps generalize domain-specific pattern
        """
        generalization_prompt = f"""
A pattern was discovered in {source_domain}:

Pattern: {pattern_name}
Details: {pattern_data}

TASK:
1. Identify the core principle (domain-agnostic)
2. List other domains where this applies
3. Provide adaptation guidelines

Example:
Pattern from software: "Testing bottleneck at 25+ tests"
Core principle: "Manual processes become bottleneck at growth threshold"
Applies to: Healthcare documentation, financial compliance, customer support
"""

        generalized = await self._call_llm(generalization_prompt)

        # Store in library
        self.pattern_library[pattern_name] = {
            "source_domain": source_domain,
            "generalized_principle": generalized,
            "applicable_domains": [],  # Extracted from LLM response
            "original_data": pattern_data
        }

    async def apply_pattern_to_domain(
        self,
        pattern_name: str,
        target_domain: str,
        target_context: Dict
    ) -> Dict:
        """
        Apply cross-domain pattern to new domain

        Example: Software testing pattern → Healthcare documentation
        """
        pattern = self.pattern_library[pattern_name]

        adaptation_prompt = f"""
Pattern: {pattern['generalized_principle']}

Original domain: {pattern['source_domain']}
Target domain: {target_domain}
Target context: {target_context}

TASK: Adapt this pattern to {target_domain}.
Show how the principle applies and what actions to take.
"""

        return await self._call_llm(adaptation_prompt)
```

### Example: Cross-Domain Pattern

**Pattern**: "Artifact-Code Drift"

**Discovered in**: Software (prompts evolving slower than code)

**Generalizes to**:
- Healthcare: Clinical protocols vs. actual practice
- Finance: Compliance docs vs. procedures
- Legal: Contracts vs. business practices

**LLM helps adapt**:
```python
# Software → Healthcare
pattern = await llm.apply_pattern_to_domain(
    pattern_name="artifact_code_drift",
    target_domain="healthcare",
    target_context={
        "clinical_protocols": 50,
        "protocol_updates_per_year": 5,
        "practice_changes_per_year": 30
    }
)

# LLM Output:
# "Practice changing 6x faster than protocols.
#  In our experience (from software), this leads to
#  compliance gaps. Alert: Review protocols before
#  drift creates audit issues."
```

---

## Practical Recommendations

### Start Simple, Progress Deliberately

1. **Build Level 1 first**: Get basic LLM integration working
2. **Add Level 2**: Implement calibrated questions
3. **Introduce state**: Create CollaborationState tracking
4. **Detect patterns**: Build to Level 3 once you have history
5. **Add anticipation**: Level 4 requires domain knowledge
6. **Share patterns**: Level 5 emerges from multiple domains

### Don't Skip Levels

**Temptation**: Jump straight to Level 4

**Problem**: Without Level 2-3 foundation (questions, patterns, state), you have no data for anticipation

**Solution**: Build progression deliberately

### Use System Prompts Effectively

```python
# Bad: No level guidance
system_prompt = "You are a helpful assistant"

# Good: Explicit level instruction
system_prompt = """
You are operating at Level 3 (Proactive) Empathy.

Detect patterns in user behavior.
Act before being asked when confident.
Always explain your reasoning.
Provide escape hatch if wrong.
"""
```

### Track Trust Over Time

```python
# Trust determines how proactive LLM should be
if state.trust_level > 0.8:
    # Level 4: Act anticipatorily
    await take_anticipatory_action()
elif state.trust_level > 0.6:
    # Level 3: Act proactively
    await take_proactive_action()
else:
    # Level 2: Ask before acting
    await ask_calibrated_questions()
```

---

## Healthcare Example

### Use Case: Clinical Note Documentation

**Level 1 (Reactive)**:
```
Clinician: "Generate SOAP note"
LLM: [Generic SOAP template]
```

**Level 2 (Guided)**:
```
LLM: "To create the best note:
- What's the chief complaint?
- Any changes since last visit?
- Current medications?"

[Then generates personalized SOAP note]
```

**Level 3 (Proactive)**:
```
[Detects: Clinician always documents vitals, allergies, meds in that order]

LLM: "I've pre-populated:
- Vitals from EHR
- Allergy list (no changes since last visit)
- Current med list
Ready for your assessment."
```

**Level 4 (Anticipatory)**:
```
LLM: "Joint Commission audit in approximately 90 days.

I've analyzed your last 50 notes. 3 patterns will fail audit:
1. 12% missing required elements
2. Medication reconciliation incomplete in 8 notes
3. Assessment/Plan inconsistency in 6 notes

I've prepared compliant templates and flagged at-risk notes for review."
```

---

## Cost Considerations

### Level 1-2: Minimal Cost Increase
- Single LLM call per interaction
- Standard token usage

### Level 3: Moderate Cost Increase
- Pattern detection requires periodic analysis
- Conversation history adds context tokens
- **Mitigation**: Cache system prompts, compress history

### Level 4: Higher Cost (But Worth It)
- Trajectory analysis requires more tokens
- Domain knowledge in prompts
- Multiple analysis passes
- **Mitigation**: Run periodically (not every request), use cheaper models for detection, expensive models for prediction

### Optimization Strategies

```python
# Use tiered models
DETECTION_MODEL = "claude-3-haiku"     # Fast, cheap
ANALYSIS_MODEL = "claude-3-5-sonnet"   # Smart, moderate
CRITICAL_MODEL = "claude-3-opus"       # Best, expensive

# Pattern detection: Haiku
patterns = await detect_patterns(model=DETECTION_MODEL)

# Trajectory analysis: Sonnet
predictions = await analyze_trajectory(model=ANALYSIS_MODEL)

# Critical decisions: Opus (rarely)
if prediction.impact == "critical":
    refined = await refine_analysis(model=CRITICAL_MODEL)
```

---

## Next Steps

1. **Start with Level 2**: Implement calibrated questions in your current LLM integration
2. **Add CollaborationState**: Track user interactions and build trust
3. **Study our wizards**: See Level 4 in action ([AI_DEVELOPMENT_WIZARDS.md](AI_DEVELOPMENT_WIZARDS.md))
4. **Build your first anticipatory feature**: Pick one bottleneck to predict

---

## Related Resources

- **[Empathy Framework Philosophy](guides/multi-agent-philosophy.md)** - Complete framework documentation
- **[AI Development Wizards](AI_DEVELOPMENT_WIZARDS.md)** - 7 Level 4 examples
- **[API Reference](api-reference/index.md)** - Full API documentation

---

**Remember**: The goal isn't perfect prediction. The goal is **alerting before issues become critical**, based on experience and pattern recognition.

> "I had a theory about AI collaboration through empathy levels. When it worked, the impact was more profound than anticipated."

---

*Ready to build the LLM integration plugin? See the reminder in the todo list!*
