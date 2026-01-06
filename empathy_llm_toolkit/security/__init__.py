"""Security Module for Empathy Framework

DEPRECATED: This module re-exports from empathy_os.memory.security
Use `from empathy_os.memory.security import ...` instead.

Provides enterprise-grade security controls including:
- PII scrubbing (GDPR, HIPAA, SOC2 compliant)
- Secrets detection (API keys, passwords, private keys)
- Audit logging (tamper-evident, SOC2/HIPAA compliant)
- Secure MemDocs integration with encryption

Author: Empathy Framework Team
Version: 2.0.0 (consolidated into empathy_os.memory)
License: Fair Source 0.9
"""

# Re-export from consolidated memory module for backwards compatibility
from empathy_os.memory.long_term import (
                                         Classification,
                                         ClassificationRules,
                                         EncryptionManager,
                                         PatternMetadata,
                                         SecureMemDocsIntegration,
                                         SecurityError,
)
from empathy_os.memory.security import (
                                         AuditEvent,
                                         AuditLogger,
                                         PIIDetection,
                                         PIIPattern,
                                         PIIScrubber,
                                         SecretDetection,
                                         SecretsDetector,
                                         SecretType,
                                         SecurityViolation,
                                         Severity,
                                         detect_secrets,
)

__all__ = [
    "AuditEvent",
    # Audit Logging
    "AuditLogger",
    "Classification",
    "ClassificationRules",
    "EncryptionManager",
    "PIIDetection",
    "PIIPattern",
    # PII Scrubbing
    "PIIScrubber",
    "PatternMetadata",
    "SecretDetection",
    "SecretType",
    # Secrets Detection
    "SecretsDetector",
    # Secure MemDocs Integration
    "SecureMemDocsIntegration",
    "SecurityError",
    "SecurityViolation",
    "Severity",
    "detect_secrets",
]
