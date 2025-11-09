# Empathy Software Development Plugin

**AI-powered code analysis wizards demonstrating Level 4 Anticipatory Empathy**

The Empathy Software Plugin provides 16+ specialized Coach wizards that analyze your codebase and alert you to emerging issues **before they become critical**. Based on real-world experience where this framework transformed development productivity with higher quality code developed many times faster.

## Table of Contents

- [Quick Start](#quick-start)
- [Available Wizards](#available-wizards)
- [Usage Examples](#usage-examples)
- [Testing Infrastructure](#testing-infrastructure)
- [Architecture](#architecture)
- [API Reference](#api-reference)

## Quick Start

### Installation

```bash
pip install empathy-framework
```

### Basic Usage

```python
from empathy_software_plugin.plugin import SoftwarePlugin
from empathy_os.plugins import get_global_registry

# Initialize plugin
plugin = SoftwarePlugin()
registry = get_global_registry()
registry.register_plugin("software", plugin)

# Get available wizards
wizards = plugin.register_wizards()
print(f"Loaded {len(wizards)} AI development wizards")

# Run security analysis wizard
if "security" in wizards:
    SecurityWizard = wizards["security"]
    wizard = SecurityWizard()
    results = await wizard.analyze_code(project_path="/path/to/project")
```

### CLI Usage

```bash
# List available wizards
empathy-software list-wizards

# Get wizard information
empathy-software wizard-info security

# Analyze project with specific wizards
empathy-software analyze /path/to/project --wizards security,performance,testing

# Analyze with all wizards
empathy-software analyze /path/to/project
```

## Available Wizards

### Core Development Wizards

| Wizard | Purpose | Empathy Level |
|--------|---------|---------------|
| **Security** | Detect vulnerabilities, insecure patterns, authentication issues | Level 4 (Anticipatory) |
| **Performance** | Identify bottlenecks, optimize algorithms, database queries | Level 4 (Anticipatory) |
| **Testing** | Suggest test cases, detect coverage gaps, quality analysis | Level 3 (Proactive) |
| **Architecture** | Review design patterns, coupling, cohesion | Level 4 (Anticipatory) |

### AI Development Wizards (Level 4 Anticipatory)

These wizards are specifically designed for AI/LLM application development:

| Wizard | Purpose |
|--------|---------|
| **Prompt Engineering** | Optimize prompts, detect anti-patterns, suggest improvements |
| **Context Window** | Manage token budgets, chunk strategies, context optimization |
| **AI Collaboration** | Human-AI workflow patterns, handoff points |
| **AI Documentation** | Generate AI-readable documentation, context files |
| **Agent Orchestration** | Multi-agent patterns, coordination strategies |
| **RAG Pattern** | Retrieval-augmented generation optimization |
| **Multi-Model** | Model selection, fallback strategies, cost optimization |

## Usage Examples

### Example 1: Security Analysis

```python
from empathy_software_plugin.wizards.security_wizard import SecurityWizard
from pathlib import Path

# Initialize wizard
wizard = SecurityWizard()

# Analyze project for security issues
results = await wizard.analyze_code(
    project_path="/path/to/project",
    focus_areas=["authentication", "input_validation", "secrets"]
)

# Results include:
# - Vulnerabilities detected
# - Severity ratings (Critical, High, Medium, Low)
# - Remediation suggestions
# - Code examples of fixes

for issue in results["vulnerabilities"]:
    print(f"[{issue['severity']}] {issue['description']}")
    print(f"  Location: {issue['file']}:{issue['line']}")
    print(f"  Fix: {issue['remediation']}\n")
```

### Example 2: Testing Wizard with Coverage Analysis

```python
from empathy_software_plugin.wizards.testing.coverage_analyzer import CoverageAnalyzer
from empathy_software_plugin.wizards.testing.test_suggester import TestSuggester

# Analyze test coverage
analyzer = CoverageAnalyzer()
report = analyzer.parse_coverage_file("coverage.xml")

print(f"Overall Coverage: {report.overall_percentage:.1f}%")
print(f"Files: {report.files_count}")
print(f"Total Lines: {report.total_lines}")
print(f"Covered Lines: {report.covered_lines}")

# Get uncovered critical areas
critical_files = [f for f in report.files if f.coverage_percentage < 50]
print(f"\n⚠️  {len(critical_files)} files below 50% coverage")

# Generate test suggestions
suggester = TestSuggester()
for file in critical_files:
    elements = suggester.analyze_file(Path(file.name))
    suggestions = suggester.suggest_tests(elements, set(file.covered_lines))

    print(f"\n{file.name}: {len(suggestions)} test suggestions")
    for sug in suggestions[:3]:  # Show top 3
        print(f"  [{sug.priority.value}] {sug.suggestion}")
```

### Example 3: AI Development - Prompt Engineering

```python
from empathy_software_plugin.wizards.prompt_engineering_wizard import PromptEngineeringWizard

wizard = PromptEngineeringWizard()

# Analyze prompts in codebase
results = await wizard.analyze_prompts("/path/to/ai_project")

# Detect anti-patterns
for anti_pattern in results["anti_patterns"]:
    print(f"⚠️  {anti_pattern['pattern']}")
    print(f"   File: {anti_pattern['location']}")
    print(f"   Issue: {anti_pattern['description']}")
    print(f"   Fix: {anti_pattern['suggestion']}\n")

# Optimization suggestions
for optimization in results["optimizations"]:
    print(f"✨ {optimization['title']}")
    print(f"   Estimated improvement: {optimization['estimated_improvement']}")
    print(f"   Recommendation: {optimization['recommendation']}\n")
```

### Example 4: Pattern Detection (Level 4 Anticipatory)

```python
from empathy_software_plugin.plugin import SoftwarePlugin

plugin = SoftwarePlugin()
patterns = plugin.register_patterns()

# Example pattern: Testing Bottleneck
testing_pattern = patterns["patterns"]["testing_bottleneck"]

print(f"Pattern: {testing_pattern['description']}")
print(f"Threshold: {testing_pattern['threshold']}")
print(f"Recommendation: {testing_pattern['recommendation']}")

# Alert triggered when:
# - Manual test count > 25
# - Total test time > 15 minutes
# → Recommend automation framework
```

## Testing Infrastructure

The Software Plugin includes comprehensive testing utilities:

### Coverage Analyzer

```python
from empathy_software_plugin.wizards.testing.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageFormat
)

analyzer = CoverageAnalyzer()

# Parse coverage from multiple formats
report_xml = analyzer.parse_coverage_file("coverage.xml", CoverageFormat.XML)
report_json = analyzer.parse_coverage_file("coverage.json", CoverageFormat.JSON)
report_lcov = analyzer.parse_coverage_file("coverage.info", CoverageFormat.LCOV)

# Generate summary
summary = analyzer.generate_summary(report_xml)
print(summary)
# Output:
# ============================================================
# COVERAGE REPORT SUMMARY
# ============================================================
# Total Files: 45
# Overall Coverage: 87.3%
# ...
```

### Quality Analyzer

```python
from empathy_software_plugin.wizards.testing.quality_analyzer import TestQualityAnalyzer

analyzer = TestQualityAnalyzer()

# Analyze test file quality
test_functions = analyzer.analyze_test_file(Path("tests/test_api.py"))

for test in test_functions:
    print(f"{test.name}: Quality Score = {test.quality_score:.0f}/100")
    if test.issues:
        print(f"  Issues: {[issue.value for issue in test.issues]}")

# Generate comprehensive report
report = analyzer.generate_quality_report(test_functions)
print(f"High Quality Tests: {report.high_quality_tests}")
print(f"Flaky Tests: {len(report.flaky_tests)}")
print(f"Slow Tests: {len(report.slow_tests)}")
```

### Test Suggester

```python
from empathy_software_plugin.wizards.testing.test_suggester import (
    TestSuggester,
    TestPriority
)

suggester = TestSuggester()

# Analyze code and suggest tests
elements = suggester.analyze_file(Path("src/api.py"))
covered_lines = {1, 2, 5, 10, 15}  # From coverage report
suggestions = suggester.suggest_tests(elements, covered_lines)

# Filter by priority
critical = [s for s in suggestions if s.priority == TestPriority.CRITICAL]

for suggestion in critical:
    print(f"🔴 CRITICAL: {suggestion.suggestion}")
    print(f"   File: {suggestion.target_file}:{suggestion.target_line}")
    print(f"   Type: {suggestion.test_type}")
    print(f"   Impact: +{suggestion.estimated_impact:.1f}% coverage")
    print(f"\nTemplate:")
    print(suggestion.template)
```

## Architecture

### Plugin Structure

```
empathy_software_plugin/
├── plugin.py                 # Main plugin class (95.71% coverage ✅)
├── cli.py                    # Command-line interface
└── wizards/
    ├── security/
    │   └── vulnerability_scanner.py
    ├── testing/
    │   ├── coverage_analyzer.py   # 75%+ coverage ✅
    │   ├── quality_analyzer.py    # 70%+ coverage ✅
    │   └── test_suggester.py      # 70%+ coverage ✅
    ├── security_wizard.py
    ├── performance_wizard.py
    ├── testing_wizard.py
    ├── architecture_wizard.py
    ├── prompt_engineering_wizard.py
    ├── ai_context_wizard.py
    ├── ai_collaboration_wizard.py
    ├── ai_documentation_wizard.py
    ├── agent_orchestration_wizard.py
    ├── rag_pattern_wizard.py
    └── multi_model_wizard.py
```

### Design Principles

1. **Graceful Degradation**: Wizards with missing dependencies don't crash - they're simply not loaded
2. **Pattern-Based**: Each wizard registers patterns that trigger proactive alerts
3. **Empathy Levels**: Wizards operate at Level 3 (Proactive) or Level 4 (Anticipatory)
4. **Cross-Domain Learning**: Patterns from one project inform suggestions in others (Level 5)

### How Wizards Work

```python
class BaseWizard:
    """Base class for all development wizards"""

    async def analyze_code(self, project_path: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze code and return findings

        Returns:
            {
                "findings": [...],
                "severity": "critical" | "high" | "medium" | "low",
                "suggestions": [...],
                "patterns_detected": [...]
            }
        """
        pass
```

## API Reference

### SoftwarePlugin

Main plugin class that registers wizards and patterns.

```python
class SoftwarePlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""

    def register_wizards(self) -> Dict[str, Type[BaseWizard]]:
        """Register all available wizards"""

    def register_patterns(self) -> Dict:
        """Register software development patterns"""
```

**Example:**

```python
plugin = SoftwarePlugin()
metadata = plugin.get_metadata()
print(f"{metadata.name} v{metadata.version}")
print(f"Domain: {metadata.domain}")
print(f"License: {metadata.license}")
```

### Pattern Registry

Access registered patterns for monitoring:

```python
patterns = plugin.register_patterns()

# Structure:
{
    "domain": "software",
    "patterns": {
        "testing_bottleneck": {
            "description": "Manual testing burden grows faster than team size...",
            "indicators": ["test_count_growth_rate", "manual_test_time"],
            "threshold": "test_time > 900 seconds",
            "recommendation": "Implement test automation framework"
        },
        "security_drift": {
            "description": "Security practices degrade over time...",
            "indicators": ["input_validation_coverage", "authentication_consistency"]
        }
    }
}
```

## Test Coverage & Quality

The Software Plugin is production-ready with comprehensive test coverage:

- **Plugin Core**: 95.71% coverage (31 tests)
- **Coverage Analyzer**: 75%+ coverage (40 tests)
- **Quality Analyzer**: 70%+ coverage (38 tests)
- **Test Suggester**: 70%+ coverage (40 tests)
- **Total**: 149+ tests for software plugin modules

All core functionality is thoroughly tested with both unit and integration tests.

## Real-World Impact

> *"The framework transformed our AI development workflow. Instead of discovering issues weeks later during debugging, the wizards alerted us to emerging problems immediately. We shipped higher quality code, many times faster."*
>
> — Development team using Empathy Framework in production

## Contributing

See the main [Empathy Framework README](README.md) for contribution guidelines.

## License

Fair Source License 0.9

Free for:
- Students and educators
- Companies with ≤5 employees

Commercial license required for companies with 6+ employees.

## Support

- Documentation: https://smartaimemory.com/empathy-framework
- Issues: https://github.com/Smart-AI-Memory/empathy/issues
- Email: contact@smartaimemory.com

---

Built with ❤️ by Deep Study AI, LLC
