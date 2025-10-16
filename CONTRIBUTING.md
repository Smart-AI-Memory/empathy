# Contributing to Empathy Framework

Thank you for your interest in contributing to the Empathy Framework! This document provides guidelines and best practices for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Deep-Study-AI/Empathy.git
cd Empathy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests to verify setup
pytest tests/
```

## Development Workflow

### Branch Strategy

- `main` - Stable releases
- `develop` - Development branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Creating a Feature

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Make your changes
# ...

# Commit with clear messages
git add .
git commit -m "feat: Add anticipatory pattern detection

- Implement trajectory analysis
- Add tests for edge cases
- Update documentation"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Format

We follow conventional commits:

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `style`: Code style changes (formatting, etc.)
- `chore`: Build process or auxiliary tool changes

**Examples:**

```
feat: Add Level 5 systems thinking module

Implements pattern sharing between multiple AI agents
for emergent collaboration capabilities.

Closes #42
```

```
fix: Correct trust calculation in feedback loops

Trust erosion was not properly clamped to [0,1] range.
Added tests to prevent regression.

Fixes #57
```

## Testing

### Writing Tests

All new code must include tests. We aim for **70%+ coverage**.

**Test Structure:**

```python
"""
Tests for Module Name

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
from empathy_os.your_module import YourClass


class TestYourClass:
    """Test YourClass functionality"""

    def test_initialization(self):
        """Test class initializes correctly"""
        obj = YourClass()
        assert obj is not None

    def test_your_method(self):
        """Test specific method behavior"""
        obj = YourClass()
        result = obj.your_method(input_data)
        assert result == expected_output

    def test_edge_case(self):
        """Test edge case handling"""
        obj = YourClass()
        # Test boundary conditions
        # Test error handling
        # Test invalid inputs
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/empathy_os --cov-report=term-missing

# Run specific test file
pytest tests/test_your_module.py

# Run specific test
pytest tests/test_your_module.py::TestYourClass::test_your_method

# Run with verbose output
pytest tests/ -v

# Run with output from print statements
pytest tests/ -s
```

### Coverage Requirements

- Minimum **70% overall coverage**
- New modules should have **80%+ coverage**
- Critical modules (core, levels) should have **90%+ coverage**

### Test Categories

1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test module interactions
3. **Example Tests** - Verify examples run correctly

## Code Standards

### Python Style

We follow **PEP 8** with these specifications:

- **Line length**: 100 characters max (more readable than 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted (stdlib, third-party, local)

### Type Hints

Use type hints for all public APIs:

```python
from typing import Dict, List, Optional, Any

def analyze_trajectory(
    data: List[Dict[str, Any]],
    threshold: float = 0.7
) -> Optional[Dict[str, Any]]:
    """
    Analyze data trajectory

    Args:
        data: Historical data points
        threshold: Confidence threshold (0.0-1.0)

    Returns:
        Analysis results or None if insufficient data
    """
    # Implementation
```

### Documentation

All public classes and methods must have docstrings:

```python
class LeveragePointAnalyzer:
    """
    Identifies high-leverage intervention points

    Based on Donella Meadows's 12 leverage points framework.
    Helps identify where to intervene in a system for maximum
    effectiveness.

    Example:
        >>> analyzer = LeveragePointAnalyzer()
        >>> problem = {"class": "trust_deficit", "description": "Low trust"}
        >>> points = analyzer.find_leverage_points(problem)
        >>> print(f"Found {len(points)} intervention points")

    Attributes:
        identified_points: List of leverage points found during analysis
    """
```

**Docstring Sections:**
- **Summary**: One-line description
- **Extended Description**: Detailed explanation (optional)
- **Example**: Usage example with >>> prompts
- **Attributes**: Public attributes (for classes)
- **Args**: Function parameters
- **Returns**: Return value description
- **Raises**: Exceptions that may be raised (if applicable)

### Code Organization

```python
# 1. Module docstring
"""Module description"""

# 2. Imports (grouped)
from typing import Dict, List  # Standard library
import numpy as np  # Third-party
from .core import EmpathyOS  # Local

# 3. Constants
DEFAULT_THRESHOLD = 0.75
MAX_ITERATIONS = 100

# 4. Classes
class YourClass:
    """Class docstring"""

    def __init__(self):
        """Initialize"""
        pass

    def public_method(self):
        """Public method"""
        pass

    def _private_method(self):
        """Private method (prefixed with _)"""
        pass

# 5. Functions
def utility_function():
    """Utility function"""
    pass
```

### Error Handling

Handle errors gracefully and provide helpful messages:

```python
def process_data(data: List[Dict]) -> Dict:
    """Process data with validation"""

    # Validate inputs
    if not data:
        raise ValueError("Data cannot be empty")

    if not all(isinstance(d, dict) for d in data):
        raise TypeError("All data items must be dictionaries")

    # Process with error handling
    try:
        result = complex_operation(data)
    except KeyError as e:
        raise KeyError(f"Missing required field: {e}")
    except Exception as e:
        raise RuntimeError(f"Processing failed: {e}")

    return result
```

## Documentation

### When to Update Documentation

Update documentation when:
- Adding new features
- Changing public APIs
- Adding examples
- Fixing bugs that affect usage

### Documentation Locations

- **README.md**: Project overview, quick start
- **examples/**: Runnable code examples
- **examples/README.md**: Example documentation
- **Docstrings**: In-code documentation
- **CONTRIBUTING.md**: This file

### Writing Examples

Good examples are:
- **Self-contained**: Run without external dependencies
- **Well-commented**: Explain what and why
- **Practical**: Show real-world use cases
- **Progressive**: Build from simple to complex

```python
"""
Example: Building Trust Through Anticipation

Demonstrates Level 4 Anticipatory Empathy by predicting
user needs before they arise.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from empathy_os import EmpathyOS

def main():
    """Demonstrate anticipatory trust building"""

    # Initialize with target level 4 (Anticipatory)
    empathy = EmpathyOS(user_id="example_user", target_level=4)

    print("Anticipatory Trust Building Example")
    print("=" * 50)

    # Your example code here...

if __name__ == "__main__":
    main()
```

## Pull Request Process

### Before Submitting

1. **Run all tests**: `pytest tests/ --cov=src/empathy_os`
2. **Check coverage**: Ensure 70%+ coverage
3. **Update documentation**: Add/update relevant docs
4. **Add examples**: If adding features, add example
5. **Self-review**: Read through your changes

### PR Checklist

- [ ] Tests pass locally
- [ ] Coverage is 70%+ overall
- [ ] New code has tests (80%+ coverage for new modules)
- [ ] Documentation updated
- [ ] Examples added/updated if relevant
- [ ] Commit messages follow conventional format
- [ ] Code follows style guide
- [ ] No merge conflicts with develop

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe testing performed:
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Examples tested manually
- [ ] Coverage: XX%

## Related Issues

Closes #XX
Relates to #YY

## Additional Notes

Any additional context or notes for reviewers.
```

### Review Process

1. **Automated checks**: CI/CD runs tests and coverage
2. **Code review**: Maintainers review code quality
3. **Testing**: Verify examples and edge cases
4. **Merge**: After approval, maintainer merges

### After Merge

- Your contribution will be included in next release
- You'll be added to contributors list
- Thank you for improving Empathy Framework!

## Getting Help

- **Issues**: GitHub Issues for bugs/features
- **Discussions**: GitHub Discussions for questions
- **Email**: [contact information if available]

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to Empathy Framework! 🤝
