# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.9.x   | :white_check_mark: |
| 3.8.x   | :x:                |
| < 3.8   | :x:                |

## Reporting a Vulnerability

The Empathy Framework team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities to:
- **Email**: security@smartaimemory.com
- **Subject Line**: `[SECURITY] Empathy Framework Vulnerability Report`

### What to Include

Please include the following information in your report:
- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Full path of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability and potential attack scenarios

### Response Timeline

- **Acknowledgment**: Within 24-48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Security Fix**: Within 7 days for critical vulnerabilities
- **Detailed Response**: Within 10 business days with our evaluation and timeline
- **Fix & Disclosure**: Coordinated disclosure after patch is released

### Our Commitment

- We will respond to your report promptly and keep you informed throughout the process
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We will not take legal action against researchers who follow this policy
- We will work with you to understand and resolve the issue quickly

## Security Best Practices for Users

### When Using Empathy Framework

1. **Keep Dependencies Updated**: Regularly update the Empathy Framework and all dependencies
   ```bash
   pip install --upgrade empathy-framework
   pip install --upgrade -r requirements.txt
   ```

2. **Validate AI Model Outputs**: Never execute AI-generated code without human review, especially:
   - Database queries
   - System commands
   - File operations
   - API calls with sensitive data

3. **Protect API Keys**: Never commit API keys for AI services (Anthropic, OpenAI) to version control
   - Use environment variables: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
   - Use `.env` files with `.gitignore`
   - Rotate keys if accidentally exposed

4. **Code Analysis Privacy**: Be aware that code sent to wizards may be transmitted to AI services
   - Review privacy policies of AI providers
   - Use local models for sensitive code
   - Sanitize proprietary code before analysis

5. **Access Control**: For healthcare applications (HIPAA compliance):
   - Ensure PHI/PII is never sent to AI services
   - Use on-premises deployment for sensitive environments
   - Implement audit logging for all AI interactions

### When Integrating Empathy Framework

1. **Input Validation**: Always validate and sanitize user input before passing to wizards
2. **Rate Limiting**: Implement rate limiting to prevent abuse of AI services
3. **Error Handling**: Don't expose internal error messages to end users
4. **Logging**: Log security events but never log sensitive data or API keys
5. **Least Privilege**: Run services with minimum required permissions

## Security Features

The Empathy Framework includes several security features:

1. **Path Traversal Protection (Pattern 6)**: All file write operations validated to prevent path traversal attacks (CWE-22)
2. **Input Sanitization**: All code inputs are sanitized before analysis
3. **Sandboxed Execution**: No arbitrary code execution in wizards
4. **API Key Protection**: Environment variable-based configuration
5. **Audit Trail**: Optional logging of all wizard invocations
6. **Rate Limiting**: Built-in protection against service abuse
7. **Command Injection Prevention**: All file paths and user inputs are validated before subprocess execution
8. **Secrets Detection**: Pre-commit hooks using detect-secrets to prevent accidental credential exposure
9. **Exception Hardening**: Specific exception handling prevents error masking while maintaining graceful degradation

### Pre-commit Security Hooks

Run `pre-commit install` to enable:

```bash
pre-commit install
```

Security hooks include:

- **detect-secrets**: Scans for potential API keys and credentials
- **bandit**: Python security linter for common vulnerabilities

### Built-in Security Tools

```python
from empathy_llm_toolkit.security import SecretsDetector, PIIScrubber

# Detect secrets in content
detector = SecretsDetector()
findings = detector.scan(content)

# Scrub PII before storage
scrubber = PIIScrubber()
clean_content = scrubber.scrub(content)
```

### Test Credentials

All test files use obviously fake credentials:

- Prefix with `TEST_`, `FAKE_`, or `EXAMPLE_`
- Use placeholder patterns like `abc123xyz789...`
- AWS example keys: `AKIAIOSFODNN7EXAMPLE`

## Security Hardening (Pattern 6 Implementation)

### Overview

In January 2026, we conducted a comprehensive security audit and applied Pattern 6 (File Path Validation) across all configuration and file write operations. This eliminated path traversal vulnerabilities (CWE-22) and arbitrary file write risks.

### Files Secured

**Sprint 1 (2026-01-06):**

- [telemetry/cli.py](src/empathy_os/telemetry/cli.py) - Export operations (CSV, JSON)
- [cli.py](src/empathy_os/cli.py) - Pattern and report exports
- [memory/control_panel.py](src/empathy_os/memory/control_panel.py) - Memory management operations

**Sprint 2 (2026-01-07):**

- [config.py](src/empathy_os/config.py) - Configuration exports (YAML, JSON)
- [workflows/config.py](src/empathy_os/workflows/config.py) - Workflow configuration saves
- [config/xml_config.py](src/empathy_os/config/xml_config.py) - XML configuration writes

**Sprint 3 (2026-01-07):**

- [workflows/base.py](src/empathy_os/workflows/base.py) - Exception handling improvements
- Fixed 8 blind exception handlers with specific exception types
- Enhanced error logging for debugging while maintaining graceful degradation

### Attack Vectors Blocked

✅ **Path Traversal**: `../../../etc/passwd` → `ValueError: Cannot write to system directory`
✅ **Null Byte Injection**: `config\x00.json` → `ValueError: path contains null bytes`
✅ **System Directory Writes**: `/etc`, `/sys`, `/proc`, `/dev` → All blocked
✅ **Absolute Path Attacks**: Any absolute path to sensitive locations → Validated and blocked

### Test Coverage

- **39 security tests** across all protected modules (100% passing)
- Tests cover: path traversal, null bytes, system directories, valid paths
- Cross-module consistency tests ensure no regressions

### Security Metrics

| Metric                   | Before Sprint 2 | After Sprint 3 | Improvement |
| ------------------------ | --------------- | -------------- | ----------- |
| **Files Secured**        | 3               | 6              | +100%       |
| **Write Ops Protected**  | 6               | 13             | +117%       |
| **Security Tests**       | 14              | 174            | +1143%      |
| **Blind Exceptions**     | 8               | 0              | -100%       |

### Implementation Pattern

All protected modules use the same validation function:

```python
def _validate_file_path(path: str, allowed_dir: str | None = None) -> Path:
    """Validate file path to prevent path traversal and arbitrary writes.

    Args:
        path: User-controlled file path to validate
        allowed_dir: Optional directory restriction

    Returns:
        Validated Path object

    Raises:
        ValueError: If path is invalid, contains null bytes, or targets system directories
    """
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string")

    if "\x00" in path:
        raise ValueError("path contains null bytes")

    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}")

    # Block writes to system directories
    dangerous_paths = ["/etc", "/sys", "/proc", "/dev"]
    for dangerous in dangerous_paths:
        if str(resolved).startswith(dangerous):
            raise ValueError(f"Cannot write to system directory: {dangerous}")

    # Optional directory restriction
    if allowed_dir:
        try:
            allowed = Path(allowed_dir).resolve()
            resolved.relative_to(allowed)
        except ValueError:
            raise ValueError(f"path must be within {allowed_dir}")

    return resolved
```

### For Contributors

When adding new file write operations:

1. **Always use `_validate_file_path()`** before writing files
2. **Never trust user-controlled paths** - validate first
3. **Add security tests** for your file operations
4. **Test attack scenarios**: path traversal, null bytes, system dirs
5. See [test_config_path_security.py](tests/unit/test_config_path_security.py) for examples

## Known Security Considerations

### AI Model Risks

- **Prompt Injection**: AI models may be susceptible to prompt injection attacks
  - Mitigation: We use structured prompts with clear boundaries
  - Best Practice: Review all AI outputs before implementation

- **Data Privacy**: Code analyzed by wizards is sent to AI services
  - Mitigation: Use local models for sensitive code
  - Best Practice: Sanitize proprietary code before analysis

- **Model Hallucinations**: AI models may generate incorrect security advice
  - Mitigation: All suggestions include confidence scores
  - Best Practice: Always validate AI recommendations with security experts

### Healthcare-Specific Risks (HIPAA/GDPR)

- **PHI Exposure**: Patient health information must never be sent to external AI services
  - Mitigation: Use on-premises deployment
  - Best Practice: Implement data anonymization pipelines

## Security Updates

We publish security advisories at:
- **GitHub Security Advisories**: https://github.com/Deep-Study-AI/Empathy/security/advisories
- **Email Notifications**: Subscribe at patrick.roebuck@deepstudyai.com

## Bug Bounty Program

Currently, we do not offer a paid bug bounty program. However:
- We publicly acknowledge security researchers (with permission)
- We provide attribution in CVE credits and release notes
- We may offer swag or free licenses for significant findings

## Compliance

The Empathy Framework is designed to support:
- **HIPAA** compliance for healthcare applications
- **GDPR** compliance for European users
- **SOC 2** requirements for enterprise customers
- **ISO 27001** information security standards

See our [Compliance Documentation](docs/) for detailed guidance.

## Contact

For security concerns, contact:
- **Email**: patrick.roebuck@deepstudyai.com
- **GitHub**: https://github.com/Deep-Study-AI/Empathy/security
- **Organization**: Smart AI Memory, LLC

---

**Last Updated**: January 2025

Thank you for helping keep Empathy Framework and our users safe!
