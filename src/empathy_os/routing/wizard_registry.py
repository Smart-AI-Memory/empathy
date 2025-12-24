"""
Wizard Registry

Central registry of available wizards with their descriptions,
capabilities, and auto-chain rules.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WizardInfo:
    """Information about a registered wizard."""

    name: str
    description: str
    keywords: list[str]  # Keywords for classification

    # Classification hints
    primary_domain: str = ""  # security, performance, testing, etc.
    handles_file_types: list[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high

    # Chaining configuration
    auto_chain: bool = False
    chain_triggers: list[dict[str, Any]] = field(default_factory=list)

    # Optional wizard class or factory
    wizard_class: type | None = None
    factory: Callable[..., Any] | None = None


# Default wizard registry
WIZARD_REGISTRY: dict[str, WizardInfo] = {
    # Workflows (cost-optimized pipelines)
    "security-audit": WizardInfo(
        name="security-audit",
        description="Analyze code for security vulnerabilities, injection risks, compliance",
        keywords=[
            "security",
            "vulnerability",
            "injection",
            "xss",
            "sql",
            "auth",
            "authentication",
            "authorization",
            "sensitive",
            "credential",
            "password",
            "secret",
            "owasp",
            "cve",
            "exploit",
        ],
        primary_domain="security",
        handles_file_types=[".py", ".js", ".ts", ".java", ".go", ".rb"],
        auto_chain=True,
        chain_triggers=[
            {"condition": "high_severity_count > 0", "next": "dependency-check"},
            {"condition": "vulnerability_type == 'injection'", "next": "code-review"},
        ],
    ),
    "code-review": WizardInfo(
        name="code-review",
        description="Review code for quality, best practices, maintainability, and bugs",
        keywords=[
            "review",
            "code",
            "quality",
            "lint",
            "style",
            "convention",
            "best practice",
            "maintainability",
            "readable",
            "clean",
            "refactor",
            "smell",
        ],
        primary_domain="quality",
        handles_file_types=[".py", ".js", ".ts", ".java", ".go", ".rb", ".cpp", ".c"],
        auto_chain=True,
        chain_triggers=[
            {"condition": "has_complexity_issues", "next": "refactor-plan"},
        ],
    ),
    "bug-predict": WizardInfo(
        name="bug-predict",
        description="Predict potential bugs based on code patterns and historical data",
        keywords=[
            "bug",
            "error",
            "crash",
            "exception",
            "fail",
            "broken",
            "fix",
            "issue",
            "problem",
            "defect",
            "null",
            "undefined",
        ],
        primary_domain="debugging",
        auto_chain=True,
        chain_triggers=[
            {"condition": "risk_score > 0.7", "next": "test-gen"},
        ],
    ),
    "perf-audit": WizardInfo(
        name="perf-audit",
        description="Analyze code for performance issues, bottlenecks, optimizations",
        keywords=[
            "performance",
            "perf",
            "slow",
            "fast",
            "speed",
            "optimize",
            "bottleneck",
            "memory",
            "cpu",
            "latency",
            "throughput",
            "cache",
            "profile",
        ],
        primary_domain="performance",
        auto_chain=True,
        chain_triggers=[
            {"condition": "hotspot_count > 5", "next": "refactor-plan"},
        ],
    ),
    "refactor-plan": WizardInfo(
        name="refactor-plan",
        description="Plan code refactoring to improve structure, reduce complexity",
        keywords=[
            "refactor",
            "restructure",
            "reorganize",
            "simplify",
            "complexity",
            "architecture",
            "design",
            "pattern",
            "clean",
        ],
        primary_domain="architecture",
        auto_chain=False,  # Require approval for refactoring
    ),
    "test-gen": WizardInfo(
        name="test-gen",
        description="Generate test cases and improve test coverage",
        keywords=[
            "test",
            "testing",
            "unit",
            "integration",
            "coverage",
            "pytest",
            "jest",
            "mock",
            "assert",
            "spec",
        ],
        primary_domain="testing",
        handles_file_types=[".py", ".js", ".ts", ".java"],
        auto_chain=True,
        chain_triggers=[
            {"condition": "coverage_low", "next": "bug-predict"},
        ],
    ),
    "doc-gen": WizardInfo(
        name="doc-gen",
        description="Generate documentation from code including API docs, READMEs, and guides",
        keywords=[
            "document",
            "doc",
            "readme",
            "api",
            "explain",
            "describe",
            "comment",
            "docstring",
            "jsdoc",
        ],
        primary_domain="documentation",
        auto_chain=False,
    ),
    "dependency-check": WizardInfo(
        name="dependency-check",
        description="Audit dependencies for vulnerabilities, updates, and license issues",
        keywords=[
            "dependency",
            "package",
            "npm",
            "pip",
            "library",
            "version",
            "update",
            "outdated",
            "license",
            "vulnerability",
        ],
        primary_domain="dependencies",
        handles_file_types=["requirements.txt", "package.json", "pyproject.toml", "Cargo.toml"],
        auto_chain=True,
        chain_triggers=[
            {"condition": "critical_vuln_count > 0", "next": "security-audit"},
        ],
    ),
    "release-prep": WizardInfo(
        name="release-prep",
        description="Pre-release quality gate with health checks, security scan, and changelog",
        keywords=[
            "release",
            "deploy",
            "publish",
            "ship",
            "version",
            "changelog",
            "ready",
            "production",
        ],
        primary_domain="release",
        auto_chain=False,  # Always require approval
    ),
    "research": WizardInfo(
        name="research",
        description="Research and synthesize information from multiple sources",
        keywords=[
            "research",
            "investigate",
            "explore",
            "analyze",
            "study",
            "understand",
            "learn",
            "compare",
        ],
        primary_domain="research",
        auto_chain=False,
    ),
}


class WizardRegistry:
    """
    Registry for managing available wizards.

    Usage:
        registry = WizardRegistry()
        info = registry.get("security-audit")
        all_wizards = registry.list_all()
    """

    def __init__(self):
        """Initialize with default wizards."""
        self._wizards: dict[str, WizardInfo] = dict(WIZARD_REGISTRY)

    def register(self, info: WizardInfo) -> None:
        """Register a new wizard."""
        self._wizards[info.name] = info

    def get(self, name: str) -> WizardInfo | None:
        """Get wizard info by name."""
        return self._wizards.get(name)

    def list_all(self) -> list[WizardInfo]:
        """List all registered wizards."""
        return list(self._wizards.values())

    def find_by_domain(self, domain: str) -> list[WizardInfo]:
        """Find wizards by primary domain."""
        return [w for w in self._wizards.values() if w.primary_domain == domain]

    def find_by_keyword(self, keyword: str) -> list[WizardInfo]:
        """Find wizards that handle a keyword."""
        keyword = keyword.lower()
        return [
            w for w in self._wizards.values() if any(keyword in kw.lower() for kw in w.keywords)
        ]

    def get_descriptions_for_classification(self) -> dict[str, str]:
        """Get wizard name to description mapping for LLM classification."""
        return {
            name: f"{info.description} (domain: {info.primary_domain})"
            for name, info in self._wizards.items()
        }

    def get_chain_triggers(self, wizard_name: str) -> list[dict[str, Any]]:
        """Get auto-chain triggers for a wizard."""
        info = self._wizards.get(wizard_name)
        if info and info.auto_chain:
            return info.chain_triggers
        return []

    def unregister(self, name: str) -> bool:
        """Remove a wizard from the registry."""
        if name in self._wizards:
            del self._wizards[name]
            return True
        return False
