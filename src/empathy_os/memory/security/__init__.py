"""
Security Module for Empathy Framework Memory

Provides enterprise-grade security controls including:
- PII scrubbing (GDPR, HIPAA, SOC2 compliant)
- Secrets detection (API keys, passwords, private keys)
- Audit logging (tamper-evident, SOC2/HIPAA compliant)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .audit_logger import AuditEvent, AuditLogger, SecurityViolation
from .pii_scrubber import PIIDetection, PIIPattern, PIIScrubber
from .secrets_detector import SecretDetection, SecretsDetector, SecretType, Severity, detect_secrets

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
]
