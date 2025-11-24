"""
Secrets Detection Module

Comprehensive secrets detection for enterprise privacy integration.
Detects API keys, passwords, private keys, OAuth tokens, JWT tokens, database
connection strings, and other sensitive credentials.

CRITICAL: This module NEVER logs or returns actual secret values. It only
returns metadata about detections (type, location, severity).

Author: Empathy Framework Team
Version: 1.8.0-beta
License: Fair Source 0.9
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from re import Pattern

import structlog

logger = structlog.get_logger(__name__)


class SecretType(Enum):
    """Types of secrets that can be detected"""

    # API Keys
    ANTHROPIC_API_KEY = "anthropic_api_key"
    OPENAI_API_KEY = "openai_api_key"
    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    GITHUB_TOKEN = "github_token"
    SLACK_TOKEN = "slack_token"
    STRIPE_KEY = "stripe_key"
    GENERIC_API_KEY = "generic_api_key"

    # Passwords
    PASSWORD = "password"
    BASIC_AUTH = "basic_auth"

    # Private Keys
    RSA_PRIVATE_KEY = "rsa_private_key"
    SSH_PRIVATE_KEY = "ssh_private_key"
    EC_PRIVATE_KEY = "ec_private_key"
    PGP_PRIVATE_KEY = "pgp_private_key"
    TLS_CERTIFICATE_KEY = "tls_certificate_key"

    # Tokens
    JWT_TOKEN = "jwt_token"
    OAUTH_TOKEN = "oauth_token"
    BEARER_TOKEN = "bearer_token"

    # Database
    DATABASE_URL = "database_url"
    CONNECTION_STRING = "connection_string"

    # High Entropy
    HIGH_ENTROPY_STRING = "high_entropy_string"


class Severity(Enum):
    """Severity levels for secret detections"""

    CRITICAL = "critical"  # Private keys, AWS credentials
    HIGH = "high"  # API keys, passwords
    MEDIUM = "medium"  # OAuth tokens, JWT
    LOW = "low"  # Potential secrets, high entropy strings


@dataclass
class SecretDetection:
    """
    Metadata about a detected secret.

    CRITICAL: The actual secret value is NEVER stored in this object.
    """

    secret_type: SecretType
    severity: Severity
    line_number: int
    column_start: int
    column_end: int
    context_snippet: str = ""  # Surrounding text (without the secret itself)
    confidence: float = 1.0  # 0.0 to 1.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/serialization"""
        return {
            "secret_type": self.secret_type.value,
            "severity": self.severity.value,
            "line_number": self.line_number,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "context_snippet": self.context_snippet,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class SecretsDetector:
    """
    Detects secrets in text content using pattern matching and entropy analysis.

    This detector is designed for high performance with compiled regex patterns
    and early exit on detection. It supports custom patterns and provides
    detailed detection metadata without exposing actual secret values.

    Example:
        >>> detector = SecretsDetector()
        >>> detections = detector.detect("api_key = 'sk_live_abc123xyz789'")
        >>> if detections:
        ...     print(f"Found {len(detections)} secrets")
        ...     for detection in detections:
        ...         print(f"  - {detection.secret_type.value} at line {detection.line_number}")
    """

    def __init__(
        self,
        enable_entropy_analysis: bool = True,
        entropy_threshold: float = 4.5,
        min_entropy_length: int = 20,
        max_context_chars: int = 50,
    ):
        """
        Initialize secrets detector.

        Args:
            enable_entropy_analysis: Whether to detect high-entropy strings
            entropy_threshold: Minimum entropy for detection (4.5 is recommended)
            min_entropy_length: Minimum string length for entropy analysis
            max_context_chars: Maximum characters to include in context snippet
        """
        self.enable_entropy_analysis = enable_entropy_analysis
        self.entropy_threshold = entropy_threshold
        self.min_entropy_length = min_entropy_length
        self.max_context_chars = max_context_chars

        # Compile regex patterns for performance
        self._patterns: dict[SecretType, tuple[Pattern, Severity]] = {}
        self._custom_patterns: dict[str, tuple[Pattern, Severity]] = {}
        self._initialize_patterns()

        logger.debug(
            "secrets_detector_initialized",
            patterns_count=len(self._patterns),
            entropy_analysis=enable_entropy_analysis,
        )

    def _initialize_patterns(self):
        """Initialize compiled regex patterns for all secret types"""

        # Anthropic API Keys (sk-ant-...)
        self._patterns[SecretType.ANTHROPIC_API_KEY] = (
            re.compile(
                r"(?i)(?:anthropic[_-]?api[_-]?key|ANTHROPIC_API_KEY)\s*[=:]\s*[\"']?(sk-ant-[a-zA-Z0-9_-]{95,})[\"']?",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

        # OpenAI API Keys (sk-...)
        self._patterns[SecretType.OPENAI_API_KEY] = (
            re.compile(
                r"(?i)(?:openai[_-]?api[_-]?key|OPENAI_API_KEY)\s*[=:]\s*[\"']?(sk-[a-zA-Z0-9]{20,})[\"']?",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

        # AWS Access Key (AKIA...)
        self._patterns[SecretType.AWS_ACCESS_KEY] = (
            re.compile(r"\b(AKIA[A-Z0-9]{16})\b", re.MULTILINE),
            Severity.CRITICAL,
        )

        # AWS Secret Access Key
        self._patterns[SecretType.AWS_SECRET_KEY] = (
            re.compile(
                r"(?i)(?:aws[_-]?secret[_-]?access[_-]?key|AWS_SECRET_ACCESS_KEY)\s*[=:]\s*[\"']?([a-zA-Z0-9/+=]{40})[\"']?",
                re.MULTILINE,
            ),
            Severity.CRITICAL,
        )

        # GitHub Token (ghp_, gho_, ghs_, ghr_)
        self._patterns[SecretType.GITHUB_TOKEN] = (
            re.compile(r"\b(gh[pousr]_[a-zA-Z0-9]{36,})\b", re.MULTILINE),
            Severity.HIGH,
        )

        # Slack Tokens (xox[abprs]-...)
        self._patterns[SecretType.SLACK_TOKEN] = (
            re.compile(r"\b(xox[abprs]-[a-zA-Z0-9-]+)\b", re.MULTILINE),
            Severity.HIGH,
        )

        # Stripe Keys (sk_live_, pk_live_, sk_test_)
        self._patterns[SecretType.STRIPE_KEY] = (
            re.compile(r"\b([sp]k_(?:live|test)_[a-zA-Z0-9]{24,})\b", re.MULTILINE),
            Severity.HIGH,
        )

        # Generic API Key patterns
        self._patterns[SecretType.GENERIC_API_KEY] = (
            re.compile(
                r"(?i)(?:api[_-]?key|apikey|access[_-]?token)\s*[=:]\s*[\"']?([a-zA-Z0-9_-]{20,})[\"']?",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

        # Password assignments
        self._patterns[SecretType.PASSWORD] = (
            re.compile(
                r"(?i)(?:password|passwd|pwd|pass)\s*[=:]\s*[\"']([^\"'\s]{4,})[\"']",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

        # Basic Auth (base64 encoded user:pass)
        self._patterns[SecretType.BASIC_AUTH] = (
            re.compile(
                r"(?i)(?:authorization:\s*basic\s+|basic\s+auth\s*[=:]\s*)([a-zA-Z0-9+/]{20,}={0,2})",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

        # RSA Private Keys
        self._patterns[SecretType.RSA_PRIVATE_KEY] = (
            re.compile(r"-----BEGIN RSA PRIVATE KEY-----", re.MULTILINE),
            Severity.CRITICAL,
        )

        # SSH Private Keys
        self._patterns[SecretType.SSH_PRIVATE_KEY] = (
            re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----", re.MULTILINE),
            Severity.CRITICAL,
        )

        # EC Private Keys
        self._patterns[SecretType.EC_PRIVATE_KEY] = (
            re.compile(r"-----BEGIN EC PRIVATE KEY-----", re.MULTILINE),
            Severity.CRITICAL,
        )

        # PGP Private Keys
        self._patterns[SecretType.PGP_PRIVATE_KEY] = (
            re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----", re.MULTILINE),
            Severity.CRITICAL,
        )

        # TLS/SSL Certificate Keys
        self._patterns[SecretType.TLS_CERTIFICATE_KEY] = (
            re.compile(r"-----BEGIN PRIVATE KEY-----", re.MULTILINE),
            Severity.CRITICAL,
        )

        # JWT Tokens (eyJ...)
        self._patterns[SecretType.JWT_TOKEN] = (
            re.compile(r"\b(eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)\b", re.MULTILINE),
            Severity.MEDIUM,
        )

        # OAuth Access Tokens
        self._patterns[SecretType.OAUTH_TOKEN] = (
            re.compile(
                r"(?i)(?:oauth[_-]?token|access[_-]?token)\s*[=:]\s*[\"']?([a-zA-Z0-9_-]{20,})[\"']?",
                re.MULTILINE,
            ),
            Severity.MEDIUM,
        )

        # Bearer Tokens
        self._patterns[SecretType.BEARER_TOKEN] = (
            re.compile(
                r"(?i)(?:authorization:\s*bearer\s+|bearer\s+token\s*[=:]\s*)([a-zA-Z0-9_-]{20,})",
                re.MULTILINE,
            ),
            Severity.MEDIUM,
        )

        # Database URLs
        self._patterns[SecretType.DATABASE_URL] = (
            re.compile(
                r"(?i)(?:postgres|mysql|mongodb|redis)://[a-zA-Z0-9_-]+:[^@\s]+@[a-zA-Z0-9.-]+",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

        # Database Connection Strings
        self._patterns[SecretType.CONNECTION_STRING] = (
            re.compile(
                r"(?i)(?:connection[_-]?string|database[_-]?url|db[_-]?url)\s*[=:]\s*[\"']([^\"']+)[\"']",
                re.MULTILINE,
            ),
            Severity.HIGH,
        )

    def detect(self, content: str) -> list[SecretDetection]:
        """
        Detect secrets in content.

        Args:
            content: Text content to scan for secrets

        Returns:
            List of SecretDetection objects (NEVER containing actual secret values)

        Example:
            >>> detector = SecretsDetector()
            >>> detections = detector.detect(code_content)
            >>> for detection in detections:
            ...     print(f"Found {detection.secret_type.value} at line {detection.line_number}")
        """
        if not content:
            return []

        detections: list[SecretDetection] = []

        # Split content into lines for line number tracking
        lines = content.split("\n")

        # Scan with all patterns
        for secret_type, (pattern, severity) in self._patterns.items():
            for match in pattern.finditer(content):
                detection = self._create_detection(
                    secret_type=secret_type,
                    severity=severity,
                    match=match,
                    content=content,
                    lines=lines,
                )
                detections.append(detection)

        # Scan with custom patterns
        for name, (pattern, severity) in self._custom_patterns.items():
            for match in pattern.finditer(content):
                # Create a custom secret type
                custom_type = SecretType.GENERIC_API_KEY  # Default fallback
                detection = self._create_detection(
                    secret_type=custom_type,
                    severity=severity,
                    match=match,
                    content=content,
                    lines=lines,
                    metadata={"custom_pattern": name},
                )
                detections.append(detection)

        # Entropy analysis for unknown secrets
        if self.enable_entropy_analysis:
            entropy_detections = self._detect_high_entropy(content, lines)
            # Filter out entropy detections that overlap with pattern detections
            entropy_detections = self._filter_overlapping_detections(entropy_detections, detections)
            detections.extend(entropy_detections)

        # Sort by line number
        detections.sort(key=lambda d: (d.line_number, d.column_start))

        if detections:
            logger.warning(
                "secrets_detected",
                count=len(detections),
                types=[d.secret_type.value for d in detections],
            )
        else:
            logger.debug("no_secrets_detected")

        return detections

    def _create_detection(
        self,
        secret_type: SecretType,
        severity: Severity,
        match: re.Match,
        content: str,
        lines: list[str],
        metadata: dict | None = None,
    ) -> SecretDetection:
        """Create a SecretDetection from a regex match"""
        # Find line number and column
        line_number, column_start = self._get_line_column(content, match.start())
        _, column_end = self._get_line_column(content, match.end())

        # Create context snippet (without the actual secret)
        context_snippet = self._create_context_snippet(lines, line_number, column_start, column_end)

        return SecretDetection(
            secret_type=secret_type,
            severity=severity,
            line_number=line_number,
            column_start=column_start,
            column_end=column_end,
            context_snippet=context_snippet,
            confidence=1.0,  # Pattern matches are high confidence
            metadata=metadata or {},
        )

    def _get_line_column(self, content: str, position: int) -> tuple[int, int]:
        """Convert absolute position to line number and column"""
        lines_before = content[:position].split("\n")
        line_number = len(lines_before)
        column = len(lines_before[-1])
        return line_number, column

    def _create_context_snippet(
        self, lines: list[str], line_number: int, column_start: int, column_end: int
    ) -> str:
        """
        Create a context snippet showing where the secret was found.

        The actual secret value is replaced with [REDACTED].
        """
        if line_number < 1 or line_number > len(lines):
            return ""

        line = lines[line_number - 1]

        # Replace the secret with [REDACTED]
        before = line[:column_start]
        after = line[column_end:]
        redacted_line = before + "[REDACTED]" + after

        # Truncate if too long
        if len(redacted_line) > self.max_context_chars:
            # Try to center around the redaction
            start = max(0, column_start - self.max_context_chars // 2)
            end = min(len(redacted_line), start + self.max_context_chars)
            redacted_line = redacted_line[start:end]
            if start > 0:
                redacted_line = "..." + redacted_line
            if end < len(line):
                redacted_line = redacted_line + "..."

        return redacted_line

    def _detect_high_entropy(self, content: str, lines: list[str]) -> list[SecretDetection]:
        """
        Detect high-entropy strings that might be secrets.

        Uses Shannon entropy to identify random-looking strings.
        """
        detections = []

        # Find strings (quoted or in assignments)
        string_pattern = re.compile(
            r'(?:["\'])([a-zA-Z0-9_\-+=\/]{' + str(self.min_entropy_length) + r',})["\']',
            re.MULTILINE,
        )

        for match in string_pattern.finditer(content):
            string_value = match.group(1)

            # Calculate entropy
            entropy = self._calculate_entropy(string_value)

            if entropy >= self.entropy_threshold:
                line_number, column_start = self._get_line_column(content, match.start())
                _, column_end = self._get_line_column(content, match.end())

                context_snippet = self._create_context_snippet(
                    lines, line_number, column_start, column_end
                )

                # Confidence based on entropy (higher entropy = higher confidence)
                confidence = min(1.0, (entropy - self.entropy_threshold) / 2.0 + 0.5)

                detections.append(
                    SecretDetection(
                        secret_type=SecretType.HIGH_ENTROPY_STRING,
                        severity=Severity.LOW,
                        line_number=line_number,
                        column_start=column_start,
                        column_end=column_end,
                        context_snippet=context_snippet,
                        confidence=confidence,
                        metadata={"entropy": round(entropy, 2), "length": len(string_value)},
                    )
                )

        return detections

    def _calculate_entropy(self, string: str) -> float:
        """
        Calculate Shannon entropy of a string.

        Higher entropy indicates more randomness (potential secret).

        Args:
            string: Input string

        Returns:
            Entropy value (typically 0-8 for base64/hex strings)
        """
        if not string:
            return 0.0

        # Count character frequencies
        char_counts = Counter(string)
        length = len(string)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _filter_overlapping_detections(
        self,
        entropy_detections: list[SecretDetection],
        pattern_detections: list[SecretDetection],
    ) -> list[SecretDetection]:
        """
        Filter out entropy detections that overlap with pattern detections.

        Pattern detections have higher confidence, so we prefer them.
        """
        filtered = []

        for entropy_detection in entropy_detections:
            overlaps = False

            for pattern_detection in pattern_detections:
                # Check if they're on the same line with overlapping columns
                if entropy_detection.line_number == pattern_detection.line_number:
                    # Check for column overlap
                    if not (
                        entropy_detection.column_end < pattern_detection.column_start
                        or entropy_detection.column_start > pattern_detection.column_end
                    ):
                        overlaps = True
                        break

            if not overlaps:
                filtered.append(entropy_detection)

        return filtered

    def add_custom_pattern(self, name: str, pattern: str, severity: str):
        """
        Add a custom secret pattern.

        Args:
            name: Name for this pattern (e.g., "company_api_key")
            pattern: Regex pattern string
            severity: "critical", "high", "medium", or "low"

        Example:
            >>> detector = SecretsDetector()
            >>> detector.add_custom_pattern(
            ...     name="acme_api_key",
            ...     pattern=r"acme_[a-zA-Z0-9]{32}",
            ...     severity="high"
            ... )
        """
        try:
            compiled_pattern = re.compile(pattern, re.MULTILINE)
            severity_enum = Severity[severity.upper()]

            self._custom_patterns[name] = (compiled_pattern, severity_enum)

            logger.info(
                "custom_pattern_added",
                name=name,
                severity=severity,
            )

        except re.error as e:
            logger.error("invalid_regex_pattern", name=name, error=str(e))
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e
        except KeyError as e:
            logger.error("invalid_severity", severity=severity)
            raise ValueError(
                f"Invalid severity '{severity}'. Must be: critical, high, medium, low"
            ) from e

    def remove_custom_pattern(self, name: str) -> bool:
        """
        Remove a custom pattern.

        Args:
            name: Name of pattern to remove

        Returns:
            True if removed, False if not found
        """
        if name in self._custom_patterns:
            del self._custom_patterns[name]
            logger.info("custom_pattern_removed", name=name)
            return True

        logger.warning("custom_pattern_not_found", name=name)
        return False

    def get_statistics(self) -> dict:
        """
        Get detector statistics.

        Returns:
            Dictionary with pattern counts and configuration
        """
        return {
            "builtin_patterns": len(self._patterns),
            "custom_patterns": len(self._custom_patterns),
            "total_patterns": len(self._patterns) + len(self._custom_patterns),
            "entropy_analysis_enabled": self.enable_entropy_analysis,
            "entropy_threshold": self.entropy_threshold,
            "min_entropy_length": self.min_entropy_length,
        }


# Convenience function for quick detection
def detect_secrets(content: str, **kwargs) -> list[SecretDetection]:
    """
    Convenience function to detect secrets without creating a detector instance.

    Args:
        content: Text content to scan
        **kwargs: Additional arguments for SecretsDetector

    Returns:
        List of SecretDetection objects

    Example:
        >>> detections = detect_secrets(code_content)
        >>> if detections:
        ...     print(f"Found {len(detections)} secrets!")
    """
    detector = SecretsDetector(**kwargs)
    return detector.detect(content)


# Example usage
if __name__ == "__main__":
    # Example 1: Basic detection
    sample_code = """
    # Configuration file
    ANTHROPIC_API_KEY = "sk-ant-api03-abc123xyz789..."
    OPENAI_API_KEY = "sk-proj-abc123xyz789..."
    AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"

    password = "my_secret_password123"

    # Database connection
    DATABASE_URL = "postgres://user:password@localhost:5432/db"
    """

    detector = SecretsDetector()
    detections = detector.detect(sample_code)

    print(f"Found {len(detections)} secrets:")
    for detection in detections:
        print(f"  - {detection.secret_type.value}")
        print(f"    Severity: {detection.severity.value}")
        print(f"    Location: Line {detection.line_number}, Col {detection.column_start}")
        print(f"    Context: {detection.context_snippet}")
        print()

    # Example 2: Custom pattern
    detector.add_custom_pattern(
        name="acme_api_key", pattern=r"acme_[a-zA-Z0-9]{32}", severity="high"
    )

    # Example 3: Statistics
    print("Detector statistics:", detector.get_statistics())
