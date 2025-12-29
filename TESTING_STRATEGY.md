# Empathy Framework Testing Strategy

## Executive Summary

This document outlines a phased approach to transform the Empathy Framework's testing infrastructure from its current state (5.7/10) to a comprehensive, efficient, and maintainable test suite (target: 8.5/10).

**Current Issues:**
- Test generation produces 80% placeholder code (non-functional)
- 44 of 85 core modules have no tests
- 149 duplicate test names across files
- Only 5.4% parametrization usage
- No shared test infrastructure

**Target Outcomes:**
- 100% executable test generation (zero TODOs/pass statements)
- 90%+ critical module coverage
- 25% reduction in test code through deduplication
- Shared test infrastructure for common patterns
- Clear unit/integration/performance test separation

---

## Phase 1: Test Infrastructure Foundation (Week 1)

### 1.1 Create Shared Test Base Classes

**File: `tests/conftest.py`** - Add shared fixtures and base classes

```python
# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import os

# ============================================================================
# SHARED FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Provide a temporary directory that's cleaned up after test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_llm_response():
    """Standard mock LLM response for testing."""
    return {
        "content": "Mock LLM response",
        "metadata": {
            "tokens_used": 100,
            "output_tokens": 50,
            "model": "test-model",
        },
        "level_used": 3,
    }

@pytest.fixture
def mock_empathy_llm(mock_llm_response):
    """Mock EmpathyLLM instance."""
    mock = AsyncMock()
    mock.interact.return_value = mock_llm_response
    return mock

@pytest.fixture
def env_with_api_keys(monkeypatch):
    """Set up environment with test API keys."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")

@pytest.fixture
def sample_python_code():
    """Sample Python code for testing code analysis."""
    return '''
def calculate_total(items: list[dict], tax_rate: float = 0.1) -> float:
    """Calculate total with tax."""
    if not items:
        raise ValueError("Items list cannot be empty")
    subtotal = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
    return subtotal * (1 + tax_rate)

async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
'''
```

**File: `tests/base_workflow_test.py`** - Base class for workflow tests

```python
# tests/base_workflow_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from abc import ABC, abstractmethod

class BaseWorkflowTest(ABC):
    """Base class for all workflow tests.

    Provides common test patterns for workflow testing,
    reducing duplication across test files.
    """

    @property
    @abstractmethod
    def workflow_class(self):
        """Return the workflow class being tested."""
        pass

    @property
    def workflow_name(self) -> str:
        """Return workflow name (derived from class name)."""
        return self.workflow_class.__name__.replace("Workflow", "").lower()

    @pytest.fixture
    def workflow(self, mock_empathy_llm):
        """Create workflow instance with mocked LLM."""
        with patch.object(self.workflow_class, '_create_default_executor') as mock_exec:
            mock_exec.return_value = MagicMock()
            instance = self.workflow_class(provider="anthropic")
            instance._llm = mock_empathy_llm
            return instance

    # ========================================================================
    # STANDARD WORKFLOW TESTS - Inherit these in subclasses
    # ========================================================================

    async def test_workflow_initialization(self, workflow):
        """Test that workflow initializes correctly."""
        assert workflow is not None
        assert workflow.name == self.workflow_name
        assert len(workflow.stages) > 0
        assert len(workflow.tier_map) > 0

    async def test_workflow_has_required_stages(self, workflow):
        """Test that workflow has expected stages."""
        for stage in self.expected_stages:
            assert stage in workflow.stages, f"Missing stage: {stage}"

    async def test_workflow_tier_mapping(self, workflow):
        """Test that all stages have tier mappings."""
        for stage in workflow.stages:
            assert stage in workflow.tier_map, f"No tier mapping for: {stage}"

    async def test_workflow_execute_success(self, workflow, sample_input):
        """Test successful workflow execution."""
        with patch.object(workflow, 'run_stage', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ({"result": "success"}, 100, 50)
            result = await workflow.execute(**sample_input)
            assert result.success is True

    async def test_workflow_execute_with_error(self, workflow, sample_input):
        """Test workflow handles errors gracefully."""
        with patch.object(workflow, 'run_stage', new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = Exception("Test error")
            result = await workflow.execute(**sample_input)
            assert result.success is False
            assert "error" in result.error.lower()

    # ========================================================================
    # COMMON LLM CALL TESTS - Replaces 149 duplicate tests
    # ========================================================================

    @pytest.mark.parametrize("tier,expected_model_pattern", [
        ("cheap", r"haiku|flash|mini"),
        ("capable", r"sonnet|pro|gpt-4o"),
        ("premium", r"opus|o1|pro"),
    ])
    async def test_llm_call_uses_correct_tier(self, workflow, tier, expected_model_pattern):
        """Test that LLM calls use the correct model tier."""
        import re
        # Implementation depends on workflow internals
        pass

    async def test_llm_call_with_mock_client(self, workflow, mock_empathy_llm):
        """Test LLM call with mocked client."""
        result = await workflow._call_llm(
            tier=workflow.tier_map[workflow.stages[0]],
            system="Test system prompt",
            user_message="Test user message",
        )
        assert result is not None

    async def test_llm_call_handles_api_error(self, workflow):
        """Test LLM call handles API errors gracefully."""
        with patch.object(workflow, '_call_llm', new_callable=AsyncMock) as mock:
            mock.side_effect = Exception("API Error")
            # Test error handling behavior
            pass
```

### 1.2 Reorganize Test Directory Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── base_workflow_test.py          # Base class for workflow tests
│
├── unit/                          # Fast, isolated unit tests
│   ├── __init__.py
│   ├── core/
│   │   ├── test_core.py
│   │   └── test_levels.py
│   ├── memory/
│   │   ├── test_graph.py          # NEW
│   │   ├── test_long_term.py      # NEW
│   │   └── test_unified_memory.py
│   ├── workflows/
│   │   ├── test_base_workflow.py  # NEW
│   │   ├── test_code_review.py    # NEW
│   │   ├── test_security_audit.py # NEW
│   │   └── ...
│   ├── models/
│   │   ├── test_executor.py       # NEW
│   │   ├── test_registry.py
│   │   └── test_provider_config.py
│   └── security/
│       ├── test_pii_scrubber.py
│       └── test_secrets_detector.py
│
├── integration/                   # Multi-component tests
│   ├── __init__.py
│   ├── test_wizard_outputs.py     # MOVED from root
│   ├── test_workflow_e2e.py
│   └── test_memory_persistence.py
│
└── performance/                   # Benchmarks
    ├── __init__.py
    └── test_workflow_performance.py
```

---

## Phase 2: Fix Test Generation Workflow (Week 2)

### 2.1 Refactor `test_gen.py` to Produce Real Tests

**Current Problem:** Generated tests are placeholders

```python
# CURRENT (BAD) - Generated test
def test_calculate_total_edge_cases():
    """Tests edge cases."""
    # TODO: Add tests for edge cases
    pass
```

**Target State:** Generated tests are immediately executable

```python
# TARGET (GOOD) - Generated test
@pytest.mark.parametrize("items,tax_rate,expected", [
    ([{"price": 100, "quantity": 1}], 0.1, 110.0),
    ([{"price": 50, "quantity": 2}], 0.1, 110.0),
    ([{"price": 100, "quantity": 1}], 0.0, 100.0),
    ([{"price": 0, "quantity": 1}], 0.1, 0.0),
])
def test_calculate_total_valid_inputs(items, tax_rate, expected):
    """Test calculate_total with valid inputs."""
    result = calculate_total(items, tax_rate)
    assert result == expected

def test_calculate_total_empty_list_raises():
    """Test that empty list raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        calculate_total([])

def test_calculate_total_missing_price():
    """Test handling of items missing price key."""
    items = [{"quantity": 2}]  # Missing 'price'
    result = calculate_total(items)
    assert result == 0.0  # Default price is 0
```

### 2.2 Enhanced Function Analysis

Replace regex-based extraction with AST analysis:

```python
# In test_gen.py - New analysis approach

import ast
from dataclasses import dataclass
from typing import List, Optional, Set

@dataclass
class FunctionSignature:
    """Detailed function analysis for test generation."""
    name: str
    params: List[tuple[str, str, Optional[str]]]  # (name, type, default)
    return_type: Optional[str]
    is_async: bool
    raises: Set[str]
    has_side_effects: bool
    docstring: Optional[str]
    complexity: int  # Cyclomatic complexity estimate

class ASTFunctionAnalyzer(ast.NodeVisitor):
    """AST-based function analyzer for accurate test generation."""

    def analyze(self, code: str) -> List[FunctionSignature]:
        """Analyze code and extract function signatures."""
        tree = ast.parse(code)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sig = self._extract_signature(node)
                functions.append(sig)

        return functions

    def _extract_signature(self, node) -> FunctionSignature:
        """Extract detailed signature from function node."""
        # Extract parameters with types and defaults
        params = []
        for arg in node.args.args:
            param_name = arg.arg
            param_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            params.append((param_name, param_type, None))

        # Extract return type
        return_type = ast.unparse(node.returns) if node.returns else None

        # Find raised exceptions
        raises = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Raise) and child.exc:
                if isinstance(child.exc, ast.Call):
                    raises.add(child.exc.func.id)

        return FunctionSignature(
            name=node.name,
            params=params,
            return_type=return_type,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            raises=raises,
            has_side_effects=self._detect_side_effects(node),
            docstring=ast.get_docstring(node),
            complexity=self._estimate_complexity(node),
        )
```

### 2.3 Smart Test Generation Templates

```python
# In test_gen.py - Improved generation

def generate_tests_for_function(sig: FunctionSignature) -> str:
    """Generate comprehensive tests based on function analysis."""
    tests = []

    # 1. Basic success path test
    tests.append(_generate_success_test(sig))

    # 2. Parametrized input variations
    if sig.params:
        tests.append(_generate_parametrized_tests(sig))

    # 3. Exception tests for each raised type
    for exception in sig.raises:
        tests.append(_generate_exception_test(sig, exception))

    # 4. Edge case tests based on parameter types
    tests.append(_generate_edge_case_tests(sig))

    # 5. Async-specific tests if applicable
    if sig.is_async:
        tests.append(_generate_async_tests(sig))

    return "\n\n".join(tests)

def _generate_parametrized_tests(sig: FunctionSignature) -> str:
    """Generate parametrized tests based on parameter types."""
    test_cases = []

    for param_name, param_type, default in sig.params:
        if "str" in param_type:
            test_cases.extend([
                f'("{param_name}_normal", "valid_string")',
                f'("{param_name}_empty", "")',
                f'("{param_name}_unicode", "unicode: \\u00e9\\u00e8")',
            ])
        elif "int" in param_type or "float" in param_type:
            test_cases.extend([
                f'("{param_name}_zero", 0)',
                f'("{param_name}_positive", 42)',
                f'("{param_name}_negative", -1)',
            ])
        elif "list" in param_type.lower():
            test_cases.extend([
                f'("{param_name}_empty", [])',
                f'("{param_name}_single", [1])',
                f'("{param_name}_multiple", [1, 2, 3])',
            ])

    return f'''
@pytest.mark.parametrize("test_name,value", [
    {chr(10).join(f"    {tc}," for tc in test_cases)}
])
def test_{sig.name}_parameter_variations(test_name, value):
    """Test {sig.name} with various parameter values."""
    # Test implementation based on parameter type
    pass
'''
```

---

## Phase 3: Add Critical Module Tests (Week 3-4)

### 3.1 Priority Modules to Test

| Module | Priority | Complexity | Estimated Tests |
|--------|----------|------------|-----------------|
| `workflows/base.py` | CRITICAL | High | 50-60 |
| `workflows/code_review.py` | HIGH | Medium | 30-40 |
| `workflows/security_audit.py` | HIGH | Medium | 30-40 |
| `memory/graph.py` | CRITICAL | High | 40-50 |
| `memory/long_term.py` | HIGH | Medium | 25-30 |
| `models/executor.py` | CRITICAL | High | 40-50 |
| `models/fallback.py` | HIGH | Medium | 30-35 |
| `routing/classifier.py` | MEDIUM | Low | 20-25 |

### 3.2 Test Template for Workflow Modules

```python
# tests/unit/workflows/test_code_review.py

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.empathy_os.workflows.code_review import CodeReviewWorkflow
from tests.base_workflow_test import BaseWorkflowTest

class TestCodeReviewWorkflow(BaseWorkflowTest):
    """Tests for CodeReviewWorkflow."""

    workflow_class = CodeReviewWorkflow
    expected_stages = ["triage", "analyze", "review", "report"]

    @pytest.fixture
    def sample_input(self):
        return {"path": ".", "files": ["test.py"]}

    # Inherits standard tests from BaseWorkflowTest

    # Workflow-specific tests

    @pytest.mark.asyncio
    async def test_triage_identifies_risky_files(self, workflow):
        """Test that triage correctly identifies high-risk files."""
        pass

    @pytest.mark.asyncio
    async def test_analyze_extracts_code_patterns(self, workflow):
        """Test code pattern extraction in analyze stage."""
        pass

    @pytest.mark.asyncio
    async def test_review_generates_actionable_feedback(self, workflow):
        """Test that review produces actionable recommendations."""
        pass

    @pytest.mark.asyncio
    async def test_report_formats_correctly(self, workflow):
        """Test report formatting and structure."""
        pass
```

---

## Phase 4: Consolidate and Deduplicate (Week 5)

### 4.1 Identify and Remove Duplicates

**Target: 149 duplicate test function names**

| Duplicate Pattern | Count | Action |
|-------------------|-------|--------|
| `call_llm_with_client` | 7 | Move to BaseWorkflowTest |
| `call_llm_no_client` | 6 | Move to BaseWorkflowTest |
| `test_initialization` | 5 | Rename to be specific |
| `test_basic_creation` | 3 | Rename to be specific |

### 4.2 Convert to Parametrized Tests

**Before (duplicated):**
```python
def test_scrub_email():
    assert scrub("test@example.com") == "[EMAIL]"

def test_scrub_phone():
    assert scrub("555-123-4567") == "[PHONE]"

def test_scrub_ssn():
    assert scrub("123-45-6789") == "[SSN]"
```

**After (parametrized):**
```python
@pytest.mark.parametrize("input_text,expected", [
    ("test@example.com", "[EMAIL]"),
    ("555-123-4567", "[PHONE]"),
    ("123-45-6789", "[SSN]"),
    ("John Smith", "[NAME]"),
    ("192.168.1.1", "[IP_ADDRESS]"),
])
def test_scrub_pii_types(input_text, expected):
    """Test PII scrubbing for various data types."""
    assert scrub(input_text) == expected
```

### 4.3 Merge Extended Test Files

**Current State:**
- `test_pii_scrubber.py` (24 tests)
- `test_pii_scrubber_extended.py` (67 tests, 30% overlap)

**Target State:**
- `test_pii_scrubber.py` (unified, ~70 tests after deduplication)

---

## Phase 5: Quality Gates and CI/CD (Week 6)

### 5.1 Coverage Requirements

```yaml
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=html --cov-fail-under=75"

# Per-module minimum coverage
[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 75
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### 5.2 GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run unit tests
        run: pytest tests/unit -v --cov --cov-fail-under=75

      - name: Run integration tests
        run: pytest tests/integration -v

      - name: Check for test quality
        run: |
          # Fail if any tests contain TODO or pass-only
          ! grep -r "# TODO" tests/ --include="*.py"
          ! grep -r "^\s*pass$" tests/ --include="*.py" | grep -v "__init__"
```

### 5.3 Test Quality Metrics Dashboard

Track these metrics weekly:

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Test count | 3,625 | 4,000+ | `pytest --collect-only \| wc -l` |
| Line coverage | ~60% | 80% | pytest-cov |
| Branch coverage | ~50% | 70% | pytest-cov |
| Duplicate tests | 149 | <20 | Script analysis |
| Parametrized files | 5.4% | 40% | grep analysis |
| Test execution time | ? | <5min | pytest timing |

---

## Implementation Timeline

| Phase | Week | Deliverables |
|-------|------|--------------|
| 1. Infrastructure | 1 | conftest.py, BaseWorkflowTest, directory reorg |
| 2. Test Generation | 2 | Refactored test_gen.py with AST analysis |
| 3. Critical Tests | 3-4 | Tests for 8 priority modules (300+ tests) |
| 4. Consolidation | 5 | Merged extended files, parametrized tests |
| 5. Quality Gates | 6 | CI/CD integration, coverage enforcement |

---

## Success Criteria

- [ ] Test generation produces 100% executable tests (0 TODOs)
- [ ] All 8 critical modules have >75% coverage
- [ ] Duplicate test count reduced from 149 to <20
- [ ] Parametrized test file usage increased from 5.4% to 40%
- [ ] Total test execution time <5 minutes
- [ ] CI/CD pipeline enforces coverage minimums

---

## Appendix: Test Naming Conventions

```
test_<module>_<function>_<scenario>.py

Examples:
- test_code_review_triage_identifies_risky_files
- test_pii_scrubber_email_standard_format
- test_executor_fallback_on_api_error
- test_memory_graph_node_retrieval_empty

Parametrized tests:
- test_<function>_<category> with @pytest.mark.parametrize
```

---

*Document Version: 1.0*
*Created: 2025-12-29*
*Author: Claude Code*
