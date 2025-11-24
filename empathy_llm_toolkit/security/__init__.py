"""
Security Module for Empathy Framework

Provides enterprise-grade security controls including:
- PII scrubbing (GDPR, HIPAA, SOC2 compliant)
- Secrets detection (API keys, passwords, private keys)
- Audit logging (tamper-evident, SOC2/HIPAA compliant)
- Secure MemDocs integration with encryption

Author: Empathy Framework Team
Version: 1.8.0-beta
License: Fair Source 0.9
"""

from .audit_logger import AuditEvent, AuditLogger, SecurityViolation
from .pii_scrubber import PIIDetection, PIIPattern, PIIScrubber
from .secrets_detector import SecretDetection, SecretsDetector, SecretType, Severity, detect_secrets
from .secure_memdocs import (
    Classification,
    ClassificationRules,
    EncryptionManager,
    PatternMetadata,
    SecureMemDocsIntegration,
    SecurityError,
)

__all__ = [
    # PII Scrubbing
    "PIIScrubber",
    "PIIDetection",
    "PIIPattern",
    # Secrets Detection
    "SecretsDetector",
    "SecretDetection",
    "SecretType",
    "Severity",
    "detect_secrets",
    # Audit Logging
    "AuditLogger",
    "AuditEvent",
    "SecurityViolation",
    # Secure MemDocs Integration
    "SecureMemDocsIntegration",
    "Classification",
    "ClassificationRules",
    "PatternMetadata",
    "EncryptionManager",
    "SecurityError",
]
