# Security Module

Enterprise-grade security controls for the Empathy Framework, including secrets detection, PII scrubbing, audit logging, and data classification.

## Phase 2: Secrets Detection (v1.8.0-beta) ✅

### Overview

The `SecretsDetector` module provides comprehensive detection of hardcoded secrets, credentials, and sensitive data in code and configuration files. It's designed for enterprise privacy integration with:

- **20+ built-in patterns** for common secret types
- **Entropy analysis** for unknown high-entropy strings
- **Custom pattern support** for organization-specific secrets
- **Zero secret leakage**: Returns only metadata, never actual secret values
- **High performance**: Compiled regex patterns with early exit

### Quick Start

```python
from empathy_llm_toolkit.security import SecretsDetector

# Initialize detector
detector = SecretsDetector()

# Scan content for secrets
code = """
ANTHROPIC_API_KEY = "sk-ant-api03-abc123..."
password = "my_secret_pass"
"""

detections = detector.detect(code)

for detection in detections:
    print(f"Found {detection.secret_type.value} at line {detection.line_number}")
    print(f"  Severity: {detection.severity.value}")
    print(f"  Context: {detection.context_snippet}")
```

### Supported Secret Types

#### API Keys
- Anthropic API keys (`sk-ant-...`)
- OpenAI API keys (`sk-...`)
- AWS Access Keys (`AKIA...`)
- AWS Secret Keys
- GitHub tokens (`ghp_...`, `gho_...`, etc.)
- Slack tokens (`xox[abprs]-...`)
- Stripe keys (`sk_live_...`, `pk_live_...`)
- Generic API key patterns

#### Passwords
- Password assignments (`password = "..."`)
- Basic Auth credentials (base64 encoded)

#### Private Keys
- RSA private keys
- SSH private keys (OpenSSH format)
- EC (Elliptic Curve) private keys
- PGP private keys
- TLS/SSL certificate keys

#### Tokens
- JWT tokens (`eyJ...`)
- OAuth access tokens
- Bearer tokens

#### Database
- Database connection URLs (PostgreSQL, MySQL, MongoDB, Redis)
- Connection strings

#### High Entropy Strings
- Automatically detects random-looking strings (potential secrets)
- Configurable entropy threshold (default: 4.5)
- Minimum length requirement (default: 20 characters)

### Advanced Features

#### Custom Patterns

Add organization-specific secret patterns:

```python
detector = SecretsDetector()

# Add custom pattern
detector.add_custom_pattern(
    name="acme_api_key",
    pattern=r"acme_[a-zA-Z0-9]{32}",
    severity="high"
)

# Detect with custom pattern
detections = detector.detect("acme_1234567890abcdefghijklmnopqrst")
```

#### Entropy Analysis

Control high-entropy string detection:

```python
detector = SecretsDetector(
    enable_entropy_analysis=True,
    entropy_threshold=4.5,       # Shannon entropy threshold
    min_entropy_length=20         # Minimum string length
)
```

#### Detection Metadata

The `SecretDetection` object provides rich metadata without exposing secrets:

```python
detection = detections[0]

print(detection.secret_type)      # SecretType.ANTHROPIC_API_KEY
print(detection.severity)          # Severity.HIGH
print(detection.line_number)       # 3
print(detection.column_start)      # 20
print(detection.column_end)        # 95
print(detection.context_snippet)   # "ANTHROPIC_API_KEY = [REDACTED]"
print(detection.confidence)        # 1.0 (for pattern matches)
print(detection.metadata)          # {"custom_pattern": "acme_api_key"}
```

#### Statistics

Get detector configuration and pattern counts:

```python
stats = detector.get_statistics()
print(stats)
# {
#     "builtin_patterns": 20,
#     "custom_patterns": 2,
#     "total_patterns": 22,
#     "entropy_analysis_enabled": True,
#     "entropy_threshold": 4.5,
#     "min_entropy_length": 20
# }
```

### Security Guarantees

1. **No Secret Leakage**: The detector NEVER logs or returns actual secret values
2. **Redaction**: Context snippets replace secrets with `[REDACTED]`
3. **Metadata Only**: Detection objects contain only type, location, and severity
4. **Audit Safe**: All outputs are safe to log without exposing credentials

### Performance

- **Compiled Patterns**: All regex patterns are pre-compiled for speed
- **Early Exit**: Detection stops on first match for each pattern
- **Large Files**: Tested with 10,000+ line files (completes < 5 seconds)
- **Efficient Entropy**: Entropy analysis only runs on quoted strings

### Integration Example

```python
from empathy_llm_toolkit.security import SecretsDetector

def scan_file(file_path: str) -> bool:
    """
    Scan a file for secrets.

    Returns:
        True if no secrets found, False otherwise
    """
    detector = SecretsDetector()

    with open(file_path, 'r') as f:
        content = f.read()

    detections = detector.detect(content)

    if detections:
        print(f"⚠️  Found {len(detections)} secrets in {file_path}")

        for d in detections:
            print(f"  - {d.secret_type.value} (Line {d.line_number})")
            print(f"    Severity: {d.severity.value}")
            print(f"    Context: {d.context_snippet}")

        return False

    print(f"✓ No secrets found in {file_path}")
    return True
```

### Testing

Comprehensive test suite with 28 tests covering:
- All secret type detections
- Custom pattern support
- Entropy analysis
- Secret redaction
- Edge cases and error handling
- Performance benchmarks

Run tests:
```bash
pytest empathy_llm_toolkit/security/test_secrets_detector.py -v
```

### Compliance

This module supports enterprise compliance requirements:

- **OWASP Top 10 A02:2021**: Cryptographic Failures (secret detection)
- **GDPR Article 32**: Security of processing (protect credentials)
- **SOC2 CC6.1**: Logical access controls (prevent hardcoded secrets)
- **HIPAA §164.312(a)(1)**: Access control (credential management)

### Architecture

```
SecretsDetector
├── Built-in Patterns (20+)
│   ├── API Keys (Anthropic, OpenAI, AWS, GitHub, Slack, Stripe)
│   ├── Passwords (various assignment patterns)
│   ├── Private Keys (RSA, SSH, EC, PGP, TLS)
│   ├── Tokens (JWT, OAuth, Bearer)
│   └── Database (connection strings, URLs)
├── Custom Patterns
│   └── Organization-specific patterns
├── Entropy Analysis
│   ├── Shannon entropy calculation
│   ├── Configurable threshold
│   └── Overlap filtering
└── Detection Output
    ├── SecretType enum
    ├── Severity enum (CRITICAL, HIGH, MEDIUM, LOW)
    └── SecretDetection dataclass
```

### Future Enhancements

Planned for Phase 3 (v1.8.0):
- Integration with CI/CD pipelines (pre-commit hooks)
- Git history scanning
- Secret redaction/replacement utilities
- Real-time monitoring with alerting
- Integration with secret management systems (HashiCorp Vault, AWS Secrets Manager)

### References

- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [SECURE_MEMORY_ARCHITECTURE.md](../../../SECURE_MEMORY_ARCHITECTURE.md)
- [Enterprise Security Policy](../../../examples/claude_memory/enterprise-CLAUDE-secure.md)

### Support

For questions or issues:
- File an issue on GitHub
- Contact the Empathy Framework team
- See main documentation at `empathy_llm_toolkit/README.md`

---

**Author**: Empathy Framework Team
**Version**: 1.8.0-beta
**License**: Fair Source 0.9
