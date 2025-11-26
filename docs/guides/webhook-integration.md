# Webhook Integration

Connect Empathy Framework to external services via webhooks for real-time notifications and automated workflows.

---

## Overview

**Webhooks** enable Empathy Framework to:

- 🔔 Send notifications to Slack, Teams, Discord
- 🐛 Create JIRA tickets for issues
- 📊 Log events to Datadog, Grafana
- 🔄 Trigger CI/CD pipelines
- ✉️ Send email alerts
- 🎯 Custom integrations with any HTTP endpoint

---

## Supported Integrations

| Service | Use Case | Events |
|---------|----------|--------|
| **Slack** | Team notifications | Predictions, alerts, summaries |
| **Microsoft Teams** | Enterprise comms | HIPAA alerts, compliance |
| **Discord** | Community updates | Feature releases, status |
| **JIRA** | Issue tracking | Bug detection, tasks |
| **GitHub** | Code management | PR comments, actions |
| **Datadog** | Monitoring | Performance, errors |
| **PagerDuty** | Incident management | Critical alerts |
| **Custom** | Any HTTP endpoint | All events |

---

## Quick Start

### Basic Webhook

```python
from empathy_os import EmpathyOS
from empathy_os.webhooks import WebhookConfig

# Configure webhook
webhook = WebhookConfig(
    url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    events=["prediction", "alert", "completion"],
    method="POST",
    headers={"Content-Type": "application/json"}
)

# Initialize with webhook
empathy = EmpathyOS(
    user_id="developer_123",
    target_level=4,
    webhooks=[webhook]
)

# Webhooks fire automatically on events
response = await empathy.interact(
    user_id="developer_123",
    user_input="Deploy the authentication service",
    context={"environment": "production"}
)

# If Level 4 prediction generated, webhook fires to Slack:
# "🔮 Prediction: Auth deployment may conflict with user-service v2.1"
```

---

## Slack Integration

### Setup

1. Create Slack App: https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook to workspace
4. Copy webhook URL

### Configuration

```python
from empathy_os.webhooks import SlackWebhook

slack = SlackWebhook(
    webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
    channel="#ai-alerts",
    username="Empathy Bot",
    icon_emoji=":robot_face:",
    events=["prediction", "alert", "error"]
)

empathy = EmpathyOS(
    user_id="team",
    webhooks=[slack]
)
```

### Message Formats

**Prediction Alert**:
```json
{
  "channel": "#ai-alerts",
  "username": "Empathy Bot",
  "icon_emoji": ":robot_face:",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🔮 Level 4 Prediction"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Prediction:* Auth deployment may conflict with user-service v2.1\n*Confidence:* 87%\n*Recommendation:* Deploy auth behind feature flag"
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "Detected by: developer_123 | Time: 2025-11-25 14:30"
        }
      ]
    }
  ]
}
```

---

## JIRA Integration

### Auto-Create Issues

```python
from empathy_os.webhooks import JiraWebhook

jira = JiraWebhook(
    url=os.getenv("JIRA_URL"),
    api_token=os.getenv("JIRA_API_TOKEN"),
    project="EMP",
    issue_type="Bug",
    events=["bug_detected", "security_vulnerability"]
)

empathy = EmpathyOS(
    user_id="code_reviewer",
    webhooks=[jira]
)

# When bug detected, JIRA ticket created automatically
bug_report = await empathy.interact(
    user_id="developer_123",
    user_input="Review auth.py for bugs",
    context={"file": "auth.py"}
)

# If bugs found, creates JIRA ticket:
# Title: "[AI Detected] SQL injection in auth.py:45"
# Description: Details of vulnerability + fix suggestion
# Priority: High
# Assignee: file owner
```

### JIRA Ticket Format

```json
{
  "fields": {
    "project": {"key": "EMP"},
    "summary": "[AI Detected] SQL injection in auth.py:45",
    "description": {
      "type": "doc",
      "content": [
        {
          "type": "paragraph",
          "content": [
            {"type": "text", "text": "Empathy Framework detected a potential SQL injection vulnerability:\n\n"},
            {"type": "text", "text": "File: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "auth.py:45\n"},
            {"type": "text", "text": "Issue: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "User input concatenated directly into SQL query\n\n"},
            {"type": "text", "text": "Recommended Fix:\n", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "Use parameterized queries: cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"}
          ]
        }
      ]
    },
    "issuetype": {"name": "Bug"},
    "priority": {"name": "High"},
    "labels": ["ai-detected", "security", "sql-injection"]
  }
}
```

---

## Datadog Integration

### Metrics & Events

```python
from empathy_os.webhooks import DatadogWebhook

datadog = DatadogWebhook(
    api_key=os.getenv("DATADOG_API_KEY"),
    app_key=os.getenv("DATADOG_APP_KEY"),
    events=["performance_issue", "prediction", "error"]
)

empathy = EmpathyOS(
    user_id="performance_agent",
    webhooks=[datadog]
)

# Performance issues sent to Datadog
performance = await empathy.interact(
    user_id="developer_123",
    user_input="Analyze API performance",
    context={"endpoint": "/api/users"}
)

# Creates Datadog event:
# Title: "Performance: /api/users response time degraded"
# Metrics: avg_response_time, p95_response_time, error_rate
# Tags: service:api, endpoint:/api/users, severity:warning
```

### Custom Metrics

```python
# Send custom metrics to Datadog
datadog.send_metric(
    metric="empathy.prediction.confidence",
    value=0.87,
    tags=["user:developer_123", "level:4"]
)

datadog.send_metric(
    metric="empathy.interactions.duration_ms",
    value=1234,
    tags=["user:developer_123"]
)
```

---

## GitHub Integration

### PR Comments

```python
from empathy_os.webhooks import GitHubWebhook

github = GitHubWebhook(
    token=os.getenv("GITHUB_TOKEN"),
    repository="Smart-AI-Memory/empathy-framework",
    events=["code_review_complete"]
)

empathy = EmpathyOS(
    user_id="code_reviewer",
    webhooks=[github]
)

# Review PR and post comment
review = await empathy.interact(
    user_id="developer_123",
    user_input="Review PR #123",
    context={"pr": 123}
)

# Posts GitHub comment:
"""
## 🤖 AI Code Review

### ✅ Looks Good
- Clean code structure
- Comprehensive test coverage

### ⚠️ Suggestions
1. **Line 45**: Consider using context manager for file handling
2. **Line 78**: N+1 query detected, use select_related()

### 🔒 Security
- No security issues detected

Confidence: 92%
"""
```

---

## Custom Webhooks

### Define Custom Endpoint

```python
from empathy_os.webhooks import CustomWebhook

custom = CustomWebhook(
    url="https://your-service.com/webhooks/empathy",
    method="POST",
    headers={
        "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
        "Content-Type": "application/json"
    },
    events=["*"],  # All events
    retry_policy={
        "max_retries": 3,
        "backoff_multiplier": 2,
        "timeout_seconds": 30
    }
)

empathy = EmpathyOS(
    user_id="custom_integration",
    webhooks=[custom]
)
```

### Webhook Payload

```json
{
  "event_type": "prediction",
  "event_id": "evt_abc123",
  "timestamp": "2025-11-25T14:30:00Z",
  "user_id": "developer_123",
  "empathy_level": 4,
  "data": {
    "prediction": "Auth deployment may conflict with user-service v2.1",
    "confidence": 0.87,
    "recommendation": "Deploy auth behind feature flag",
    "context": {
      "service": "authentication",
      "environment": "production"
    }
  },
  "metadata": {
    "framework_version": "1.8.0",
    "model": "claude-sonnet-4.5"
  }
}
```

---

## Event Types

| Event | Trigger | Use Case |
|-------|---------|----------|
| `prediction` | Level 4 prediction generated | Slack alerts |
| `alert` | Warning/error detected | PagerDuty |
| `bug_detected` | Code issue found | JIRA ticket |
| `security_vulnerability` | Security issue | Security team alert |
| `performance_issue` | Slow code detected | Datadog metric |
| `code_review_complete` | Review finished | GitHub comment |
| `test_failure` | Test failed | Slack notification |
| `deployment_risk` | Risky deployment | Approval workflow |
| `compliance_violation` | HIPAA/GDPR issue | Legal team alert |
| `pattern_discovered` | New pattern learned | Team knowledge base |

---

## Filtering & Routing

### Event Filters

```python
# Only send high-severity events to PagerDuty
pagerduty = PagerDutyWebhook(
    api_key=os.getenv("PAGERDUTY_API_KEY"),
    events=["alert"],
    filter=lambda event: event.severity == "high"
)

# Send all events to Datadog for logging
datadog = DatadogWebhook(
    api_key=os.getenv("DATADOG_API_KEY"),
    events=["*"]  # All events
)

# Healthcare-specific alerts to compliance team
compliance = CustomWebhook(
    url="https://compliance.hospital.com/webhook",
    events=["compliance_violation", "phi_access"],
    filter=lambda event: event.classification == "SENSITIVE"
)

empathy = EmpathyOS(
    user_id="multi_webhook",
    webhooks=[pagerduty, datadog, compliance]
)
```

---

## Error Handling

### Retry Logic

```python
webhook = CustomWebhook(
    url="https://unreliable-service.com/webhook",
    retry_policy={
        "max_retries": 5,
        "backoff_multiplier": 2,  # 1s, 2s, 4s, 8s, 16s
        "timeout_seconds": 30,
        "retry_on_status": [500, 502, 503, 504]
    }
)
```

### Failure Callbacks

```python
def on_webhook_failure(webhook, event, error):
    logger.error(f"Webhook failed: {webhook.url}")
    logger.error(f"Event: {event.event_type}")
    logger.error(f"Error: {error}")

    # Fallback: Store event for manual retry
    database.store_failed_webhook(webhook, event)

webhook = CustomWebhook(
    url="https://service.com/webhook",
    on_failure=on_webhook_failure
)
```

---

## Security

### Authentication

```python
# Bearer token
webhook = CustomWebhook(
    url="https://service.com/webhook",
    headers={"Authorization": f"Bearer {os.getenv('WEBHOOK_TOKEN')}"}
)

# API key
webhook = CustomWebhook(
    url="https://service.com/webhook",
    headers={"X-API-Key": os.getenv('API_KEY')}
)

# HMAC signature (webhook validation)
webhook = CustomWebhook(
    url="https://service.com/webhook",
    signing_secret=os.getenv('WEBHOOK_SECRET'),
    sign_payload=True  # Adds X-Signature header
)
```

### Verify Signatures (Receiving Webhooks)

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

# In your webhook handler
@app.post("/webhooks/empathy")
async def handle_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Signature")

    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process webhook
    event = json.loads(payload)
    process_event(event)

    return {"status": "ok"}
```

---

## Rate Limiting

### Webhook Throttling

```python
webhook = CustomWebhook(
    url="https://service.com/webhook",
    rate_limit={
        "max_requests_per_minute": 60,
        "max_requests_per_hour": 1000,
        "strategy": "sliding_window"
    }
)

# If rate limit exceeded, events queued and sent later
```

---

## Monitoring

### Webhook Performance

```python
from empathy_os.webhooks import WebhookMonitor

monitor = WebhookMonitor()

stats = monitor.get_webhook_stats("slack_webhook")

print(f"Total sent: {stats['total_sent']}")
print(f"Success rate: {stats['success_rate']:.0%}")
print(f"Avg response time: {stats['avg_response_time_ms']}ms")
print(f"Failed deliveries: {stats['failed_count']}")
```

---

## Best Practices

### ✅ Do

1. **Use environment variables** for secrets/tokens
2. **Implement retry logic** for reliability
3. **Validate webhook signatures** for security
4. **Filter events** to reduce noise
5. **Monitor webhook performance**
6. **Set appropriate timeouts** (30s max)

### ❌ Don't

1. **Don't hardcode secrets** in code
2. **Don't send sensitive data** without encryption
3. **Don't ignore rate limits**
4. **Don't skip error handling**
5. **Don't send all events** to all webhooks

---

## Examples

See the complete [Webhook Event Integration Example](../examples/webhook-event-integration.md) for implementations with:

- Slack notifications
- JIRA ticket creation
- Datadog metrics
- GitHub PR comments
- Custom webhooks

---

## See Also

- [Webhook Example](../examples/webhook-event-integration.md) - Full implementation
- [Security Architecture](security-architecture.md) - Webhook security
- [EmpathyOS API](../api-reference/empathy-os.md) - Webhook configuration
