# Agent Improvement Recommendations

A comprehensive evaluation of existing software development agents with recommendations for improvement using the new Agent Factory features.

---

## Executive Summary

The Empathy Framework contains **35+ agent/wizard implementations** across several categories. This document evaluates each major agent type and provides actionable recommendations for leveraging the new Agent Factory, ModelRouter, and workflow capabilities.

**Priority Legend:**
- 🔴 **Critical** - High impact, immediate value
- 🟡 **Recommended** - Medium impact, should implement
- 🟢 **Nice-to-have** - Low impact, consider for polish

---

## 1. Code Inspection Agent

**Location:** `agents/code_inspection/agent.py`

### Current State
- Uses LangGraph StateGraph directly
- Multi-phase orchestration (5 phases)
- Parallel execution for static analysis
- Pattern learning integration

### Recommendations

| Priority | Recommendation | Expected Benefit |
|----------|----------------|------------------|
| 🔴 | **Migrate to Agent Factory LangGraph adapter** | Framework-agnostic, easier testing, unified interface |
| 🔴 | **Add Model Tier Routing per phase** | Cost savings: Use Haiku for lint parsing, Sonnet for analysis, Opus only for synthesis |
| 🟡 | **Use AgentFactory.create_code_review_pipeline()** | Simplify orchestration code |
| 🟡 | **Add cost tracking** | ROI visibility for code inspections |
| 🟢 | **Enable framework switching** | Allow LangChain users to run same inspections |

### Implementation Sketch

```python
# Before: Direct LangGraph implementation
from langgraph.graph import StateGraph
graph = StateGraph(InspectionState)
graph.add_node("static_analysis", static_analysis_node)
# ... 200+ lines of graph setup

# After: Using Agent Factory
from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

factory = AgentFactory(framework=Framework.LANGGRAPH)

# Phase agents with optimized model tiers
linter = factory.create_agent(
    name="linter",
    role="analyzer",
    model_tier="cheap",  # Haiku for parsing
    system_prompt="Parse lint output and categorize findings"
)

security_analyzer = factory.create_agent(
    name="security",
    role="security",
    model_tier="capable",  # Sonnet for analysis
    system_prompt="Analyze code for security vulnerabilities"
)

synthesizer = factory.create_agent(
    name="synthesizer",
    role="coordinator",
    model_tier="premium",  # Opus for synthesis
    system_prompt="Synthesize all findings into actionable report"
)

pipeline = factory.create_workflow(
    name="code_inspection",
    agents=[linter, security_analyzer, synthesizer],
    mode="graph"
)
```

**Estimated Cost Savings:** 40-60% by using Haiku for parsing phases

---

## 2. Compliance Anticipation Agent

**Location:** `agents/compliance_anticipation_agent.py`

### Current State
- LangGraph StateGraph implementation
- Level 4 anticipatory intelligence
- Audit prediction and gap detection

### Recommendations

| Priority | Recommendation | Expected Benefit |
|----------|----------------|------------------|
| 🔴 | **Add model tier routing for different phases** | Prediction (Opus) vs notification (Haiku) |
| 🟡 | **Migrate to Agent Factory** | Unified management with other agents |
| 🟡 | **Add workflow checkpointing** | Resume interrupted compliance checks |
| 🟢 | **Enable multi-framework support** | Allow AutoGen for stakeholder conversations |

### Model Tier Optimization

```python
# Optimal model allocation for compliance phases
PHASE_TIERS = {
    "predict_audit": "premium",    # Opus - Complex prediction
    "detect_gaps": "capable",      # Sonnet - Pattern matching
    "generate_package": "capable", # Sonnet - Document generation
    "notify_stakeholders": "cheap" # Haiku - Simple messaging
}
```

**Estimated Cost Savings:** 30-40%

---

## 3. Book Production Agents

**Location:** `agents/book_production/base.py`

### Current State
- 4 specialized agents (Research, Writer, Editor, Reviewer)
- Redis state management
- MemDocs pattern storage
- Manual model selection (Opus for creative, Sonnet for structured)

### Recommendations

| Priority | Recommendation | Expected Benefit |
|----------|----------------|------------------|
| 🔴 | **Use AgentFactory convenience methods** | `factory.create_researcher()`, `create_writer()`, etc. |
| 🔴 | **Use create_research_pipeline()** | Pre-built workflow matches existing pattern |
| 🟡 | **Add cost tracking per chapter** | ROI visibility for content production |
| 🟡 | **Enable streaming output** | Better UX for long-running tasks |
| 🟢 | **Add parallel research capability** | Research multiple topics concurrently |

### Implementation Sketch

```python
# Before: Manual agent creation
from agents.book_production import ResearchAgent, WriterAgent, EditorAgent

research = ResearchAgent(model="opus")
writer = WriterAgent(model="opus")
editor = EditorAgent(model="sonnet")

# After: Using Agent Factory
factory = AgentFactory(framework="native")

pipeline = factory.create_research_pipeline(
    topic=chapter_topic,
    include_reviewer=True
)

# Or custom configuration
research = factory.create_researcher(model_tier="capable")  # Sonnet
writer = factory.create_writer(model_tier="premium")        # Opus
editor = factory.create_agent(name="editor", role="editor", model_tier="capable")
reviewer = factory.create_reviewer(model_tier="capable")

content_pipeline = factory.create_workflow(
    name="book_chapter",
    agents=[research, writer, editor, reviewer],
    mode="sequential"
)
```

**Estimated Cost Savings:** 25% by using Sonnet for research/review

---

## 4. Coach Development Wizards (15)

**Location:** `examples/coach/wizards/`

### Current State
- Role-based context management
- Risk tracking and mitigation
- Manual model configuration

### Recommendations

| Priority | Recommendation | Expected Benefit |
|----------|----------------|------------------|
| 🔴 | **Create wizard-to-agent adapter** | Wrap existing wizards in Agent Factory interface |
| 🔴 | **Add per-wizard model tier defaults** | Optimize costs based on wizard complexity |
| 🟡 | **Enable wizard composition in workflows** | Chain wizards for complex tasks |
| 🟡 | **Add pattern learning hooks** | Learn from wizard interactions |
| 🟢 | **Create workflow templates** | Pre-built wizard combinations |

### Wizard Model Tier Recommendations

| Wizard | Recommended Tier | Rationale |
|--------|------------------|-----------|
| DebuggingWizard | capable | Pattern matching, hypothesis generation |
| SecurityWizard | capable | Vulnerability pattern detection |
| PerformanceWizard | capable | Profiling analysis |
| TestingWizard | capable | Test case generation |
| RefactoringWizard | capable | Code transformation |
| DatabaseWizard | capable | Schema optimization |
| APIWizard | capable | Contract design |
| DevOpsWizard | capable | Configuration generation |
| DocumentationWizard | cheap | Template-based generation |
| MonitoringWizard | cheap | Dashboard configuration |
| AccessibilityWizard | capable | WCAG pattern matching |
| ComplianceWizard | capable | Regulatory analysis |
| DesignReviewWizard | premium | Architecture decisions |
| RetrospectiveWizard | cheap | Structured facilitation |
| OnboardingWizard | cheap | Process documentation |

### Implementation: Wizard Adapter

```python
# New file: empathy_llm_toolkit/agent_factory/adapters/wizard_adapter.py

from empathy_llm_toolkit.agent_factory.base import BaseAgent, AgentConfig

class WizardAdapter(BaseAgent):
    """Adapt existing wizards to Agent Factory interface."""

    def __init__(self, wizard_class, config: AgentConfig):
        super().__init__(config)
        self._wizard = wizard_class(config=self._build_wizard_config())

    async def invoke(self, input_data, context=None):
        result = await self._wizard.process(input_data, context)
        return {
            "output": result.get("response"),
            "metadata": {
                "wizard": self._wizard.__class__.__name__,
                "empathy_level": result.get("level"),
                "risks": result.get("risks", [])
            }
        }
```

**Estimated Cost Savings:** 50% by right-sizing wizard model tiers

---

## 5. Software Plugin Wizards (18+)

**Location:** `empathy_software_plugin/wizards/`

### Current State
- Most advanced wizard implementations
- Level 4 anticipatory capabilities
- Security patterns and learning

### High-Priority Improvements

| Wizard | Priority | Recommendation |
|--------|----------|----------------|
| AdvancedDebuggingWizard | 🔴 | Add memory-enhanced debugging via Agent Factory |
| SecurityAnalysisWizard | 🔴 | Chain with PatternRetrieverWizard for context |
| TechDebtWizard | 🟡 | Add cost tracking to show debt vs development cost |
| CodeReviewWizard | 🔴 | Migrate to Agent Factory parallel workflow |
| PerformanceProfilingWizard | 🟡 | Add model routing (Haiku for parsing, Sonnet for analysis) |
| MultiModelWizard | 🔴 | Integrate with ModelRouter for automatic selection |
| RAGPatternWizard | 🟡 | Enable Haystack adapter for production RAG |

### CodeReviewWizard Workflow Upgrade

```python
# Enhanced code review using Agent Factory
factory = AgentFactory(framework="langgraph")

# Create specialized review agents
security = factory.create_agent(
    name="security_review",
    role="security",
    model_tier="capable",
    capabilities=[AgentCapability.CODE_EXECUTION]
)

quality = factory.create_agent(
    name="quality_review",
    role="reviewer",
    model_tier="capable"
)

performance = factory.create_agent(
    name="performance_review",
    role="reviewer",
    model_tier="capable",
    system_prompt="Analyze code for performance issues"
)

# Parallel review workflow
review_pipeline = factory.create_workflow(
    name="comprehensive_review",
    agents=[security, quality, performance],
    mode="parallel"  # All reviews run concurrently
)

# Add synthesis coordinator
synthesizer = factory.create_coordinator(
    system_prompt="Synthesize all review findings into prioritized action items"
)

# Final pipeline
full_review = factory.create_workflow(
    name="code_review_with_synthesis",
    agents=[review_pipeline, synthesizer],
    mode="sequential"
)
```

---

## 6. Domain Wizards

**Location:** `empathy_llm_toolkit/wizards/`

### Current State
- TechnologyWizard, HealthcareWizard, CustomerSupportWizard
- Security-aware with PII scrubbing
- Classification system (PUBLIC, INTERNAL, SENSITIVE)

### Recommendations

| Priority | Recommendation | Expected Benefit |
|----------|----------------|------------------|
| 🔴 | **Add domain-specific model routing** | Healthcare uses higher tier for accuracy |
| 🟡 | **Create domain-specific workflows** | Pre-built pipelines per domain |
| 🟡 | **Enable multi-framework for RAG** | Haystack for healthcare document retrieval |
| 🟢 | **Add domain-specific cost limits** | Budget controls per domain |

### Healthcare Wizard Model Routing

```python
# Healthcare requires higher accuracy - default to premium for patient safety
HEALTHCARE_TIER_OVERRIDES = {
    "diagnosis_support": "premium",    # Opus - Patient safety critical
    "treatment_protocol": "premium",   # Opus - Accuracy paramount
    "documentation": "capable",        # Sonnet - Structured output
    "scheduling": "cheap"              # Haiku - Simple operations
}
```

---

## 7. New Agent Recommendations

Based on the analysis, these new agents would add significant value:

### A. Smart Debugging Pipeline

```python
# Combines multiple debugging approaches
factory = AgentFactory()

pipeline = factory.create_workflow(
    name="smart_debugging",
    agents=[
        factory.create_agent(
            name="error_parser",
            role="analyzer",
            model_tier="cheap",
            system_prompt="Parse error logs and stack traces"
        ),
        factory.create_agent(
            name="hypothesis_generator",
            role="researcher",
            model_tier="capable",
            system_prompt="Generate hypotheses for root cause"
        ),
        factory.create_agent(
            name="fix_proposer",
            role="debugger",
            model_tier="capable",
            capabilities=[AgentCapability.CODE_EXECUTION]
        ),
        factory.create_agent(
            name="test_generator",
            role="tester",
            model_tier="capable",
            system_prompt="Generate regression tests for the fix"
        )
    ],
    mode="sequential"
)
```

### B. PR Review Agent

```python
# Comprehensive PR review with parallel analysis
factory = AgentFactory(framework="langgraph")

pr_review = factory.create_workflow(
    name="pr_review",
    agents=[
        # Parallel analysis phase
        factory.create_agent(name="diff_analyzer", model_tier="capable"),
        factory.create_agent(name="test_coverage", model_tier="cheap"),
        factory.create_agent(name="security_scan", model_tier="capable"),
        factory.create_agent(name="style_check", model_tier="cheap"),
    ],
    mode="parallel"
)
```

### C. Incident Response Agent

```python
# Level 4 anticipatory incident handling
factory = AgentFactory()

incident_agent = factory.create_workflow(
    name="incident_response",
    agents=[
        factory.create_agent(
            name="triage",
            model_tier="cheap",  # Fast initial assessment
            system_prompt="Quickly categorize and prioritize incident"
        ),
        factory.create_agent(
            name="root_cause",
            model_tier="premium",  # Deep analysis
            system_prompt="Identify root cause and blast radius"
        ),
        factory.create_agent(
            name="remediation",
            model_tier="capable",
            system_prompt="Propose and validate remediation steps"
        )
    ]
)
```

---

## 8. Implementation Priority Matrix

### Phase 1: Quick Wins (Week 1-2)

| Task | Impact | Effort |
|------|--------|--------|
| Add model tier routing to existing wizards | High | Low |
| Create WizardAdapter for Agent Factory | High | Medium |
| Add cost tracking to Code Inspection Agent | Medium | Low |
| Update documentation with tier recommendations | Medium | Low |

### Phase 2: Core Migrations (Week 3-4)

| Task | Impact | Effort |
|------|--------|--------|
| Migrate Code Inspection Agent to Agent Factory | High | Medium |
| Migrate Book Production Agents to Agent Factory | High | Medium |
| Create pre-built workflow templates | Medium | Medium |

### Phase 3: Advanced Features (Week 5-6)

| Task | Impact | Effort |
|------|--------|--------|
| Migrate Compliance Agent with checkpointing | High | High |
| Enable multi-framework support for RAG wizards | Medium | Medium |
| Create Smart Debugging Pipeline | High | Medium |
| Create PR Review Agent | High | Medium |

### Phase 4: Polish (Week 7+)

| Task | Impact | Effort |
|------|--------|--------|
| Add streaming support to all agents | Medium | Medium |
| Create domain-specific cost limits | Low | Low |
| Build visual dashboard for agent monitoring | Medium | High |

---

## 9. Expected ROI Summary

| Improvement Area | Expected Cost Savings | Development Time |
|------------------|----------------------|------------------|
| Model Tier Routing | 40-60% | 1 week |
| Agent Factory Migration | 10-20% (reduced maintenance) | 2 weeks |
| Parallel Workflows | 30% faster execution | 1 week |
| Pattern Learning Integration | 15% fewer repeat errors | Ongoing |

**Total Estimated API Cost Savings:** 40-60% when fully implemented

---

## 10. Next Steps

1. **Immediate:** Add model tier routing to existing agents (no migration needed)
2. **Short-term:** Create WizardAdapter to wrap existing wizards
3. **Medium-term:** Migrate Code Inspection and Book Production to Agent Factory
4. **Long-term:** Build new specialized agents using Agent Factory patterns

---

---

## Appendix A: Best Practices Assessment

### Evaluation Criteria

Each agent was evaluated against these software engineering best practices:

| Category | Criteria |
|----------|----------|
| **SOLID Principles** | Single responsibility, Open/closed, Dependency inversion |
| **Clean Code** | Readability, naming, function size, comments |
| **Error Handling** | Comprehensive try/catch, graceful degradation, retries |
| **Testing** | Unit test coverage, mocking capability, test isolation |
| **Type Safety** | Type hints, runtime validation, Pydantic/dataclasses |
| **Documentation** | Docstrings, usage examples, architectural notes |
| **Security** | Input validation, secrets handling, audit logging |
| **Performance** | Async patterns, caching, connection pooling |

---

### Agent-by-Agent Assessment

#### 1. Code Inspection Agent (`agents/code_inspection/agent.py`)

| Category | Score | Notes |
|----------|-------|-------|
| SOLID | ⭐⭐⭐⭐ | Good separation of nodes, but routing logic could be more modular |
| Clean Code | ⭐⭐⭐⭐⭐ | Excellent readability, clear naming conventions |
| Error Handling | ⭐⭐⭐ | LangGraph fallback good, but individual node errors not handled |
| Testing | ⭐⭐⭐ | Can mock LangGraph, but node functions need isolation |
| Type Safety | ⭐⭐⭐⭐ | Uses TypedDict for state, could add Pydantic validation |
| Documentation | ⭐⭐⭐⭐⭐ | Excellent docstrings and architectural comments |
| Security | ⭐⭐⭐⭐ | No PII concerns, good logging hygiene |
| Performance | ⭐⭐⭐⭐ | Parallel mode flag good, async throughout |

**Strengths:**
- ✅ Clean modular architecture with separate node functions
- ✅ Graceful fallback when LangGraph unavailable
- ✅ Multiple output format support (JSON, SARIF, HTML)
- ✅ Pattern learning integration

**Improvements Needed:**
```python
# Current: No error handling in nodes
state = await run_static_analysis(state)

# Recommended: Wrap each phase with error handling
async def _run_phase_safely(self, phase_func, state, phase_name):
    try:
        return await phase_func(state)
    except Exception as e:
        logger.error(f"Phase {phase_name} failed: {e}")
        state["errors"].append({"phase": phase_name, "error": str(e)})
        state["health_status"] = "degraded"
        return state
```

---

#### 2. Compliance Anticipation Agent (`agents/compliance_anticipation_agent.py`)

| Category | Score | Notes |
|----------|-------|-------|
| SOLID | ⭐⭐⭐⭐ | Functions are focused, but state class is monolithic |
| Clean Code | ⭐⭐⭐⭐⭐ | Exceptional documentation, clear phase separation |
| Error Handling | ⭐⭐⭐⭐ | Has errors/warnings in state, audit trail |
| Testing | ⭐⭐⭐ | Uses `import random` for simulation - should be injected |
| Type Safety | ⭐⭐⭐⭐⭐ | Comprehensive TypedDict with all fields |
| Documentation | ⭐⭐⭐⭐⭐ | Best-in-class documentation with design philosophy |
| Security | ⭐⭐⭐⭐⭐ | Healthcare-appropriate, audit trail, no hardcoded secrets |
| Performance | ⭐⭐⭐ | No caching, no connection pooling for external services |

**Strengths:**
- ✅ Exceptional state management design
- ✅ Comprehensive audit trail for compliance
- ✅ Level 4 anticipatory logic well-implemented
- ✅ Clear phase separation with edge routing

**Improvements Needed:**
```python
# Current: Simulation logic inline
import random
is_compliant = random.random() < 0.90

# Recommended: Dependency injection for testability
class ComplianceDataSource(ABC):
    @abstractmethod
    async def check_compliance(self, hospital_id: str, requirement: dict) -> bool:
        pass

class MockComplianceDataSource(ComplianceDataSource):
    """For testing"""
    async def check_compliance(self, hospital_id: str, requirement: dict) -> bool:
        return random.random() < 0.90

class EHRComplianceDataSource(ComplianceDataSource):
    """Production: queries actual EHR system"""
    async def check_compliance(self, hospital_id: str, requirement: dict) -> bool:
        # Real implementation
        pass
```

---

#### 3. Book Production Base Agent (`agents/book_production/base.py`)

| Category | Score | Notes |
|----------|-------|-------|
| SOLID | ⭐⭐⭐⭐⭐ | Excellent ABC pattern, clear specialization (Opus/Sonnet) |
| Clean Code | ⭐⭐⭐⭐ | Good structure, but has duplicate AgentConfig |
| Error Handling | ⭐⭐⭐⭐ | Retry logic, connection error handling |
| Testing | ⭐⭐⭐⭐⭐ | LLM provider injection, Redis mock-friendly |
| Type Safety | ⭐⭐⭐⭐ | Dataclasses for config, could use Pydantic |
| Documentation | ⭐⭐⭐⭐ | Good docstrings, design philosophy noted |
| Security | ⭐⭐⭐⭐ | API key from env var, no secrets in logs |
| Performance | ⭐⭐⭐⭐ | Lazy initialization, async Redis |

**Strengths:**
- ✅ Best dependency injection pattern in codebase
- ✅ Clear OpusAgent/SonnetAgent specialization
- ✅ Redis and MemDocs abstraction
- ✅ Comprehensive audit trail support

**Improvements Needed:**
```python
# Current: Duplicate AgentConfig (conflicts with Agent Factory)
@dataclass
class AgentConfig:  # In book_production/base.py
    model: str = "claude-sonnet-4-20250514"
    ...

# From agent_factory/base.py
@dataclass
class AgentConfig:  # Different fields!
    name: str
    role: AgentRole
    ...

# Recommended: Unify or namespace
from empathy_llm_toolkit.agent_factory.base import AgentConfig as FactoryAgentConfig

@dataclass
class BookProductionConfig:
    """Book production specific config, extends factory config."""
    factory_config: FactoryAgentConfig
    memdocs_config: MemDocsConfig
    redis_config: RedisConfig
```

---

#### 4. Advanced Debugging Wizard (`empathy_software_plugin/wizards/advanced_debugging_wizard.py`)

| Category | Score | Notes |
|----------|-------|-------|
| SOLID | ⭐⭐⭐⭐⭐ | Clean separation: parsing, analysis, fixing, verification |
| Clean Code | ⭐⭐⭐⭐⭐ | Modular sub-modules, clear naming |
| Error Handling | ⭐⭐⭐ | Returns error dict, but doesn't handle parse failures |
| Testing | ⭐⭐⭐⭐ | Each sub-module testable independently |
| Type Safety | ⭐⭐⭐⭐ | LintIssue dataclass, typed returns |
| Documentation | ⭐⭐⭐⭐ | Good docstrings, phase documentation |
| Security | ⭐⭐⭐⭐ | No file writes without explicit request |
| Performance | ⭐⭐⭐⭐ | Could parallelize multi-linter parsing |

**Strengths:**
- ✅ Best modular design among wizards
- ✅ Level 4/5 features well-implemented
- ✅ Cross-language pattern detection
- ✅ Trajectory analysis is production-ready

**Improvements Needed:**
```python
# Current: Sequential linter parsing
for linter_name, output_source in linters.items():
    issues = parse_linter_output(linter_name, output)
    all_issues.extend(issues)

# Recommended: Parallel parsing for performance
async def _parse_all_linters(self, linters: dict) -> list[LintIssue]:
    async def parse_one(name, output):
        return parse_linter_output(name, output)

    tasks = [parse_one(n, o) for n, o in linters.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_issues = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Linter parse failed: {result}")
        else:
            all_issues.extend(result)
    return all_issues
```

---

#### 5. Software Plugin Base Wizard (`empathy_software_plugin/wizards/base_wizard.py`)

| Category | Score | Notes |
|----------|-------|-------|
| SOLID | ⭐⭐⭐⭐⭐ | Perfect ABC implementation, single responsibilities |
| Clean Code | ⭐⭐⭐⭐⭐ | Excellent organization of caching, sharing, staging |
| Error Handling | ⭐⭐⭐⭐ | Graceful handling when Redis unavailable |
| Testing | ⭐⭐⭐⭐⭐ | Optional Redis injection, all methods return bool |
| Type Safety | ⭐⭐⭐⭐⭐ | Full type hints, AgentCredentials dataclass |
| Documentation | ⭐⭐⭐⭐⭐ | Excellent docstrings with examples |
| Security | ⭐⭐⭐⭐⭐ | AccessTier control, credential system |
| Performance | ⭐⭐⭐⭐ | Caching built-in, TTL configurable |

**This is the gold standard for the codebase.**

**Minor Improvements:**
```python
# Current: Cache key uses MD5
hash_val = hashlib.md5(context_str.encode(), usedforsecurity=False).hexdigest()[:12]

# Recommended: Use faster hash for non-security purposes
import xxhash  # Much faster for cache keys
hash_val = xxhash.xxh64(context_str.encode()).hexdigest()[:12]
```

---

### Summary: Best Practices Ranking

| Agent/Wizard | Overall Score | Primary Strength | Primary Gap |
|--------------|---------------|------------------|-------------|
| Software Plugin Base Wizard | ⭐⭐⭐⭐⭐ | Architecture pattern | None significant |
| Advanced Debugging Wizard | ⭐⭐⭐⭐½ | Modular design | Error handling |
| Compliance Anticipation Agent | ⭐⭐⭐⭐ | Documentation | Testability |
| Code Inspection Agent | ⭐⭐⭐⭐ | LangGraph integration | Error handling |
| Book Production Base Agent | ⭐⭐⭐⭐ | DI pattern | Config duplication |

---

### Recommended Architectural Improvements

#### 1. Unified Configuration Layer

Create a single source of truth for agent configuration:

```python
# empathy_llm_toolkit/config/unified.py

from pydantic import BaseModel, Field

class UnifiedAgentConfig(BaseModel):
    """Single configuration model for all agents."""

    # Identity
    name: str
    role: str = "custom"

    # Model selection
    model_tier: Literal["cheap", "capable", "premium"] = "capable"
    model_override: str | None = None
    provider: str = "anthropic"

    # Empathy
    empathy_level: int = Field(ge=1, le=5, default=4)

    # Features
    memory_enabled: bool = True
    pattern_learning: bool = True
    cost_tracking: bool = True

    # LLM params
    temperature: float = 0.7
    max_tokens: int = 4096

    # Extensions
    extra: dict = {}
```

#### 2. Error Handling Decorator

Standardize error handling across all agents:

```python
# empathy_llm_toolkit/agent_factory/decorators.py

from functools import wraps

def safe_agent_operation(operation_name: str):
    """Decorator for safe agent operations with logging."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"{operation_name} failed: {e}")
                self.add_audit_entry(
                    state=kwargs.get("state", {}),
                    action=f"{operation_name}_error",
                    details={"error": str(e), "type": type(e).__name__}
                )
                raise AgentOperationError(operation_name, e) from e
        return wrapper
    return decorator
```

#### 3. Agent Factory Integration for Wizards

Create a bridge between wizards and Agent Factory:

```python
# empathy_llm_toolkit/agent_factory/wizard_bridge.py

class WizardToAgentBridge(BaseAgent):
    """Bridge existing wizards to Agent Factory interface."""

    def __init__(self, wizard: BaseWizard, config: AgentConfig):
        super().__init__(config)
        self._wizard = wizard

    async def invoke(self, input_data, context=None):
        result = await self._wizard.analyze({
            "input": input_data,
            **(context or {})
        })
        return {
            "output": result.get("recommendations", []),
            "metadata": {
                "predictions": result.get("predictions", []),
                "confidence": result.get("confidence", 0.0),
                "level": self._wizard.level
            }
        }
```

---

### Implementation Roadmap

| Week | Action | Files Affected | Effort |
|------|--------|----------------|--------|
| 1 | Create UnifiedAgentConfig | New file + imports | Low |
| 1 | Add error handling decorator | New file | Low |
| 2 | Update Code Inspection Agent with error handling | 1 file | Medium |
| 2 | Create WizardToAgentBridge | New file | Medium |
| 3 | Refactor Compliance Agent for testability | 1 file | Medium |
| 3 | Resolve AgentConfig duplication | 2 files | Low |
| 4 | Add parallel parsing to Debugging Wizard | 1 file | Low |

---

*Document generated: December 2025*
*Empathy Framework v2.3.0*
