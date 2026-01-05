# XML Enhancement Specification - Raw Response

<thinking>
Let me analyze the requirements and context systematically:

1. **Current State Analysis:**
   - xml_enhanced_crew.py exists with XMLAgent, XMLTask, parse_xml_response()
   - manage_documentation.py already migrated (Phase 1 complete)
   - 10 workflows need migration
   - 5,941 passing tests, 64% coverage target
   - Python 3.10+, production-ready framework

2. **Requirements Breakdown:**
   - All 6 options in parallel (4-6 hour timeline)
   - use_xml_structure=True by default with opt-out
   - Local metrics storage (.empathy/prompt_metrics.json)
   - Moderate compression for optimization
   - Simple heuristic for task complexity
   - Multi-language support (ES, FR, DE) with English tags

3. **Architecture Considerations:**
   - Backward compatibility is critical
   - Feature flags for gradual rollout
   - Hybrid TDD approach
   - Type hints required
   - Follow existing patterns

4. **Implementation Strategy:**
   - Phase 1: Core infrastructure (metrics, adaptive agent, config)
   - Phase 2: Prove pattern with 3 workflows
   - Phase 3: Advanced features (validation, optimization, i18n)
   - Phase 4: Complete migration and testing

5. **Key Technical Decisions:**
   - Use dataclasses for metrics and configuration
   - XSD schemas for validation with graceful fallback
   - Configurable compression levels
   - Token-based complexity scoring
   - Translation dictionaries for i18n

Let me now create a comprehensive implementation plan.
</thinking>

<answer>
# XML Enhancement Implementation Plan
## Empathy Framework v3.6.0 - Comprehensive Technical Specification

---

## 1. Executive Summary

This document provides a complete implementation plan for enhancing the Empathy Framework's XML prompting capabilities across 6 major options. The implementation will be completed in 4 phases over 4-6 hours, maintaining backward compatibility while establishing XML-enhanced prompting as the default approach.

**Key Deliverables:**
- 10 workflows migrated to XML-enhanced prompting
- XML schema validation with graceful fallback
- Prompt performance tracking and metrics dashboard
- Context window optimization (20-30% token reduction)
- Dynamic prompt adaptation based on task complexity
- Multi-language support (EN, ES, FR, DE)

**Success Criteria:**
- All workflows use XMLAgent/XMLTask by default
- <5% performance regression
- >95% XML parsing success rate
- Metrics collection operational
- Test coverage maintained at 64%+

---

## 2. Technical Architecture

### 2.1 Option 1: Comprehensive Workflow Migration

**Objective:** Migrate all 10 LLM-using workflows to xml_enhanced_crew.py pattern

**Architecture:**

```python
# Pattern for all workflow migrations
from empathy.xml_enhanced_crew import XMLAgent, XMLTask, parse_xml_response

class WorkflowXMLCrew:
    """Base pattern for XML-enhanced workflows"""

    def __init__(self, use_xml_structure: bool = True):
        self.use_xml_structure = use_xml_structure

    def create_agents(self) -> List[XMLAgent]:
        """Create XML-enhanced agents"""
        pass

    def create_tasks(self) -> List[XMLTask]:
        """Create XML-enhanced tasks"""
        pass

    def execute(self) -> Dict[str, Any]:
        """Execute workflow with XML parsing"""
        pass
```

**Files to Create:**
- None (use existing xml_enhanced_crew.py)

**Files to Modify:**

1. **src/empathy/workflows/code_review.py**
   - Replace `CodeReviewCrew` with XML-enhanced version
   - Add `use_xml_structure` parameter (default True)
   - Update agent prompts to use XML tags
   - Modify task outputs to parse XML responses

2. **src/empathy/workflows/bug_predict.py**
   - Replace `BugPredictionCrew` with XML-enhanced version
   - Add structured XML output for bug predictions
   - Include confidence scores in XML format

3. **src/empathy/workflows/test_gen.py**
   - Replace `TestGenerationCrew` with XML-enhanced version
   - Structure test cases in XML format
   - Add test metadata tags

4. **src/empathy/workflows/refactor_plan.py**
   - Replace `RefactorPlanCrew` with XML-enhanced version
   - Structure refactoring steps in XML
   - Add risk assessment tags

5. **src/empathy/workflows/security_audit.py**
   - Replace `SecurityAuditCrew` with XML-enhanced version
   - Structure vulnerabilities in XML format
   - Add severity and remediation tags

6. **src/empathy/workflows/document_gen.py**
   - Replace `DocumentationCrew` with XML-enhanced version
   - Structure documentation sections in XML
   - Add metadata tags

7. **src/empathy/workflows/research_synthesis.py**
   - Replace `ResearchCrew` with XML-enhanced version
   - Structure findings in XML format
   - Add source citation tags

8. **src/empathy/workflows/perf_audit.py**
   - Replace `PerformanceAuditCrew` with XML-enhanced version
   - Structure performance metrics in XML
   - Add optimization recommendation tags

9. **src/empathy/workflows/pr_review.py**
   - Replace `PRReviewCrew` with XML-enhanced version
   - Structure review comments in XML
   - Add approval/rejection tags

10. **src/empathy/workflows/release_prep.py**
    - Replace `ReleasePrepCrew` with XML-enhanced version
    - Structure release checklist in XML
    - Add readiness status tags

**Migration Pattern Example (code_review.py):**

```python
# Before
class CodeReviewCrew:
    def __init__(self):
        self.reviewer = Agent(
            role="Code Reviewer",
            goal="Review code for quality",
            backstory="Expert reviewer",
            llm=ChatOpenAI(model="gpt-4")
        )

# After
from empathy.xml_enhanced_crew import XMLAgent, XMLTask, parse_xml_response

class CodeReviewCrew:
    def __init__(self, use_xml_structure: bool = True):
        self.use_xml_structure = use_xml_structure
        self.reviewer = XMLAgent(
            role="Code Reviewer",
            goal="Review code for quality",
            backstory="Expert reviewer",
            llm=ChatOpenAI(model="gpt-4"),
            use_xml_structure=use_xml_structure
        )

    def create_review_task(self, code: str) -> XMLTask:
        return XMLTask(
            description=f"Review the following code:\n{code}",
            expected_output="""
            <code_review>
                <thinking>Analysis process</thinking>
                <answer>
                    <issues>
                        <issue severity="high|medium|low">
                            <description>Issue description</description>
                            <location>File:Line</location>
                            <recommendation>Fix recommendation</recommendation>
                        </issue>
                    </issues>
                    <summary>Overall assessment</summary>
                </answer>
            </code_review>
            """,
            agent=self.reviewer,
            use_xml_structure=self.use_xml_structure
        )
```

**Tests to Create:**
- `tests/workflows/test_code_review_xml.py`
- `tests/workflows/test_bug_predict_xml.py`
- `tests/workflows/test_test_gen_xml.py`
- `tests/workflows/test_refactor_plan_xml.py`
- `tests/workflows/test_security_audit_xml.py`
- `tests/workflows/test_document_gen_xml.py`
- `tests/workflows/test_research_synthesis_xml.py`
- `tests/workflows/test_perf_audit_xml.py`
- `tests/workflows/test_pr_review_xml.py`
- `tests/workflows/test_release_prep_xml.py`

**Risks & Mitigation:**
- **Risk:** Breaking existing workflows
  - **Mitigation:** Feature flag `use_xml_structure` with default True, allow opt-out
- **Risk:** Performance regression
  - **Mitigation:** Benchmark before/after, optimize if >5% regression
- **Risk:** Parsing failures
  - **Mitigation:** Graceful fallback to non-XML parsing

---

### 2.2 Option 2: XML Schema Validation

**Objective:** Add XSD schema validation for XML responses with graceful fallback

**Architecture:**

```python
from dataclasses import dataclass
from typing import Optional
from lxml import etree
import logging

@dataclass
class ValidationResult:
    """Result of XML validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class XMLValidator:
    """Validates XML responses against XSD schemas"""

    def __init__(self, schema_dir: str = ".empathy/schemas"):
        self.schema_dir = Path(schema_dir)
        self.schemas = self._load_schemas()
        self.logger = logging.getLogger(__name__)

    def _load_schemas(self) -> Dict[str, etree.XMLSchema]:
        """Load all XSD schemas from schema directory"""
        pass

    def validate(self, xml_string: str, schema_name: str) -> ValidationResult:
        """Validate XML against specified schema"""
        pass

    def validate_with_fallback(self, xml_string: str, schema_name: str) -> Tuple[bool, str]:
        """Validate with graceful fallback on errors"""
        pass
```

**Files to Create:**

1. **src/empathy/xml_validator.py** (new file)
   - `XMLValidator` class
   - `ValidationResult` dataclass
   - Schema loading and caching
   - Validation with fallback logic

2. **.empathy/schemas/agent_response.xsd** (new file)
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
       <xs:element name="response">
           <xs:complexType>
               <xs:sequence>
                   <xs:element name="thinking" type="xs:string"/>
                   <xs:element name="answer" type="xs:string"/>
               </xs:sequence>
           </xs:complexType>
       </xs:element>
   </xs:schema>
   ```

3. **.empathy/schemas/thinking_answer.xsd** (new file)
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
       <xs:element name="thinking" type="xs:string"/>
       <xs:element name="answer">
           <xs:complexType mixed="true">
               <xs:sequence>
                   <xs:any minOccurs="0" maxOccurs="unbounded" processContents="lax"/>
               </xs:sequence>
           </xs:complexType>
       </xs:element>
   </xs:schema>
   ```

4. **.empathy/schemas/code_review.xsd** (new file)
   - Schema for code review responses

5. **.empathy/schemas/bug_prediction.xsd** (new file)
   - Schema for bug prediction responses

6. **.empathy/schemas/test_generation.xsd** (new file)
   - Schema for test generation responses

**Files to Modify:**

1. **src/empathy/xml_enhanced_crew.py**
   - Import `XMLValidator`
   - Add validation to `parse_xml_response()`
   - Add `validate_schema` parameter (default False for backward compatibility)
   - Log validation errors but continue processing

```python
# Enhanced parse_xml_response with validation
def parse_xml_response(
    response: str,
    validate_schema: bool = False,
    schema_name: Optional[str] = None
) -> Dict[str, Any]:
    """Parse XML response with optional schema validation"""

    if validate_schema and schema_name:
        validator = XMLValidator()
        validation_result = validator.validate(response, schema_name)

        if not validation_result.is_valid:
            logger.warning(f"XML validation failed: {validation_result.errors}")
            # Continue with parsing despite validation failure

    # Existing parsing logic
    root = ET.fromstring(response)
    # ...
```

**Tests to Create:**
- `tests/test_xml_validator.py`
  - Test schema loading
  - Test valid XML validation
  - Test invalid XML validation
  - Test fallback behavior
  - Test schema caching

**Configuration:**

```python
# src/empathy/config.py
@dataclass
class XMLConfig:
    validate_schemas: bool = False  # Feature flag
    schema_dir: str = ".empathy/schemas"
    strict_validation: bool = False  # Fail on validation errors
```

**Risks & Mitigation:**
- **Risk:** Schema validation overhead
  - **Mitigation:** Make validation optional (default False), cache schemas
- **Risk:** Schema maintenance burden
  - **Mitigation:** Start with core schemas, add incrementally
- **Risk:** False positives blocking valid responses
  - **Mitigation:** Graceful fallback, log warnings only

---

### 2.3 Option 3: Prompt Performance Tracking

**Objective:** Track prompt metrics for optimization and A/B testing

**Architecture:**

```python
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

@dataclass
class PromptMetrics:
    """Metrics for a single prompt execution"""
    timestamp: str
    workflow: str
    agent_role: str
    task_description: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    retry_count: int
    parsing_success: bool
    validation_success: Optional[bool]
    error_message: Optional[str]
    xml_structure_used: bool

class MetricsTracker:
    """Tracks and persists prompt metrics"""

    def __init__(self, metrics_file: str = ".empathy/prompt_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def log_metric(self, metric: PromptMetrics) -> None:
        """Log a single metric to file"""
        pass

    def get_metrics(
        self,
        workflow: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PromptMetrics]:
        """Retrieve metrics with optional filtering"""
        pass

    def get_summary(self, workflow: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregated metrics summary"""
        pass

class ABTestFramework:
    """Framework for A/B testing prompt variations"""

    def __init__(self, metrics_tracker: MetricsTracker):
        self.tracker = metrics_tracker

    def create_experiment(
        self,
        name: str,
        variant_a: str,
        variant_b: str,
        traffic_split: float = 0.5
    ) -> str:
        """Create new A/B test experiment"""
        pass

    def get_variant(self, experiment_id: str, user_id: str) -> str:
        """Get variant for user (consistent hashing)"""
        pass

    def analyze_results(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze A/B test results"""
        pass
```

**Files to Create:**

1. **src/empathy/metrics/prompt_metrics.py** (new file)
   - `PromptMetrics` dataclass
   - `MetricsTracker` class
   - JSON persistence logic
   - Query and aggregation methods

2. **src/empathy/metrics/ab_testing.py** (new file)
   - `ABTestFramework` class
   - Experiment management
   - Consistent hashing for variant assignment
   - Statistical analysis methods

3. **src/empathy/metrics/__init__.py** (new file)
   - Export public API

4. **.empathy/prompt_metrics.json** (created automatically)
   - JSON Lines format for append-only writes
   - One metric per line

5. **src/empathy/dashboard/metrics_dashboard.py** (new file)
   - Simple CLI dashboard for viewing metrics
   - Summary statistics
   - Trend analysis

**Files to Modify:**

1. **src/empathy/xml_enhanced_crew.py**
   - Add metrics tracking to `XMLAgent.execute()`
   - Add metrics tracking to `XMLTask.execute()`
   - Capture token usage from LLM responses
   - Track parsing success/failure

```python
# Enhanced XMLAgent with metrics
class XMLAgent(Agent):
    def __init__(self, *args, track_metrics: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.track_metrics = track_metrics
        self.metrics_tracker = MetricsTracker() if track_metrics else None

    def execute_task(self, task: Task) -> TaskOutput:
        start_time = time.time()
        retry_count = 0

        try:
            output = super().execute_task(task)
            latency_ms = (time.time() - start_time) * 1000

            if self.track_metrics:
                metric = PromptMetrics(
                    timestamp=datetime.now().isoformat(),
                    workflow=task.workflow_name,
                    agent_role=self.role,
                    task_description=task.description[:100],
                    model=self.llm.model_name,
                    prompt_tokens=output.token_usage.get('prompt_tokens', 0),
                    completion_tokens=output.token_usage.get('completion_tokens', 0),
                    total_tokens=output.token_usage.get('total_tokens', 0),
                    latency_ms=latency_ms,
                    retry_count=retry_count,
                    parsing_success=True,
                    validation_success=None,
                    error_message=None,
                    xml_structure_used=self.use_xml_structure
                )
                self.metrics_tracker.log_metric(metric)

            return output

        except Exception as e:
            # Log failure metric
            if self.track_metrics:
                metric = PromptMetrics(
                    timestamp=datetime.now().isoformat(),
                    workflow=task.workflow_name,
                    agent_role=self.role,
                    task_description=task.description[:100],
                    model=self.llm.model_name,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency_ms=(time.time() - start_time) * 1000,
                    retry_count=retry_count,
                    parsing_success=False,
                    validation_success=None,
                    error_message=str(e),
                    xml_structure_used=self.use_xml_structure
                )
                self.metrics_tracker.log_metric(metric)
            raise
```

**Tests to Create:**
- `tests/metrics/test_prompt_metrics.py`
  - Test metric logging
  - Test metric retrieval
  - Test aggregation
  - Test file persistence
- `tests/metrics/test_ab_testing.py`
  - Test experiment creation
  - Test variant assignment
  - Test result analysis

**Dashboard Integration:**

```python
# CLI dashboard command
# src/empathy/cli/metrics_command.py

@click.command()
@click.option('--workflow', help='Filter by workflow')
@click.option('--days', default=7, help='Days of history')
def metrics(workflow: Optional[str], days: int):
    """Display prompt performance metrics"""
    tracker = MetricsTracker()
    summary = tracker.get_summary(workflow=workflow)

    click.echo("=== Prompt Performance Metrics ===")
    click.echo(f"Total Prompts: {summary['total_prompts']}")
    click.echo(f"Avg Tokens: {summary['avg_tokens']:.0f}")
    click.echo(f"Avg Latency: {summary['avg_latency_ms']:.0f}ms")
    click.echo(f"Success Rate: {summary['success_rate']:.1%}")
    click.echo(f"Retry Rate: {summary['retry_rate']:.1%}")
```

**Risks & Mitigation:**
- **Risk:** Metrics file growth
  - **Mitigation:** Implement log rotation, archive old metrics
- **Risk:** Performance overhead
  - **Mitigation:** Async logging, make tracking optional
- **Risk:** Privacy concerns
  - **Mitigation:** Don't log sensitive data, add sanitization

---

### 2.4 Option 4: Context Window Optimization

**Objective:** Reduce token usage by 20-30% through compression and caching

**Architecture:**

```python
from enum import Enum
from typing import Dict, Optional

class CompressionLevel(Enum):
    """Compression levels for XML prompts"""
    NONE = "none"           # No compression
    LIGHT = "light"         # Remove extra whitespace
    MODERATE = "moderate"   # Short tags + whitespace removal
    AGGRESSIVE = "aggressive"  # Minimal tags + no whitespace

@dataclass
class OptimizationConfig:
    """Configuration for context window optimization"""
    compression_level: CompressionLevel = CompressionLevel.MODERATE
    use_short_tags: bool = True
    strip_whitespace: bool = True
    cache_system_prompts: bool = True
    max_context_tokens: int = 8000

class ContextOptimizer:
    """Optimizes prompts for context window efficiency"""

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.tag_mappings = self._load_tag_mappings()

    def _load_tag_mappings(self) -> Dict[str, str]:
        """Load short-form tag mappings"""
        return {
            "thinking": "t",
            "answer": "a",
            "agent_role": "r",
            "agent_goal": "g",
            "agent_backstory": "b",
            "instructions": "i",
            "context": "c",
            "output_structure": "o",
        }

    def optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt based on configuration"""
        if self.config.compression_level == CompressionLevel.NONE:
            return prompt

        optimized = prompt

        if self.config.use_short_tags:
            optimized = self._compress_tags(optimized)

        if self.config.strip_whitespace:
            optimized = self._strip_whitespace(optimized)

        return optimized

    def _compress_tags(self, prompt: str) -> str:
        """Replace long tags with short versions"""
        for long_tag, short_tag in self.tag_mappings.items():
            prompt = prompt.replace(f"<{long_tag}>", f"<{short_tag}>")
            prompt = prompt.replace(f"</{long_tag}>", f"</{short_tag}>")
        return prompt

    def _strip_whitespace(self, prompt: str) -> str:
        """Remove unnecessary whitespace"""
        import re
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in prompt.split('\n')]
        # Remove empty lines
        lines = [line for line in lines if line]
        # Join with single newline
        return '\n'.join(lines)

class SystemPromptCache:
    """Cache system prompts to reduce token usage"""

    def __init__(self):
        self.cache: Dict[str, str] = {}

    def get_or_create(self, key: str, generator: callable) -> str:
        """Get cached prompt or generate and cache"""
        if key not in self.cache:
            self.cache[key] = generator()
        return self.cache[key]
```

**Files to Create:**

1. **src/empathy/optimization/context_optimizer.py** (new file)
   - `CompressionLevel` enum
   - `OptimizationConfig` dataclass
   - `ContextOptimizer` class
   - Tag compression logic
   - Whitespace stripping

2. **src/empathy/optimization/system_prompt_cache.py** (new file)
   - `SystemPromptCache` class
   - LRU cache implementation
   - Cache invalidation logic

3. **src/empathy/optimization/__init__.py** (new file)
   - Export public API

4. **.empathy/tag_mappings.json** (new file)
   ```json
   {
     "thinking": "t",
     "answer": "a",
     "agent_role": "r",
     "agent_goal": "g",
     "agent_backstory": "b",
     "instructions": "i",
     "context": "c",
     "output_structure": "o",
     "code_review": "cr",
     "bug_prediction": "bp",
     "test_generation": "tg"
   }
   ```

**Files to Modify:**

1. **src/empathy/xml_enhanced_crew.py**
   - Add `ContextOptimizer` integration
   - Add `optimization_config` parameter
   - Optimize prompts before sending to LLM

```python
# Enhanced XMLAgent with optimization
class XMLAgent(Agent):
    def __init__(
        self,
        *args,
        optimization_config: Optional[OptimizationConfig] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.optimizer = ContextOptimizer(
            optimization_config or OptimizationConfig()
        )

    def _build_prompt(self, task: Task) -> str:
        """Build and optimize prompt"""
        prompt = super()._build_prompt(task)
        return self.optimizer.optimize_prompt(prompt)
```

2. **src/empathy/config.py**
   - Add `OptimizationConfig` to global config
   - Add feature flag for optimization

**Tests to Create:**
- `tests/optimization/test_context_optimizer.py`
  - Test tag compression
  - Test whitespace stripping
  - Test compression levels
  - Test token reduction (measure before/after)
- `tests/optimization/test_system_prompt_cache.py`
  - Test cache hit/miss
  - Test cache invalidation

**Benchmarking:**

```python
# tests/benchmarks/test_optimization_impact.py

def test_token_reduction():
    """Measure token reduction from optimization"""
    original_prompt = """
    <agent_role>
        You are a Senior Code Reviewer
    </agent_role>
    <agent_goal>
        Review code for quality and best practices
    </agent_goal>
    """

    optimizer = ContextOptimizer(OptimizationConfig(
        compression_level=CompressionLevel.MODERATE
    ))

    optimized_prompt = optimizer.optimize_prompt(original_prompt)

    original_tokens = count_tokens(original_prompt)
    optimized_tokens = count_tokens(optimized_prompt)

    reduction = (original_tokens - optimized_tokens) / original_tokens
    assert reduction >= 0.20  # At least 20% reduction
```

**Risks & Mitigation:**
- **Risk:** Reduced readability
  - **Mitigation:** Make compression configurable, default to moderate
- **Risk:** Breaking XML parsing
  - **Mitigation:** Maintain tag mapping consistency, test thoroughly
- **Risk:** Cache invalidation issues
  - **Mitigation:** Simple cache key strategy, clear invalidation rules

---

### 2.5 Option 5: Dynamic Prompt Adaptation

**Objective:** Automatically adapt prompt verbosity and model selection based on task complexity

**Architecture:**

```python
from enum import Enum
from typing import Dict, Optional

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"       # <100 tokens, <50 LOC
    MODERATE = "moderate"   # 100-500 tokens, 50-200 LOC
    COMPLEX = "complex"     # 500-2000 tokens, 200-1000 LOC
    VERY_COMPLEX = "very_complex"  # >2000 tokens, >1000 LOC

class ModelTier(Enum):
    """Model capability tiers"""
    CHEAP = "cheap"         # gpt-3.5-turbo, claude-instant
    CAPABLE = "capable"     # gpt-4, claude-2
    PREMIUM = "premium"     # gpt-4-turbo, claude-3-opus

@dataclass
class ComplexityScore:
    """Task complexity scoring"""
    token_count: int
    line_count: int
    file_count: int
    complexity_level: TaskComplexity
    confidence: float

class TaskComplexityScorer:
    """Scores task complexity using simple heuristics"""

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def score_task(
        self,
        description: str,
        context: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> ComplexityScore:
        """Score task complexity"""

        # Count tokens
        token_count = len(self.tokenizer.encode(description))
        if context:
            token_count += len(self.tokenizer.encode(context))

        # Count lines of code
        line_count = 0
        if context:
            line_count = len(context.split('\n'))

        # Count files
        file_count = len(files) if files else 0

        # Determine complexity level
        if token_count < 100 and line_count < 50:
            complexity = TaskComplexity.SIMPLE
        elif token_count < 500 and line_count < 200:
            complexity = TaskComplexity.MODERATE
        elif token_count < 2000 and line_count < 1000:
            complexity = TaskComplexity.COMPLEX
        else:
            complexity = TaskComplexity.VERY_COMPLEX

        return ComplexityScore(
            token_count=token_count,
            line_count=line_count,
            file_count=file_count,
            complexity_level=complexity,
            confidence=0.8  # Simple heuristic has moderate confidence
        )

@dataclass
class AdaptationStrategy:
    """Strategy for adapting prompts based on complexity"""
    model_tier: ModelTier
    compression_level: CompressionLevel
    max_retries: int
    timeout_seconds: int

class AdaptiveXMLAgent(XMLAgent):
    """XML Agent that adapts to task complexity"""

    def __init__(
        self,
        *args,
        enable_adaptation: bool = True,
        model_tier_mapping: Optional[Dict[TaskComplexity, ModelTier]] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.enable_adaptation = enable_adaptation
        self.complexity_scorer = TaskComplexityScorer()
        self.model_tier_mapping = model_tier_mapping or {
            TaskComplexity.SIMPLE: ModelTier.CHEAP,
            TaskComplexity.MODERATE: ModelTier.CAPABLE,
            TaskComplexity.COMPLEX: ModelTier.CAPABLE,
            TaskComplexity.VERY_COMPLEX: ModelTier.PREMIUM,
        }

    def _get_adaptation_strategy(
        self,
        complexity: ComplexityScore
    ) -> AdaptationStrategy:
        """Get adaptation strategy for complexity level"""

        model_tier = self.model_tier_mapping[complexity.complexity_level]

        # Adjust compression based on complexity
        if complexity.complexity_level == TaskComplexity.SIMPLE:
            compression = CompressionLevel.AGGRESSIVE
        elif complexity.complexity_level == TaskComplexity.MODERATE:
            compression = CompressionLevel.MODERATE
        else:
            compression = CompressionLevel.LIGHT

        # Adjust retries based on complexity
        max_retries = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MODERATE: 2,
            TaskComplexity.COMPLEX: 3,
            TaskComplexity.VERY_COMPLEX: 3,
        }[complexity.complexity_level]

        return AdaptationStrategy(
            model_tier=model_tier,
            compression_level=compression,
            max_retries=max_retries,
            timeout_seconds=30 * (complexity.complexity_level.value + 1)
        )

    def execute_task(self, task: Task) -> TaskOutput:
        """Execute task with adaptive strategy"""

        if not self.enable_adaptation:
            return super().execute_task(task)

        # Score task complexity
        complexity = self.complexity_scorer.score_task(
            description=task.description,
            context=task.context
        )

        # Get adaptation strategy
        strategy = self._get_adaptation_strategy(complexity)

        # Apply strategy
        original_llm = self.llm
        original_optimizer = self.optimizer

        try:
            # Switch model if needed
            self.llm = self._get_model_for_tier(strategy.model_tier)

            # Adjust optimization
            self.optimizer = ContextOptimizer(OptimizationConfig(
                compression_level=strategy.compression_level
            ))

            # Execute with adapted settings
            return super().execute_task(task)

        finally:
            # Restore original settings
            self.llm = original_llm
            self.optimizer = original_optimizer

    def _get_model_for_tier(self, tier: ModelTier) -> BaseChatModel:
        """Get LLM instance for model tier"""
        model_map = {
            ModelTier.CHEAP: "gpt-3.5-turbo",
            ModelTier.CAPABLE: "gpt-4",
            ModelTier.PREMIUM: "gpt-4-turbo-preview",
        }
        return ChatOpenAI(model=model_map[tier])
```

**Files to Create:**

1. **src/empathy/adaptive/task_complexity.py** (new file)
   - `TaskComplexity` enum
   - `ComplexityScore` dataclass
   - `TaskComplexityScorer` class
   - Heuristic scoring logic

2. **src/empathy/adaptive/adaptation_strategy.py** (new file)
   - `ModelTier` enum
   - `AdaptationStrategy` dataclass
   - Strategy selection logic

3. **src/empathy/adaptive/adaptive_agent.py** (new file)
   - `AdaptiveXMLAgent` class
   - Model switching logic
   - Optimization adjustment

4. **src/empathy/adaptive/__init__.py** (new file)
   - Export public API

**Files to Modify:**

1. **src/empathy/xml_enhanced_crew.py**
   - Export `AdaptiveXMLAgent`
   - Add to `__all__`

2. **src/empathy/config.py**
   - Add `AdaptiveConfig` dataclass
   - Add model tier mappings
   - Add feature flag

```python
@dataclass
class AdaptiveConfig:
    """Configuration for adaptive prompting"""
    enable_adaptation: bool = True
    model_tier_mapping: Dict[str, str] = field(default_factory=lambda: {
        "simple": "gpt-3.5-turbo",
        "moderate": "gpt-4",
        "complex": "gpt-4",
        "very_complex": "gpt-4-turbo-preview",
    })
    complexity_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "simple_tokens": 100,
        "moderate_tokens": 500,
        "complex_tokens": 2000,
    })
```

**Tests to Create:**
- `tests/adaptive/test_task_complexity.py`
  - Test complexity scoring
  - Test threshold boundaries
  - Test confidence calculation
- `tests/adaptive/test_adaptation_strategy.py`
  - Test strategy selection
  - Test model tier mapping
- `tests/adaptive/test_adaptive_agent.py`
  - Test model switching
  - Test optimization adjustment
  - Test fallback behavior

**Risks & Mitigation:**
- **Risk:** Incorrect complexity assessment
  - **Mitigation:** Conservative thresholds, allow manual override
- **Risk:** Cost increase from premium models
  - **Mitigation:** Track costs in metrics, set budget limits
- **Risk:** Inconsistent results across models
  - **Mitigation:** Test thoroughly, document model differences

---

### 2.6 Option 6: Multi-Language XML Templates

**Objective:** Support Spanish, French, and German with locale-aware templates

**Architecture:**

```python
from enum import Enum
from typing import Dict, Optional

class SupportedLanguage(Enum):
    """Supported languages for XML templates"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"

@dataclass
class TranslationConfig:
    """Configuration for multi-language support"""
    default_language: SupportedLanguage = SupportedLanguage.ENGLISH
    translate_tags: bool = False  # Keep tags in English by default
    translate_content: bool = True
    fallback_to_english: bool = True

class TranslationDictionary:
    """Translation dictionary for XML templates"""

    def __init__(self):
        self.translations = self._load_translations()

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation dictionaries"""
        return {
            "es": {
                # Agent components
                "You are a": "Eres un",
                "Your goal is": "Tu objetivo es",
                "Your backstory": "Tu historia",
                "Senior": "Senior",
                "Expert": "Experto",
                "Specialist": "Especialista",

                # Instructions
                "Review the following": "Revisa lo siguiente",
                "Analyze": "Analiza",
                "Generate": "Genera",
                "Provide": "Proporciona",

                # Output structure
                "Think step-by-step": "Piensa paso a paso",
                "Provide your analysis": "Proporciona tu análisis",
                "Structure your response": "Estructura tu respuesta",
            },
            "fr": {
                # Agent components
                "You are a": "Vous êtes un",
                "Your goal is": "Votre objectif est",
                "Your backstory": "Votre histoire",
                "Senior": "Senior",
                "Expert": "Expert",
                "Specialist": "Spécialiste",

                # Instructions
                "Review the following": "Examinez ce qui suit",
                "Analyze": "Analysez",
                "Generate": "Générez",
                "Provide": "Fournissez",

                # Output structure
                "Think step-by-step": "Réfléchissez étape par étape",
                "Provide your analysis": "Fournissez votre analyse",
                "Structure your response": "Structurez votre réponse",
            },
            "de": {
                # Agent components
                "You are a": "Sie sind ein",
                "Your goal is": "Ihr Ziel ist",
                "Your backstory": "Ihre Geschichte",
                "Senior": "Senior",
                "Expert": "Experte",
                "Specialist": "Spezialist",

                # Instructions
                "Review the following": "Überprüfen Sie Folgendes",
                "Analyze": "Analysieren",
                "Generate": "Generieren",
                "Provide": "Bereitstellen",

                # Output structure
                "Think step-by-step": "Denken Sie Schritt für Schritt",
                "Provide your analysis": "Geben Sie Ihre Analyse",
                "Structure your response": "Strukturieren Sie Ihre Antwort",
            }
        }

    def translate(
        self,
        text: str,
        target_language: SupportedLanguage
    ) -> str:
        """Translate text to target language"""
        if target_language == SupportedLanguage.ENGLISH:
            return text

        lang_dict = self.translations.get(target_language.value, {})

        # Simple word/phrase replacement
        translated = text
        for english, translation in lang_dict.items():
            translated = translated.replace(english, translation)

        return translated

class MultilingualXMLAgent(XMLAgent):
    """XML Agent with multi-language support"""

    def __init__(
        self,
        *args,
        language: SupportedLanguage = SupportedLanguage.ENGLISH,
        translation_config: Optional[TranslationConfig] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.language = language
        self.translation_config = translation_config or TranslationConfig()
        self.translator = TranslationDictionary()

    def _build_prompt(self, task: Task) -> str:
        """Build prompt with language support"""
        prompt = super()._build_prompt(task)

        if self.language != SupportedLanguage.ENGLISH:
            # Translate content but keep tags in English
            if self.translation_config.translate_content:
                prompt = self._translate_content(prompt)

            # Optionally translate tags
            if self.translation_config.translate_tags:
                prompt = self._translate_tags(prompt)

        return prompt

    def _translate_content(self, prompt: str) -> str:
        """Translate prompt content while preserving XML structure"""
        import re

        # Extract text between tags
        def translate_match(match):
            text = match.group(1)
            translated = self.translator.translate(text, self.language)
            return f">{translated}<"

        # Translate text between tags
        pattern = r'>([^<]+)<'
        return re.sub(pattern, translate_match, prompt)

    def _translate_tags(self, prompt: str) -> str:
        """Translate XML tag names"""
        tag_translations = {
            "thinking": {
                "es": "pensamiento",
                "fr": "réflexion",
                "de": "denken"
            },
            "answer": {
                "es": "respuesta",
                "fr": "réponse",
                "de": "antwort"
            },
            # Add more tag translations
        }

        translated = prompt
        for english_tag, translations in tag_translations.items():
            target_tag = translations.get(self.language.value, english_tag)
            translated = translated.replace(f"<{english_tag}>", f"<{target_tag}>")
            translated = translated.replace(f"</{english_tag}>", f"</{target_tag}>")

        return translated
```

**Files to Create:**

1. **src/empathy/i18n/translation_dictionary.py** (new file)
   - `SupportedLanguage` enum
   - `TranslationDictionary` class
   - Translation loading and caching

2. **src/empathy/i18n/multilingual_agent.py** (new file)
   - `MultilingualXMLAgent` class
   - Content translation logic
   - Tag translation logic (optional)

3. **src/empathy/i18n/__init__.py** (new file)
   - Export public API

4. **.empathy/translations/es.json** (new file)
   ```json
   {
     "agent_phrases": {
       "You are a": "Eres un",
       "Your goal is": "Tu objetivo es"
     },
     "instructions": {
       "Review the following": "Revisa lo siguiente",
       "Analyze": "Analiza"
     },
     "tags": {
       "thinking": "pensamiento",
       "answer": "respuesta"
     }
   }
   ```

5. **.empathy/translations/fr.json** (new file)
   - French translations

6. **.empathy/translations/de.json** (new file)
   - German translations

**Files to Modify:**

1. **src/empathy/xml_enhanced_crew.py**
   - Export `MultilingualXMLAgent`
   - Add to `__all__`

2. **src/empathy/config.py**
   - Add `TranslationConfig` dataclass
   - Add language preference setting

```python
@dataclass
class I18nConfig:
    """Configuration for internationalization"""
    default_language: str = "en"
    translate_tags: bool = False
    translate_content: bool = True
    fallback_to_english: bool = True
    translation_dir: str = ".empathy/translations"
```

**Tests to Create:**
- `tests/i18n/test_translation_dictionary.py`
  - Test translation loading
  - Test phrase translation
  - Test fallback behavior
- `tests/i18n/test_multilingual_agent.py`
  - Test content translation
  - Test tag translation
  - Test language switching
  - Test XML structure preservation

**Example Usage:**

```python
# Spanish code review agent
reviewer = MultilingualXMLAgent(
    role="Code Reviewer",
    goal="Review code for quality",
    backstory="Expert reviewer",
    language=SupportedLanguage.SPANISH,
    llm=ChatOpenAI(model="gpt-4")
)

# Prompt will be:
# <agent_role>Eres un Code Reviewer</agent_role>
# <agent_goal>Tu objetivo es Review code for quality</agent_goal>
```

**Risks & Mitigation:**
- **Risk:** Translation quality
  - **Mitigation:** Start with common phrases, expand incrementally
- **Risk:** XML structure corruption
  - **Mitigation:** Preserve tags in English, translate content only
- **Risk:** Model performance in non-English
  - **Mitigation:** Test with multilingual models, document limitations

---

## 3. File-by-File Implementation Plan

### Phase 1: Core Infrastructure (60-90 min)

#### 3.1 Metrics System

**File: `src/empathy/metrics/prompt_metrics.py`**
```python
"""Prompt performance metrics tracking"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class PromptMetrics:
    """Metrics for a single prompt execution"""
    timestamp: str
    workflow: str
    agent_role: str
    task_description: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    retry_count: int
    parsing_success: bool
    validation_success: Optional[bool]
    error_message: Optional[str]
    xml_structure_used: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PromptMetrics':
        """Create from dictionary"""
        return cls(**data)

class MetricsTracker:
    """Tracks and persists prompt metrics"""

    def __init__(self, metrics_file: str = ".empathy/prompt_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.metrics_file.exists():
            self.metrics_file.write_text("")

    def log_metric(self, metric: PromptMetrics) -> None:
        """Log a single metric to file (JSON Lines format)"""
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metric.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to log metric: {e}")

    def get_metrics(
        self,
        workflow: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PromptMetrics]:
        """Retrieve metrics with optional filtering"""
        metrics = []

        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        metric = PromptMetrics.from_dict(data)

                        # Apply filters
                        if workflow and metric.workflow != workflow:
                            continue

                        metric_time = datetime.fromisoformat(metric.timestamp)
                        if start_date and metric_time < start_date:
                            continue
                        if end_date and metric_time > end_date:
                            continue

                        metrics.append(metric)
        except Exception as e:
            logger.error(f"Failed to read metrics: {e}")

        return metrics

    def get_summary(self, workflow: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregated metrics summary"""
        metrics = self.get_metrics(workflow=workflow)

        if not metrics:
            return {
                "total_prompts": 0,
                "avg_tokens": 0,
                "avg_latency_ms": 0,
                "success_rate": 0,
                "retry_rate": 0,
            }

        total_prompts = len(metrics)
        total_tokens = sum(m.total_tokens for m in metrics)
        total_latency = sum(m.latency_ms for m in metrics)
        successful = sum(1 for m in metrics if m.parsing_success)
        retries = sum(m.retry_count for m in metrics)

        return {
            "total_prompts": total_prompts,
            "avg_tokens": total_tokens / total_prompts,
            "avg_latency_ms": total_latency / total_prompts,
            "success_rate": successful / total_prompts,
            "retry_rate": retries / total_prompts,
        }
```

**Tests: `tests/metrics/test_prompt_metrics.py`**
```python
"""Tests for prompt metrics tracking"""

import pytest
from pathlib import Path
from datetime import datetime
from empathy.metrics.prompt_metrics import PromptMetrics, MetricsTracker

@pytest.fixture
def temp_metrics_file(tmp_path):
    """Create temporary metrics file"""
    return str(tmp_path / "test_metrics.json")

def test_prompt_metrics_creation():
    """Test PromptMetrics dataclass creation"""
    metric = PromptMetrics(
        timestamp=datetime.now().isoformat(),
        workflow="test_workflow",
        agent_role="Test Agent",
        task_description="Test task",
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        latency_ms=1000.0,
        retry_count=0,
        parsing_success=True,
        validation_success=True,
        error_message=None,
        xml_structure_used=True
    )

    assert metric.workflow == "test_workflow"
    assert metric.total_tokens == 150

def test_metrics_tracker_log(temp_metrics_file):
    """Test logging metrics to file"""
    tracker = MetricsTracker(temp_metrics_file)

    metric = PromptMetrics(
        timestamp=datetime.now().isoformat(),
        workflow="test_workflow",
        agent_role="Test Agent",
        task_description="Test task",
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        latency_ms=1000.0,
        retry_count=0,
        parsing_success=True,
        validation_success=True,
        error_message=None,
        xml_structure_used=True
    )

    tracker.log_metric(metric)

    # Verify file was created and contains data
    assert Path(temp_metrics_file).exists()
    metrics = tracker.get_metrics()
    assert len(metrics) == 1
    assert metrics[0].workflow == "test_workflow"

def test_metrics_tracker_summary(temp_metrics_file):
    """Test metrics summary calculation"""
    tracker = MetricsTracker(temp_metrics_file)

    # Log multiple metrics
    for i in range(5):
        metric = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow="test_workflow",
            agent_role="Test Agent",
            task_description=f"Test task {i}",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1000.0,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True
        )
        tracker.log_metric(metric)

    summary = tracker.get_summary()
    assert summary["total_prompts"] == 5
    assert summary["avg_tokens"] == 150
    assert summary["success_rate"] == 1.0
```

**Effort: 30 minutes**

---

#### 3.2 Adaptive Agent System

**File: `src/empathy/adaptive/task_complexity.py`**
```python
"""Task complexity scoring"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import tiktoken

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

@dataclass
class ComplexityScore:
    """Task complexity scoring result"""
    token_count: int
    line_count: int
    file_count: int
    complexity_level: TaskComplexity
    confidence: float

class TaskComplexityScorer:
    """Scores task complexity using simple heuristics"""

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def score_task(
        self,
        description: str,
        context: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> ComplexityScore:
        """Score task complexity"""

        # Count tokens
        token_count = len(self.tokenizer.encode(description))
        if context:
            token_count += len(self.tokenizer.encode(context))

        # Count lines of code
        line_count = 0
        if context:
            line_count = len(context.split('\n'))

        # Count files
        file_count = len(files) if files else 0

        # Determine complexity level
        if token_count < 100 and line_count < 50:
            complexity = TaskComplexity.SIMPLE
        elif token_count < 500 and line_count < 200:
            complexity = TaskComplexity.MODERATE
        elif token_count < 2000 and line_count < 1000:
            complexity = TaskComplexity.COMPLEX
        else:
            complexity = TaskComplexity.VERY_COMPLEX

        return ComplexityScore(
            token_count=token_count,
            line_count=line_count,
            file_count=file_count,
            complexity_level=complexity,
            confidence=0.8
        )
```

**File: `src/empathy/adaptive/adaptive_agent.py`**
```python
"""Adaptive XML Agent implementation"""

from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass

from empathy.xml_enhanced_crew import XMLAgent
from empathy.adaptive.task_complexity import TaskComplexityScorer, TaskComplexity
from empathy.optimization.context_optimizer import ContextOptimizer, OptimizationConfig, CompressionLevel
from langchain.chat_models import ChatOpenAI

class ModelTier(Enum):
    """Model capability tiers"""
    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"

@dataclass
class AdaptationStrategy:
    """Strategy for adapting prompts"""
    model_tier: ModelTier
    compression_level: CompressionLevel
    max_retries: int
    timeout_seconds: int

class AdaptiveXMLAgent(XMLAgent):
    """XML Agent that adapts to task complexity"""

    def __init__(
        self,
        *args,
        enable_adaptation: bool = True,
        model_tier_mapping: Optional[Dict[TaskComplexity, ModelTier]] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.enable_adaptation = enable_adaptation
        self.complexity_scorer = TaskComplexityScorer()
        self.model_tier_mapping = model_tier_mapping or {
            TaskComplexity.SIMPLE: ModelTier.CHEAP,
            TaskComplexity.MODERATE: ModelTier.CAPABLE,
            TaskComplexity.COMPLEX: ModelTier.CAPABLE,
            TaskComplexity.VERY_COMPLEX: ModelTier.PREMIUM,
        }

    def _get_adaptation_strategy(
        self,
        complexity: ComplexityScore
    ) -> AdaptationStrategy:
        """Get adaptation strategy for complexity level"""

        model_tier = self.model_tier_mapping[complexity.complexity_level]

        # Adjust compression based on complexity
        if complexity.complexity_level == TaskComplexity.SIMPLE:
            compression = CompressionLevel.AGGRESSIVE
        elif complexity.complexity_level == TaskComplexity.MODERATE:
            compression = CompressionLevel.MODERATE
        else:
            compression = CompressionLevel.LIGHT

        # Adjust retries based on complexity
        max_retries = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MODERATE: 2,
            TaskComplexity.COMPLEX: 3,
            TaskComplexity.VERY_COMPLEX: 3,
        }[complexity.complexity_level]

        return AdaptationStrategy(
            model_tier=model_tier,
            compression_level=compression,
            max_retries=max_retries,
            timeout_seconds=30 * (list(TaskComplexity).index(complexity.complexity_level) + 1)
        )
```

**Tests: `tests/adaptive/test_task_complexity.py`**
```python
"""Tests for task complexity scoring"""

import pytest
from empathy.adaptive.task_complexity import TaskComplexityScorer, TaskComplexity

def test_simple_task_scoring():
    """Test scoring of simple task"""
    scorer = TaskComplexityScorer()

    score = scorer.score_task(
        description="Fix typo in README",
        context="# README\nTypo here",
        files=["README.md"]
    )

    assert score.complexity_level == TaskComplexity.SIMPLE
    assert score.token_count < 100

def test_complex_task_scoring():
    """Test scoring of complex task"""
    scorer = TaskComplexityScorer()

    # Generate large context
    context = "\n".join([f"line {i}" for i in range(500)])

    score = scorer.score_task(
        description="Refactor entire module with 500 lines",
        context=context,
        files=["module.py"]
    )

    assert score.complexity_level in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]
    assert score.line_count >= 500
```

**Effort: 45 minutes**

---

#### 3.3 Configuration System

**File: `src/empathy/config.py` (modifications)**
```python
"""Enhanced configuration with feature flags"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum

# ... existing config ...

@dataclass
class XMLConfig:
    """XML prompting configuration"""
    use_xml_structure: bool = True  # Default to XML
    validate_schemas: bool = False  # Feature flag
    schema_dir: str = ".empathy/schemas"
    strict_validation: bool = False

@dataclass
class OptimizationConfig:
    """Context window optimization configuration"""
    compression_level: str = "moderate"  # none, light, moderate, aggressive
    use_short_tags: bool = True
    strip_whitespace: bool = True
    cache_system_prompts: bool = True
    max_context_tokens: int = 8000

@dataclass
class AdaptiveConfig:
    """Adaptive prompting configuration"""
    enable_adaptation: bool = True
    model_tier_mapping: Dict[str, str] = field(default_factory=lambda: {
        "simple": "gpt-3.5-turbo",
        "moderate": "gpt-4",
        "complex": "gpt-4",
        "very_complex": "gpt-4-turbo-preview",
    })
    complexity_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "simple_tokens": 100,
        "moderate_tokens": 500,
        "complex_tokens": 2000,
    })

@dataclass
class I18nConfig:
    """Internationalization configuration"""
    default_language: str = "en"
    translate_tags: bool = False
    translate_content: bool = True
    fallback_to_english: bool = True
    translation_dir: str = ".empathy/translations"

@dataclass
class MetricsConfig:
    """Metrics tracking configuration"""
    enable_tracking: bool = True
    metrics_file: str = ".empathy/prompt_metrics.json"
    track_token_usage: bool = True
    track_latency: bool = True
    track_retries: bool = True

@dataclass
class EmpathyConfig:
    """Main Empathy configuration"""
    xml: XMLConfig = field(default_factory=XMLConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    adaptive: AdaptiveConfig = field(default_factory=AdaptiveConfig)
    i18n: I18nConfig = field(default_factory=I18nConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)

    @classmethod
    def load_from_file(cls, config_file: str = ".empathy/config.json") -> 'EmpathyConfig':
        """Load configuration from file"""
        # Implementation
        pass
```

**Effort: 15 minutes**

---

### Phase 2: Sample Workflow Migration (45-60 min
