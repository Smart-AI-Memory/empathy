"""Trust Management Module

Cross-domain transfer of reliability patterns to human-AI trust management.
Implements Level 5 (Systems Thinking) capability.

Pattern Source: Circuit Breaker (reliability/circuit_breaker.py)
Transfer: Protect user trust like protecting system stability
"""

from .circuit_breaker import (
    TrustCircuitBreaker,
    TrustConfig,
    TrustDamageEvent,
    TrustDamageType,
    TrustRecoveryEvent,
    TrustState,
    create_trust_breaker,
)

__all__ = [
    "TrustCircuitBreaker",
    "TrustConfig",
    "TrustDamageEvent",
    "TrustDamageType",
    "TrustRecoveryEvent",
    "TrustState",
    "create_trust_breaker",
]
