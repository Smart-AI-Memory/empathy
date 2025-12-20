"""
Secrets Detector Examples

Demonstrates practical usage of the SecretsDetector module for
enterprise privacy integration.

Author: Empathy Framework Team
Version: 1.8.0-beta
"""

from empathy_llm_toolkit.security import SecretsDetector, SecretType, Severity, detect_secrets


def example_1_basic_detection():
    """Example 1: Basic secrets detection"""
    print("=" * 60)
    print("Example 1: Basic Secrets Detection")
    print("=" * 60)

    detector = SecretsDetector()

    # Sample code with secrets
    code = """
    # Configuration
    ANTHROPIC_API_KEY = "sk-ant-api03-abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr"
    password = "my_secret_password"
    DATABASE_URL = "postgres://user:pass123@localhost:5432/db"
    """

    detections = detector.detect(code)

    print(f"Found {len(detections)} secrets:\n")
    for d in detections:
        print(f"  {d.secret_type.value}")
        print(f"    Severity: {d.severity.value}")
        print(f"    Location: Line {d.line_number}, Column {d.column_start}")
        print(f"    Context: {d.context_snippet}")
        print()


def example_2_file_scanning():
    """Example 2: Scan a configuration file"""
    print("=" * 60)
    print("Example 2: File Scanning")
    print("=" * 60)

    def scan_file_for_secrets(file_path: str) -> bool:
        """
        Scan a file for secrets and report findings.

        Returns:
            True if no secrets found, False otherwise
        """
        detector = SecretsDetector()

        try:
            with open(file_path) as f:
                content = f.read()

            detections = detector.detect(content)

            if detections:
                print(f"⚠️  Found {len(detections)} secrets in {file_path}")

                # Group by severity
                critical = [d for d in detections if d.severity == Severity.CRITICAL]
                high = [d for d in detections if d.severity == Severity.HIGH]
                medium = [d for d in detections if d.severity == Severity.MEDIUM]

                if critical:
                    print(f"\n  CRITICAL ({len(critical)}):")
                    for d in critical:
                        print(f"    - {d.secret_type.value} at line {d.line_number}")

                if high:
                    print(f"\n  HIGH ({len(high)}):")
                    for d in high:
                        print(f"    - {d.secret_type.value} at line {d.line_number}")

                if medium:
                    print(f"\n  MEDIUM ({len(medium)}):")
                    for d in medium:
                        print(f"    - {d.secret_type.value} at line {d.line_number}")

                return False

            print(f"✓ No secrets found in {file_path}")
            return True

        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return False

    # Example usage
    print("\nScanning example file...")
    # In practice, you would scan actual files:
    # scan_file_for_secrets(".env")
    # scan_file_for_secrets("config.py")
    print("(File scanning function ready to use)")


def example_3_custom_patterns():
    """Example 3: Organization-specific secrets"""
    print("\n" + "=" * 60)
    print("Example 3: Custom Patterns for Organization Secrets")
    print("=" * 60)

    detector = SecretsDetector()

    # Add company-specific patterns
    detector.add_custom_pattern(name="acme_api_key", pattern=r"ACME_[A-Z0-9]{32}", severity="high")

    detector.add_custom_pattern(
        name="internal_token", pattern=r"INT_TKN_[a-z0-9]{24}", severity="medium"
    )

    # Test with custom secrets
    code = (
        "# Company-specific credentials\n"
        + "ACME_"
        + "A" * 32
        + "\n"
        + "INT_TKN_abc123def456ghi789jkl012\n"
    )

    detections = detector.detect(code)

    print(f"Found {len(detections)} company-specific secrets:\n")
    for d in detections:
        if "custom_pattern" in d.metadata:
            print(f"  Custom Pattern: {d.metadata['custom_pattern']}")
            print(f"    Severity: {d.severity.value}")
            print(f"    Location: Line {d.line_number}")
            print()


def example_4_entropy_detection():
    """Example 4: High entropy string detection"""
    print("=" * 60)
    print("Example 4: Entropy-Based Detection")
    print("=" * 60)

    # Enable entropy detection
    detector = SecretsDetector(enable_entropy_analysis=True, entropy_threshold=4.5)

    code = """
    # High entropy strings (likely secrets)
    token = "aB3xK9mQ7pL2wE5rT8uY1iO4sD6fG0hJ"

    # Low entropy strings (not secrets)
    name = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    """

    detections = detector.detect(code)

    print(f"Found {len(detections)} high-entropy strings:\n")
    for d in detections:
        if d.secret_type == SecretType.HIGH_ENTROPY_STRING:
            print("  High Entropy String")
            print(f"    Confidence: {d.confidence:.2f}")
            print(f"    Entropy: {d.metadata.get('entropy', 'N/A')}")
            print(f"    Length: {d.metadata.get('length', 'N/A')}")
            print(f"    Location: Line {d.line_number}")
            print()


def example_5_ci_cd_integration():
    """Example 5: CI/CD Pipeline Integration"""
    print("=" * 60)
    print("Example 5: CI/CD Pipeline Integration")
    print("=" * 60)

    def pre_commit_secrets_check(staged_files: list[str]) -> bool:
        """
        Pre-commit hook to check for secrets.

        Args:
            staged_files: List of files to check

        Returns:
            True if no secrets found, False if secrets detected
        """
        detector = SecretsDetector()
        all_clean = True

        for file_path in staged_files:
            # Skip binary files, node_modules, etc.
            if any(
                skip in file_path
                for skip in [
                    "node_modules/",
                    ".git/",
                    "__pycache__/",
                    ".pyc",
                    ".jpg",
                    ".png",
                ]
            ):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                detections = detector.detect(content)

                if detections:
                    print(f"❌ SECRETS DETECTED in {file_path}")
                    for d in detections:
                        print(f"   - {d.secret_type.value} at line {d.line_number}")
                    all_clean = False

            except (UnicodeDecodeError, FileNotFoundError):
                # Skip files that can't be read
                continue

        return all_clean

    # Example usage
    print("\nPre-commit hook function ready.")
    print("In practice, integrate with git hooks:")
    print("  - .git/hooks/pre-commit")
    print("  - pre-commit framework")
    print("  - GitHub Actions")


def example_6_audit_integration():
    """Example 6: Integration with audit logging"""
    print("\n" + "=" * 60)
    print("Example 6: Audit Trail Integration")
    print("=" * 60)

    def detect_and_audit(content: str, user_id: str, file_path: str) -> dict:
        """
        Detect secrets and create audit log entry.

        Args:
            content: Content to scan
            user_id: User performing the action
            file_path: Path to file being scanned

        Returns:
            Audit log entry dictionary
        """
        detector = SecretsDetector()
        detections = detector.detect(content)

        audit_entry = {
            "timestamp": "2025-11-24T14:00:00Z",
            "user_id": user_id,
            "action": "secrets_scan",
            "file_path": file_path,
            "secrets_detected": len(detections),
            "secret_types": [d.secret_type.value for d in detections],
            "severity_counts": {
                "critical": sum(1 for d in detections if d.severity == Severity.CRITICAL),
                "high": sum(1 for d in detections if d.severity == Severity.HIGH),
                "medium": sum(1 for d in detections if d.severity == Severity.MEDIUM),
                "low": sum(1 for d in detections if d.severity == Severity.LOW),
            },
            "status": "blocked" if detections else "passed",
        }

        return audit_entry

    # Example usage
    code = 'api_key = "sk-test-abc123xyz789"'
    audit_entry = detect_and_audit(code, "user@example.com", "config.py")

    print("\nAudit Log Entry:")
    for key, value in audit_entry.items():
        print(f"  {key}: {value}")


def example_7_convenience_function():
    """Example 7: Quick one-liner detection"""
    print("\n" + "=" * 60)
    print("Example 7: Convenience Function")
    print("=" * 60)

    # One-liner for quick detection
    detections = detect_secrets('password = "secret123"')

    print(f"Quick detection: {len(detections)} secret(s) found")
    if detections:
        print(f"  Type: {detections[0].secret_type.value}")
        print(f"  Severity: {detections[0].severity.value}")


def main():
    """Run all examples"""
    example_1_basic_detection()
    example_2_file_scanning()
    example_3_custom_patterns()
    example_4_entropy_detection()
    example_5_ci_cd_integration()
    example_6_audit_integration()
    example_7_convenience_function()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
