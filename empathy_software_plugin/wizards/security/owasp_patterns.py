"""
OWASP Top 10 Pattern Detection

Detects security vulnerabilities based on OWASP Top 10.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class OWASPCategory(Enum):
    """OWASP Top 10 categories"""
    INJECTION = "injection"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA = "sensitive_data_exposure"
    XML_EXTERNAL = "xml_external_entities"
    BROKEN_ACCESS = "broken_access_control"
    SECURITY_MISCONFIG = "security_misconfiguration"
    XSS = "cross_site_scripting"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    COMPONENTS_VULNS = "components_with_known_vulnerabilities"
    INSUFFICIENT_LOGGING = "insufficient_logging"


@dataclass
class SecurityPattern:
    """Security vulnerability pattern"""
    category: OWASPCategory
    name: str
    patterns: List[str]  # Regex patterns
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    example_vulnerable: str
    example_safe: str


class OWASPPatternDetector:
    """
    Detects OWASP Top 10 vulnerability patterns in code.
    """

    def __init__(self):
        self.patterns = self._build_pattern_library()

    def _build_pattern_library(self) -> List[SecurityPattern]:
        """Build library of OWASP patterns"""
        return [
            # SQL Injection
            SecurityPattern(
                category=OWASPCategory.INJECTION,
                name="SQL Injection",
                patterns=[
                    r"execute\s*\(\s*f['\"].*?{.*?}.*?['\"]",  # Python f-string in SQL
                    r"execute\s*\(\s*['\"].*?\+.*?['\"]",  # String concatenation
                    r"query\s*\(\s*['\"].*?\+.*?['\"]",
                    r"SELECT\s+.*?\+",  # SQL with concatenation
                    r"cursor\.execute.*?%.*?%",  # Old-style formatting
                ],
                severity="CRITICAL",
                description="SQL query built with string concatenation - vulnerable to injection",
                example_vulnerable="cursor.execute(f\"SELECT * FROM users WHERE name='{username}'\")",
                example_safe="cursor.execute('SELECT * FROM users WHERE name = ?', (username,))"
            ),

            # Command Injection
            SecurityPattern(
                category=OWASPCategory.INJECTION,
                name="Command Injection",
                patterns=[
                    r"os\.system\s*\(.*?\+",  # os.system with concatenation
                    r"subprocess\.\w+\(.*?shell\s*=\s*True",  # shell=True is dangerous
                    r"eval\s*\(",  # eval() is very dangerous
                    r"exec\s*\(",  # exec() is very dangerous
                ],
                severity="CRITICAL",
                description="Command execution with unsanitized input",
                example_vulnerable="os.system('rm ' + user_file)",
                example_safe="subprocess.run(['rm', user_file])"
            ),

            # XSS (Cross-Site Scripting)
            SecurityPattern(
                category=OWASPCategory.XSS,
                name="Cross-Site Scripting",
                patterns=[
                    r"innerHTML\s*=",  # Direct innerHTML assignment
                    r"document\.write\s*\(",  # document.write with user input
                    r"\.html\s*\(.*?\+",  # jQuery .html() with concatenation
                    r"dangerouslySetInnerHTML",  # React dangerous prop
                ],
                severity="HIGH",
                description="User input rendered without sanitization",
                example_vulnerable="element.innerHTML = userInput",
                example_safe="element.textContent = userInput"
            ),

            # Hardcoded Credentials
            SecurityPattern(
                category=OWASPCategory.BROKEN_AUTH,
                name="Hardcoded Credentials",
                patterns=[
                    r"password\s*=\s*['\"][^'\"]+['\"]",  # password = "secret"
                    r"api_key\s*=\s*['\"][^'\"]+['\"]",
                    r"secret\s*=\s*['\"][^'\"]+['\"]",
                    r"token\s*=\s*['\"][A-Za-z0-9]{20,}['\"]",
                ],
                severity="CRITICAL",
                description="Hardcoded credentials in source code",
                example_vulnerable="password = 'admin123'",
                example_safe="password = os.environ.get('DB_PASSWORD')"
            ),

            # Weak Cryptography
            SecurityPattern(
                category=OWASPCategory.SENSITIVE_DATA,
                name="Weak Cryptography",
                patterns=[
                    r"MD5\(",  # MD5 is broken
                    r"SHA1\(",  # SHA1 is weak
                    r"DES\(",  # DES is obsolete
                    r"Random\(",  # Not cryptographically secure
                ],
                severity="HIGH",
                description="Weak or broken cryptographic algorithm",
                example_vulnerable="hashlib.md5(password)",
                example_safe="hashlib.sha256(password)"
            ),

            # Missing Authentication
            SecurityPattern(
                category=OWASPCategory.BROKEN_AUTH,
                name="Missing Authentication Check",
                patterns=[
                    r"@app\.route.*?\n(?!.*@.*require.*auth).*?def",  # Flask route without auth
                    r"router\.\w+\(.*?\).*?\n(?!.*auth).*?function",  # Express route without auth
                ],
                severity="CRITICAL",
                description="Endpoint lacks authentication check",
                example_vulnerable="@app.route('/admin')\\ndef admin_panel():",
                example_safe="@app.route('/admin')\\n@require_auth\\ndef admin_panel():"
            ),

            # Insecure Deserialization
            SecurityPattern(
                category=OWASPCategory.INSECURE_DESERIALIZATION,
                name="Insecure Deserialization",
                patterns=[
                    r"pickle\.loads?\(",  # Python pickle is unsafe
                    r"yaml\.load\((?!.*Loader\s*=)",  # PyYAML unsafe load
                    r"eval\(",  # Deserializing code
                ],
                severity="CRITICAL",
                description="Deserializing untrusted data",
                example_vulnerable="pickle.loads(user_data)",
                example_safe="json.loads(user_data)"
            ),

            # Sensitive Data Logging
            SecurityPattern(
                category=OWASPCategory.SENSITIVE_DATA,
                name="Sensitive Data in Logs",
                patterns=[
                    r"log.*password",
                    r"print.*password",
                    r"console\.log.*password",
                    r"log.*credit.*card",
                ],
                severity="HIGH",
                description="Logging sensitive data",
                example_vulnerable="logger.info(f'Login: {username}:{password}')",
                example_safe="logger.info(f'Login: {username}:***')"
            ),

            # Path Traversal
            SecurityPattern(
                category=OWASPCategory.BROKEN_ACCESS,
                name="Path Traversal",
                patterns=[
                    r"open\s*\(.*?user.*?\)",  # open() with user input
                    r"file_path\s*=.*?\+",  # Path concatenation
                ],
                severity="HIGH",
                description="File path built from user input",
                example_vulnerable="open('/uploads/' + user_file)",
                example_safe="open(os.path.join(UPLOAD_DIR, secure_filename(user_file)))"
            ),

            # CSRF Missing Protection
            SecurityPattern(
                category=OWASPCategory.BROKEN_ACCESS,
                name="Missing CSRF Protection",
                patterns=[
                    r"@app\.route.*?methods\s*=\s*\[.*?POST.*?\].*?\n(?!.*csrf).*?def",
                ],
                severity="MEDIUM",
                description="POST endpoint without CSRF protection",
                example_vulnerable="@app.route('/transfer', methods=['POST'])\\ndef transfer():",
                example_safe="@app.route('/transfer', methods=['POST'])\\n@csrf_protect\\ndef transfer():"
            )
        ]

    def detect_vulnerabilities(
        self,
        code: str,
        file_path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Detect vulnerabilities in code.

        Args:
            code: Source code to analyze
            file_path: Path to file (for context)

        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []

        for pattern_def in self.patterns:
            for regex_pattern in pattern_def.patterns:
                matches = re.finditer(regex_pattern, code, re.MULTILINE | re.IGNORECASE)

                for match in matches:
                    # Find line number
                    line_number = code[:match.start()].count('\n') + 1

                    vulnerabilities.append({
                        "category": pattern_def.category.value,
                        "name": pattern_def.name,
                        "severity": pattern_def.severity,
                        "file_path": file_path,
                        "line_number": line_number,
                        "matched_code": match.group(0),
                        "description": pattern_def.description,
                        "example_safe": pattern_def.example_safe
                    })

        return vulnerabilities

    def get_pattern_by_category(
        self,
        category: OWASPCategory
    ) -> List[SecurityPattern]:
        """Get all patterns for a category"""
        return [p for p in self.patterns if p.category == category]
