"""
Monitoring Wizard

Observability, SLO definition, alerting, incident response, and dashboard creation.
Uses Empathy Framework Level 3 (Proactive) for metrics analysis and Level 4
(Anticipatory) for predicting incidents and SLO violations.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)


class MonitoringWizard(BaseWizard):
    """
    Wizard for observability, monitoring, and incident response

    Uses:
    - Level 2: Guide user through monitoring setup
    - Level 3: Proactively detect anomalies and degradation
    - Level 4: Anticipate incidents and SLO violations before they occur
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a monitoring/observability task"""
        # High-priority monitoring phrases (worth 2 points each)
        monitoring_phrases = ["monitoring", "observability", "slo", "sli", "alert", "incident"]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "dashboard",
            "grafana",
            "prometheus",
            "datadog",
            "new relic",
            "metrics",
            "logging",
            "tracing",
            "apm",
            "uptime",
            "downtime",
            "runbook",
            "postmortem",
            "on-call",
            "pager",
        ]

        task_lower = (task.task + " " + task.context).lower()

        primary_matches = sum(2 for phrase in monitoring_phrases if phrase in task_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute monitoring setup workflow"""

        self._assess_emotional_state(task)
        self._extract_constraints(task)

        diagnosis = self._analyze_monitoring_requirements(task)
        slo_definitions = self._define_slos(task)
        alert_rules = self._create_alert_rules(task, slo_definitions)
        dashboards = self._design_dashboards(task, slo_definitions)
        runbooks = self._create_runbooks(task)
        monitoring_forecast = self._predict_monitoring_gaps(task, slo_definitions)

        artifacts = [
            WizardArtifact(
                type="doc",
                title="Observability Strategy",
                content=self._generate_observability_strategy(diagnosis),
            ),
            WizardArtifact(type="doc", title="SLO Definitions", content=slo_definitions),
            WizardArtifact(type="code", title="Alert Rules (Prometheus)", content=alert_rules),
            WizardArtifact(type="code", title="Grafana Dashboards", content=dashboards),
            WizardArtifact(type="doc", title="Incident Response Runbooks", content=runbooks),
            WizardArtifact(
                type="doc",
                title="Postmortem Template",
                content=self._create_postmortem_template(task),
            ),
            WizardArtifact(type="doc", title="Monitoring Forecast", content=monitoring_forecast),
        ]

        plan = [
            "1. Define SLIs and SLOs (uptime, latency, error rate)",
            "2. Set up metrics collection (Prometheus, Datadog)",
            "3. Create monitoring dashboards (Grafana)",
            "4. Configure alerting rules",
            "5. Write incident response runbooks",
            "6. Test alert escalation",
            "7. Set up on-call rotation",
        ]

        empathy_checks = EmpathyChecks(
            cognitive="Considered on-call engineers: alert fatigue, sleep disruption, incident stress",
            emotional="Acknowledged: Being woken at 3am is stressful, alerts must be actionable",
            anticipatory=(
                monitoring_forecast[:200] + "..."
                if len(monitoring_forecast) > 200
                else monitoring_forecast
            ),
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=self._identify_risks(task, slo_definitions),
            handoffs=self._create_handoffs(task),
            next_actions=plan[:5] + self._generate_anticipatory_actions(task),
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_monitoring_requirements(self, task: WizardTask) -> str:
        """Analyze monitoring requirements"""
        analysis = "# Monitoring Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        task_lower = (task.task + " " + task.context).lower()

        # Detect monitoring type
        types = []
        if any(kw in task_lower for kw in ["uptime", "availability", "downtime"]):
            types.append("Uptime Monitoring")
        if any(kw in task_lower for kw in ["latency", "performance", "response time"]):
            types.append("Performance Monitoring")
        if any(kw in task_lower for kw in ["error", "exception", "crash"]):
            types.append("Error Tracking")
        if any(kw in task_lower for kw in ["log", "logging"]):
            types.append("Log Aggregation")
        if any(kw in task_lower for kw in ["trace", "tracing", "apm"]):
            types.append("Distributed Tracing")

        if not types:
            types.append("Full Observability Stack")

        analysis += f"**Monitoring Type**: {', '.join(types)}\n"
        analysis += (
            f"**Context**: {task.context[:300]}...\n"
            if len(task.context) > 300
            else f"**Context**: {task.context}\n"
        )

        return analysis

    def _define_slos(self, task: WizardTask) -> str:
        """Define Service Level Objectives"""
        slos = "# Service Level Objectives (SLOs)\n\n"

        slos += "## SLO Philosophy\n\n"
        slos += "- **SLI**: Service Level Indicator (what we measure)\n"
        slos += "- **SLO**: Service Level Objective (target for SLI)\n"
        slos += "- **SLA**: Service Level Agreement (contractual commitment to customers)\n\n"
        slos += "**Rule**: SLO should be stricter than SLA (buffer for safety)\n"
        slos += "- Example: SLA = 99.9%, SLO = 99.95% (gives us breathing room)\n\n"

        slos += "## Critical SLOs\n\n"

        slos += "### 1. Availability / Uptime\n\n"
        slos += "**SLI**: Percentage of successful requests (HTTP 200-299, 300-399)\n"
        slos += "**SLO**: 99.95% over 30-day window\n"
        slos += "**Error Budget**: 0.05% = 21.6 minutes downtime per month\n\n"
        slos += "**Measurement**:\n"
        slos += "```\n"
        slos += "availability = (successful_requests / total_requests) * 100\n"
        slos += "```\n\n"
        slos += "**Why this target**: Industry standard for SaaS, allows ~2 incidents per month\n\n"

        slos += "### 2. Latency (p95)\n\n"
        slos += "**SLI**: 95th percentile response time for API requests\n"
        slos += "**SLO**: p95 < 500ms\n"
        slos += "**Measurement**: 95% of requests complete within 500ms\n\n"
        slos += '**Why this target**: User perception of "instant" is ~1s, we aim for 2x safety margin\n\n'
        slos += "**Breakdown by endpoint**:\n"
        slos += "- GET requests: p95 < 200ms (read-heavy)\n"
        slos += "- POST requests: p95 < 500ms (write operations)\n"
        slos += "- Heavy operations: p95 < 2000ms (reports, exports)\n\n"

        slos += "### 3. Error Rate\n\n"
        slos += "**SLI**: Percentage of requests resulting in errors (HTTP 500-599)\n"
        slos += "**SLO**: < 0.1% error rate\n"
        slos += "**Error Budget**: 1 in 1000 requests can fail\n\n"
        slos += "**Measurement**:\n"
        slos += "```\n"
        slos += "error_rate = (error_requests / total_requests) * 100\n"
        slos += "```\n\n"

        slos += "### 4. Data Freshness\n\n"
        slos += "**SLI**: Time between data update and availability in UI\n"
        slos += "**SLO**: < 5 minutes lag\n"
        slos += "**Measurement**: Timestamp of last successful data sync\n\n"

        slos += "## Error Budget Policy\n\n"
        slos += "**If error budget exhausted (SLO violated)**:\n"
        slos += "1. **Freeze feature development** - focus on reliability\n"
        slos += "2. **Postmortem required** - understand root cause\n"
        slos += "3. **Remediation** - fix underlying issue before resuming features\n"
        slos += "4. **Review SLO** - too strict? Adjust if needed\n\n"

        slos += "**If error budget healthy (> 50% remaining)**:\n"
        slos += "- Safe to deploy risky features\n"
        slos += "- Can afford to experiment\n"
        slos += "- Velocity over stability\n\n"

        slos += "## SLO Dashboard\n\n"
        slos += "Track these metrics in real-time:\n"
        slos += "- Current SLO status (Green/Yellow/Red)\n"
        slos += "- Error budget remaining (minutes/requests)\n"
        slos += "- Trend over 30 days\n"
        slos += "- Time to budget exhaustion (at current burn rate)\n"

        return slos

    def _create_alert_rules(self, task: WizardTask, slo_definitions: str) -> str:
        """Create alerting rules"""
        alerts = "# Alerting Rules (Prometheus)\n\n"

        alerts += "```yaml\n"
        alerts += "# prometheus-alerts.yaml\n\n"
        alerts += "groups:\n"
        alerts += "  - name: slo_alerts\n"
        alerts += "    interval: 30s\n"
        alerts += "    rules:\n\n"

        alerts += "      # High Severity: Page on-call immediately\n"
        alerts += "      - alert: HighErrorRate\n"
        alerts += "        expr: |\n"
        alerts += "          (\n"
        alerts += '            sum(rate(http_requests_total{status=~"5.."}[5m]))\n'
        alerts += "            /\n"
        alerts += "            sum(rate(http_requests_total[5m]))\n"
        alerts += "          ) > 0.05\n"
        alerts += "        for: 5m\n"
        alerts += "        labels:\n"
        alerts += "          severity: critical\n"
        alerts += "        annotations:\n"
        alerts += '          summary: "High error rate (> 5%)"\n'
        alerts += '          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"\n'
        alerts += '          runbook: "https://wiki.company.com/runbooks/high-error-rate"\n\n'

        alerts += "      - alert: HighLatency\n"
        alerts += "        expr: |\n"
        alerts += "          histogram_quantile(0.95, \n"
        alerts += "            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)\n"
        alerts += "          ) > 0.5\n"
        alerts += "        for: 10m\n"
        alerts += "        labels:\n"
        alerts += "          severity: critical\n"
        alerts += "        annotations:\n"
        alerts += '          summary: "High latency (p95 > 500ms)"\n'
        alerts += '          description: "p95 latency is {{ $value }}s (threshold: 0.5s)"\n'
        alerts += '          runbook: "https://wiki.company.com/runbooks/high-latency"\n\n'

        alerts += "      - alert: ServiceDown\n"
        alerts += "        expr: up == 0\n"
        alerts += "        for: 2m\n"
        alerts += "        labels:\n"
        alerts += "          severity: critical\n"
        alerts += "        annotations:\n"
        alerts += '          summary: "Service {{ $labels.instance }} is down"\n'
        alerts += '          description: "Service has been down for 2 minutes"\n'
        alerts += '          runbook: "https://wiki.company.com/runbooks/service-down"\n\n'

        alerts += "      # Medium Severity: Alert, but don't page (Slack/email)\n"
        alerts += "      - alert: HighMemoryUsage\n"
        alerts += "        expr: |\n"
        alerts += "          (\n"
        alerts += "            node_memory_MemAvailable_bytes\n"
        alerts += "            /\n"
        alerts += "            node_memory_MemTotal_bytes\n"
        alerts += "          ) < 0.15\n"
        alerts += "        for: 15m\n"
        alerts += "        labels:\n"
        alerts += "          severity: warning\n"
        alerts += "        annotations:\n"
        alerts += '          summary: "High memory usage (< 15% available)"\n'
        alerts += '          description: "Available memory: {{ $value | humanizePercentage }}"\n\n'

        alerts += "      - alert: DiskSpaceLow\n"
        alerts += "        expr: |\n"
        alerts += "          (\n"
        alerts += '            node_filesystem_avail_bytes{mountpoint="/"}\n'
        alerts += "            /\n"
        alerts += '            node_filesystem_size_bytes{mountpoint="/"}\n'
        alerts += "          ) < 0.15\n"
        alerts += "        for: 10m\n"
        alerts += "        labels:\n"
        alerts += "          severity: warning\n"
        alerts += "        annotations:\n"
        alerts += '          summary: "Disk space low (< 15% available)"\n'
        alerts += '          description: "Available: {{ $value | humanizePercentage }}"\n\n'

        alerts += "      # SLO Budget Alerts\n"
        alerts += "      - alert: ErrorBudgetBurning\n"
        alerts += "        expr: |\n"
        alerts += "          (\n"
        alerts += '            sum(rate(http_requests_total{status=~"5.."}[1h]))\n'
        alerts += "            /\n"
        alerts += "            sum(rate(http_requests_total[1h]))\n"
        alerts += "          ) > 0.001  # 0.1% error rate = SLO threshold\n"
        alerts += "        for: 1h\n"
        alerts += "        labels:\n"
        alerts += "          severity: warning\n"
        alerts += "        annotations:\n"
        alerts += '          summary: "Error budget burning fast"\n'
        alerts += (
            '          description: "At current rate, error budget will be exhausted in < 7 days"\n'
        )
        alerts += "```\n\n"

        alerts += "## Alert Severity Levels\n\n"
        alerts += "| Severity | Response | Examples |\n"
        alerts += "|----------|----------|----------|\n"
        alerts += "| **Critical** | Page on-call immediately | Service down, high error rate, data loss |\n"
        alerts += "| **Warning** | Slack/Email, no page | Disk 80% full, elevated latency, approaching SLO |\n"
        alerts += "| **Info** | Dashboard only | Deployment started, backup completed |\n\n"

        alerts += "## Alert Best Practices\n\n"
        alerts += "1. **Actionable**: Every alert must have a runbook (what to do)\n"
        alerts += "2. **No False Positives**: Tune thresholds to avoid alert fatigue\n"
        alerts += "3. **Appropriate Severity**: Don't page for warnings, don't ignore critical\n"
        alerts += "4. **Self-Resolving**: Alerts auto-resolve when issue fixed\n"
        alerts += "5. **Contextual**: Include relevant labels (service, instance, region)\n\n"

        alerts += "## Alert Routing (PagerDuty)\n\n"
        alerts += "```yaml\n"
        alerts += "# alertmanager.yaml\n"
        alerts += "route:\n"
        alerts += "  receiver: 'default'\n"
        alerts += "  routes:\n"
        alerts += "    - match:\n"
        alerts += "        severity: critical\n"
        alerts += "      receiver: 'pagerduty'\n"
        alerts += "      continue: true\n"
        alerts += "    - match:\n"
        alerts += "        severity: warning\n"
        alerts += "      receiver: 'slack'\n\n"
        alerts += "receivers:\n"
        alerts += "  - name: 'pagerduty'\n"
        alerts += "    pagerduty_configs:\n"
        alerts += "      - service_key: '<pagerduty-integration-key>'\n"
        alerts += "  - name: 'slack'\n"
        alerts += "    slack_configs:\n"
        alerts += "      - channel: '#alerts'\n"
        alerts += "        text: '{{ .CommonAnnotations.summary }}'\n"
        alerts += "```\n"

        return alerts

    def _design_dashboards(self, task: WizardTask, slo_definitions: str) -> str:
        """Design monitoring dashboards"""
        dashboards = "# Grafana Dashboards\n\n"

        dashboards += "## 1. SLO Overview Dashboard\n\n"
        dashboards += "**Purpose**: Executive-level view of service health\n\n"
        dashboards += "**Panels**:\n"
        dashboards += "- **Uptime (30-day)**: Gauge showing 99.95% SLO (Green/Yellow/Red)\n"
        dashboards += "- **Error Budget Remaining**: Progress bar (50% = healthy)\n"
        dashboards += "- **p95 Latency**: Time series graph with 500ms threshold line\n"
        dashboards += "- **Error Rate**: Time series graph with 0.1% threshold\n"
        dashboards += "- **Incidents This Month**: Counter\n\n"

        dashboards += "```json\n"
        dashboards += "{\n"
        dashboards += '  "dashboard": {\n'
        dashboards += '    "title": "SLO Overview",\n'
        dashboards += '    "panels": [\n'
        dashboards += "      {\n"
        dashboards += '        "title": "Uptime (30-day)",\n'
        dashboards += '        "type": "gauge",\n'
        dashboards += '        "targets": [\n'
        dashboards += "          {\n"
        dashboards += '            "expr": "(\n'
        dashboards += '              sum(rate(http_requests_total{status!~\\"5..\\"}[30d]))\n'
        dashboards += "              /\n"
        dashboards += "              sum(rate(http_requests_total[30d]))\n"
        dashboards += '            ) * 100"\n'
        dashboards += "          }\n"
        dashboards += "        ],\n"
        dashboards += '        "thresholds": {\n'
        dashboards += '          "green": 99.95,\n'
        dashboards += '          "yellow": 99.9,\n'
        dashboards += '          "red": 99.5\n'
        dashboards += "        }\n"
        dashboards += "      }\n"
        dashboards += "    ]\n"
        dashboards += "  }\n"
        dashboards += "}\n"
        dashboards += "```\n\n"

        dashboards += "## 2. Request Dashboard\n\n"
        dashboards += "**Purpose**: Detailed request metrics\n\n"
        dashboards += "**Panels**:\n"
        dashboards += "- **Request Rate**: Requests per second\n"
        dashboards += "- **Status Code Distribution**: 2xx, 4xx, 5xx breakdown\n"
        dashboards += "- **Latency Percentiles**: p50, p95, p99\n"
        dashboards += "- **Top Slowest Endpoints**: Table\n"
        dashboards += "- **Error Rate by Endpoint**: Heatmap\n\n"

        dashboards += "## 3. Infrastructure Dashboard\n\n"
        dashboards += "**Purpose**: System resource utilization\n\n"
        dashboards += "**Panels**:\n"
        dashboards += "- **CPU Usage**: Time series by instance\n"
        dashboards += "- **Memory Usage**: Time series with swap\n"
        dashboards += "- **Disk I/O**: Read/write operations\n"
        dashboards += "- **Network Traffic**: Ingress/egress bandwidth\n"
        dashboards += "- **Pod Count**: Kubernetes pod status\n\n"

        dashboards += "## 4. Business Metrics Dashboard\n\n"
        dashboards += "**Purpose**: Product/business KPIs\n\n"
        dashboards += "**Panels**:\n"
        dashboards += "- **Active Users**: Real-time active sessions\n"
        dashboards += "- **Sign-ups**: New user registrations per hour\n"
        dashboards += "- **Conversions**: Trial → paid conversion rate\n"
        dashboards += "- **Revenue**: Real-time revenue tracking\n\n"

        dashboards += "## Dashboard Design Principles\n\n"
        dashboards += "1. **Red Line Principle**: Draw red line at SLO threshold\n"
        dashboards += "2. **Time Window**: Default to 1 hour, allow zoom to 30 days\n"
        dashboards += "3. **Color Coding**: Green (good), Yellow (warning), Red (critical)\n"
        dashboards += "4. **Drill-Down**: Click panel to see detailed view\n"
        dashboards += "5. **Context**: Include annotations for deployments, incidents\n"

        return dashboards

    def _create_runbooks(self, task: WizardTask) -> str:
        """Create incident response runbooks"""
        runbooks = "# Incident Response Runbooks\n\n"

        runbooks += "## Runbook: High Error Rate\n\n"
        runbooks += "**Alert**: Error rate > 5% for 5 minutes\n\n"
        runbooks += "**Severity**: Critical (page on-call)\n\n"
        runbooks += "**Investigation Steps**:\n\n"
        runbooks += "1. **Check dashboard**: Which endpoints have errors?\n"
        runbooks += "   - Grafana → Request Dashboard → Error Rate by Endpoint\n\n"
        runbooks += "2. **Review error logs**: What's the error message?\n"
        runbooks += "   ```bash\n"
        runbooks += "   kubectl logs -n production -l app=api --tail=100 | grep ERROR\n"
        runbooks += "   ```\n\n"
        runbooks += "3. **Check recent deployments**: Did we deploy recently?\n"
        runbooks += "   ```bash\n"
        runbooks += "   kubectl rollout history deployment/api -n production\n"
        runbooks += "   ```\n\n"
        runbooks += "4. **Check dependencies**: Are external services down?\n"
        runbooks += "   - Database: Check connection pool\n"
        runbooks += "   - Redis: Check connectivity\n"
        runbooks += "   - External APIs: Check status pages\n\n"

        runbooks += "**Common Causes & Fixes**:\n\n"
        runbooks += "| Cause | Symptoms | Fix |\n"
        runbooks += "|-------|----------|-----|\n"
        runbooks += "| Bad deployment | Errors started after deploy | Rollback deployment |\n"
        runbooks += (
            "| Database overload | Timeout errors | Scale up database or add read replicas |\n"
        )
        runbooks += (
            "| External API down | 502 errors | Enable circuit breaker, serve cached data |\n"
        )
        runbooks += (
            "| Memory leak | OOM errors, crashes | Restart pods, investigate memory leak |\n\n"
        )

        runbooks += "**Mitigation**:\n"
        runbooks += "```bash\n"
        runbooks += "# Option 1: Rollback deployment\n"
        runbooks += "kubectl rollout undo deployment/api -n production\n\n"
        runbooks += "# Option 2: Scale up (if load issue)\n"
        runbooks += "kubectl scale deployment/api --replicas=10 -n production\n\n"
        runbooks += "# Option 3: Restart pods (if memory leak)\n"
        runbooks += "kubectl rollout restart deployment/api -n production\n"
        runbooks += "```\n\n"

        runbooks += (
            "**Escalation**: If not resolved in 15 minutes, escalate to engineering lead\n\n"
        )
        runbooks += "---\n\n"

        runbooks += "## Runbook: High Latency\n\n"
        runbooks += "**Alert**: p95 latency > 500ms for 10 minutes\n\n"
        runbooks += "**Severity**: Critical (page on-call)\n\n"
        runbooks += "**Investigation**:\n\n"
        runbooks += "1. **Identify slow endpoints**:\n"
        runbooks += "   - Grafana → Request Dashboard → Top Slowest Endpoints\n\n"
        runbooks += "2. **Check database performance**:\n"
        runbooks += "   ```sql\n"
        runbooks += "   -- PostgreSQL: Find slow queries\n"
        runbooks += "   SELECT query, mean_exec_time, calls\n"
        runbooks += "   FROM pg_stat_statements\n"
        runbooks += "   ORDER BY mean_exec_time DESC LIMIT 10;\n"
        runbooks += "   ```\n\n"
        runbooks += "3. **Check cache hit rate**:\n"
        runbooks += "   - Low cache hit rate = more DB queries = higher latency\n\n"
        runbooks += "4. **Check resource utilization**:\n"
        runbooks += "   - CPU at 100%? Scale horizontally\n"
        runbooks += "   - Memory high? Check for memory leak\n\n"

        runbooks += "**Mitigation**:\n"
        runbooks += "```bash\n"
        runbooks += "# Scale horizontally (add more pods)\n"
        runbooks += "kubectl scale deployment/api --replicas=10 -n production\n\n"
        runbooks += "# Clear cache (if stale cache causing issues)\n"
        runbooks += "redis-cli FLUSHDB\n"
        runbooks += "```\n\n"

        runbooks += "---\n\n"

        runbooks += "## Runbook: Service Down\n\n"
        runbooks += "**Alert**: Service not responding for 2 minutes\n\n"
        runbooks += "**Severity**: Critical (page on-call)\n\n"
        runbooks += "**Investigation**:\n\n"
        runbooks += "1. **Check pod status**:\n"
        runbooks += "   ```bash\n"
        runbooks += "   kubectl get pods -n production\n"
        runbooks += "   kubectl describe pod <pod-name> -n production\n"
        runbooks += "   ```\n\n"
        runbooks += "2. **Check logs**:\n"
        runbooks += "   ```bash\n"
        runbooks += "   kubectl logs <pod-name> -n production --tail=100\n"
        runbooks += "   ```\n\n"
        runbooks += "3. **Check cluster health**:\n"
        runbooks += "   ```bash\n"
        runbooks += "   kubectl get nodes\n"
        runbooks += "   kubectl top nodes\n"
        runbooks += "   ```\n\n"

        runbooks += "**Mitigation**:\n"
        runbooks += "```bash\n"
        runbooks += "# Restart deployment\n"
        runbooks += "kubectl rollout restart deployment/api -n production\n\n"
        runbooks += "# If pods are pending (no resources)\n"
        runbooks += (
            "kubectl scale deployment/api --replicas=5 -n production  # Scale down temporarily\n"
        )
        runbooks += "```\n\n"

        runbooks += "**Communication**:\n"
        runbooks += "- Post to #incidents Slack channel\n"
        runbooks += "- Update status page (status.company.com)\n"
        runbooks += "- If > 5 minutes: Email affected customers\n\n"

        return runbooks

    def _create_postmortem_template(self, task: WizardTask) -> str:
        """Create postmortem template"""
        template = "# Postmortem Template\n\n"

        template += "**Date**: YYYY-MM-DD\n"
        template += "**Duration**: X hours Y minutes\n"
        template += "**Severity**: Critical / High / Medium\n"
        template += "**Author**: [Your Name]\n"
        template += "**Reviewers**: [Team Lead, SRE Lead]\n\n"

        template += "## Summary\n\n"
        template += "[1-2 sentence summary of what happened]\n\n"
        template += "Example: API service experienced 15 minutes of downtime due to database connection pool exhaustion, affecting 1,200 active users.\n\n"

        template += "## Impact\n\n"
        template += "- **Users Affected**: [Number of users or % of traffic]\n"
        template += "- **Duration**: [Start time - end time]\n"
        template += "- **Services Affected**: [List of services]\n"
        template += "- **Revenue Impact**: [$X lost revenue or N/A]\n"
        template += "- **SLO Impact**: [Error budget consumed: X minutes]\n\n"

        template += "## Timeline (All times in UTC)\n\n"
        template += "| Time | Event |\n"
        template += "|------|-------|\n"
        template += "| 14:00 | Deployment of version 1.2.3 to production |\n"
        template += "| 14:05 | Error rate begins climbing (2% → 15%) |\n"
        template += "| 14:07 | PagerDuty alert fires, on-call engineer paged |\n"
        template += "| 14:10 | Engineer investigates, identifies DB connection pool issue |\n"
        template += "| 14:15 | Rollback initiated |\n"
        template += "| 14:20 | Rollback complete, error rate returns to normal |\n\n"

        template += "## Root Cause\n\n"
        template += "[Detailed explanation of what caused the incident]\n\n"
        template += "Example: Database connection pool size was set to 10 connections. Under load, this was insufficient, causing connection timeouts. The issue was introduced in commit abc123, which reduced the pool size from 50 to 10 during a refactoring.\n\n"

        template += "## Detection\n\n"
        template += "- **How was it detected?**: [Alert / User report / Monitoring]\n"
        template += "- **Time to detect**: [X minutes after incident started]\n"
        template += "- **Could we have detected sooner?**: [Yes/No, explanation]\n\n"

        template += "## Response\n\n"
        template += "- **Time to acknowledge**: [X minutes]\n"
        template += "- **Time to mitigate**: [X minutes]\n"
        template += "- **What went well?**: [e.g., Fast rollback, good communication]\n"
        template += "- **What went poorly?**: [e.g., Alert fired late, unclear runbook]\n\n"

        template += "## Action Items\n\n"
        template += "| Action | Owner | Deadline | Priority |\n"
        template += "|--------|-------|----------|----------|\n"
        template += "| Increase DB connection pool to 50 | @engineer | 2025-01-20 | P0 |\n"
        template += "| Add connection pool monitoring | @sre | 2025-01-25 | P1 |\n"
        template += (
            "| Update deployment checklist to verify config | @team-lead | 2025-01-30 | P2 |\n"
        )
        template += "| Conduct load test with realistic traffic | @qa | 2025-02-05 | P2 |\n\n"

        template += "## Lessons Learned\n\n"
        template += "**What went well**:\n"
        template += "- Rollback was fast (5 minutes)\n"
        template += "- Team communicated well in Slack\n"
        template += "- Customer impact was minimized\n\n"

        template += "**What to improve**:\n"
        template += "- Better load testing before deploys\n"
        template += "- Monitor connection pool utilization\n"
        template += "- Update runbook with connection pool troubleshooting\n\n"

        template += "## References\n\n"
        template += "- Incident Slack thread: [Link]\n"
        template += "- Related alerts: [Links to PagerDuty/Grafana]\n"
        template += "- Git commit: [Link to commit that caused issue]\n"

        return template

    def _predict_monitoring_gaps(self, task: WizardTask, slo_definitions: str) -> str:
        """Level 4: Predict monitoring gaps and incidents"""
        forecast = "# Monitoring Forecast (Level 4: Anticipatory)\n\n"

        forecast += "## Current State\n"
        forecast += "- SLOs defined: 4 (availability, latency, error rate, data freshness)\n"
        forecast += "- Alerts configured: Basic (uptime, error rate)\n"
        forecast += "- Dashboards: SLO overview only\n\n"

        forecast += "## Projected Issues (Next 30-90 Days)\n\n"

        forecast += "### ⚠️ Alert Fatigue (30 days)\n"
        forecast += "**Prediction**: Too many alerts (>10/day) will lead to ignored pages\n"
        forecast += "**Impact**: Real incidents missed, on-call burnout, attrition\n"
        forecast += "**Cause**: Overly sensitive thresholds, alerting on symptoms not causes\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Review alert thresholds weekly\n"
        forecast += "- Track alert-to-incident ratio (target: 50%+)\n"
        forecast += "- Silence non-actionable alerts\n"
        forecast += "- Consolidate related alerts (one root cause = one alert)\n\n"

        forecast += "### ⚠️ Blind Spot Incident (45 days)\n"
        forecast += (
            "**Prediction**: Incident occurs in unmonitored area (queue depth, cache hit rate)\n"
        )
        forecast += "**Impact**: Late detection, prolonged outage, customer impact\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Add monitoring for: queue depth, cache hit rate, DB connection pool\n"
        forecast += "- Review architecture for blind spots quarterly\n"
        forecast += "- Monitor upstream/downstream dependencies\n\n"

        forecast += "### ⚠️ SLO Violation Without Warning (60 days)\n"
        forecast += "**Prediction**: SLO violated but no alert fired (slow burn)\n"
        forecast += "**Impact**: Error budget exhausted, customer SLA breach\n"
        forecast += "**Cause**: Alerts only detect fast-burning issues, not slow degradation\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Add multi-window alerts (1h, 6h, 24h burn rates)\n"
        forecast += "- Alert when error budget < 50% remaining\n"
        forecast += "- Weekly SLO review in team meeting\n\n"

        forecast += "### ⚠️ Runbook Drift (90 days)\n"
        forecast += "**Prediction**: Runbooks become outdated as system evolves\n"
        forecast += "**Impact**: Slow incident response, on-call confusion, wrong fixes applied\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Update runbook after every incident (mandatory)\n"
        forecast += "- Test runbooks in game days (simulate incidents)\n"
        forecast += "- Link runbooks to alerts (one-click access)\n\n"

        forecast += "## On-Call Health Metrics\n\n"
        forecast += "Track these to prevent burnout:\n\n"
        forecast += "| Metric | Target | Current | Trend |\n"
        forecast += "|--------|--------|---------|-------|\n"
        forecast += "| Alerts per week | < 10 | 15 | ⬆️ (bad) |\n"
        forecast += "| Pages per week | < 3 | 2 | ✅ (good) |\n"
        forecast += "| False positives | < 10% | 25% | ⬆️ (bad) |\n"
        forecast += "| MTTD (mean time to detect) | < 5 min | 3 min | ✅ (good) |\n"
        forecast += "| MTTR (mean time to resolve) | < 30 min | 45 min | ⬆️ (needs work) |\n\n"

        forecast += "**Action**: Reduce false positives by tuning alert thresholds\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Week 1**: Set up SLO dashboards\n"
        forecast += "- **Week 2**: Configure alerting rules\n"
        forecast += "- **Week 3**: Write runbooks for top 3 alerts\n"
        forecast += "- **Week 4**: Test alerts in staging\n"
        forecast += "- **Week 5**: Enable production alerts\n"
        forecast += "- **Ongoing**: Weekly alert review, monthly runbook updates\n"

        return forecast

    def _generate_observability_strategy(self, diagnosis: str) -> str:
        """Generate observability strategy document"""
        strategy = f"{diagnosis}\n\n"

        strategy += "## Observability Strategy\n\n"

        strategy += "### Three Pillars of Observability\n\n"
        strategy += "1. **Metrics**: Quantitative measurements (latency, error rate, CPU)\n"
        strategy += "   - Tools: Prometheus, Datadog, New Relic\n"
        strategy += "   - Use case: Dashboards, alerts, SLO tracking\n\n"

        strategy += "2. **Logs**: Event records (errors, warnings, debug info)\n"
        strategy += "   - Tools: ELK Stack, Splunk, Loki\n"
        strategy += "   - Use case: Debugging, audit trail, compliance\n\n"

        strategy += "3. **Traces**: Request flow through distributed system\n"
        strategy += "   - Tools: Jaeger, Zipkin, Datadog APM\n"
        strategy += "   - Use case: Latency investigation, bottleneck identification\n\n"

        strategy += "### Monitoring Maturity Model\n\n"
        strategy += "**Level 1 (Current)**: Basic uptime monitoring\n"
        strategy += "**Level 2 (Target Q2)**: SLO-based alerting, runbooks\n"
        strategy += "**Level 3 (Target Q4)**: Distributed tracing, advanced analytics\n"
        strategy += "**Level 4 (Future)**: Predictive analytics, AIOps\n\n"

        strategy += "### Implementation Priorities\n\n"
        strategy += "1. Define SLOs (Week 1)\n"
        strategy += "2. Set up metrics collection (Week 2)\n"
        strategy += "3. Create dashboards (Week 3)\n"
        strategy += "4. Configure alerts (Week 4)\n"
        strategy += "5. Write runbooks (Week 5-6)\n"
        strategy += "6. On-call rotation (Week 7+)\n"

        return strategy

    def _identify_risks(self, task: WizardTask, slo_definitions: str) -> list[WizardRisk]:
        """Identify monitoring risks"""
        risks = []

        risks.append(
            WizardRisk(
                risk="Alert fatigue leads to ignored pages and missed incidents",
                mitigation="Tune alert thresholds. Track false positive rate. Review alerts weekly.",
                severity="high",
            )
        )

        risks.append(
            WizardRisk(
                risk="Monitoring blind spots allow incidents to go undetected",
                mitigation="Quarterly architecture review for monitoring gaps. Monitor dependencies.",
                severity="high",
            )
        )

        risks.append(
            WizardRisk(
                risk="Outdated runbooks slow down incident response",
                mitigation="Update runbooks after every incident. Test in game days.",
                severity="medium",
            )
        )

        risks.append(
            WizardRisk(
                risk="On-call burnout due to excessive paging",
                mitigation="Limit to <3 pages/week. Provide comp time. Improve automation.",
                severity="medium",
            )
        )

        return risks

    def _create_handoffs(self, task: WizardTask) -> list[WizardHandoff]:
        """Create handoffs for monitoring work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(
                WizardHandoff(
                    owner="SRE / Platform Team",
                    what="Set up monitoring infrastructure (Prometheus, Grafana), configure alerting, on-call rotation",
                    when="Before production launch",
                )
            )
            handoffs.append(
                WizardHandoff(
                    owner="Engineering Team",
                    what="Write and maintain runbooks, participate in on-call rotation, respond to incidents",
                    when="Ongoing",
                )
            )

        return handoffs
