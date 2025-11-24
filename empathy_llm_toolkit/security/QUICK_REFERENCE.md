# Audit Logger Quick Reference

## Import

```python
from empathy_llm_toolkit.security import AuditLogger
```

## Initialize

```python
# Production
logger = AuditLogger(log_dir="/var/log/empathy")

# Development
logger = AuditLogger(log_dir="./logs", enable_console_logging=True)
```

## Log Events

### LLM Request
```python
logger.log_llm_request(
    user_id="user@company.com",
    empathy_level=3,
    provider="anthropic",
    model="claude-sonnet-4",
    memory_sources=["enterprise", "user", "project"],
    pii_count=0,
    secrets_count=0
)
```

### Pattern Storage
```python
logger.log_pattern_store(
    user_id="user@company.com",
    pattern_id="pattern_123",
    pattern_type="architecture",
    classification="INTERNAL",  # PUBLIC, INTERNAL, or SENSITIVE
    pii_scrubbed=2,
    retention_days=180
)
```

### Pattern Retrieval
```python
logger.log_pattern_retrieve(
    user_id="user@company.com",
    pattern_id="pattern_123",
    classification="INTERNAL",
    access_granted=True
)
```

### Security Violation
```python
logger.log_security_violation(
    user_id="user@company.com",
    violation_type="secrets_detected",
    severity="HIGH",  # LOW, MEDIUM, HIGH, or CRITICAL
    details={"secret_type": "api_key"},
    blocked=True
)
```

## Query Logs

### Basic Queries
```python
# By event type
events = logger.query(event_type="llm_request")

# By user
events = logger.query(user_id="user@company.com")

# By status
events = logger.query(status="failed")
```

### Date Range
```python
from datetime import datetime, timedelta

events = logger.query(
    start_date=datetime.utcnow() - timedelta(days=7),
    end_date=datetime.utcnow()
)
```

### Nested Filters
```python
# Patterns with >5 PII items scrubbed
events = logger.query(
    event_type="store_pattern",
    security__pii_scrubbed__gt=5
)

# Failed requests with secrets
events = logger.query(
    event_type="llm_request",
    status="failed",
    security__secrets_detected__gt=0
)
```

### Comparison Operators
- `__gt`: greater than
- `__gte`: greater than or equal
- `__lt`: less than
- `__lte`: less than or equal
- `__ne`: not equal

## Reports

### Violation Summary
```python
summary = logger.get_violation_summary(user_id="user@company.com")
print(f"Total: {summary['total_violations']}")
print(f"By type: {summary['by_type']}")
print(f"By severity: {summary['by_severity']}")
```

### Compliance Report
```python
report = logger.get_compliance_report(
    start_date=datetime.utcnow() - timedelta(days=30)
)

print(f"LLM requests: {report['llm_requests']['total']}")
print(f"Pattern storage: {report['pattern_storage']['total']}")
print(f"GDPR compliance: {report['compliance_metrics']['gdpr_compliant_rate']:.2%}")
print(f"HIPAA compliance: {report['compliance_metrics']['hipaa_compliant_rate']:.2%}")
```

## Log Format

Each line in `audit.jsonl`:
```json
{
  "event_id": "evt_abc123",
  "timestamp": "2025-11-24T19:03:08.114456Z",
  "version": "1.0",
  "event_type": "llm_request",
  "user_id": "user@company.com",
  "status": "success",
  "llm": { "provider": "anthropic", "model": "claude-sonnet-4", "empathy_level": 3 },
  "security": { "pii_detected": 0, "secrets_detected": 0 },
  "compliance": { "gdpr_compliant": true, "hipaa_compliant": true }
}
```

## Configuration Options

```python
AuditLogger(
    log_dir="/var/log/empathy",      # Log directory
    log_filename="audit.jsonl",       # Log file name
    max_file_size_mb=100,             # Max file size before rotation
    retention_days=365,               # Days to retain logs
    enable_rotation=True,             # Enable automatic rotation
    enable_console_logging=False      # Also log to console
)
```

## Common Patterns

### Integration with EmpathyLLM
```python
from empathy_llm_toolkit import EmpathyLLM

audit_logger = AuditLogger()
llm = EmpathyLLM(provider="anthropic")

async def interact_with_audit(user_id, user_input):
    response = await llm.interact(user_id, user_input, {})

    audit_logger.log_llm_request(
        user_id=user_id,
        empathy_level=response["empathy_level"],
        provider="anthropic",
        model="claude-sonnet-4",
        memory_sources=["enterprise", "user"],
        pii_count=0,
        secrets_count=0
    )

    return response
```

### Daily Compliance Check
```python
from datetime import datetime, timedelta

# Generate yesterday's report
report = logger.get_compliance_report(
    start_date=datetime.utcnow() - timedelta(days=1)
)

# Alert if compliance drops
if report['compliance_metrics']['gdpr_compliant_rate'] < 0.95:
    send_alert("GDPR compliance below 95%")
```

### Monitor Security Violations
```python
# Check recent violations
violations = logger.query(
    event_type="security_violation",
    start_date=datetime.utcnow() - timedelta(hours=24)
)

# Alert on critical violations
for v in violations:
    if v['violation']['severity'] == 'CRITICAL':
        send_alert(f"Critical violation: {v['violation']['type']}")
```

## Event Types Reference

| Event Type | Purpose | Key Fields |
|------------|---------|------------|
| `llm_request` | LLM API calls | provider, model, empathy_level, pii_detected, secrets_detected |
| `store_pattern` | Pattern storage | pattern_id, classification, pii_scrubbed, encrypted |
| `retrieve_pattern` | Pattern access | pattern_id, classification, access_granted |
| `security_violation` | Policy violations | violation_type, severity, blocked |

## Classification Levels

| Level | Use Case | Encryption | Retention |
|-------|----------|------------|-----------|
| `PUBLIC` | General patterns, shareable | No | 365 days |
| `INTERNAL` | Company confidential | Optional | 180 days |
| `SENSITIVE` | HIPAA/PCI-DSS data | Required | 90 days |

## Compliance Mapping

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| **SOC2** CC7.2 | System Monitoring | Comprehensive audit logging |
| **HIPAA** §164.312(b) | Audit Controls | Tamper-evident logs |
| **GDPR** Art. 30 | Records of Processing | Complete audit trail |

## Troubleshooting

### Logs not being created
```python
# Check directory permissions
import os
print(os.access("/var/log/empathy", os.W_OK))

# Use fallback directory
logger = AuditLogger(log_dir="./logs")
```

### Query not returning results
```python
# Check log file exists
print(logger.log_path.exists())

# Check query filters
events = logger.query(limit=10)  # Get first 10
print(f"Total events: {len(events)}")
```

### Performance issues
```python
# Use date ranges to limit scan
events = logger.query(
    start_date=datetime.utcnow() - timedelta(days=1),
    limit=1000
)

# Enable rotation to prevent large files
logger = AuditLogger(
    max_file_size_mb=50,  # Smaller files
    enable_rotation=True
)
```

## Testing

```bash
# Run tests
cd empathy_llm_toolkit/security
python3 -m pytest test_audit_logger.py -v

# Run example
python3 audit_logger_example.py

# View logs
cat logs/audit.jsonl | jq '.'
```

## Security Best Practices

1. **Never log actual PII or secrets** - only counts
2. **Use restrictive permissions** - 0700 for directory, 0600 for files
3. **Enable rotation** - prevent unlimited growth
4. **Monitor violations** - alert on CRITICAL severity
5. **Regular compliance reports** - daily or weekly
6. **Retain logs appropriately** - 365 days for compliance
7. **Back up logs** - store in secure, separate location

## Support

- **Documentation**: `README.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Architecture**: `../../SECURE_MEMORY_ARCHITECTURE.md`
- **Tests**: `test_audit_logger.py`
- **Example**: `audit_logger_example.py`

---

**Version**: 1.0.0
**License**: Fair Source 0.9
