"""Compliance Database with Append-Only Architecture.

Provides immutable audit trail for healthcare compliance tracking.
Supports INSERT operations only (no UPDATE/DELETE) for regulatory compliance.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ComplianceDatabase:
    """SQLite database for compliance tracking with append-only operations.

    Features:
    - Immutable audit trail (INSERT only, no UPDATE/DELETE)
    - Audit date tracking
    - Compliance status monitoring
    - Gap detection and recording
    - Thread-safe operations

    Regulatory Compliance:
    - Append-only design satisfies HIPAA audit log requirements
    - No modification of historical records
    - Complete audit trail preservation
    """

    def __init__(self, db_path: str | None = None):
        """Initialize compliance database.

        Args:
            db_path: Path to SQLite database file.
                    Defaults to agents/data/compliance.db
        """
        if db_path is None:
            # Default to agents/data/compliance.db
            agents_dir = Path(__file__).parent
            data_dir = agents_dir / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "compliance.db")

        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with automatic cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Data integrity violations (unique constraints, foreign keys, etc.)
            logger.error(f"Compliance database integrity error: {e}")
            if conn:
                conn.rollback()
            raise  # Re-raise - caller must handle data validation
        except sqlite3.OperationalError as e:
            # Database locked, disk full, permission denied, etc.
            logger.critical(f"Compliance database operational error: {e}")
            if conn:
                conn.rollback()
            raise  # Re-raise - critical database issue
        except sqlite3.DatabaseError as e:
            # General database errors
            logger.error(f"Compliance database error: {e}")
            if conn:
                conn.rollback()
            raise  # Re-raise - unexpected database issue
        except OSError as e:
            # File system errors (disk full, permission denied, etc.)
            logger.critical(f"Compliance database file system error: {e}")
            if conn:
                conn.rollback()
            raise  # Re-raise - critical system issue
        except Exception as e:
            # Unexpected errors - log with full context
            logger.exception(f"Unexpected error in compliance database operation: {e}")
            if conn:
                conn.rollback()
            raise  # Re-raise - preserve error for audit trail
        finally:
            if conn:
                conn.close()

    def _init_schema(self) -> None:
        """Initialize database schema if not exists."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS compliance_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_date TIMESTAMP NOT NULL,
                    audit_type TEXT NOT NULL,  -- 'HIPAA', 'GDPR', 'SOC2', etc.
                    findings TEXT,             -- JSON string of findings
                    risk_score INTEGER,        -- 0-100
                    auditor TEXT,              -- Who performed the audit
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    -- No updated_at field (immutable records)
                );

                CREATE TABLE IF NOT EXISTS compliance_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gap_type TEXT NOT NULL,        -- 'missing_policy', 'expired_cert', etc.
                    severity TEXT NOT NULL,        -- 'critical', 'high', 'medium', 'low'
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    affected_systems TEXT,         -- JSON string of affected systems
                    compliance_framework TEXT,     -- 'HIPAA', 'GDPR', etc.
                    detection_source TEXT          -- 'automated_scan', 'manual_review', etc.
                    -- No status field (can't mark as "fixed", only add new record showing fix)
                );

                CREATE TABLE IF NOT EXISTS compliance_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    compliance_framework TEXT NOT NULL,  -- 'HIPAA', 'GDPR', 'SOC2', etc.
                    status TEXT NOT NULL,                -- 'compliant', 'non_compliant', 'pending'
                    effective_date TIMESTAMP NOT NULL,
                    notes TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_audits_date ON compliance_audits(audit_date DESC);
                CREATE INDEX IF NOT EXISTS idx_gaps_severity ON compliance_gaps(severity, detected_at DESC);
                CREATE INDEX IF NOT EXISTS idx_status_framework ON compliance_status(compliance_framework, effective_date DESC);
                """
            )

    def record_audit(
        self,
        audit_date: datetime,
        audit_type: str,
        findings: str | None = None,
        risk_score: int | None = None,
        auditor: str | None = None,
    ) -> int:
        """Record a compliance audit (append-only).

        Args:
            audit_date: When the audit was performed
            audit_type: Type of audit ('HIPAA', 'GDPR', 'SOC2', etc.)
            findings: JSON string of audit findings
            risk_score: Risk score 0-100
            auditor: Who performed the audit

        Returns:
            Audit record ID

        Note:
            This is an append-only operation. Cannot modify existing audits.
        """
        logger.info(
            f"Recording compliance audit: type={audit_type}, "
            f"risk_score={risk_score}, auditor={auditor}"
        )
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO compliance_audits (audit_date, audit_type, findings, risk_score, auditor)
                VALUES (?, ?, ?, ?, ?)
                """,
                (audit_date, audit_type, findings, risk_score, auditor),
            )
            audit_id = cursor.lastrowid
            logger.info(f"Compliance audit recorded successfully: id={audit_id}")
            return audit_id

    def get_last_audit(self, audit_type: str | None = None) -> dict[str, Any] | None:
        """Get most recent audit record (read-only).

        Args:
            audit_type: Optional filter by audit type

        Returns:
            Audit record dict or None if no audits found
        """
        with self._get_connection() as conn:
            if audit_type:
                cursor = conn.execute(
                    """
                    SELECT * FROM compliance_audits
                    WHERE audit_type = ?
                    ORDER BY audit_date DESC
                    LIMIT 1
                    """,
                    (audit_type,),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM compliance_audits
                    ORDER BY audit_date DESC
                    LIMIT 1
                    """
                )

            row = cursor.fetchone()
            if row is None:
                return None

            return {
                "id": row["id"],
                "audit_date": row["audit_date"],
                "audit_type": row["audit_type"],
                "findings": row["findings"],
                "risk_score": row["risk_score"],
                "auditor": row["auditor"],
                "created_at": row["created_at"],
            }

    def record_gap(
        self,
        gap_type: str,
        severity: str,
        description: str | None = None,
        affected_systems: str | None = None,
        compliance_framework: str | None = None,
        detection_source: str = "automated_scan",
    ) -> int:
        """Record a compliance gap (append-only).

        Args:
            gap_type: Type of gap ('missing_policy', 'expired_cert', etc.)
            severity: Severity level ('critical', 'high', 'medium', 'low')
            description: Human-readable description
            affected_systems: JSON string of affected systems
            compliance_framework: Related framework ('HIPAA', 'GDPR', etc.)
            detection_source: How gap was detected

        Returns:
            Gap record ID

        Note:
            This is an append-only operation. To mark a gap as fixed,
            add a new status record, don't modify this one.
        """
        logger.warning(
            f"Recording compliance gap: type={gap_type}, severity={severity}, "
            f"framework={compliance_framework}, source={detection_source}"
        )
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO compliance_gaps (
                    gap_type, severity, description, affected_systems,
                    compliance_framework, detection_source
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    gap_type,
                    severity,
                    description,
                    affected_systems,
                    compliance_framework,
                    detection_source,
                ),
            )
            gap_id = cursor.lastrowid
            logger.warning(f"Compliance gap recorded: id={gap_id}, severity={severity}")
            return gap_id

    def get_active_gaps(
        self, severity: str | None = None, framework: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all recorded gaps (read-only).

        Args:
            severity: Optional filter by severity
            framework: Optional filter by compliance framework

        Returns:
            List of gap records

        Note:
            Returns all gaps. In append-only design, gaps are never deleted.
            To track fixes, use separate status records.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM compliance_gaps WHERE 1=1"
            params: list[Any] = []

            if severity:
                query += " AND severity = ?"
                params.append(severity)

            if framework:
                query += " AND compliance_framework = ?"
                params.append(framework)

            query += " ORDER BY detected_at DESC"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [
                {
                    "id": row["id"],
                    "gap_type": row["gap_type"],
                    "severity": row["severity"],
                    "detected_at": row["detected_at"],
                    "description": row["description"],
                    "affected_systems": row["affected_systems"],
                    "compliance_framework": row["compliance_framework"],
                    "detection_source": row["detection_source"],
                }
                for row in rows
            ]

    def record_compliance_status(
        self,
        compliance_framework: str,
        status: str,
        effective_date: datetime,
        notes: str | None = None,
    ) -> int:
        """Record compliance status change (append-only).

        Args:
            compliance_framework: Framework name ('HIPAA', 'GDPR', 'SOC2', etc.)
            status: Status ('compliant', 'non_compliant', 'pending')
            effective_date: When this status became effective
            notes: Additional notes

        Returns:
            Status record ID

        Note:
            This is an append-only operation. Status history is preserved.
        """
        log_level = logging.INFO if status == "compliant" else logging.WARNING
        logger.log(
            log_level,
            f"Recording compliance status change: framework={compliance_framework}, "
            f"status={status}, effective_date={effective_date}",
        )
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO compliance_status (compliance_framework, status, effective_date, notes)
                VALUES (?, ?, ?, ?)
                """,
                (compliance_framework, status, effective_date, notes),
            )
            status_id = cursor.lastrowid
            logger.log(
                log_level,
                f"Compliance status recorded: id={status_id}, framework={compliance_framework}, status={status}",
            )
            return status_id

    def get_current_compliance_status(self, compliance_framework: str) -> dict[str, Any] | None:
        """Get most recent compliance status (read-only).

        Args:
            compliance_framework: Framework name

        Returns:
            Status record or None
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM compliance_status
                WHERE compliance_framework = ?
                ORDER BY effective_date DESC, recorded_at DESC
                LIMIT 1
                """,
                (compliance_framework,),
            )

            row = cursor.fetchone()
            if row is None:
                return None

            return {
                "id": row["id"],
                "compliance_framework": row["compliance_framework"],
                "status": row["status"],
                "effective_date": row["effective_date"],
                "notes": row["notes"],
                "recorded_at": row["recorded_at"],
            }
