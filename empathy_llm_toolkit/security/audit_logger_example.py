"""
Example usage of the AuditLogger

Demonstrates how to use the audit logging framework for compliance tracking.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from audit_logger import AuditLogger


def main():
    """Demonstrate audit logger functionality"""

    # Initialize audit logger
    # In production, use /var/log/empathy
    # For testing, use local directory
    logger = AuditLogger(
        log_dir="./logs",
        log_filename="audit.jsonl",
        enable_console_logging=True,
    )

    print("=" * 60)
    print("Empathy Framework Audit Logger - Example")
    print("=" * 60)
    print()

    # Example 1: Log an LLM request
    print("1. Logging LLM request...")
    logger.log_llm_request(
        user_id="developer@company.com",
        empathy_level=3,
        provider="anthropic",
        model="claude-sonnet-4",
        memory_sources=["enterprise", "user", "project"],
        pii_count=0,
        secrets_count=0,
        request_size_bytes=1234,
        response_size_bytes=5678,
        duration_ms=2500,
        memdocs_patterns_used=["pattern_abc", "pattern_def"],
        session_id="sess_xyz123",
    )
    print("   ✓ LLM request logged")
    print()

    # Example 2: Log pattern storage
    print("2. Logging MemDocs pattern storage...")
    logger.log_pattern_store(
        user_id="developer@company.com",
        pattern_id="pattern_abc123",
        pattern_type="architecture",
        classification="INTERNAL",
        pii_scrubbed=2,
        secrets_detected=0,
        retention_days=180,
        encrypted=False,
        session_id="sess_xyz123",
    )
    print("   ✓ Pattern storage logged")
    print()

    # Example 3: Log pattern retrieval
    print("3. Logging MemDocs pattern retrieval...")
    logger.log_pattern_retrieve(
        user_id="developer@company.com",
        pattern_id="pattern_abc123",
        classification="INTERNAL",
        access_granted=True,
        permission_level="team_member",
        session_id="sess_xyz123",
    )
    print("   ✓ Pattern retrieval logged")
    print()

    # Example 4: Log a security violation
    print("4. Logging security violation...")
    logger.log_security_violation(
        user_id="developer@company.com",
        violation_type="secrets_detected",
        severity="HIGH",
        details={"secret_type": "api_key", "action": "llm_request"},
        session_id="sess_xyz123",
        blocked=True,
    )
    print("   ✓ Security violation logged")
    print()

    # Example 5: Log SENSITIVE pattern storage (encrypted)
    print("5. Logging SENSITIVE pattern storage...")
    logger.log_pattern_store(
        user_id="healthcare@company.com",
        pattern_id="pattern_health_001",
        pattern_type="medical_workflow",
        classification="SENSITIVE",
        pii_scrubbed=5,
        secrets_detected=0,
        retention_days=90,
        encrypted=True,
        session_id="sess_health456",
    )
    print("   ✓ SENSITIVE pattern storage logged")
    print()

    # Example 6: Query audit logs
    print("6. Querying audit logs...")
    print()

    # Query all LLM requests
    llm_requests = logger.query(event_type="llm_request")
    print(f"   Total LLM requests: {len(llm_requests)}")

    # Query security violations
    violations = logger.query(event_type="security_violation")
    print(f"   Total security violations: {len(violations)}")

    # Query events by user
    user_events = logger.query(user_id="developer@company.com")
    print(f"   Events by developer@company.com: {len(user_events)}")

    # Query with nested filter (high PII counts)
    high_pii = logger.query(event_type="store_pattern", security__pii_scrubbed__gt=2)
    print(f"   Patterns with >2 PII items scrubbed: {len(high_pii)}")
    print()

    # Example 7: Get violation summary
    print("7. Security violation summary...")
    summary = logger.get_violation_summary()
    print(f"   Total violations: {summary['total_violations']}")
    print(f"   By type: {summary['by_type']}")
    print(f"   By severity: {summary['by_severity']}")
    print()

    # Example 8: Generate compliance report
    print("8. Compliance report...")
    report = logger.get_compliance_report()
    print(f"   LLM requests: {report['llm_requests']['total']}")
    print(f"   Pattern storage: {report['pattern_storage']['total']}")
    print(f"   Pattern storage by classification: {report['pattern_storage']['by_classification']}")
    print(f"   Security violations: {report['security_violations']['total']}")
    print(f"   GDPR compliance rate: {report['compliance_metrics']['gdpr_compliant_rate']:.2%}")
    print(f"   HIPAA compliance rate: {report['compliance_metrics']['hipaa_compliant_rate']:.2%}")
    print(f"   SOC2 compliance rate: {report['compliance_metrics']['soc2_compliant_rate']:.2%}")
    print()

    print("=" * 60)
    print("Example complete! Check ./logs/audit.jsonl for the log file.")
    print("=" * 60)


if __name__ == "__main__":
    main()
