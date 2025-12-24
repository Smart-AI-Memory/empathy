# Example: Webhook & Event Integration

**Difficulty**: Intermediate
**Time**: 25 minutes
**Features**: Event bus, webhooks, external integrations
**Integrations**: Slack, GitHub, JIRA, custom webhooks

---

## Overview

This example shows how to integrate the Empathy Framework with external systems using:
- **Event bus**: Internal pub/sub system for framework events
- **Webhooks**: HTTP callbacks to external services
- **Bidirectional integration**: Trigger empathy from external events (GitHub PRs, Slack messages)
- **Real-time notifications**: Alert teams instantly about Level 4 predictions

**Use Cases**:
- Notify Slack when high-confidence predictions occur
- Create GitHub issues from anticipatory warnings
- Trigger JIRA tickets for predicted problems
- Send metrics to Datadog/NewRelic
- Custom integrations with your tools

---

## Installation

```bash
pip install empathy-framework[webhooks]
```

---

## Part 1: Event Bus Basics

### Subscribe to Framework Events

```python
from empathy_os import EmpathyOS
from empathy_os.events import EventBus, Event

# Create event bus
bus = EventBus()

# Subscribe to events
@bus.on("pattern_learned")
def handle_pattern_learned(event: Event):
    print(f"📚 New pattern learned: {event.data['pattern_name']}")
    print(f"   Confidence: {event.data['confidence']:.0%}")
    print(f"   User: {event.data['user_id']}")

@bus.on("level_4_prediction")
def handle_prediction(event: Event):
    print(f"🔮 Level 4 Prediction!")
    print(f"   {event.data['prediction']}")
    print(f"   Confidence: {event.data['confidence']:.0%}")

@bus.on("trust_milestone")
def handle_trust_milestone(event: Event):
    print(f"🎉 Trust milestone reached!")
    print(f"   User: {event.data['user_id']}")
    print(f"   Trust level: {event.data['trust_level']:.0%}")
    print(f"   Milestone: {event.data['milestone']}")

# Create empathy with event bus
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    event_bus=bus  # Connect to event bus
)

# Interact (events will fire automatically)
response = empathy.interact(
    user_id="user_123",
    user_input="Analyze this code for security issues",
    context={"code": "SELECT * FROM users WHERE id = " + user_id}
)

# Events emitted:
# 🔮 Level 4 Prediction!
#    SQL injection vulnerability detected
#    Confidence: 95%
#
# 📚 New pattern learned: sql_injection_detection
#    Confidence: 95%
#    User: user_123
```

---

## Part 2: Webhook Notifications

### Send Events to External Services

```python
from empathy_os.webhooks import WebhookManager
from empathy_os.events import EventBus

bus = EventBus()
webhooks = WebhookManager(bus)

# Register Slack webhook
webhooks.register(
    event_type="level_4_prediction",
    url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    headers={"Content-Type": "application/json"},
    payload_template={
        "text": "🔮 *Level 4 Prediction*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Prediction:* {prediction}\n*Confidence:* {confidence:.0%}\n*User:* {user_id}"
                }
            }
        ]
    }
)

# When Level 4 prediction occurs, Slack gets notified automatically
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    event_bus=bus
)

response = empathy.interact(
    user_id="user_123",
    user_input="About to deploy API changes to production",
    context={
        "deployment": "production",
        "service": "user-api",
        "changes": ["schema_modification", "new_endpoints"]
    }
)

# If Level 4 prediction is made, Slack receives:
# 🔮 **Level 4 Prediction**
# Prediction: Schema modification may break mobile app (uses old API contract)
# Confidence: 87%
# User: user_123
```

---

## Part 3: Multiple Webhook Integrations

### Notify Multiple Services

```python
from empathy_os.webhooks import WebhookManager
from empathy_os.events import EventBus
import os

bus = EventBus()
webhooks = WebhookManager(bus)

# 1. Slack notification
webhooks.register(
    event_type="level_4_prediction",
    url=os.getenv("SLACK_WEBHOOK_URL"),
    payload_template={
        "text": "🔮 Prediction: {prediction}",
        "username": "Empathy Bot",
        "icon_emoji": ":crystal_ball:"
    }
)

# 2. Datadog metrics
webhooks.register(
    event_type="level_4_prediction",
    url="https://api.datadoghq.com/api/v1/events",
    headers={
        "Content-Type": "application/json",
        "DD-API-KEY": os.getenv("DATADOG_API_KEY")
    },
    payload_template={
        "title": "Empathy Level 4 Prediction",
        "text": "{prediction}",
        "priority": "normal",
        "tags": ["empathy:level4", "confidence:{confidence}", "user:{user_id}"],
        "alert_type": "info"
    }
)

# 3. Custom internal webhook
webhooks.register(
    event_type="level_4_prediction",
    url="https://internal-api.company.com/webhooks/empathy",
    headers={
        "Authorization": f"Bearer {os.getenv('INTERNAL_API_TOKEN')}",
        "Content-Type": "application/json"
    },
    payload_template={
        "event_type": "prediction",
        "data": {
            "prediction": "{prediction}",
            "confidence": "{confidence}",
            "user_id": "{user_id}",
            "timestamp": "{timestamp}"
        }
    }
)

# Single event triggers all 3 webhooks
empathy = EmpathyOS(user_id="user_123", target_level=4, event_bus=bus)

response = empathy.interact(
    user_id="user_123",
    user_input="Merge this PR",
    context={"pr_number": 456, "changes": ["auth_module"]}
)

# All 3 services notified simultaneously:
# ✅ Slack: Team alerted
# ✅ Datadog: Metric recorded
# ✅ Internal API: Custom processing triggered
```

---

## Part 4: Conditional Webhooks

### Fire Webhooks Based on Conditions

```python
from empathy_os.webhooks import ConditionalWebhook

# Only notify for HIGH confidence predictions (>85%)
webhooks.register_conditional(
    event_type="level_4_prediction",
    condition=lambda event: event.data['confidence'] > 0.85,
    url=os.getenv("SLACK_HIGH_CONFIDENCE_WEBHOOK"),
    payload_template={
        "text": "⚠️ *HIGH CONFIDENCE PREDICTION* ({confidence:.0%})",
        "attachments": [{
            "color": "warning",
            "text": "{prediction}"
        }]
    }
)

# Only notify for security-related predictions
webhooks.register_conditional(
    event_type="level_4_prediction",
    condition=lambda event: "security" in event.data.get('tags', []),
    url=os.getenv("SECURITY_TEAM_WEBHOOK"),
    payload_template={
        "text": "🔒 Security prediction: {prediction}",
        "channel": "#security-alerts"
    }
)

# Only notify during business hours (9am-5pm)
import datetime

webhooks.register_conditional(
    event_type="level_4_prediction",
    condition=lambda event: 9 <= datetime.datetime.now().hour < 17,
    url=os.getenv("SLACK_BUSINESS_HOURS_WEBHOOK"),
    payload_template={"text": "Prediction (business hours): {prediction}"}
)
```

---

## Part 5: GitHub Integration

### Create Issues from Predictions

```python
from empathy_os.integrations import GitHubIntegration
from empathy_os.events import EventBus

# Setup GitHub integration
github = GitHubIntegration(
    token=os.getenv("GITHUB_TOKEN"),
    repo="username/repo"
)

bus = EventBus()

# Auto-create GitHub issue for high-severity predictions
@bus.on("level_4_prediction")
async def create_github_issue(event: Event):
    if event.data['confidence'] > 0.85:
        issue = await github.create_issue(
            title=f"🔮 Prediction: {event.data['prediction'][:50]}...",
            body=f"""
## Empathy Level 4 Prediction

**Prediction:** {event.data['prediction']}

**Confidence:** {event.data['confidence']:.0%}

**Context:**
- User: {event.data['user_id']}
- Timestamp: {event.data['timestamp']}

**Recommended Action:**
{event.data.get('recommendation', 'Review and address this prediction')}

---
*This issue was automatically created by Empathy Framework*
            """,
            labels=["empathy-prediction", "needs-review"],
            assignees=["tech-lead"]
        )

        print(f"✅ Created GitHub issue #{issue.number}")

# Connect empathy to GitHub
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    event_bus=bus,
    integrations=[github]
)

# Prediction triggers GitHub issue creation
response = empathy.interact(
    user_id="user_123",
    user_input="Deploying authentication refactor",
    context={"deployment": "production"}
)

# If prediction made:
# ✅ Created GitHub issue #789
```

---

## Part 6: Bidirectional Integration

### Trigger Empathy from External Events

```python
from empathy_os import EmpathyOS
from empathy_os.integrations import GitHubIntegration

github = GitHubIntegration(
    token=os.getenv("GITHUB_TOKEN"),
    repo="username/repo"
)

empathy = EmpathyOS(
    user_id="ci_agent",
    target_level=4,
    integrations=[github]
)

# Listen for GitHub webhook events
@github.on("pull_request.opened")
async def analyze_pr(pr_data):
    """
    When PR is opened, analyze it with Empathy
    """

    # Get PR details
    pr_number = pr_data['number']
    pr_author = pr_data['user']['login']
    pr_title = pr_data['title']
    files_changed = await github.get_pr_files(pr_number)

    # Analyze with Empathy
    response = empathy.interact(
        user_id=f"github_user_{pr_author}",
        user_input=f"Review PR #{pr_number}: {pr_title}",
        context={
            "pr_number": pr_number,
            "files_changed": files_changed,
            "diff": await github.get_pr_diff(pr_number)
        }
    )

    # Post analysis as PR comment
    await github.comment_on_pr(
        pr_number=pr_number,
        comment=f"""
## 🤖 Empathy Code Review

{response.response}

---

**Empathy Level:** {response.level}
**Confidence:** {response.confidence:.0%}

"""
    )

    # If Level 4 prediction, add labels
    if response.level == 4 and response.predictions:
        await github.add_labels(
            pr_number=pr_number,
            labels=["⚠️ empathy-prediction", "needs-review"]
        )

    print(f"✅ Analyzed PR #{pr_number}")

# GitHub sends webhook → Empathy analyzes → Posts comment
# Fully automated code review with Level 4 anticipatory intelligence!
```

---

## Part 7: Slack Integration

### Slash Commands

```python
from empathy_os import EmpathyOS
from empathy_os.integrations import SlackIntegration
from flask import Flask, request

app = Flask(__name__)

slack = SlackIntegration(
    bot_token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

empathy = EmpathyOS(
    user_id="slack_bot",
    target_level=4,
    integrations=[slack]
)

@app.route("/slack/commands/empathy", methods=["POST"])
def handle_slack_command():
    """
    Handle /empathy slash command in Slack
    """

    # Verify Slack signature
    if not slack.verify_request(request):
        return "Invalid request", 403

    # Parse command
    data = request.form
    user_id = data['user_id']
    channel_id = data['channel_id']
    text = data['text']  # User's query after /empathy

    # Query Empathy
    response = empathy.interact(
        user_id=f"slack_user_{user_id}",
        user_input=text,
        context={
            "channel_id": channel_id,
            "platform": "slack"
        }
    )

    # Send response to Slack
    slack.send_message(
        channel=channel_id,
        text=response.response,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response.response}
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Empathy Level {response.level} | Confidence: {response.confidence:.0%}"
                    }
                ]
            }
        ]
    )

    return "", 200

# Usage in Slack:
# /empathy How do I fix this SQL injection?
# → Bot responds with Level 4 anticipatory analysis
```

### Proactive Slack Notifications

```python
from empathy_os.integrations import SlackIntegration
import asyncio

slack = SlackIntegration(bot_token=os.getenv("SLACK_BOT_TOKEN"))

# Monitor for patterns and notify team
@empathy.on("pattern_learned")
async def notify_team_of_new_pattern(event: Event):
    """
    When AI learns a new pattern, share it with the team
    """

    await slack.send_message(
        channel="#engineering",
        text=f"📚 *New Pattern Learned*",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""
*Pattern:* {event.data['pattern_name']}
*Confidence:* {event.data['confidence']:.0%}
*Learn
ed from:* <@{event.data['user_id']}>

This pattern is now available for the whole team! 🎉
                    """
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Pattern"},
                        "url": f"https://empathy-dashboard.company.com/patterns/{event.data['pattern_id']}"
                    }
                ]
            }
        ]
    )
```

---

## Part 8: JIRA Integration

### Auto-Create Tickets from Predictions

```python
from empathy_os.integrations import JIRAIntegration

jira = JIRAIntegration(
    url="https://company.atlassian.net",
    username=os.getenv("JIRA_USERNAME"),
    api_token=os.getenv("JIRA_API_TOKEN"),
    project_key="ENG"
)

@bus.on("level_4_prediction")
async def create_jira_ticket(event: Event):
    """
    Create JIRA ticket for high-confidence predictions
    """

    if event.data['confidence'] > 0.85 and event.data.get('severity') == 'high':
        ticket = await jira.create_issue(
            project="ENG",
            issue_type="Bug" if "bug" in event.data.get('tags', []) else "Task",
            summary=f"🔮 Predicted Issue: {event.data['prediction'][:100]}",
            description=f"""
h2. Empathy Level 4 Prediction

*Prediction:*
{event.data['prediction']}

*Confidence:* {event.data['confidence']:.0%}

*Context:*
* User: {event.data['user_id']}
* Timestamp: {event.data['timestamp']}
* Tags: {', '.join(event.data.get('tags', []))}

*Recommended Action:*
{event.data.get('recommendation', 'Review and address this prediction')}

---
_This ticket was automatically created by Empathy Framework_
            """,
            priority="High" if event.data['confidence'] > 0.90 else "Medium",
            labels=["empathy-prediction", "ai-generated"],
            assignee="tech-lead"
        )

        print(f"✅ Created JIRA ticket {ticket.key}")

# Prediction → JIRA ticket created automatically
```

---

## Part 9: Custom Webhook Server

### Receive Webhooks from Empathy

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/webhooks/empathy", methods=["POST"])
def handle_empathy_webhook():
    """
    Receive webhooks from Empathy Framework
    """

    # Parse webhook payload
    data = request.json

    event_type = data.get('event_type')
    timestamp = data.get('timestamp')
    payload = data.get('data', {})

    # Handle different event types
    if event_type == "level_4_prediction":
        handle_prediction(payload)

    elif event_type == "pattern_learned":
        handle_pattern_learned(payload)

    elif event_type == "trust_milestone":
        handle_trust_milestone(payload)

    elif event_type == "coordination_request":
        handle_coordination_request(payload)

    return {"status": "received"}, 200

def handle_prediction(payload):
    """Custom business logic for predictions"""

    prediction = payload['prediction']
    confidence = payload['confidence']
    user_id = payload['user_id']

    # Store in database
    db.predictions.insert({
        "prediction": prediction,
        "confidence": confidence,
        "user_id": user_id,
        "timestamp": datetime.utcnow()
    })

    # Alert ops team if critical
    if confidence > 0.90:
        ops_alert_system.send(
            severity="high",
            message=f"Critical prediction: {prediction}"
        )

    # Update analytics dashboard
    analytics.track_event("empathy_prediction", {
        "confidence": confidence,
        "user_id": user_id
    })

# Start webhook server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

---

## Part 10: Event Types Reference

### All Available Events

```python
# Complete list of Empathy Framework events

EVENT_TYPES = {
    # Core interaction events
    "interaction_started": {
        "data": ["user_id", "user_input", "timestamp"],
        "description": "User started interaction"
    },

    "interaction_completed": {
        "data": ["user_id", "response", "level", "confidence", "duration_ms"],
        "description": "Interaction completed"
    },

    # Level transition events
    "level_transition": {
        "data": ["user_id", "from_level", "to_level", "reason"],
        "description": "Empathy level changed"
    },

    # Level-specific events
    "level_1_response": {"description": "Reactive response (Level 1)"},
    "level_2_clarification": {"description": "Guided clarification (Level 2)"},
    "level_3_proactive_suggestion": {"description": "Proactive suggestion (Level 3)"},
    "level_4_prediction": {"description": "Anticipatory prediction (Level 4)"},
    "level_5_transformation": {"description": "Transformative framework (Level 5)"},

    # Pattern events
    "pattern_learned": {
        "data": ["pattern_id", "pattern_name", "confidence", "user_id"],
        "description": "New pattern learned"
    },

    "pattern_applied": {
        "data": ["pattern_id", "pattern_name", "confidence", "success"],
        "description": "Pattern applied to interaction"
    },

    "pattern_updated": {
        "data": ["pattern_id", "old_confidence", "new_confidence"],
        "description": "Pattern confidence updated"
    },

    # Trust events
    "trust_increased": {
        "data": ["user_id", "old_trust", "new_trust", "delta"],
        "description": "Trust level increased"
    },

    "trust_decreased": {
        "data": ["user_id", "old_trust", "new_trust", "delta"],
        "description": "Trust level decreased"
    },

    "trust_milestone": {
        "data": ["user_id", "trust_level", "milestone"],
        "description": "Trust milestone reached (e.g., 0.5, 0.75, 0.9)"
    },

    # Coordination events (multi-agent)
    "coordination_request": {
        "data": ["requesting_agent", "target_agents", "topic", "priority"],
        "description": "Agent requested coordination"
    },

    "conflict_detected": {
        "data": ["agent1", "agent2", "resource", "severity"],
        "description": "Conflict detected between agents"
    },

    "handoff_initiated": {
        "data": ["from_agent", "to_agent", "task", "context"],
        "description": "Task handoff between agents"
    },

    # Failure/error events
    "prediction_failure": {
        "data": ["prediction_id", "reason", "confidence"],
        "description": "Prediction was incorrect or rejected"
    },

    "error": {
        "data": ["error_type", "error_message", "context"],
        "description": "Error occurred during interaction"
    }
}
```

---

## Performance & Best Practices

**Webhook Performance**:
- Average latency: ~50-100ms (HTTP POST)
- Retry logic: 3 attempts with exponential backoff
- Timeout: 5 seconds default
- Async delivery: Webhooks don't block interactions

**Best Practices**:
1. **Use conditional webhooks**: Don't spam low-value events
2. **Batch when possible**: Group multiple events into single webhook
3. **Monitor failures**: Set up alerts for webhook delivery failures
4. **Secure endpoints**: Use HTTPS + API tokens
5. **Idempotency**: Make webhook handlers idempotent (handle duplicates)

---

## Security Considerations

**Webhook Security**:
```python
from empathy_os.webhooks import SecureWebhook

# Add HMAC signature verification
webhooks.register(
    event_type="level_4_prediction",
    url="https://external-service.com/webhook",
    secret=os.getenv("WEBHOOK_SECRET"),  # HMAC signing key
    verify_ssl=True,  # Verify SSL certificates
    timeout=10,  # Request timeout (seconds)
    retry_count=3  # Number of retries on failure
)

# Receiving end verifies signature:
import hmac
import hashlib

def verify_webhook_signature(request, secret):
    signature = request.headers.get('X-Empathy-Signature')
    body = request.get_data()

    expected_sig = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)
```

---

## Next Steps

**Enhance integrations**:
1. **Add more services**: Microsoft Teams, Discord, PagerDuty
2. **Custom event types**: Define domain-specific events
3. **Event filtering**: Advanced filtering rules for webhooks
4. **Webhook dashboard**: Monitor delivery rates, failures
5. **Real-time dashboards**: Stream events to live dashboard

**Related examples**:
- [Multi-Agent Coordination](multi-agent-team-coordination.md) - Coordination events
- [Adaptive Learning](adaptive-learning-system.md) - Adaptation events
- [SBAR Clinical Handoff](sbar-clinical-handoff.md) - Healthcare events

---

## Troubleshooting

**"Webhook delivery failed"**
- Check URL is reachable: `curl https://webhook-url`
- Verify SSL certificate if HTTPS
- Check request timeout (increase if needed)
- Review webhook logs: `webhooks.get_delivery_logs()`

**"Events not firing"**
- Verify event bus connected: `empathy.event_bus is not None`
- Check event handler registered: `bus.handlers`
- Test event manually: `bus.emit(Event(type="test", data={}))`

**"Too many webhook requests"**
- Add conditional webhooks (filter low-value events)
- Batch events: `batch_size=10, batch_timeout_seconds=5`
- Use async webhooks: `async_delivery=True`

---

**Questions?** See [Webhook Integration Guide](../guides/webhook-integration.md)
