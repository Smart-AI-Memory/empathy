# Example: Adaptive Learning System

**Difficulty**: Advanced
**Time**: 25 minutes
**Empathy Level**: 3-4 (Self-improving)
**Features**: Dynamic thresholds, pattern decay, transfer learning

---

## Overview

This example shows how the Empathy Framework adapts and learns over time:
- **Dynamic confidence thresholds** that adjust based on user feedback
- **Pattern decay** for stale patterns that haven't been used
- **Transfer learning** to adapt patterns from one domain to another
- **User preference learning** for personalized AI behavior

**Key Insight**: Instead of fixed rules, the system learns what works for each user.

---

## Installation

```bash
pip install empathy-framework
```

---

## Part 1: Dynamic Confidence Thresholds

### Problem: Fixed Thresholds Don't Work for Everyone

```python
from empathy_os import EmpathyOS

# Traditional approach: Fixed threshold
empathy_fixed = EmpathyOS(
    user_id="user_conservative",
    target_level=4,
    confidence_threshold=0.80  # Fixed: same for everyone
)

# User A (conservative): Wants high confidence before seeing predictions
# User B (adventurous): Wants to see predictions even with lower confidence

# With fixed threshold=0.80:
# - User A is happy (only sees high-confidence predictions)
# - User B is frustrated (misses many useful predictions at 70-75%)
```

### Solution: Adaptive Thresholds

```python
from empathy_os.adaptive import AdaptiveLearning

# Create adaptive system
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75,  # Starting point
    adaptive_learning=True  # Enable adaptation
)

adaptive = AdaptiveLearning(empathy)

# User accepts a Level 4 prediction with 72% confidence
adaptive.record_outcome(
    prediction_id="pred_001",
    prediction_confidence=0.72,  # Below 75% threshold
    user_action="accepted",      # User found it helpful!
    outcome="success"             # Prediction was correct
)

# System learns: This user accepts predictions at 72%
# Adjust threshold down
new_threshold = adaptive.adjust_threshold(user_id="user_123")

print(f"Threshold adjusted: 0.75 → {new_threshold:.2f}")
# Output: Threshold adjusted: 0.75 → 0.72

# User rejects a prediction with 78% confidence
adaptive.record_outcome(
    prediction_id="pred_002",
    prediction_confidence=0.78,
    user_action="rejected",  # User didn't find it useful
    outcome="failure"        # Prediction was wrong or not helpful
)

# System learns: This user wants higher confidence
new_threshold = adaptive.adjust_threshold(user_id="user_123")

print(f"Threshold adjusted: 0.72 → {new_threshold:.2f}")
# Output: Threshold adjusted: 0.72 → 0.74

# After 50 interactions
for i in range(48):
    # Simulate mix of accepts (40) and rejects (10)
    confidence = random.uniform(0.65, 0.90)
    accepted = confidence > 0.70 and random.random() > 0.2
    outcome = "success" if accepted else "failure"

    adaptive.record_outcome(
        prediction_id=f"pred_{i+3}",
        prediction_confidence=confidence,
        user_action="accepted" if accepted else "rejected",
        outcome=outcome
    )

# Final threshold personalized to user's preferences
final_threshold = adaptive.get_threshold(user_id="user_123")
print(f"\nPersonalized threshold after 50 interactions: {final_threshold:.2f}")
# Output: Personalized threshold: 0.71
# (Lower than default 0.75 because user accepts lower-confidence predictions)
```

---

## Part 2: Per-Pattern Thresholds

### Different Patterns Need Different Confidence Levels

```python
from empathy_os.adaptive import PatternThresholds

adaptive = AdaptiveLearning(empathy)

# User's behavior varies by pattern type
scenarios = [
    # Security patterns: User wants HIGH confidence (cautious)
    {"pattern": "security_vulnerability_detection", "confidence": 0.82, "accepted": True},
    {"pattern": "security_vulnerability_detection", "confidence": 0.75, "accepted": False},
    {"pattern": "security_vulnerability_detection", "confidence": 0.88, "accepted": True},

    # Code style patterns: User accepts LOW confidence (flexible)
    {"pattern": "code_style_suggestion", "confidence": 0.65, "accepted": True},
    {"pattern": "code_style_suggestion", "confidence": 0.68, "accepted": True},
    {"pattern": "code_style_suggestion", "confidence": 0.62, "accepted": True},
]

for scenario in scenarios:
    adaptive.record_outcome(
        prediction_id=f"pred_{scenario['pattern']}_{random.randint(1000,9999)}",
        prediction_confidence=scenario['confidence'],
        pattern_name=scenario['pattern'],
        user_action="accepted" if scenario['accepted'] else "rejected",
        outcome="success" if scenario['accepted'] else "failure"
    )

# Get per-pattern thresholds
thresholds = adaptive.get_pattern_thresholds(user_id="user_123")

print("Personalized Thresholds by Pattern:")
for pattern, threshold in thresholds.items():
    print(f"  {pattern}: {threshold:.2f}")

# Output:
# Personalized Thresholds by Pattern:
#   security_vulnerability_detection: 0.85 (high - user is cautious)
#   code_style_suggestion: 0.63 (low - user is flexible)
#   default: 0.75 (baseline for unknown patterns)
```

---

## Part 3: Pattern Decay

### Stale Patterns Lose Confidence Over Time

```python
from empathy_os.adaptive import PatternDecay
import datetime

# Create pattern with decay enabled
pattern = {
    "id": "react_class_components",
    "name": "React Class Component Best Practices",
    "created_at": datetime.datetime(2024, 1, 1),  # 11 months ago
    "last_used": datetime.datetime(2024, 2, 15),  # 9 months ago
    "confidence": 0.92,
    "usage_count": 45,
    "decay_rate": 0.05  # 5% decay per month of disuse
}

decay = PatternDecay()

# Calculate current confidence with decay
current_confidence = decay.calculate_confidence(pattern)

print(f"Pattern: {pattern['name']}")
print(f"  Original confidence: {pattern['confidence']:.2f}")
print(f"  Last used: {pattern['last_used'].strftime('%Y-%m-%d')} (9 months ago)")
print(f"  Current confidence: {current_confidence:.2f}")
print(f"  Decay: {(pattern['confidence'] - current_confidence):.2f} ({(1 - current_confidence/pattern['confidence'])*100:.1f}%)")

# Output:
# Pattern: React Class Component Best Practices
#   Original confidence: 0.92
#   Last used: 2024-02-15 (9 months ago)
#   Current confidence: 0.59
#   Decay: 0.33 (35.9%)

# Pattern is now low-confidence, triggers refresh prompt
if current_confidence < 0.65:
    print(f"\n⚠️ Pattern '{pattern['name']}' has decayed to {current_confidence:.0%}")
    print("   Recommendation: Refresh with current best practices")
    print("   Reason: React has moved to hooks-based patterns since 2024")
```

### Auto-Refresh Stale Patterns

```python
from empathy_os.adaptive import PatternRefresh

refresh = PatternRefresh(empathy)

# When user encounters old pattern
response = empathy.interact(
    user_id="user_123",
    user_input="How do I create a React component?",
    context={"framework": "React"}
)

# System retrieves old "react_class_components" pattern (confidence: 59%)
# Automatically suggests refresh

print(response.response)
# Output:
# "I have a pattern for React components, but it's based on older
#  class-based syntax (last used 9 months ago, confidence: 59%).
#
#  React has since moved to hooks-based functional components.
#  Would you like me to:
#
#  A) Use the old pattern (class components)
#  B) Update the pattern to modern React hooks
#  C) Create a new pattern from scratch
#
#  I recommend option B to keep your codebase modern."

# User chooses B
refresh_result = refresh.update_pattern(
    pattern_id="react_class_components",
    new_approach="hooks_based_functional_components",
    context={
        "old_syntax": "class components with lifecycle methods",
        "new_syntax": "functional components with hooks (useState, useEffect)"
    }
)

print(f"\n✅ Pattern refreshed: {refresh_result['new_name']}")
print(f"   Confidence: {refresh_result['confidence']:.2f}")
# Output:
# ✅ Pattern refreshed: react_hooks_functional_components
#    Confidence: 0.85 (high confidence in modern approach)
```

---

## Part 4: Transfer Learning Across Domains

### Adapt Patterns from One Domain to Another

```python
from empathy_os.adaptive import TransferLearning

transfer = TransferLearning(empathy)

# Pattern learned in software development domain
pattern_software = {
    "domain": "software_development",
    "name": "code_review_checklist",
    "description": "Systematic code review process",
    "steps": [
        "Check for security vulnerabilities (SQL injection, XSS)",
        "Verify test coverage (>80% for critical paths)",
        "Ensure documentation is updated (README, API docs)",
        "Validate performance impact (profiling, benchmarks)",
        "Review error handling (try/catch, error messages)"
    ],
    "success_rate": 0.91,
    "usage_count": 87
}

# User asks about clinical protocol review (healthcare domain)
healthcare_query = {
    "domain": "healthcare",
    "task": "Review clinical protocol for patient handoff",
    "context": "Need systematic checklist for SBAR reports"
}

# Transfer pattern from software → healthcare
adapted_pattern = transfer.adapt_pattern(
    source_pattern=pattern_software,
    target_domain="healthcare",
    target_context=healthcare_query
)

print("Adapted Pattern for Healthcare:")
print(f"  Name: {adapted_pattern['name']}")
print(f"  Domain: {adapted_pattern['domain']}")
print(f"  Steps:")
for i, step in enumerate(adapted_pattern['steps'], 1):
    print(f"    {i}. {step}")

# Output:
# Adapted Pattern for Healthcare:
#   Name: clinical_protocol_review_checklist
#   Domain: healthcare
#   Steps:
#     1. Check for patient safety issues (medication errors, allergies)
#     2. Verify protocol compliance (>80% adherence to clinical guidelines)
#     3. Ensure documentation is complete (SBAR, assessments)
#     4. Validate clinical outcome impact (patient outcomes, metrics)
#     5. Review error handling (escalation procedures, safety nets)

print(f"\n  Transfer confidence: {adapted_pattern['transfer_confidence']:.0%}")
print(f"  Source pattern success rate: {pattern_software['success_rate']:.0%}")
print(f"  Expected success rate: {adapted_pattern['expected_success']:.0%}")

# Output:
#   Transfer confidence: 78%
#   Source pattern success rate: 91%
#   Expected success rate: 71% (lower due to domain shift)
```

### Domain Embeddings for Better Transfer

```python
from empathy_os.adaptive import DomainEmbeddings

embeddings = DomainEmbeddings()

# Create vector representations of domains
domains = {
    "software_development": ["code", "testing", "debugging", "API", "database"],
    "healthcare": ["patient", "clinical", "diagnosis", "treatment", "safety"],
    "legal": ["contract", "compliance", "liability", "precedent", "statute"],
    "finance": ["risk", "portfolio", "trading", "compliance", "audit"]
}

# Calculate domain similarity
similarity = embeddings.calculate_similarity(
    domain1="software_development",
    domain2="healthcare",
    vocabulary1=domains["software_development"],
    vocabulary2=domains["healthcare"]
)

print(f"Domain similarity (software ↔ healthcare): {similarity:.0%}")
# Output: 32% (some overlap: testing/safety, compliance)

# Patterns transfer better between similar domains
similarity_finance = embeddings.calculate_similarity(
    domain1="software_development",
    domain2="finance",
    vocabulary1=domains["software_development"],
    vocabulary2=domains["finance"]
)

print(f"Domain similarity (software ↔ finance): {similarity_finance:.0%}")
# Output: 58% (more overlap: testing/audit, compliance, risk management)

# Transfer learning works better for similar domains
transfer_confidence_healthcare = 0.78  # Lower confidence (32% similarity)
transfer_confidence_finance = 0.88     # Higher confidence (58% similarity)
```

---

## Part 5: User Preference Learning

### Learn User's Working Style

```python
from empathy_os.adaptive import PreferenceLearning

preferences = PreferenceLearning(empathy)

# Track user's preferences over time
interactions = [
    # User prefers concise responses
    {"response_length": "concise", "user_rating": 5},
    {"response_length": "concise", "user_rating": 5},
    {"response_length": "detailed", "user_rating": 3},
    {"response_length": "concise", "user_rating": 4},

    # User prefers code examples over explanations
    {"response_type": "code_example", "user_rating": 5},
    {"response_type": "code_example", "user_rating": 5},
    {"response_type": "explanation", "user_rating": 3},
    {"response_type": "code_example", "user_rating": 5},

    # User prefers proactive suggestions
    {"empathy_level": 3, "user_rating": 5},  # Level 3 (proactive)
    {"empathy_level": 2, "user_rating": 3},  # Level 2 (guided) - too passive
    {"empathy_level": 4, "user_rating": 4},  # Level 4 (anticipatory) - occasionally too much
    {"empathy_level": 3, "user_rating": 5},  # Level 3 is sweet spot
]

for interaction in interactions:
    preferences.record_preference(
        user_id="user_123",
        preference_type=list(interaction.keys())[0],
        value=list(interaction.values())[0],
        rating=interaction.get('user_rating', 3)
    )

# Get learned preferences
learned = preferences.get_preferences(user_id="user_123")

print("Learned User Preferences:")
print(f"  Response length: {learned['response_length']} (avg rating: {learned['response_length_rating']:.1f}/5)")
print(f"  Response type: {learned['response_type']} (avg rating: {learned['response_type_rating']:.1f}/5)")
print(f"  Preferred empathy level: {learned['empathy_level']} (avg rating: {learned['empathy_level_rating']:.1f}/5)")

# Output:
# Learned User Preferences:
#   Response length: concise (avg rating: 4.7/5)
#   Response type: code_example (avg rating: 5.0/5)
#   Preferred empathy level: 3 (avg rating: 5.0/5)

# Apply preferences to future interactions
empathy.apply_preferences(learned)

response = empathy.interact(
    user_id="user_123",
    user_input="How do I handle errors in async functions?",
    context={}
)

# Response automatically uses:
# - Concise format (not verbose)
# - Code example (not long explanation)
# - Level 3 empathy (proactive, not too anticipatory)

print(response.response)
# Output:
# """
# ```python
# async def fetch_data():
#     try:
#         result = await api_call()
#         return result
#     except APIError as e:
#         logger.error(f"API failed: {e}")
#         return None
# ```
#
# I notice you often handle API errors. Would you like me to create
# a reusable error handling decorator? (Level 3: Proactive suggestion)
# """
```

---

## Part 6: Continuous Improvement Metrics

### Track Adaptation Performance

```python
from empathy_os.adaptive import AdaptationMetrics

metrics = AdaptationMetrics(empathy)

# After 30 days of adaptive learning
report = metrics.generate_report(days=30)

print(report.to_markdown())
```

**Output**:
```markdown
# Adaptive Learning Report
## Period: Last 30 days

### Threshold Adaptation
- **Starting threshold**: 0.75 (global default)
- **Current threshold**: 0.71 (personalized)
- **Adjustment count**: 23 (0.77/day)
- **Direction**: Trending down (user accepts lower confidence)

### Per-Pattern Thresholds
| Pattern                            | Threshold | Adjustments | Trend   |
|------------------------------------|-----------|-------------|---------|
| security_vulnerability_detection   | 0.85      | 8           | ↑ Up    |
| code_style_suggestion              | 0.63      | 12          | ↓ Down  |
| performance_optimization           | 0.77      | 5           | → Stable|

### Pattern Decay
- **Patterns decayed**: 5 (out of 47 total patterns)
- **Average decay**: 12.3% confidence loss
- **Patterns refreshed**: 3
- **Patterns archived**: 2 (too old, <30% confidence)

### Transfer Learning
- **Patterns transferred**: 8
- **Success rate**: 75% (6 successful, 2 failed)
- **Top transfers**:
  - software → finance: 3 patterns (88% success)
  - software → healthcare: 2 patterns (65% success)
  - healthcare → legal: 1 pattern (80% success)

### User Preferences
- **Preferences learned**: 7
  - Response length: concise (confidence: 95%)
  - Response type: code_example (confidence: 98%)
  - Empathy level: 3 (confidence: 92%)
  - Language: Python (confidence: 100%)
  - Framework: React (confidence: 87%)
  - Explanation depth: medium (confidence: 78%)
  - Code comments: minimal (confidence: 85%)

### Performance Impact
- **User acceptance rate**:
  - Day 1-7: 68% (baseline, fixed threshold)
  - Day 8-14: 74% (early adaptation)
  - Day 15-21: 81% (preferences learned)
  - Day 22-30: 87% (fully personalized)
- **Improvement**: +28% acceptance rate vs baseline

### Recommendations
✅ **Adaptation working well**: 87% acceptance rate (target: 80%)
⚡ **security_vulnerability_detection** threshold increased to 85% (good - safety-critical)
💡 **Consider**: User prefers Level 3 (proactive) - rarely needs Level 4 (anticipatory)
   → Adjust `target_level=3` for better alignment
```

---

## Part 7: Real-World Scenario

### Complete Adaptive Learning Flow

```python
import asyncio
from empathy_os import EmpathyOS
from empathy_os.adaptive import AdaptiveLearning, PreferenceLearning, TransferLearning

async def adaptive_learning_demo():
    """
    Demonstrate 30-day adaptive learning journey
    """

    # Day 1: Fresh user, default settings
    empathy = EmpathyOS(
        user_id="new_developer",
        target_level=4,
        confidence_threshold=0.75,  # Default
        adaptive_learning=True
    )

    adaptive = AdaptiveLearning(empathy)
    preferences = PreferenceLearning(empathy)
    transfer = TransferLearning(empathy)

    print("Day 1: New user with default settings")
    print(f"  Confidence threshold: {empathy.confidence_threshold}")
    print(f"  Target empathy level: {empathy.target_level}")

    # Simulate 30 days of interactions
    for day in range(1, 31):
        # User has 5-10 interactions per day
        for interaction in range(random.randint(5, 10)):
            # Simulate varied confidence levels
            confidence = random.uniform(0.65, 0.95)

            # User's acceptance depends on:
            # - Confidence (higher = more likely to accept)
            # - Day (as preferences are learned, acceptance improves)
            base_acceptance_prob = 0.68 + (day * 0.006)  # Improves 0.6%/day
            confidence_factor = (confidence - 0.65) / 0.30  # 0-1 based on confidence
            acceptance_prob = min(base_acceptance_prob + (confidence_factor * 0.2), 0.95)

            accepted = random.random() < acceptance_prob

            # Record outcome
            adaptive.record_outcome(
                prediction_id=f"pred_day{day}_{interaction}",
                prediction_confidence=confidence,
                user_action="accepted" if accepted else "rejected",
                outcome="success" if accepted else "failure"
            )

            # Record preference (every 3rd interaction)
            if interaction % 3 == 0:
                preferences.record_preference(
                    user_id="new_developer",
                    preference_type=random.choice(["response_length", "response_type", "empathy_level"]),
                    value=random.choice(["concise", "code_example", 3]),
                    rating=random.randint(3, 5) if accepted else random.randint(1, 3)
                )

        # Weekly reports
        if day % 7 == 0:
            threshold = adaptive.get_threshold(user_id="new_developer")
            prefs = preferences.get_preferences(user_id="new_developer")
            acceptance_rate = adaptive.get_acceptance_rate(user_id="new_developer", days=7)

            print(f"\nDay {day} (Week {day//7}):")
            print(f"  Threshold: {threshold:.2f}")
            print(f"  Acceptance rate (last 7 days): {acceptance_rate:.1%}")
            print(f"  Learned preferences: {len(prefs)} types")

    # Final report
    print("\n" + "="*60)
    print("Day 30: Fully Personalized System")
    print("="*60)

    final_threshold = adaptive.get_threshold(user_id="new_developer")
    final_prefs = preferences.get_preferences(user_id="new_developer")
    final_acceptance = adaptive.get_acceptance_rate(user_id="new_developer", days=30)

    print(f"\nThreshold Evolution:")
    print(f"  Day 1: 0.75 (default)")
    print(f"  Day 30: {final_threshold:.2f} (personalized)")
    print(f"  Change: {final_threshold - 0.75:.2f}")

    print(f"\nAcceptance Rate Evolution:")
    print(f"  Day 1-7: 68% (baseline)")
    print(f"  Day 30: {final_acceptance:.0%} (personalized)")
    print(f"  Improvement: +{(final_acceptance - 0.68)*100:.0f} percentage points")

    print(f"\nLearned Preferences:")
    for pref_type, value in final_prefs.items():
        if not pref_type.endswith('_rating'):
            print(f"  {pref_type}: {value}")

    print(f"\nPerformance Metrics:")
    metrics = adaptive.get_metrics(user_id="new_developer")
    print(f"  Total interactions: {metrics['total_interactions']}")
    print(f"  Threshold adjustments: {metrics['threshold_adjustments']}")
    print(f"  Patterns learned: {metrics['patterns_learned']}")
    print(f"  Patterns transferred: {metrics['patterns_transferred']}")

# Run demo
asyncio.run(adaptive_learning_demo())
```

---

## Performance Impact

**Without Adaptive Learning**:
- Fixed threshold (0.75) for all users
- ~68% acceptance rate (many useful predictions rejected)
- No personalization (one-size-fits-all)

**With Adaptive Learning**:
- Personalized threshold (e.g., 0.71 for flexible users, 0.82 for cautious users)
- ~87% acceptance rate (+28% improvement)
- Full personalization (7+ preference types learned)

**Value**: **28% more useful AI interactions** without overwhelming users

---

## Next Steps

**Enhance adaptive learning**:
1. **Multi-dimensional adaptation**: Adapt based on time of day, task type, stress level
2. **Team-wide learning**: Share preferences across team members with similar roles
3. **A/B testing**: Test new adaptation algorithms on subset of users
4. **Explainable adaptation**: Show users why thresholds changed
5. **Opt-out controls**: Let users override adaptation for specific patterns

**Related examples**:
- [Multi-Agent Coordination](multi-agent-team-coordination.md) - Collective learning
- [Webhook Integration](webhook-integration.md) - Event-driven adaptation
- [Simple Chatbot](simple-chatbot.md) - Trust building basics

---

## Troubleshooting

**"Threshold not adapting"**
- Check: `adaptive_learning=True` in config
- Verify: Calling `adaptive.record_outcome()` after interactions
- Minimum: Need 10+ outcomes before adaptation kicks in

**Adaptation too aggressive**
- Reduce learning rate: `learning_rate=0.01` (default: 0.05)
- Increase stability window: `min_samples=20` (default: 10)

**Pattern decay too fast**
- Lower decay rate: `decay_rate=0.02` (default: 0.05 = 5%/month)
- Extend archive threshold: `archive_threshold=0.20` (default: 0.30)

---

**Questions?** See [Adaptive Learning Guide](../guides/adaptive-learning.md)
