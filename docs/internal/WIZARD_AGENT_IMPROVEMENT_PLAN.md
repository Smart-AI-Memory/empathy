# Wizard & Agent Improvement Plan

**Created:** December 12, 2025
**Status:** PLAN ONLY - Not yet implemented
**Scope:** 55 wizards + 6 agents

---

## Executive Summary

Systematic review of all wizards and agents revealed significant improvement opportunities:

- **74% of wizards** (40/55) are incomplete stubs or lack memory capabilities
- **Only 14%** implement persistent cross-session learning
- **Coach wizards** (20) are template stubs with no real implementation
- **Agents** have sophisticated patterns that wizards should adopt

### Gold Standard Reference

Three wizards represent modern best practices:
- `memory_enhanced_debugging_wizard.py` - Bug correlation with historical patterns
- `tech_debt_wizard.py` - Trajectory analysis with predictions
- `security_learning_wizard.py` - Team decision learning

All other wizards should be upgraded to match these patterns.

---

## Current State Analysis

### Wizard Quality Matrix

| Category | Total | Memory | Async | Level 4 | Quality |
|----------|-------|--------|-------|---------|---------|
| **Software** | 18 | 3 (17%) | 90% | 60% | Mixed |
| **Healthcare** | 18 | 11 (61%)* | 100% | 40% | Good |
| **Coach** | 19 | 0 (0%) | 0% | 0% | **Stubs** |
| **Domain** | 16 | 0 (0%) | 40% | 30% | Mixed |

*Healthcare uses Redis sessions, not cross-session pattern learning

### Agent vs Wizard Comparison

| Aspect | Agents | Wizards |
|--------|--------|---------|
| Purpose | Autonomous multi-step workflows | Guided user decisions |
| State | TypedDict with 50+ fields | Simple input/output |
| Orchestration | LangGraph conditional routing | Linear progression |
| Model Selection | Strategic (Opus/Sonnet) | Single model |
| Pattern Learning | Active extraction & storage | Minimal |
| Error Handling | Sophisticated fallbacks | Linear failure |

---

## Improvement Plan

### Phase 1: Foundation (Weeks 1-2)

#### 1.1 Coach Wizard Implementation
**Scope:** 20 wizards currently stub implementations
**Effort:** High
**Impact:** Critical - these are foundational

**Current state:**
```python
# All coach wizards look like this:
async def analyze(self, context: dict) -> dict:
    pass  # Not implemented
```

**Target state:**
```python
async def analyze(self, context: dict) -> dict:
    # Actual implementation with:
    # - Pattern storage
    # - Issue detection
    # - Predictions
    # - Error handling
```

**Wizards to upgrade:**
1. `security_wizard.py` - Security best practices
2. `performance_wizard.py` - Performance optimization
3. `testing_wizard.py` - Test strategy
4. `refactoring_wizard.py` - Code refactoring
5. `database_wizard.py` - Database design
6. `api_wizard.py` - API design
7. `debugging_wizard.py` - Debugging strategies
8. `scaling_wizard.py` - Scaling patterns
9. `observability_wizard.py` - Logging/metrics
10. `cicd_wizard.py` - Pipeline automation
11. `documentation_wizard.py` - Documentation
12. `compliance_wizard.py` - Compliance
13. `migration_wizard.py` - System migration
14. `monitoring_wizard.py` - Application monitoring
15. `localization_wizard.py` - i18n patterns
16. `accessibility_wizard.py` - WCAG compliance

**Implementation pattern per wizard:**
```python
class SecurityWizard(BaseWizard):
    def __init__(self, pattern_storage_path: str = "./patterns/coach/security"):
        self.pattern_storage = Path(pattern_storage_path)

    async def analyze(self, context: dict) -> dict:
        # 1. Scan code for security issues
        issues = await self._scan_for_issues(context)

        # 2. Correlate with historical patterns
        historical = await self._find_historical_matches(issues)

        # 3. Generate predictions
        predictions = await self._predict_future_issues(issues)

        # 4. Store new patterns
        await self._store_patterns(issues)

        return {
            "issues": issues,
            "historical_matches": historical,
            "predictions": predictions,
            "recommendations": self._generate_recommendations(issues)
        }
```

#### 1.2 Unified Base Class
**Scope:** Create shared foundation for agents and wizards
**Effort:** Medium
**Impact:** High - reduces duplication, enables sharing

**New class hierarchy:**
```
BaseAutonomousComponent
├── BaseAgent (for autonomous workflows)
│   ├── BookProductionAgent
│   ├── ComplianceAgent
│   └── ...
└── BaseWizard (for guided processes)
    ├── MemoryEnhancedWizard
    ├── HealthcareWizard
    └── ...
```

**Shared capabilities:**
- Redis state management
- MemDocs pattern storage
- Audit trail logging
- Error handling patterns
- LangGraph integration hooks

---

### Phase 2: Memory Enhancement (Weeks 3-4)

#### 2.1 Software Wizard Persistence
**Scope:** 7 software wizards lacking memory
**Effort:** Medium
**Impact:** High

**Wizards to upgrade:**
1. `ai_collaboration_wizard.py` - Add collaboration pattern learning
2. `agent_orchestration_wizard.py` - Store orchestration patterns
3. `rag_pattern_wizard.py` - Learn effective RAG configurations
4. `prompt_engineering_wizard.py` - Store prompt effectiveness data
5. `ai_documentation_wizard.py` - Track documentation patterns
6. `multi_model_wizard.py` - Learn model selection strategies
7. `enhanced_testing_wizard.py` - Store test coverage trends

**Implementation:**
```python
# Add to each wizard:
class AICollaborationWizard(BaseWizard):
    async def record_pattern(self, pattern: dict) -> str:
        """Store successful collaboration pattern for future learning."""
        pattern_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pattern_file = self.pattern_storage / f"{pattern_id}.json"

        with open(pattern_file, 'w') as f:
            json.dump({
                "id": pattern_id,
                "pattern": pattern,
                "stored_at": datetime.now().isoformat(),
                "effectiveness_score": None  # Updated after validation
            }, f, indent=2)

        return pattern_id
```

#### 2.2 Healthcare Cross-Session Learning
**Scope:** 11 healthcare wizards with Redis but no pattern learning
**Effort:** Medium-High
**Impact:** High (clinical improvement tracking)

**Add to healthcare wizards:**
- Clinical outcome tracking (like tech_debt trajectory)
- HIPAA-compliant decision recording
- Pattern discovery in audit trail
- Cross-session learning with encryption

**Example - SBAR Wizard enhancement:**
```python
async def record_clinical_outcome(self, sbar_id: str, outcome: dict) -> None:
    """Track clinical outcome for learning and quality improvement."""
    # Encrypt PHI before storage
    encrypted_outcome = self._encrypt_phi(outcome)

    # Store in HIPAA-compliant pattern storage
    await self._store_clinical_pattern({
        "sbar_id": sbar_id,
        "outcome": encrypted_outcome,
        "outcome_date": datetime.now().isoformat(),
        "quality_indicators": self._extract_quality_indicators(outcome)
    })
```

---

### Phase 3: Prediction Enhancement (Weeks 5-6)

#### 3.1 Level 4 Anticipatory Capabilities
**Scope:** All wizards lacking prediction features
**Effort:** High
**Impact:** High - differentiating capability

**Pattern from gold standard:**
```python
def _calculate_trajectory(self, history: list, current: dict) -> dict:
    """Calculate trajectory and predictions from historical data."""
    if len(history) < 2:
        return {"trend": "insufficient_data"}

    # Calculate growth rate
    previous = history[-1]["total"]
    current_total = current["total"]
    change_percent = ((current_total - previous) / previous) * 100

    # Project future
    monthly_rate = change_percent / 30
    projection_30 = int(current_total * (1 + monthly_rate))
    projection_90 = int(current_total * (1 + monthly_rate * 3))

    # Days until critical threshold
    if monthly_rate > 0:
        days_until_2x = int(math.log(2) / math.log(1 + monthly_rate/30) * 30)
    else:
        days_until_2x = None

    return {
        "change_percent": change_percent,
        "trend": "increasing" if change_percent > 5 else "stable",
        "projection_30_days": projection_30,
        "projection_90_days": projection_90,
        "days_until_critical": days_until_2x
    }
```

**Apply to:**
- Security wizards → Security vulnerability trajectory
- Performance wizards → Performance degradation prediction
- Testing wizards → Test coverage trend analysis
- Database wizards → Query performance trajectory
- Healthcare wizards → Clinical outcome predictions

---

### Phase 4: Agent Evolution (Weeks 7-8)

#### 4.1 Wizard → Agent Transformations
**Scope:** Select wizards that should become autonomous agents
**Effort:** High
**Impact:** Medium-High

**Candidates for transformation:**

| Wizard | Agent Version | Rationale |
|--------|---------------|-----------|
| Security Analysis | SecurityMonitorAgent | Continuous monitoring, proactive alerts |
| Testing | TestGenerationAgent | Autonomous test creation, failure learning |
| Performance Profiling | PerformanceAgent | Autonomous optimization |
| Documentation | DocumentationAgent | Maintain docs as code changes |
| Compliance | ComplianceMonitorAgent | Continuous compliance checking |

**Transformation criteria:**
- Can operate without user interaction
- Benefits from continuous monitoring
- Has clear success metrics
- Can learn from outcomes autonomously

#### 4.2 Multi-Agent Orchestration
**Scope:** Create reusable orchestration framework
**Effort:** High
**Impact:** High

**Create AgentOrchestrator class:**
```python
class AgentOrchestrator:
    """Handles multi-agent coordination."""

    def __init__(self):
        self.agent_registry = {}
        self.graph = StateGraph(OrchestratorState)

    def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register agent for orchestration."""
        self.agent_registry[agent_id] = agent

    def create_pipeline(self, agent_sequence: list[str]) -> CompiledGraph:
        """Create execution pipeline from agent sequence."""
        for i, agent_id in enumerate(agent_sequence):
            self.graph.add_node(agent_id, self.agent_registry[agent_id].execute)
            if i > 0:
                prev = agent_sequence[i-1]
                self.graph.add_edge(prev, agent_id)

        return self.graph.compile()

    def execute(self, initial_state: dict) -> dict:
        """Execute the pipeline."""
        return self.pipeline.invoke(initial_state)
```

---

### Phase 5: Quality & Testing (Weeks 9-10)

#### 5.1 Test Suite Creation
**Scope:** Zero tests currently exist for wizards_consolidated
**Effort:** Medium
**Impact:** High

**Test categories:**
```
tests/wizards_consolidated/
├── test_memory_patterns.py      # Pattern storage/retrieval
├── test_async_behavior.py       # Async chain integrity
├── test_error_handling.py       # Error recovery
├── test_predictions.py          # Trajectory calculations
├── test_redis_integration.py    # Redis fallback
└── test_loader.py               # Manifest loader
```

**Target coverage:** 80%+

#### 5.2 Performance Benchmarks
**Scope:** Establish performance baselines
**Effort:** Low
**Impact:** Medium

**Metrics to track:**
- Wizard initialization time
- Analysis execution time
- Pattern storage/retrieval latency
- Redis connection overhead
- Memory usage per wizard

---

## Implementation Priority Matrix

| Priority | Phase | Scope | Effort | Impact | Timeline |
|----------|-------|-------|--------|--------|----------|
| **P0** | 1.1 | Coach wizard implementation | High | Critical | Weeks 1-2 |
| **P0** | 1.2 | Unified base class | Medium | High | Week 2 |
| **P1** | 2.1 | Software wizard persistence | Medium | High | Week 3 |
| **P1** | 2.2 | Healthcare cross-session | Medium-High | High | Week 4 |
| **P2** | 3.1 | Level 4 predictions | High | High | Weeks 5-6 |
| **P2** | 4.1 | Wizard → Agent transforms | High | Medium-High | Weeks 7-8 |
| **P3** | 4.2 | Multi-agent orchestration | High | High | Week 8 |
| **P3** | 5.1 | Test suite | Medium | High | Weeks 9-10 |

---

## Success Metrics

### Before (Current State)
- Memory-enhanced wizards: 3/55 (5%)
- Async coverage: 45%
- Level 4 predictions: 25%
- Test coverage: 0%

### After (Target State)
- Memory-enhanced wizards: 55/55 (100%)
- Async coverage: 100%
- Level 4 predictions: 80%
- Test coverage: 80%

---

## Resource Requirements

### Development Time
- Total estimated: 10 weeks
- Phase 1 (Foundation): 2 weeks
- Phase 2 (Memory): 2 weeks
- Phase 3 (Predictions): 2 weeks
- Phase 4 (Agents): 2 weeks
- Phase 5 (Testing): 2 weeks

### Skills Required
- Python async/await patterns
- LangGraph orchestration
- Redis operations
- Healthcare compliance (HIPAA)
- Test framework (pytest)

---

## Appendix: Detailed Wizard Inventory

### A. Software Wizards (18)

| Wizard | Lines | Memory | Async | Status |
|--------|-------|--------|-------|--------|
| memory_enhanced_debugging_wizard | 711 | ✅ | ✅ | Gold Standard |
| tech_debt_wizard | 735 | ✅ | ✅ | Gold Standard |
| security_learning_wizard | 755 | ✅ | ✅ | Gold Standard |
| advanced_debugging_wizard | 388 | ❌ | Partial | Needs memory |
| ai_collaboration_wizard | 499 | ❌ | Partial | Needs memory |
| performance_profiling_wizard | ~350 | ❌ | ✅ | Needs memory |
| ai_context_wizard | 435 | ❌ | Unknown | Review needed |
| agent_orchestration_wizard | 447 | ❌ | Unknown | Review needed |
| rag_pattern_wizard | 449 | ❌ | Unknown | Needs memory |
| prompt_engineering_wizard | 426 | ❌ | Partial | Needs memory |
| ai_documentation_wizard | 501 | ❌ | Partial | Needs memory |
| book_chapter_wizard | 518 | ❌ | Partial | Needs memory |
| enhanced_testing_wizard | 533 | ❌ | Partial | Needs memory |
| multi_model_wizard | 497 | ❌ | Partial | Needs memory |
| security_analysis_wizard | 321 | ❌ | Unknown | Legacy |
| testing_wizard | ~250 | ❌ | Unknown | Legacy |
| base_wizard | ~200 | N/A | N/A | Base class |

### B. Healthcare Wizards (18)

| Wizard | Lines | Memory | Status |
|--------|-------|--------|--------|
| sbar_wizard | 608 | Redis | Add pattern learning |
| admission_assessment_wizard | 644 | Redis | Add outcome tracking |
| shift_handoff_wizard | 535 | Redis | Add pattern learning |
| soap_note_wizard | 679 | Redis | Add HIPAA audit |
| clinical_assessment | 769 | Redis | Add scoring |
| discharge_summary_wizard | 466 | Redis | Add follow-up tracking |
| patient_education | 654 | Redis | Add personalization |
| quality_improvement | 705 | Redis | Add QI metrics |
| incident_report_wizard | 452 | Redis | Add trend analysis |
| dosage_calculation | 497 | ❌ | Add safety history |
| sbar_report | 323 | ❌ | Add persistence |
| medication_reconciliation | ~400 | Redis | Add drug interaction |
| clinical_protocol_monitor | ~350 | Redis | Add compliance metrics |
| nursing_assessment | ~350 | Redis | Add history |

### C. Coach Wizards (19)

**All are stub implementations requiring full implementation:**

1. security_wizard
2. performance_wizard
3. testing_wizard
4. refactoring_wizard
5. database_wizard
6. api_wizard
7. debugging_wizard
8. scaling_wizard
9. observability_wizard
10. cicd_wizard
11. documentation_wizard
12. compliance_wizard
13. migration_wizard
14. monitoring_wizard
15. localization_wizard
16. accessibility_wizard
17. base_wizard (base class - OK)
18. generate_wizards (utility - OK)

### D. Domain Wizards (16)

| Wizard | Status |
|--------|--------|
| healthcare_wizard | Needs memory |
| finance_wizard | Needs memory |
| legal_wizard | Needs memory |
| hr_wizard | Needs memory |
| education_wizard | Needs memory |
| retail_wizard | Needs memory |
| manufacturing_wizard | Needs memory |
| logistics_wizard | Needs memory |
| insurance_wizard | Needs memory |
| real_estate_wizard | Needs memory |
| government_wizard | Needs memory |
| research_wizard | Needs memory |
| sales_wizard | Needs memory |
| customer_support_wizard | Needs memory |
| accounting_wizard | Needs memory |
| technology_wizard | Needs memory |

---

*This plan is for review and approval. Implementation should not begin until priorities are confirmed.*
