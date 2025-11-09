"""
Security Analysis Components

Supporting modules for Security Analysis Wizard.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from .exploit_analyzer import ExploitAnalyzer
from .owasp_patterns import OWASPPatternDetector
from .vulnerability_scanner import (
    DependencyVulnerability,
    Severity,
    Vulnerability,
    VulnerabilityScanner,
    VulnerabilityScanReport,
    VulnerabilityType,
)

__all__ = [
    # Vulnerability Scanning
    "VulnerabilityScanner",
    "Vulnerability",
    "DependencyVulnerability",
    "VulnerabilityScanReport",
    "VulnerabilityType",
    "Severity",
    # Exploit Analysis
    "ExploitAnalyzer",
    # OWASP Patterns
    "OWASPPatternDetector",
]
