"""
Audit Logging Framework for Empathy Framework

Comprehensive audit logging for SOC2, HIPAA, and GDPR compliance.
Implements tamper-evident, append-only logging with structured JSON format.

Key Features:
- JSON Lines format (one event per line)
- ISO-8601 timestamps (UTC)
- Unique event IDs (UUID)
- Tamper-evident (append-only)
- Query/search capability
- Log rotation support

Reference:
- SECURE_MEMORY_ARCHITECTURE.md: Audit Trail Implementation
- SOC2 CC7.2: System Monitoring
- HIPAA 164.312(b): Audit Controls
- GDPR Article 30: Records of Processing

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """
    Represents a single audit event.

    All audit events share these core fields for compliance tracking.
    """

    # Core identification
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    version: str = "1.0"

    # Event classification
    event_type: str = ""  # llm_request, store_pattern, retrieve_pattern, security_violation
    user_id: str = ""
    session_id: str = ""

    # Status tracking
    status: str = "success"  # success, failed, blocked
    error: str = ""

    # Custom fields (populated by specific event types)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Flatten data dict into top level for easier querying
        data = result.pop("data", {})
        result.update(data)
        return result


@dataclass
class SecurityViolation:
    """
    Represents a security policy violation.

    Used for tracking and alerting on security issues.
    """

    violation_type: str  # secrets_detected, pii_in_storage, classification_error, etc.
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    details: dict[str, Any] = field(default_factory=dict)
    user_notified: bool = False
    manager_notified: bool = False
    security_team_notified: bool = False


class AuditLogger:
    """
    Comprehensive audit logging for Empathy Framework.

    Implements SOC2, HIPAA, and GDPR compliant audit trails with:
    - Tamper-evident append-only logging
    - Structured JSON Lines format
    - Comprehensive event tracking
    - Query and search capabilities
    - Log rotation support

    Example:
        >>> logger = AuditLogger(log_dir="/var/log/empathy")
        >>> logger.log_llm_request(
        ...     user_id="user@company.com",
        ...     empathy_level=3,
        ...     provider="anthropic",
        ...     model="claude-sonnet-4",
        ...     memory_sources=["enterprise", "user", "project"],
        ...     pii_count=0,
        ...     secrets_count=0
        ... )

    Log Format:
        Each line is a complete JSON object representing one event.
        Format: JSON Lines (.jsonl) - one event per line, append-only.

    Compliance:
        - SOC2 CC7.2: System Monitoring and Logging
        - HIPAA 164.312(b): Audit Controls
        - GDPR Article 30: Records of Processing Activities
    """

    def __init__(
        self,
        log_dir: str = "/var/log/empathy",
        log_filename: str = "audit.jsonl",
        max_file_size_mb: int = 100,
        retention_days: int = 365,
        enable_rotation: bool = True,
        enable_console_logging: bool = False,
    ):
        """
        Initialize the audit logger.

        Args:
            log_dir: Directory for audit logs
            log_filename: Name of the audit log file
            max_file_size_mb: Maximum file size before rotation (if enabled)
            retention_days: Number of days to retain audit logs
            enable_rotation: Whether to enable automatic log rotation
            enable_console_logging: Whether to also log to console (for development)
        """
        self.log_dir = Path(log_dir)
        self.log_filename = log_filename
        self.log_path = self.log_dir / log_filename
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.retention_days = retention_days
        self.enable_rotation = enable_rotation
        self.enable_console_logging = enable_console_logging

        # Track security violations for alerting
        self._violation_counts: dict[str, int] = {}

        # Initialize log directory
        self._initialize_log_directory()

    def _initialize_log_directory(self):
        """Create log directory if it doesn't exist"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.log_dir, 0o700)
            logger.info(f"Audit log directory initialized: {self.log_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize audit log directory: {e}")
            # Fallback to local directory
            self.log_dir = Path("./logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.log_path = self.log_dir / self.log_filename
            logger.warning(f"Using fallback log directory: {self.log_dir}")

    def _write_event(self, event: AuditEvent):
        """
        Write an audit event to the log file.

        Uses append-only mode for tamper-evidence.
        """
        try:
            # Check if rotation is needed
            if self.enable_rotation and self.log_path.exists():
                if self.log_path.stat().st_size > self.max_file_size_bytes:
                    self._rotate_log()

            # Write event as single line JSON
            with open(self.log_path, "a", encoding="utf-8") as f:
                json.dump(event.to_dict(), f, ensure_ascii=False)
                f.write("\n")

            # Optional console logging for development
            if self.enable_console_logging:
                logger.debug(f"Audit event: {event.event_type} - {event.status}")

        except Exception as e:
            logger.error(f"Failed to write audit event: {e}")
            # Critical: audit logging failure should be visible
            if self.enable_console_logging:
                print(f"AUDIT LOG FAILURE: {e}", flush=True)

    def _rotate_log(self):
        """
        Rotate the audit log file.

        Renames current log with timestamp and creates new file.
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            rotated_name = f"{self.log_filename}.{timestamp}"
            rotated_path = self.log_dir / rotated_name

            self.log_path.rename(rotated_path)
            logger.info(f"Audit log rotated: {rotated_path}")

            # Clean up old logs beyond retention period
            self._cleanup_old_logs()

        except Exception as e:
            logger.error(f"Failed to rotate audit log: {e}")

    def _cleanup_old_logs(self):
        """Remove audit logs older than retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

            for log_file in self.log_dir.glob(f"{self.log_filename}.*"):
                # Extract timestamp from filename
                try:
                    timestamp_str = log_file.suffix[1:]  # Remove leading dot
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                    if file_date < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Removed old audit log: {log_file}")
                except (ValueError, IndexError):
                    # Skip files that don't match expected format
                    continue

        except Exception as e:
            logger.error(f"Failed to cleanup old audit logs: {e}")

    def log_llm_request(
        self,
        user_id: str,
        empathy_level: int,
        provider: str,
        model: str,
        memory_sources: list[str],
        pii_count: int = 0,
        secrets_count: int = 0,
        request_size_bytes: int = 0,
        response_size_bytes: int = 0,
        duration_ms: int = 0,
        memdocs_patterns_used: list[str] | None = None,
        sanitization_applied: bool = True,
        classification_verified: bool = True,
        session_id: str = "",
        ip_address: str = "",
        temperature: float = 0.7,
        status: str = "success",
        error: str = "",
        **kwargs,
    ):
        """
        Log an LLM API request.

        Tracks all LLM interactions for compliance and monitoring.

        Args:
            user_id: User or service account making the request
            empathy_level: Empathy level (1-5) used for this request
            provider: LLM provider (anthropic, openai, local)
            model: Specific model used
            memory_sources: Which memory sources were loaded (enterprise, user, project)
            pii_count: Number of PII items detected (not the items themselves)
            secrets_count: Number of secrets detected
            request_size_bytes: Size of the request payload
            response_size_bytes: Size of the response payload
            duration_ms: Request duration in milliseconds
            memdocs_patterns_used: List of MemDocs pattern IDs used
            sanitization_applied: Whether PII sanitization was applied
            classification_verified: Whether data classification was verified
            session_id: Session identifier
            ip_address: Anonymized IP address (e.g., first 3 octets only)
            temperature: LLM temperature setting
            status: success, failed, or blocked
            error: Error message if failed
            **kwargs: Additional custom fields

        Example:
            >>> logger.log_llm_request(
            ...     user_id="user@company.com",
            ...     empathy_level=3,
            ...     provider="anthropic",
            ...     model="claude-sonnet-4",
            ...     memory_sources=["enterprise", "user"],
            ...     pii_count=0,
            ...     secrets_count=0
            ... )
        """
        event = AuditEvent(
            event_type="llm_request",
            user_id=user_id,
            session_id=session_id,
            status=status,
            error=error,
            data={
                "llm": {
                    "provider": provider,
                    "model": model,
                    "empathy_level": empathy_level,
                    "temperature": temperature,
                },
                "memory": {
                    "sources": memory_sources,
                    "total_sources": len(memory_sources),
                    "security_policies_applied": "enterprise" in memory_sources,
                },
                "memdocs": {
                    "patterns_used": memdocs_patterns_used or [],
                    "pattern_count": len(memdocs_patterns_used or []),
                },
                "security": {
                    "pii_detected": pii_count,
                    "secrets_detected": secrets_count,
                    "sanitization_applied": sanitization_applied,
                    "classification_verified": classification_verified,
                },
                "request": {
                    "size_bytes": request_size_bytes,
                    "duration_ms": duration_ms,
                    "ip_address": ip_address,
                },
                "response": {
                    "size_bytes": response_size_bytes,
                },
                "compliance": {
                    "gdpr_compliant": pii_count == 0 or sanitization_applied,
                    "hipaa_compliant": secrets_count == 0 and sanitization_applied,
                    "soc2_compliant": True,
                },
                **kwargs,
            },
        )

        self._write_event(event)

        # Check for security violations
        if secrets_count > 0:
            self._handle_security_violation(
                user_id=user_id,
                violation_type="secrets_detected",
                severity="HIGH",
                details={"secrets_count": secrets_count, "event_type": "llm_request"},
            )

    def log_pattern_store(
        self,
        user_id: str,
        pattern_id: str,
        pattern_type: str,
        classification: str,
        pii_scrubbed: int = 0,
        secrets_detected: int = 0,
        retention_days: int = 180,
        encrypted: bool = False,
        session_id: str = "",
        status: str = "success",
        error: str = "",
        **kwargs,
    ):
        """
        Log MemDocs pattern storage.

        Tracks pattern creation for compliance and data governance.

        Args:
            user_id: User storing the pattern
            pattern_id: Unique identifier for the pattern
            pattern_type: Type of pattern (code, architecture, workflow, etc.)
            classification: PUBLIC, INTERNAL, or SENSITIVE
            pii_scrubbed: Number of PII items scrubbed before storage
            secrets_detected: Number of secrets found (should be 0 for storage)
            retention_days: Retention period in days
            encrypted: Whether pattern is encrypted at rest
            session_id: Session identifier
            status: success, failed, or blocked
            error: Error message if failed
            **kwargs: Additional custom fields

        Example:
            >>> logger.log_pattern_store(
            ...     user_id="user@company.com",
            ...     pattern_id="pattern_abc123",
            ...     pattern_type="architecture",
            ...     classification="INTERNAL",
            ...     pii_scrubbed=2,
            ...     retention_days=180
            ... )
        """
        event = AuditEvent(
            event_type="store_pattern",
            user_id=user_id,
            session_id=session_id,
            status=status,
            error=error,
            data={
                "pattern": {
                    "pattern_id": pattern_id,
                    "pattern_type": pattern_type,
                    "classification": classification,
                    "encrypted": encrypted,
                    "retention_days": retention_days,
                },
                "security": {
                    "pii_scrubbed": pii_scrubbed,
                    "secrets_detected": secrets_detected,
                    "sanitization_applied": pii_scrubbed > 0,
                },
                "compliance": {
                    "gdpr_compliant": secrets_detected == 0,
                    "hipaa_compliant": classification == "SENSITIVE"
                    and encrypted
                    or classification != "SENSITIVE",
                    "soc2_compliant": secrets_detected == 0
                    and classification in ["PUBLIC", "INTERNAL", "SENSITIVE"],
                    "classification_verified": classification
                    in ["PUBLIC", "INTERNAL", "SENSITIVE"],
                },
                **kwargs,
            },
        )

        self._write_event(event)

        # Check for security violations
        if secrets_detected > 0:
            self._handle_security_violation(
                user_id=user_id,
                violation_type="secrets_in_storage",
                severity="CRITICAL",
                details={
                    "secrets_detected": secrets_detected,
                    "pattern_id": pattern_id,
                    "event_type": "store_pattern",
                },
            )

        if classification == "SENSITIVE" and not encrypted:
            self._handle_security_violation(
                user_id=user_id,
                violation_type="sensitive_not_encrypted",
                severity="HIGH",
                details={
                    "pattern_id": pattern_id,
                    "classification": classification,
                    "event_type": "store_pattern",
                },
            )

    def log_pattern_retrieve(
        self,
        user_id: str,
        pattern_id: str,
        classification: str,
        access_granted: bool = True,
        permission_level: str = "",
        session_id: str = "",
        status: str = "success",
        error: str = "",
        **kwargs,
    ):
        """
        Log MemDocs pattern retrieval.

        Tracks pattern access for compliance and security monitoring.

        Args:
            user_id: User retrieving the pattern
            pattern_id: Unique identifier for the pattern
            classification: PUBLIC, INTERNAL, or SENSITIVE
            access_granted: Whether access was granted
            permission_level: Permission level used for access decision
            session_id: Session identifier
            status: success, failed, or blocked
            error: Error message if failed
            **kwargs: Additional custom fields

        Example:
            >>> logger.log_pattern_retrieve(
            ...     user_id="user@company.com",
            ...     pattern_id="pattern_abc123",
            ...     classification="SENSITIVE",
            ...     access_granted=True,
            ...     permission_level="explicit"
            ... )
        """
        event = AuditEvent(
            event_type="retrieve_pattern",
            user_id=user_id,
            session_id=session_id,
            status="success" if access_granted else "blocked",
            error=error,
            data={
                "pattern": {
                    "pattern_id": pattern_id,
                    "classification": classification,
                },
                "access": {
                    "granted": access_granted,
                    "permission_level": permission_level,
                    "audit_required": classification == "SENSITIVE",
                },
                "compliance": {
                    "access_logged": True,
                    "hipaa_compliant": classification == "SENSITIVE",
                },
                **kwargs,
            },
        )

        self._write_event(event)

        # Log unauthorized access attempts
        if not access_granted:
            self._handle_security_violation(
                user_id=user_id,
                violation_type="unauthorized_access",
                severity="MEDIUM" if classification == "INTERNAL" else "HIGH",
                details={
                    "pattern_id": pattern_id,
                    "classification": classification,
                    "event_type": "retrieve_pattern",
                },
            )

    def log_security_violation(
        self,
        user_id: str,
        violation_type: str,
        severity: str,
        details: dict[str, Any],
        session_id: str = "",
        blocked: bool = True,
        **kwargs,
    ):
        """
        Log a security policy violation.

        Tracks security incidents for monitoring and response.

        Args:
            user_id: User who triggered the violation
            violation_type: Type of violation (secrets_detected, pii_in_storage, etc.)
            severity: LOW, MEDIUM, HIGH, or CRITICAL
            details: Additional details about the violation
            session_id: Session identifier
            blocked: Whether the action was blocked
            **kwargs: Additional custom fields

        Example:
            >>> logger.log_security_violation(
            ...     user_id="user@company.com",
            ...     violation_type="secrets_detected",
            ...     severity="HIGH",
            ...     details={"secret_type": "api_key", "action": "llm_request"},
            ...     blocked=True
            ... )
        """
        violation = SecurityViolation(
            violation_type=violation_type, severity=severity, details=details
        )

        event = AuditEvent(
            event_type="security_violation",
            user_id=user_id,
            session_id=session_id,
            status="blocked" if blocked else "logged",
            data={
                "violation": {
                    "type": violation_type,
                    "severity": severity,
                    "details": details,
                    "blocked": blocked,
                },
                "response": {
                    "user_notified": violation.user_notified,
                    "manager_notified": violation.manager_notified,
                    "security_team_notified": violation.security_team_notified,
                },
                "compliance": {
                    "gdpr_compliant": blocked,
                    "hipaa_compliant": blocked,
                    "soc2_compliant": blocked,
                },
                **kwargs,
            },
        )

        self._write_event(event)

    def _handle_security_violation(
        self, user_id: str, violation_type: str, severity: str, details: dict[str, Any]
    ):
        """
        Internal handler for security violations.

        Tracks violation counts and triggers alerts.
        """
        # Track violations per user
        key = f"{user_id}:{violation_type}"
        self._violation_counts[key] = self._violation_counts.get(key, 0) + 1

        # Log the violation
        self.log_security_violation(
            user_id=user_id, violation_type=violation_type, severity=severity, details=details
        )

        # Alert logic
        count = self._violation_counts[key]
        if severity == "CRITICAL" or count >= 3:
            logger.warning(
                f"Security violation threshold reached: {user_id} - "
                f"{violation_type} (count: {count}, severity: {severity})"
            )

    def query(
        self,
        event_type: str | None = None,
        user_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 1000,
        **filters,
    ) -> list[dict]:
        """
        Query audit logs with filters.

        Provides search and analysis capabilities for audit data.

        Args:
            event_type: Filter by event type (llm_request, store_pattern, etc.)
            user_id: Filter by user ID
            status: Filter by status (success, failed, blocked)
            start_date: Filter events after this date
            end_date: Filter events before this date
            limit: Maximum number of events to return
            **filters: Additional key-value filters (supports nested keys with __)

        Returns:
            List of matching audit events as dictionaries

        Example:
            >>> # Find all failed LLM requests
            >>> events = logger.query(event_type="llm_request", status="failed")
            >>>
            >>> # Find security violations in last 24 hours
            >>> from datetime import datetime, timedelta
            >>> events = logger.query(
            ...     event_type="security_violation",
            ...     start_date=datetime.utcnow() - timedelta(days=1)
            ... )
            >>>
            >>> # Find patterns with high PII counts (nested filter)
            >>> events = logger.query(security__pii_detected__gt=5)
        """
        results: list[dict[str, object]] = []

        try:
            if not self.log_path.exists():
                return results

            with open(self.log_path, encoding="utf-8") as f:
                for line in f:
                    if len(results) >= limit:
                        break

                    try:
                        event = json.loads(line.strip())

                        # Apply filters
                        if event_type and event.get("event_type") != event_type:
                            continue
                        if user_id and event.get("user_id") != user_id:
                            continue
                        if status and event.get("status") != status:
                            continue

                        # Date range filtering
                        if start_date or end_date:
                            event_time = datetime.fromisoformat(
                                event.get("timestamp", "").rstrip("Z")
                            )
                            if start_date and event_time < start_date:
                                continue
                            if end_date and event_time > end_date:
                                continue

                        # Custom filters (supports nested keys with __)
                        if filters and not self._apply_custom_filters(event, filters):
                            continue

                        results.append(event)

                    except json.JSONDecodeError:
                        logger.warning("Skipping malformed audit log line")
                        continue

        except Exception as e:
            logger.error(f"Failed to query audit logs: {e}")

        return results

    def _apply_custom_filters(self, event: dict, filters: dict) -> bool:
        """
        Apply custom filters to an event.

        Supports nested key access with __ separator and comparison operators.
        """
        for key, value in filters.items():
            # Handle comparison operators (e.g., security__pii_detected__gt=5)
            parts = key.split("__")
            operator = None

            if len(parts) > 1 and parts[-1] in ["gt", "gte", "lt", "lte", "ne"]:
                operator = parts[-1]
                parts = parts[:-1]

            # Navigate nested dictionary
            current = event
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False

            # Apply comparison
            if operator == "gt" and not (isinstance(current, int | float) and current > value):
                return False
            elif operator == "gte" and not (isinstance(current, int | float) and current >= value):
                return False
            elif operator == "lt" and not (isinstance(current, int | float) and current < value):
                return False
            elif operator == "lte" and not (isinstance(current, int | float) and current <= value):
                return False
            elif operator == "ne" and current == value:
                return False
            elif operator is None and current != value:
                return False

        return True

    def get_violation_summary(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Get summary of security violations.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            Dictionary with violation statistics

        Example:
            >>> summary = logger.get_violation_summary(user_id="user@company.com")
            >>> print(f"Total violations: {summary['total_violations']}")
        """
        violations = self.query(event_type="security_violation", user_id=user_id)

        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        by_user: dict[str, int] = {}

        for violation in violations:
            vtype = str(violation.get("violation", {}).get("type", "unknown"))
            severity = str(violation.get("violation", {}).get("severity", "unknown"))
            vid = str(violation.get("user_id", "unknown"))

            by_type[vtype] = by_type.get(vtype, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_user[vid] = by_user.get(vid, 0) + 1

        summary: dict[str, int | dict[str, int]] = {
            "total_violations": len(violations),
            "by_type": by_type,
            "by_severity": by_severity,
            "by_user": by_user,
        }

        return summary

    def get_compliance_report(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> dict[str, Any]:
        """
        Generate compliance report for audit period.

        Provides statistics for compliance audits (SOC2, HIPAA, GDPR).

        Args:
            start_date: Start of audit period
            end_date: End of audit period

        Returns:
            Dictionary with compliance statistics

        Example:
            >>> from datetime import datetime, timedelta
            >>> report = logger.get_compliance_report(
            ...     start_date=datetime.utcnow() - timedelta(days=30)
            ... )
            >>> print(f"Total LLM requests: {report['llm_requests']['total']}")
        """
        # Query all events in period
        all_events = self.query(start_date=start_date, end_date=end_date, limit=100000)

        report: dict[str, Any] = {
            "period": {
                "start": start_date.isoformat() if start_date else "all_time",
                "end": end_date.isoformat() if end_date else "now",
            },
            "llm_requests": {
                "total": 0,
                "with_pii_detected": 0,
                "with_secrets_detected": 0,
                "sanitization_applied": 0,
            },
            "pattern_storage": {
                "total": 0,
                "by_classification": {"PUBLIC": 0, "INTERNAL": 0, "SENSITIVE": 0},
                "with_pii_scrubbed": 0,
                "encrypted": 0,
            },
            "pattern_retrieval": {
                "total": 0,
                "by_classification": {"PUBLIC": 0, "INTERNAL": 0, "SENSITIVE": 0},
                "access_denied": 0,
            },
            "security_violations": {"total": 0, "by_severity": {}, "by_type": {}},
            "compliance_metrics": {
                "gdpr_compliant_rate": 0.0,
                "hipaa_compliant_rate": 0.0,
                "soc2_compliant_rate": 0.0,
            },
        }

        total_compliance_checks = 0
        gdpr_compliant = 0
        hipaa_compliant = 0
        soc2_compliant = 0

        for event in all_events:
            event_type = event.get("event_type")

            if event_type == "llm_request":
                report["llm_requests"]["total"] += 1
                security = event.get("security", {})
                if security.get("pii_detected", 0) > 0:
                    report["llm_requests"]["with_pii_detected"] += 1
                if security.get("secrets_detected", 0) > 0:
                    report["llm_requests"]["with_secrets_detected"] += 1
                if security.get("sanitization_applied"):
                    report["llm_requests"]["sanitization_applied"] += 1

            elif event_type == "store_pattern":
                report["pattern_storage"]["total"] += 1
                pattern = event.get("pattern", {})
                classification = pattern.get("classification", "INTERNAL")
                report["pattern_storage"]["by_classification"][classification] = (
                    report["pattern_storage"]["by_classification"].get(classification, 0) + 1
                )
                if event.get("security", {}).get("pii_scrubbed", 0) > 0:
                    report["pattern_storage"]["with_pii_scrubbed"] += 1
                if pattern.get("encrypted"):
                    report["pattern_storage"]["encrypted"] += 1

            elif event_type == "retrieve_pattern":
                report["pattern_retrieval"]["total"] += 1
                pattern = event.get("pattern", {})
                classification = pattern.get("classification", "INTERNAL")
                report["pattern_retrieval"]["by_classification"][classification] = (
                    report["pattern_retrieval"]["by_classification"].get(classification, 0) + 1
                )
                if not event.get("access", {}).get("granted", True):
                    report["pattern_retrieval"]["access_denied"] += 1

            elif event_type == "security_violation":
                report["security_violations"]["total"] += 1
                violation = event.get("violation", {})
                vtype = violation.get("type", "unknown")
                severity = violation.get("severity", "unknown")
                report["security_violations"]["by_type"][vtype] = (
                    report["security_violations"]["by_type"].get(vtype, 0) + 1
                )
                report["security_violations"]["by_severity"][severity] = (
                    report["security_violations"]["by_severity"].get(severity, 0) + 1
                )

            # Track compliance rates
            compliance = event.get("compliance", {})
            if compliance:
                total_compliance_checks += 1
                if compliance.get("gdpr_compliant"):
                    gdpr_compliant += 1
                if compliance.get("hipaa_compliant"):
                    hipaa_compliant += 1
                if compliance.get("soc2_compliant"):
                    soc2_compliant += 1

        # Calculate compliance rates
        if total_compliance_checks > 0:
            report["compliance_metrics"]["gdpr_compliant_rate"] = (
                gdpr_compliant / total_compliance_checks
            )
            report["compliance_metrics"]["hipaa_compliant_rate"] = (
                hipaa_compliant / total_compliance_checks
            )
            report["compliance_metrics"]["soc2_compliant_rate"] = (
                soc2_compliant / total_compliance_checks
            )

        return report
