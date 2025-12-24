# Empathy Framework - Plugin System

## Overview

The Empathy Framework is now **modular**, with a public core and domain-specific plugins. This enables:

- **Public Core**: Universal empathy framework (Apache 2.0)
- **Domain Plugins**: Specialized wizards for software, healthcare, finance, etc.
- **Cross-Domain Learning**: Patterns shared across all domains (Level 5 Systems Empathy)

## Architecture

```
📦 empathy-framework (CORE)
   ├── EmpathyOS orchestrator
   ├── 5 empathy levels (abstract)
   ├── Pattern library (cross-domain learning)
   ├── Systems thinking (feedback loops, leverage points)
   └── Plugin system (registry, auto-discovery)

📦 empathy-framework-software (PRIMARY PLUGIN)
   ├── 16+ Coach wizards
   ├── Security, performance, testing, architecture analysis
   └── Level 4 anticipatory code analysis

📦 empathy-framework-healthcare (SECONDARY PLUGIN)
   ├── Clinical wizards (SOAP, SBAR)
   ├── Compliance anticipation agents
   └── Regulatory gap analysis
```

## Installation

```bash
# Install core framework
pip install empathy-framework

# Install software development plugin (primary)
pip install empathy-framework-software

# Install healthcare plugin (optional)
pip install empathy-framework-healthcare
```

## Quick Start - Software Development

```python
from empathy_os.plugins import get_global_registry

# Auto-discover all installed plugins
registry = get_global_registry()

# List available plugins
print(registry.list_plugins())
# Output: ['software', 'healthcare']

# Get software plugin
software_plugin = registry.get_plugin('software')

# List available wizards
print(software_plugin.list_wizards())
# Output: ['security', 'performance', 'testing', 'architecture', ...]

# Get testing wizard
TestingWizard = registry.get_wizard('software', 'testing')

# Create wizard instance
wizard = TestingWizard()

# Analyze your project
result = await wizard.analyze({
    'project_path': '/path/to/your/repo',
    'test_files': ['tests/test_auth.py', 'tests/test_api.py', ...],
    'test_framework': 'pytest',
    'team_size': 5
})

# View results
print(result['issues'])          # Current problems
print(result['predictions'])      # Future bottlenecks (Level 4)
print(result['recommendations'])  # Actionable steps
```

### Example Output

```
ISSUES:
- [WARNING] Low test count - consider adding more tests

PREDICTIONS:
- [ALERT] Testing burden approaching critical threshold.
  In our experience, manual testing becomes unsustainable around 25+ tests.
  Consider implementing test automation framework before this becomes blocking.

  Prevention steps:
  - Design test automation framework
  - Implement shared test fixtures
  - Create parameterized test generation
  - Set up CI/CD integration

RECOMMENDATIONS:
1. Implement test automation framework proactively
2. Extract shared test utilities to reduce duplication
3. Set up CI/CD integration for automated test execution

Confidence: 0.8
```

## Command-Line Interface

```bash
# Analyze your repository
empathy-software analyze /path/to/repo --wizards security,performance,testing

# Get plugin statistics
empathy-framework plugins --stats

# List all wizards
empathy-framework wizards --list

# Find Level 4 (Anticipatory) wizards
empathy-framework wizards --level 4
```

## Creating Your Own Plugin

### 1. Create Plugin Structure

```
my-domain-plugin/
├── my_domain_plugin/
│   ├── __init__.py
│   ├── plugin.py           # Plugin registration
│   └── wizards/
│       ├── __init__.py
│       └── my_wizard.py    # Your wizards
├── pyproject.toml
└── README.md
```

### 2. Implement Plugin Class

```python
# my_domain_plugin/plugin.py
from empathy_os.plugins import BasePlugin, PluginMetadata, BaseWizard
from typing import Dict, Type

class MyDomainPlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Domain Plugin",
            version="1.0.0",
            domain="my_domain",
            description="Description of what your plugin does",
            author="Your Name",
            license="Apache-2.0",
            requires_core_version="1.0.0"
        )

    def register_wizards(self) -> Dict[str, Type[BaseWizard]]:
        from .wizards.my_wizard import MyWizard

        return {
            'my_wizard': MyWizard
        }
```

### 3. Implement Wizard

```python
# my_domain_plugin/wizards/my_wizard.py
from empathy_os.plugins import BaseWizard
from typing import Dict, Any, List

class MyWizard(BaseWizard):
    def __init__(self):
        super().__init__(
            name="My Wizard",
            domain="my_domain",
            empathy_level=4,  # 1-5
            category="analysis"
        )

    def get_required_context(self) -> List[str]:
        return ['data', 'config']  # Required context keys

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Validate context has required fields
        self.validate_context(context)

        # Your analysis logic here
        issues = []  # Current problems
        predictions = []  # Future issues (Level 4)

        return {
            "issues": issues,
            "predictions": predictions,
            "recommendations": ["Do X", "Do Y"],
            "patterns": [],  # For cross-domain learning
            "confidence": 0.85
        }
```

### 4. Register Entry Point

```toml
# pyproject.toml
[project]
name = "my-domain-plugin"
version = "1.0.0"

[project.entry-points."empathy_framework.plugins"]
my_domain = "my_domain_plugin.plugin:MyDomainPlugin"
```

### 5. Install and Use

```bash
pip install -e .  # Install in development mode

# Plugin is auto-discovered!
python -c "from empathy_os.plugins import get_global_registry; \
           print(get_global_registry().list_plugins())"
# Output: ['software', 'healthcare', 'my_domain']
```

## Empathy Levels Guide

### Level 1: Reactive
- Help after being asked
- Traditional Q&A

### Level 2: Guided
- Ask clarifying questions
- Collaborative exploration

### Level 3: Proactive
- Act before being asked
- Pattern detection

### Level 4: Anticipatory ⭐
- **Predict future needs**
- **Alert to bottlenecks before they're critical**
- **Design relief in advance**

### Level 5: Systems
- Build structures that scale
- Cross-domain pattern learning

## Experience-Based Philosophy

> "I had a theory: what if AI collaboration could progress through empathy levels? I built the framework and applied it to real projects. When it worked, the impact was more profound than I'd anticipated.
>
> In our experience developing the Empathy Framework across software and healthcare domains, we found ourselves building higher quality code many times faster—not because the AI wrote more code, but because it anticipated structural issues before they became costly to fix."

### Key Principles

1. **Honest**: We share what we've experienced, not what we promise
2. **Alert, Don't Predict**: We alert to bottlenecks in advance (not "67 days")
3. **Pattern-Based**: Recommendations based on real patterns we've observed
4. **Experience-Driven**: Built from actual use, not theory

## Registry Features

### Auto-Discovery

Plugins are automatically discovered via entry points—no manual registration needed.

```python
from empathy_os.plugins import get_global_registry

registry = get_global_registry()
# All installed plugins loaded automatically!
```

### Graceful Degradation

Missing plugins don't crash the system:

```python
# If healthcare plugin not installed, other plugins still work
plugin = registry.get_plugin('healthcare')  # Returns None if missing
```

### Query by Level

```python
# Find all Level 4 (Anticipatory) wizards
level_4_wizards = registry.find_wizards_by_level(4)

for wizard_info in level_4_wizards:
    print(f"{wizard_info['name']} ({wizard_info['plugin']})")
```

### Statistics

```python
stats = registry.get_statistics()
print(stats)
# {
#   'total_plugins': 2,
#   'total_wizards': 20,
#   'wizards_by_level': {
#     'level_3': 4,
#     'level_4': 16
#   },
#   'plugins': [...]
# }
```

## Cross-Domain Pattern Learning (Level 5)

Patterns discovered in one domain can apply to others:

```python
# Pattern discovered in software development:
pattern = {
    "pattern_type": "growth_trajectory_alert",
    "description": "Alert before threshold, not after",
    "applicable_to": [
        "software testing",
        "healthcare documentation",
        "compliance tracking",
        "financial auditing"
    ]
}

# Healthcare plugin can leverage this pattern!
```

## Book Structure

**Part 1: Core Framework** (Chapters 1-3)
- The 5 empathy levels
- Systems thinking integration
- EmpathyOS implementation

**Part 2: Software Development Plugin** (Chapters 4-7) - PRIMARY
- 16+ Coach wizards
- Security, performance, testing analysis
- Level 4 anticipatory examples
- "Run this on YOUR code today"

**Part 3: Healthcare Plugin** (Chapter 8) - PROOF OF MODULARITY
- Clinical compliance agents
- Shows same framework, different domain
- "If it works in regulated healthcare, it's production-ready"

**Part 4: Build Your Own** (Chapters 9-10)
- Plugin development guide
- Template implementations
- Pattern contribution

## Contributing

We welcome plugins for new domains:
- Finance (fraud detection, compliance)
- DevOps (infrastructure, deployment)
- Customer Support (ticket analysis, response optimization)
- Education (curriculum design, learning paths)
- And more...

## License

- **Core Framework**: Apache 2.0 (public)
- **Software Plugin**: Apache 2.0 (public)
- **Healthcare Plugin**: Apache 2.0 or Commercial (TBD)

## Resources

- Documentation: https://empathy-framework.readthedocs.io
- Examples: `/examples` directory
- Plugin Template: `/plugin-template` directory
- GitHub: https://github.com/your-org/empathy-framework

---

**Built from experience. Shared with honesty. Extended by community.**
