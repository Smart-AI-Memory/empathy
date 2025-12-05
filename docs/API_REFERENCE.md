# Empathy Framework API Reference

**Version:** 1.0.0
**License:** Fair Source 0.9
**Copyright:** 2025 Smart AI Memory, LLC

---

## Table of Contents

- [Overview](#overview)
- [Core Framework](#core-framework)
  - [EmpathyLLM](#empathyllm)
  - [CollaborationState](#collaborationstate)
  - [EmpathyLevel](#empathylevel)
- [LLM Providers](#llm-providers)
  - [AnthropicProvider](#anthropicprovider)
  - [OpenAIProvider](#openaiprovider)
  - [LocalProvider](#localprovider)
- [Configuration](#configuration)
  - [EmpathyConfig](#empathyconfig)
- [Coach Wizards](#coach-wizards)
  - [BaseCoachWizard](#basecoachwizard)
  - [SecurityWizard](#securitywizard)
  - [PerformanceWizard](#performancewizard)
  - [All Available Wizards](#all-available-wizards)
- [Plugin System](#plugin-system)
  - [BasePlugin](#baseplugin)
  - [SoftwarePlugin](#softwareplugin)
- [Data Models](#data-models)
- [Pattern Library](#pattern-library)
- [Utilities](#utilities)

---

## Overview

The Empathy Framework provides a comprehensive API for building AI systems that progress from reactive (Level 1) to anticipatory (Level 4) and systems-level (Level 5) collaboration. This reference documents all public APIs, classes, methods, and their usage.

### Core Concepts

- **Level 1 (Reactive)**: Simple question-answer, no memory
- **Level 2 (Guided)**: Contextual collaboration with clarifying questions
- **Level 3 (Proactive)**: Pattern detection and proactive actions
- **Level 4 (Anticipatory)**: Trajectory prediction and bottleneck prevention
- **Level 5 (Systems)**: Cross-domain pattern learning and structural design

---

## Core Framework

### EmpathyLLM

Main class that wraps any LLM provider with Empathy Framework levels.

#### Constructor

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider: str = "anthropic",
    target_level: int = 3,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    pattern_library: Optional[Dict] = None,
    **kwargs
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | `str` | `"anthropic"` | LLM provider: `"anthropic"`, `"openai"`, or `"local"` |
| `target_level` | `int` | `3` | Maximum empathy level (1-5) |
| `api_key` | `Optional[str]` | `None` | API key for provider (or use environment variable) |
| `model` | `Optional[str]` | `None` | Specific model to use (provider defaults apply) |
| `pattern_library` | `Optional[Dict]` | `None` | Shared pattern library for Level 5 |
| `**kwargs` | - | - | Provider-specific options |

**Example:**

```python
# Using Anthropic (Claude)
llm = EmpathyLLM(
    provider="anthropic",
    target_level=4,
    api_key="sk-ant-..."
)

# Using OpenAI (GPT-4)
llm = EmpathyLLM(
    provider="openai",
    target_level=3,
    api_key="sk-...",
    model="gpt-4-turbo-preview"
)

# Using local model (Ollama)
llm = EmpathyLLM(
    provider="local",
    target_level=2,
    endpoint="http://localhost:11434",
    model="llama2"
)
```

#### Methods

##### `interact()`

Main interaction method that automatically selects appropriate empathy level.

```python
async def interact(
    user_id: str,
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    force_level: Optional[int] = None
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `str` | Yes | Unique user identifier |
| `user_input` | `str` | Yes | User's input/question |
| `context` | `Optional[Dict]` | No | Additional context dictionary |
| `force_level` | `Optional[int]` | No | Force specific level (testing/demo) |

**Returns:**

```python
{
    "content": str,              # LLM response
    "level_used": int,           # Which empathy level was used (1-5)
    "level_description": str,    # Human-readable level description
    "proactive": bool,           # Whether action was proactive
    "metadata": {
        "tokens_used": int,
        "model": str,
        # ... additional metadata
    }
}
```

**Example:**

```python
import asyncio

async def main():
    llm = EmpathyLLM(provider="anthropic", target_level=4)

    result = await llm.interact(
        user_id="developer_123",
        user_input="Help me optimize my database queries",
        context={
            "project_type": "web_app",
            "database": "postgresql"
        }
    )

    print(f"Level {result['level_used']}: {result['level_description']}")
    print(f"Response: {result['content']}")
    print(f"Proactive: {result['proactive']}")

asyncio.run(main())
```

##### `update_trust()`

Update trust level based on interaction outcome.

```python
def update_trust(
    user_id: str,
    outcome: str,
    magnitude: float = 1.0
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `str` | Yes | User identifier |
| `outcome` | `str` | Yes | `"success"` or `"failure"` |
| `magnitude` | `float` | No | Adjustment magnitude (0.0-1.0) |

**Example:**

```python
# Positive feedback
llm.update_trust("developer_123", outcome="success", magnitude=1.0)

# Negative feedback (reduce trust)
llm.update_trust("developer_123", outcome="failure", magnitude=0.5)
```

##### `add_pattern()`

Manually add a detected pattern for proactive behavior.

```python
def add_pattern(
    user_id: str,
    pattern: UserPattern
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `str` | Yes | User identifier |
| `pattern` | `UserPattern` | Yes | Pattern instance |

**Example:**

```python
from empathy_llm_toolkit import UserPattern, PatternType

pattern = UserPattern(
    pattern_type=PatternType.SEQUENTIAL,
    trigger="code review request",
    action="run security scan",
    confidence=0.85
)

llm.add_pattern("developer_123", pattern)
```

##### `get_statistics()`

Get collaboration statistics for a user.

```python
def get_statistics(user_id: str) -> Dict[str, Any]
```

**Returns:**

```python
{
    "total_interactions": int,
    "trust_level": float,
    "detected_patterns": int,
    "successful_actions": int,
    "failed_actions": int,
    "success_rate": float
}
```

---

### CollaborationState

Tracks collaboration state for individual users.

#### Properties

```python
class CollaborationState:
    user_id: str
    trust_level: float          # 0.0 to 1.0
    interactions: List[Dict]    # Interaction history
    detected_patterns: List[UserPattern]
    successful_actions: int
    failed_actions: int
    created_at: datetime
    updated_at: datetime
```

#### Methods

##### `add_interaction()`

```python
def add_interaction(
    role: str,
    content: str,
    level: int,
    metadata: Optional[Dict] = None
)
```

##### `get_conversation_history()`

```python
def get_conversation_history(
    max_turns: int = 10
) -> List[Dict[str, str]]
```

Returns conversation history formatted for LLM consumption.

##### `should_progress_to_level()`

```python
def should_progress_to_level(level: int) -> bool
```

Determines if sufficient trust exists to progress to a level.

---

### EmpathyLevel

Utility class for level-specific information.

#### Static Methods

##### `get_description()`

```python
@staticmethod
def get_description(level: int) -> str
```

Returns human-readable description of level.

**Example:**

```python
from empathy_llm_toolkit import EmpathyLevel

desc = EmpathyLevel.get_description(4)
# Returns: "Anticipatory - Predicts future needs based on trajectory"
```

##### `get_system_prompt()`

```python
@staticmethod
def get_system_prompt(level: int) -> str
```

Returns appropriate system prompt for the level.

##### `get_temperature_recommendation()`

```python
@staticmethod
def get_temperature_recommendation(level: int) -> float
```

Returns recommended temperature setting for the level.

##### `get_max_tokens_recommendation()`

```python
@staticmethod
def get_max_tokens_recommendation(level: int) -> int
```

Returns recommended max_tokens for the level.

---

## LLM Providers

### AnthropicProvider

Provider for Anthropic's Claude models with advanced features.

#### Constructor

```python
from empathy_llm_toolkit.providers import AnthropicProvider

provider = AnthropicProvider(
    api_key: Optional[str] = None,
    model: str = "claude-3-5-sonnet-20241022",
    use_prompt_caching: bool = True,
    use_thinking: bool = False,
    **kwargs
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `Optional[str]` | `None` | Anthropic API key |
| `model` | `str` | `"claude-3-5-sonnet-20241022"` | Claude model version |
| `use_prompt_caching` | `bool` | `True` | Enable prompt caching (90% cost reduction) |
| `use_thinking` | `bool` | `False` | Enable extended thinking mode |

**Supported Models:**

- `claude-3-opus-20240229` - Most capable, best for complex reasoning
- `claude-3-5-sonnet-20241022` - Balanced performance and cost (recommended)
- `claude-3-haiku-20240307` - Fastest, lowest cost

#### Methods

##### `generate()`

```python
async def generate(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    **kwargs
) -> LLMResponse
```

##### `analyze_large_codebase()`

Claude-specific method for analyzing entire repositories using 200K context window.

```python
async def analyze_large_codebase(
    codebase_files: List[Dict[str, str]],
    analysis_prompt: str,
    **kwargs
) -> LLMResponse
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `codebase_files` | `List[Dict]` | List of `{"path": "...", "content": "..."}` dicts |
| `analysis_prompt` | `str` | What to analyze for |

**Example:**

```python
provider = AnthropicProvider(
    api_key="sk-ant-...",
    use_prompt_caching=True
)

files = [
    {"path": "app.py", "content": "..."},
    {"path": "models.py", "content": "..."},
    {"path": "utils.py", "content": "..."}
]

result = await provider.analyze_large_codebase(
    codebase_files=files,
    analysis_prompt="Find all security vulnerabilities"
)

print(result.content)
```

##### `get_model_info()`

```python
def get_model_info() -> Dict[str, Any]
```

Returns model capabilities and pricing:

```python
{
    "max_tokens": 200000,
    "cost_per_1m_input": 3.00,
    "cost_per_1m_output": 15.00,
    "supports_prompt_caching": True,
    "supports_thinking": True,
    "ideal_for": "General development, balanced cost/performance"
}
```

---

### OpenAIProvider

Provider for OpenAI's GPT models.

#### Constructor

```python
from empathy_llm_toolkit.providers import OpenAIProvider

provider = OpenAIProvider(
    api_key: Optional[str] = None,
    model: str = "gpt-4-turbo-preview",
    **kwargs
)
```

**Supported Models:**

- `gpt-4-turbo-preview` - Latest GPT-4 with 128K context (recommended)
- `gpt-4` - Standard GPT-4 (8K context)
- `gpt-3.5-turbo` - Faster, cheaper option (16K context)

#### Methods

Same interface as `BaseLLMProvider`:
- `generate()`
- `get_model_info()`

---

### LocalProvider

Provider for local models (Ollama, LM Studio, etc.).

#### Constructor

```python
from empathy_llm_toolkit.providers import LocalProvider

provider = LocalProvider(
    endpoint: str = "http://localhost:11434",
    model: str = "llama2",
    **kwargs
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `endpoint` | `str` | `"http://localhost:11434"` | Local server endpoint |
| `model` | `str` | `"llama2"` | Model name |

**Example:**

```python
# Using Ollama
provider = LocalProvider(
    endpoint="http://localhost:11434",
    model="llama2"
)

# Using LM Studio
provider = LocalProvider(
    endpoint="http://localhost:1234",
    model="mistral-7b"
)
```

---

## Configuration

### EmpathyConfig

Comprehensive configuration management supporting YAML, JSON, and environment variables.

#### Constructor

```python
from empathy_os.config import EmpathyConfig

config = EmpathyConfig(
    user_id: str = "default_user",
    target_level: int = 3,
    confidence_threshold: float = 0.75,
    trust_building_rate: float = 0.05,
    trust_erosion_rate: float = 0.10,
    persistence_enabled: bool = True,
    persistence_backend: str = "sqlite",
    persistence_path: str = "./empathy_data",
    state_persistence: bool = True,
    state_path: str = "./empathy_state",
    metrics_enabled: bool = True,
    metrics_path: str = "./metrics.db",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    structured_logging: bool = True,
    pattern_library_enabled: bool = True,
    pattern_sharing: bool = True,
    pattern_confidence_threshold: float = 0.3,
    async_enabled: bool = True,
    feedback_loop_monitoring: bool = True,
    leverage_point_analysis: bool = True,
    metadata: Dict[str, Any] = {}
)
```

#### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | `str` | `"default_user"` | Default user identifier |
| `target_level` | `int` | `3` | Maximum empathy level (1-5) |
| `confidence_threshold` | `float` | `0.75` | Minimum confidence for actions |
| `trust_building_rate` | `float` | `0.05` | Trust increase per success |
| `trust_erosion_rate` | `float` | `0.10` | Trust decrease per failure |
| `persistence_enabled` | `bool` | `True` | Enable state persistence |
| `persistence_backend` | `str` | `"sqlite"` | Backend: `"sqlite"`, `"json"`, `"none"` |
| `metrics_enabled` | `bool` | `True` | Enable metrics collection |
| `pattern_library_enabled` | `bool` | `True` | Enable pattern learning |

#### Class Methods

##### `from_yaml()`

```python
@classmethod
def from_yaml(cls, filepath: str) -> EmpathyConfig
```

Load configuration from YAML file.

**Example:**

```python
config = EmpathyConfig.from_yaml("empathy.config.yml")
```

##### `from_json()`

```python
@classmethod
def from_json(cls, filepath: str) -> EmpathyConfig
```

Load configuration from JSON file.

##### `from_env()`

```python
@classmethod
def from_env(cls, prefix: str = "EMPATHY_") -> EmpathyConfig
```

Load configuration from environment variables.

**Example:**

```bash
export EMPATHY_USER_ID=alice
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.8
```

```python
config = EmpathyConfig.from_env()
```

##### `from_file()`

```python
@classmethod
def from_file(cls, filepath: Optional[str] = None) -> EmpathyConfig
```

Auto-detect and load configuration. Searches for:
1. Provided filepath
2. `.empathy.yml`
3. `.empathy.yaml`
4. `empathy.config.yml`
5. `empathy.config.yaml`
6. `.empathy.json`
7. `empathy.config.json`

#### Instance Methods

##### `to_yaml()`

```python
def to_yaml(filepath: str)
```

Save configuration to YAML file.

##### `to_json()`

```python
def to_json(filepath: str, indent: int = 2)
```

Save configuration to JSON file.

##### `validate()`

```python
def validate() -> bool
```

Validate configuration values. Raises `ValueError` if invalid.

##### `update()`

```python
def update(**kwargs)
```

Update configuration fields dynamically.

**Example:**

```python
config = EmpathyConfig()
config.update(user_id="alice", target_level=4)
```

##### `merge()`

```python
def merge(other: EmpathyConfig) -> EmpathyConfig
```

Merge with another configuration (other takes precedence).

---

## Coach Wizards

### BaseCoachWizard

Abstract base class for all Coach wizards implementing Level 4 Anticipatory Empathy.

#### Constructor

```python
from coach_wizards import BaseCoachWizard

class MyWizard(BaseCoachWizard):
    def __init__(self):
        super().__init__(
            name: str,
            category: str,
            languages: List[str]
        )
```

#### Abstract Methods (Must Implement)

##### `analyze_code()`

```python
@abstractmethod
def analyze_code(
    code: str,
    file_path: str,
    language: str
) -> List[WizardIssue]
```

Analyze code for current issues.

##### `predict_future_issues()`

```python
@abstractmethod
def predict_future_issues(
    code: str,
    file_path: str,
    project_context: Dict[str, Any],
    timeline_days: int = 90
) -> List[WizardPrediction]
```

Level 4 Anticipatory: Predict issues 30-90 days ahead.

##### `suggest_fixes()`

```python
@abstractmethod
def suggest_fixes(issue: WizardIssue) -> str
```

Suggest how to fix an issue with code examples.

#### Methods

##### `run_full_analysis()`

```python
def run_full_analysis(
    code: str,
    file_path: str,
    language: str,
    project_context: Optional[Dict[str, Any]] = None
) -> WizardResult
```

Run complete analysis: current issues + future predictions.

**Example:**

```python
from coach_wizards import SecurityWizard

wizard = SecurityWizard()

code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)
"""

result = wizard.run_full_analysis(
    code=code,
    file_path="auth.py",
    language="python",
    project_context={
        "team_size": 10,
        "deployment_frequency": "daily",
        "user_count": 5000
    }
)

print(f"Summary: {result.summary}")
print(f"Current issues: {len(result.issues)}")
print(f"Predicted issues: {len(result.predictions)}")

for issue in result.issues:
    print(f"  - [{issue.severity}] {issue.message}")

for prediction in result.predictions:
    print(f"  - [Predicted {prediction.predicted_date}] {prediction.issue_type}")
    print(f"    Probability: {prediction.probability:.0%}")
    print(f"    Prevention: {prediction.prevention_steps}")
```

---

### SecurityWizard

Detects security vulnerabilities and predicts future attack vectors.

```python
from coach_wizards import SecurityWizard

wizard = SecurityWizard()
```

**Detects:**
- SQL injection
- XSS (Cross-Site Scripting)
- CSRF vulnerabilities
- Hardcoded secrets
- Insecure dependencies
- Authentication flaws
- Authorization bypass
- Insecure deserialization

**Predicts (Level 4):**
- Emerging vulnerabilities
- Dependency risks
- Attack surface growth
- Zero-day exposure

**Supported Languages:**
- Python
- JavaScript/TypeScript
- Java
- Go
- Rust

---

### PerformanceWizard

Analyzes performance issues and predicts scalability bottlenecks.

```python
from coach_wizards import PerformanceWizard

wizard = PerformanceWizard()
```

**Detects:**
- N+1 query problems
- Memory leaks
- Inefficient algorithms
- Blocking operations
- Missing indexes
- Large object allocations

**Predicts (Level 4):**
- Scalability bottlenecks at growth rate
- Performance degradation timeline
- Resource exhaustion points

---

### All Available Wizards

The framework includes 16+ specialized Coach wizards:

#### Security & Compliance

- **SecurityWizard** - Security vulnerabilities
- **ComplianceWizard** - GDPR, SOC 2, PII handling

#### Performance & Scalability

- **PerformanceWizard** - Performance issues
- **DatabaseWizard** - Database optimization
- **ScalingWizard** - Scalability analysis

#### Code Quality

- **RefactoringWizard** - Code smells and complexity
- **TestingWizard** - Test coverage and quality
- **DebuggingWizard** - Error detection

#### API & Integration

- **APIWizard** - API design consistency
- **MigrationWizard** - Deprecated API detection

#### DevOps & Operations

- **CICDWizard** - CI/CD pipeline optimization
- **ObservabilityWizard** - Logging and metrics
- **MonitoringWizard** - System monitoring

#### User Experience

- **AccessibilityWizard** - WCAG compliance
- **LocalizationWizard** - Internationalization

#### Documentation

- **DocumentationWizard** - Documentation quality

**Import Example:**

```python
from coach_wizards import (
    SecurityWizard,
    PerformanceWizard,
    TestingWizard,
    AccessibilityWizard,
    # ... import others as needed
)
```

---

## Plugin System

### BasePlugin

Abstract base class for domain plugins.

```python
from empathy_os.plugins import BasePlugin, PluginMetadata

class MyPlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Plugin",
            version="1.0.0",
            domain="my_domain",
            description="Plugin description",
            author="Your Name",
            license="Apache-2.0",
            requires_core_version="1.0.0",
            dependencies=[]
        )

    def register_wizards(self) -> Dict[str, Type[BaseWizard]]:
        return {
            "my_wizard": MyWizard
        }

    def register_patterns(self) -> Dict:
        return {
            "domain": "my_domain",
            "patterns": { ... }
        }
```

---

### SoftwarePlugin

Built-in software development plugin providing 16+ Coach wizards.

```python
from empathy_software_plugin import SoftwarePlugin

plugin = SoftwarePlugin()
metadata = plugin.get_metadata()
wizards = plugin.register_wizards()
patterns = plugin.register_patterns()
```

---

## Data Models

### WizardIssue

Represents an issue found by a wizard.

```python
from coach_wizards.base_wizard import WizardIssue

issue = WizardIssue(
    severity: str,              # 'error', 'warning', 'info'
    message: str,               # Issue description
    file_path: str,             # File path
    line_number: Optional[int], # Line number
    code_snippet: Optional[str],# Code snippet
    fix_suggestion: Optional[str], # Fix suggestion
    category: str,              # Issue category
    confidence: float           # 0.0 to 1.0
)
```

### WizardPrediction

Level 4 Anticipatory: Predicts future issues.

```python
from coach_wizards.base_wizard import WizardPrediction

prediction = WizardPrediction(
    predicted_date: datetime,   # When issue will occur
    issue_type: str,            # Type of issue
    probability: float,         # 0.0 to 1.0
    impact: str,                # 'low', 'medium', 'high', 'critical'
    prevention_steps: List[str],# Steps to prevent
    reasoning: str              # Why this is predicted
)
```

### WizardResult

Complete wizard analysis result.

```python
from coach_wizards.base_wizard import WizardResult

result = WizardResult(
    wizard_name: str,
    issues: List[WizardIssue],
    predictions: List[WizardPrediction],
    summary: str,
    analyzed_files: int,
    analysis_time: float,
    recommendations: List[str]
)
```

### LLMResponse

Standardized response from any LLM provider.

```python
from empathy_llm_toolkit.providers import LLMResponse

response = LLMResponse(
    content: str,               # Response content
    model: str,                 # Model used
    tokens_used: int,           # Total tokens
    finish_reason: str,         # Why generation stopped
    metadata: Dict[str, Any]    # Additional metadata
)
```

### UserPattern

Represents a detected user pattern for Level 3 Proactive behavior.

```python
from empathy_llm_toolkit import UserPattern, PatternType

pattern = UserPattern(
    pattern_type: PatternType,  # SEQUENTIAL, CONDITIONAL, ADAPTIVE
    trigger: str,               # What triggers the pattern
    action: str,                # What action to take
    confidence: float,          # 0.0 to 1.0
    usage_count: int = 0,       # How many times used
    success_rate: float = 1.0   # Success rate
)
```

**PatternType Enum:**
- `PatternType.SEQUENTIAL` - Sequential workflow
- `PatternType.CONDITIONAL` - Conditional logic
- `PatternType.ADAPTIVE` - Adapts based on context

---

## Pattern Library

The pattern library enables Level 5 Systems Empathy through cross-domain learning.

### Pattern Structure

```python
pattern_library = {
    "domain": "software",
    "patterns": {
        "pattern_id": {
            "description": str,
            "indicators": List[str],
            "threshold": str,
            "recommendation": str
        }
    }
}
```

### Example Patterns

```python
software_patterns = {
    "domain": "software",
    "patterns": {
        "testing_bottleneck": {
            "description": "Manual testing burden grows faster than team",
            "indicators": [
                "test_count_growth_rate",
                "manual_test_time",
                "wizard_count"
            ],
            "threshold": "test_time > 900 seconds",
            "recommendation": "Implement test automation framework"
        },
        "security_drift": {
            "description": "Security practices degrade without monitoring",
            "indicators": [
                "input_validation_coverage",
                "authentication_consistency"
            ],
            "threshold": "coverage < 80%",
            "recommendation": "Add security wizard to CI/CD"
        }
    }
}
```

---

## Utilities

### load_config()

Flexible configuration loading with precedence.

```python
from empathy_os.config import load_config

config = load_config(
    filepath: Optional[str] = None,
    use_env: bool = True,
    defaults: Optional[Dict[str, Any]] = None
) -> EmpathyConfig
```

**Precedence (highest to lowest):**
1. Environment variables (if `use_env=True`)
2. Configuration file (if provided/found)
3. Defaults (if provided)
4. Built-in defaults

**Example:**

```python
# Load with all defaults
config = load_config()

# Load from specific file
config = load_config("my-config.yml")

# Load with custom defaults
config = load_config(defaults={"target_level": 4})

# Load file + override with env vars
config = load_config("empathy.yml", use_env=True)
```

---

## Complete Example

Here's a comprehensive example using multiple APIs:

```python
import asyncio
from empathy_llm_toolkit import EmpathyLLM, UserPattern, PatternType
from empathy_os.config import load_config
from coach_wizards import SecurityWizard, PerformanceWizard

async def main():
    # Load configuration
    config = load_config("empathy.config.yml", use_env=True)

    # Initialize EmpathyLLM with Claude
    llm = EmpathyLLM(
        provider="anthropic",
        target_level=config.target_level,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Initialize wizards
    security = SecurityWizard()
    performance = PerformanceWizard()

    # Analyze code with security wizard
    code = open("app.py").read()
    security_result = security.run_full_analysis(
        code=code,
        file_path="app.py",
        language="python",
        project_context={
            "team_size": 10,
            "deployment_frequency": "daily",
            "user_count": 5000
        }
    )

    # Report current issues
    print(f"Security Analysis: {security_result.summary}")
    for issue in security_result.issues:
        print(f"  [{issue.severity}] {issue.message} (line {issue.line_number})")

    # Report Level 4 predictions
    print("\nLevel 4 Anticipatory Predictions:")
    for pred in security_result.predictions:
        print(f"  {pred.issue_type} predicted on {pred.predicted_date}")
        print(f"  Probability: {pred.probability:.0%}, Impact: {pred.impact}")
        print(f"  Prevention: {pred.prevention_steps}")

    # Use EmpathyLLM for conversational help
    result = await llm.interact(
        user_id="developer_alice",
        user_input="How do I fix the SQL injection on line 42?",
        context={
            "wizard_results": security_result,
            "file": "app.py"
        }
    )

    print(f"\nLevel {result['level_used']} Response:")
    print(result['content'])

    # Update trust based on outcome
    llm.update_trust("developer_alice", outcome="success")

    # Add pattern for future proactive help
    pattern = UserPattern(
        pattern_type=PatternType.SEQUENTIAL,
        trigger="code review request",
        action="run security scan automatically",
        confidence=0.90
    )
    llm.add_pattern("developer_alice", pattern)

    # Get statistics
    stats = llm.get_statistics("developer_alice")
    print(f"\nCollaboration Stats:")
    print(f"  Trust level: {stats['trust_level']:.2f}")
    print(f"  Success rate: {stats['success_rate']:.0%}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Environment Variables

All configuration can be set via environment variables:

```bash
# Core settings
export EMPATHY_USER_ID=alice
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.8

# LLM providers
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...

# Persistence
export EMPATHY_PERSISTENCE_ENABLED=true
export EMPATHY_PERSISTENCE_BACKEND=sqlite
export EMPATHY_PERSISTENCE_PATH=./empathy_data

# Metrics
export EMPATHY_METRICS_ENABLED=true
export EMPATHY_METRICS_PATH=./metrics.db

# Pattern library
export EMPATHY_PATTERN_LIBRARY_ENABLED=true
export EMPATHY_PATTERN_SHARING=true
```

---

## Error Handling

All API methods raise standard Python exceptions:

```python
try:
    llm = EmpathyLLM(
        provider="anthropic",
        api_key="invalid_key"
    )
except ValueError as e:
    print(f"Configuration error: {e}")

try:
    result = await llm.interact(
        user_id="test",
        user_input="Hello"
    )
except Exception as e:
    print(f"Runtime error: {e}")
```

**Common Exceptions:**
- `ValueError` - Invalid configuration or parameters
- `ImportError` - Missing dependencies
- `FileNotFoundError` - Configuration file not found
- `JSONDecodeError` - Invalid JSON configuration

---

## Support & Resources

- **Documentation:** https://github.com/Deep-Study-AI/Empathy/tree/main/docs
- **Issues:** https://github.com/Deep-Study-AI/Empathy/issues
- **Discussions:** https://github.com/Deep-Study-AI/Empathy/discussions
- **Email:** patrick.roebuck@deepstudyai.com

**Commercial Support:**
- Priority bug fixes and feature requests
- Direct access to core development team
- Guaranteed response times
- Security advisories

Learn more: https://github.com/Deep-Study-AI/Empathy/blob/main/SPONSORSHIP.md

---

**Copyright 2025 Smart AI Memory, LLC**
**Licensed under Fair Source 0.9**
