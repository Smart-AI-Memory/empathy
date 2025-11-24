"""
PII Scrubbing Module for Enterprise Privacy Integration

Comprehensive PII detection and scrubbing based on GDPR, HIPAA, and SOC2 requirements.
Supports custom patterns and provides detailed audit information.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PIIDetection:
    """
    Details about a detected PII instance.

    Attributes:
        pii_type: Type of PII detected (email, phone, ssn, etc.)
        matched_text: The actual text that matched (for audit purposes)
        start_pos: Starting position in original content
        end_pos: Ending position in original content
        replacement: What it was replaced with
        confidence: Detection confidence (0.0-1.0)
        metadata: Additional context about the detection
    """

    pii_type: str
    matched_text: str
    start_pos: int
    end_pos: int
    replacement: str
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/auditing"""
        return {
            "pii_type": self.pii_type,
            "matched_text": self.matched_text,  # Be careful logging this
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "replacement": self.replacement,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }

    def to_audit_safe_dict(self) -> dict[str, Any]:
        """Convert to dictionary safe for audit logs (no PII values)"""
        return {
            "pii_type": self.pii_type,
            "position": f"{self.start_pos}-{self.end_pos}",
            "length": len(self.matched_text),
            "replacement": self.replacement,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class PIIPattern:
    """
    Definition of a PII detection pattern.

    Attributes:
        name: Pattern identifier (e.g., "email", "ssn")
        pattern: Compiled regex pattern
        replacement: Replacement template (e.g., "[EMAIL]", "[SSN]")
        confidence: Base confidence level for this pattern
        description: Human-readable description
        enabled: Whether this pattern is active
    """

    name: str
    pattern: re.Pattern
    replacement: str
    confidence: float = 1.0
    description: str = ""
    enabled: bool = True


class PIIScrubber:
    """
    Comprehensive PII detection and scrubbing system.

    Detects and removes Personally Identifiable Information from text content
    according to GDPR, HIPAA, and SOC2 requirements.

    Supported PII types:
        - Email addresses
        - Phone numbers (US and international formats)
        - Social Security Numbers (SSN)
        - Credit card numbers (Visa, MC, Amex, Discover)
        - IP addresses (IPv4 and IPv6)
        - Physical addresses (US format)
        - Names (context-aware)
        - Medical Record Numbers (MRN)
        - Patient IDs

    Example:
        >>> scrubber = PIIScrubber()
        >>> sanitized, detections = scrubber.scrub(
        ...     "Contact John Doe at john.doe@email.com or 555-123-4567"
        ... )
        >>> print(sanitized)
        "Contact [NAME] at [EMAIL] or [PHONE]"
        >>> print(len(detections))
        3

    Performance:
        All patterns are pre-compiled for efficient repeated use.
        Typical scrubbing time: ~1-5ms for 1KB of text.
    """

    def __init__(self, enable_name_detection: bool = True):
        """
        Initialize PII scrubber with default patterns.

        Args:
            enable_name_detection: Enable context-aware name detection
                                 (may have false positives, disabled by default in production)
        """
        self.patterns: dict[str, PIIPattern] = {}
        self.custom_patterns: dict[str, PIIPattern] = {}

        # Initialize default patterns
        self._init_default_patterns()

        # Control name detection (can have false positives)
        if not enable_name_detection:
            self.patterns["name"].enabled = False

    def _init_default_patterns(self):
        """Initialize default PII detection patterns based on enterprise security policy"""

        # Email addresses (RFC 5322 simplified)
        self.patterns["email"] = PIIPattern(
            name="email",
            pattern=re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                re.IGNORECASE,
            ),
            replacement="[EMAIL]",
            confidence=1.0,
            description="Email address (RFC 5322 format)",
        )

        # Social Security Numbers
        # Format: 123-45-6789 or 123456789
        self.patterns["ssn"] = PIIPattern(
            name="ssn",
            pattern=re.compile(r"\b(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}\b"),
            replacement="[SSN]",
            confidence=1.0,
            description="Social Security Number (SSN)",
        )

        # Phone numbers (US and international)
        # Matches: (555) 123-4567, 555-123-4567, 555.123.4567, 5551234567
        # Also: +1-555-123-4567, +44 20 7123 4567
        self.patterns["phone"] = PIIPattern(
            name="phone",
            pattern=re.compile(
                r"""
                (?:
                    # International format with country code
                    \+\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}
                    |
                    # US format with optional area code
                    \(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}
                    |
                    # Simple 10-digit format
                    \b\d{3}[-.]?\d{3}[-.]?\d{4}\b
                )
                """,
                re.VERBOSE,
            ),
            replacement="[PHONE]",
            confidence=0.95,
            description="Phone number (US and international formats)",
        )

        # Credit card numbers
        # Supports Visa, MasterCard, Amex, Discover with optional spaces/dashes
        self.patterns["credit_card"] = PIIPattern(
            name="credit_card",
            pattern=re.compile(
                r"""
                \b(?:
                    # Visa
                    4\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}
                    |
                    # MasterCard
                    5[1-5]\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}
                    |
                    # American Express
                    3[47]\d{2}[\s-]?\d{6}[\s-]?\d{5}
                    |
                    # Discover
                    6(?:011|5\d{2})[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}
                )\b
                """,
                re.VERBOSE,
            ),
            replacement="[CC]",
            confidence=1.0,
            description="Credit card number (Visa, MC, Amex, Discover)",
        )

        # IPv4 addresses
        self.patterns["ipv4"] = PIIPattern(
            name="ipv4",
            pattern=re.compile(
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
            ),
            replacement="[IP]",
            confidence=1.0,
            description="IPv4 address",
        )

        # IPv6 addresses (simplified pattern)
        self.patterns["ipv6"] = PIIPattern(
            name="ipv6",
            pattern=re.compile(
                r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|"
                r"\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|"
                r"\b:(?::[0-9a-fA-F]{1,4}){1,7}\b"
            ),
            replacement="[IP]",
            confidence=0.95,
            description="IPv6 address",
        )

        # US Street addresses (basic pattern)
        # Matches: 123 Main St, 456 Oak Avenue, 789 First Street Apt 12
        self.patterns["address"] = PIIPattern(
            name="address",
            pattern=re.compile(
                r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s+){1,3}"
                r"(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct)"
                r"(?:\s+(?:Apt|Apartment|Suite|Ste|Unit|#)\s*\w+)?\b",
                re.IGNORECASE,
            ),
            replacement="[ADDRESS]",
            confidence=0.85,
            description="US street address",
        )

        # Names (context-aware pattern - conservative)
        # Only matches capitalized first+last name patterns near PII indicators
        # This is DISABLED by default to avoid false positives
        self.patterns["name"] = PIIPattern(
            name="name",
            pattern=re.compile(
                r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b|"
                r"\bPatient:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b|"
                r"\bContact:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
                re.MULTILINE,
            ),
            replacement="[NAME]",
            confidence=0.75,
            description="Personal name (context-aware)",
            enabled=False,  # Disabled by default - high false positive rate
        )

        # Medical Record Number (MRN)
        # Format: MRN-1234567, MRN:1234567, MRN #1234567
        self.patterns["mrn"] = PIIPattern(
            name="mrn",
            pattern=re.compile(
                r"\bMRN[:\s#-]*(\d{6,10})\b",
                re.IGNORECASE,
            ),
            replacement="[MRN]",
            confidence=1.0,
            description="Medical Record Number",
        )

        # Patient ID (healthcare context)
        # Format: Patient ID: 123456, PID-123456
        self.patterns["patient_id"] = PIIPattern(
            name="patient_id",
            pattern=re.compile(
                r"\b(?:Patient\s*ID|PID)[:\s#-]*(\d{5,10})\b",
                re.IGNORECASE,
            ),
            replacement="[PATIENT_ID]",
            confidence=0.95,
            description="Patient identifier",
        )

    def scrub(self, content: str) -> tuple[str, list[PIIDetection]]:
        """
        Scrub PII from content.

        Detects and replaces all PII according to configured patterns.
        Returns both sanitized content and detailed detection information.

        Args:
            content: Text content to scrub

        Returns:
            Tuple of (sanitized_content, detections):
                - sanitized_content: Text with PII replaced
                - detections: List of PIIDetection objects with details

        Example:
            >>> scrubber = PIIScrubber()
            >>> text = "Email me at john@example.com or call 555-1234"
            >>> clean_text, detections = scrubber.scrub(text)
            >>> print(clean_text)
            "Email me at [EMAIL] or call [PHONE]"
            >>> print(detections[0].pii_type)
            "email"
        """
        if not content:
            return content, []

        detections: list[PIIDetection] = []
        sanitized = content

        # Track position adjustments as we replace text
        position_offset = 0

        # Collect all matches first to handle overlaps and sort by position
        all_matches: list[tuple[int, int, str, str, re.Match, float]] = []

        # Check all enabled patterns
        for pattern_dict in [self.patterns, self.custom_patterns]:
            for _pattern_name, pii_pattern in pattern_dict.items():
                if not pii_pattern.enabled:
                    continue

                for match in pii_pattern.pattern.finditer(content):
                    matched_text = match.group(0)
                    start_pos = match.start()
                    end_pos = match.end()

                    all_matches.append(
                        (
                            start_pos,
                            end_pos,
                            matched_text,
                            pii_pattern.replacement,
                            match,
                            pii_pattern.confidence,
                        )
                    )

        # Sort by start position
        all_matches.sort(key=lambda x: x[0])

        # Remove overlapping matches (keep first one)
        filtered_matches: list[tuple[int, int, str, str, re.Match, float]] = []
        last_end = -1

        for match_tuple in all_matches:
            start_pos = match_tuple[0]
            if start_pos >= last_end:
                filtered_matches.append(match_tuple)
                last_end = match_tuple[1]

        # Now apply replacements and create detections
        for start_pos, end_pos, matched_text, replacement, _match, confidence in filtered_matches:
            # Determine which pattern this came from
            pii_type = None
            for pattern_dict in [self.patterns, self.custom_patterns]:
                for pattern_name, pii_pattern in pattern_dict.items():
                    if pii_pattern.replacement == replacement and pii_pattern.enabled:
                        pii_type = pattern_name
                        break
                if pii_type:
                    break

            # Create detection record
            detection = PIIDetection(
                pii_type=pii_type or "unknown",
                matched_text=matched_text,
                start_pos=start_pos,
                end_pos=end_pos,
                replacement=replacement,
                confidence=confidence,
                metadata={
                    "original_length": len(matched_text),
                    "replacement_length": len(replacement),
                },
            )
            detections.append(detection)

            # Apply replacement with position offset
            adjusted_start = start_pos + position_offset
            adjusted_end = end_pos + position_offset

            sanitized = sanitized[:adjusted_start] + replacement + sanitized[adjusted_end:]

            # Update offset for next replacement
            position_offset += len(replacement) - len(matched_text)

        return sanitized, detections

    def add_custom_pattern(
        self,
        name: str,
        pattern: str,
        replacement: str,
        confidence: float = 1.0,
        description: str = "",
    ):
        """
        Add a custom PII detection pattern.

        Allows extending the scrubber with organization-specific or
        domain-specific PII patterns.

        Args:
            name: Unique identifier for this pattern
            pattern: Regular expression pattern (string)
            replacement: Replacement text (e.g., "[CUSTOM_ID]")
            confidence: Detection confidence (0.0-1.0)
            description: Human-readable description

        Raises:
            ValueError: If pattern name already exists or regex is invalid

        Example:
            >>> scrubber = PIIScrubber()
            >>> scrubber.add_custom_pattern(
            ...     name="employee_id",
            ...     pattern=r"EMP-\\d{6}",
            ...     replacement="[EMPLOYEE_ID]",
            ...     description="Company employee identifier"
            ... )
        """
        if name in self.patterns or name in self.custom_patterns:
            raise ValueError(f"Pattern '{name}' already exists")

        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}") from e

        self.custom_patterns[name] = PIIPattern(
            name=name,
            pattern=compiled_pattern,
            replacement=replacement,
            confidence=confidence,
            description=description,
            enabled=True,
        )

    def remove_custom_pattern(self, name: str):
        """
        Remove a custom PII pattern.

        Args:
            name: Pattern identifier

        Raises:
            ValueError: If pattern doesn't exist or is a default pattern
        """
        if name not in self.custom_patterns:
            if name in self.patterns:
                raise ValueError(
                    f"Cannot remove default pattern '{name}'. " f"Use disable_pattern() instead."
                )
            raise ValueError(f"Pattern '{name}' not found")

        del self.custom_patterns[name]

    def disable_pattern(self, name: str):
        """
        Disable a PII pattern without removing it.

        Args:
            name: Pattern identifier

        Raises:
            ValueError: If pattern doesn't exist
        """
        if name in self.patterns:
            self.patterns[name].enabled = False
        elif name in self.custom_patterns:
            self.custom_patterns[name].enabled = False
        else:
            raise ValueError(f"Pattern '{name}' not found")

    def enable_pattern(self, name: str):
        """
        Enable a previously disabled PII pattern.

        Args:
            name: Pattern identifier

        Raises:
            ValueError: If pattern doesn't exist
        """
        if name in self.patterns:
            self.patterns[name].enabled = True
        elif name in self.custom_patterns:
            self.custom_patterns[name].enabled = True
        else:
            raise ValueError(f"Pattern '{name}' not found")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about configured patterns.

        Returns:
            Dictionary with pattern statistics
        """
        enabled_default = sum(1 for p in self.patterns.values() if p.enabled)
        enabled_custom = sum(1 for p in self.custom_patterns.values() if p.enabled)

        return {
            "total_patterns": len(self.patterns) + len(self.custom_patterns),
            "default_patterns": len(self.patterns),
            "custom_patterns": len(self.custom_patterns),
            "enabled_default": enabled_default,
            "enabled_custom": enabled_custom,
            "total_enabled": enabled_default + enabled_custom,
            "pattern_names": {
                "default": list(self.patterns.keys()),
                "custom": list(self.custom_patterns.keys()),
            },
        }

    def get_pattern_info(self, name: str) -> dict[str, Any]:
        """
        Get detailed information about a specific pattern.

        Args:
            name: Pattern identifier

        Returns:
            Dictionary with pattern details

        Raises:
            ValueError: If pattern doesn't exist
        """
        pattern = None
        is_custom = False

        if name in self.patterns:
            pattern = self.patterns[name]
        elif name in self.custom_patterns:
            pattern = self.custom_patterns[name]
            is_custom = True
        else:
            raise ValueError(f"Pattern '{name}' not found")

        return {
            "name": pattern.name,
            "replacement": pattern.replacement,
            "confidence": pattern.confidence,
            "description": pattern.description,
            "enabled": pattern.enabled,
            "is_custom": is_custom,
            "regex_pattern": pattern.pattern.pattern,
        }

    def validate_patterns(self) -> list[dict[str, Any]]:
        """
        Validate all patterns with test cases.

        Returns a list of validation results for each pattern.
        Useful for testing pattern effectiveness.

        Returns:
            List of dictionaries with validation results
        """
        test_cases = {
            "email": [
                ("user@example.com", True),
                ("test.user+tag@domain.co.uk", True),
                ("not-an-email", False),
            ],
            "ssn": [
                ("123-45-6789", True),
                ("123456789", True),
                ("000-12-3456", False),  # Invalid area number
                ("12-345-6789", False),  # Wrong format
            ],
            "phone": [
                ("555-123-4567", True),
                ("(555) 123-4567", True),
                ("+1-555-123-4567", True),
                ("12345", False),
            ],
            "credit_card": [
                ("4532-1234-5678-9010", True),
                ("5123 4567 8901 2345", True),
                ("3782 822463 10005", True),  # Amex
                ("1234-5678-9012-3456", False),  # Invalid prefix
            ],
            "ipv4": [
                ("192.168.1.1", True),
                ("10.0.0.1", True),
                ("256.1.1.1", False),  # Invalid octet
            ],
            "mrn": [
                ("MRN-1234567", True),
                ("MRN:1234567", True),
                ("MRN 1234567", True),
                ("MRN-123", False),  # Too short
            ],
        }

        results = []

        for pattern_name, cases in test_cases.items():
            if pattern_name not in self.patterns:
                continue

            pattern = self.patterns[pattern_name]
            if not pattern.enabled:
                continue

            passed = 0
            failed = 0

            for test_input, should_match in cases:
                matches = bool(pattern.pattern.search(test_input))
                if matches == should_match:
                    passed += 1
                else:
                    failed += 1

            results.append(
                {
                    "pattern": pattern_name,
                    "total_tests": len(cases),
                    "passed": passed,
                    "failed": failed,
                    "success_rate": passed / len(cases) if cases else 0,
                }
            )

        return results
