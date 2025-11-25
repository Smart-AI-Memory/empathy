"""
Comprehensive tests for all 16 Coach Wizards

Level 4 Anticipatory Empathy implementation using the Empathy Framework.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from datetime import datetime

import pytest

from coach_wizards import (
    AccessibilityWizard,
    APIWizard,
    CICDWizard,
    ComplianceWizard,
    DatabaseWizard,
    DebuggingWizard,
    DocumentationWizard,
    LocalizationWizard,
    MigrationWizard,
    MonitoringWizard,
    ObservabilityWizard,
    PerformanceWizard,
    RefactoringWizard,
    ScalingWizard,
    SecurityWizard,
    TestingWizard,
)
from coach_wizards.base_wizard import BaseCoachWizard, WizardIssue, WizardPrediction

# All 16 Coach Wizards for parametrized testing
ALL_WIZARDS = [
    AccessibilityWizard,
    APIWizard,
    CICDWizard,
    ComplianceWizard,
    DatabaseWizard,
    DebuggingWizard,
    DocumentationWizard,
    LocalizationWizard,
    MigrationWizard,
    MonitoringWizard,
    ObservabilityWizard,
    PerformanceWizard,
    RefactoringWizard,
    ScalingWizard,
    SecurityWizard,
    TestingWizard,
]

# Wizard specifications: (WizardClass, name, category, supported_languages)
WIZARD_SPECS = [
    (
        AccessibilityWizard,
        "AccessibilityWizard",
        "Accessibility",
        ["html", "jsx", "tsx", "vue", "svelte"],
    ),
    (APIWizard, "APIWizard", "API", ["python", "javascript", "typescript", "java", "go", "rust"]),
    (CICDWizard, "CICDWizard", "DevOps", ["yaml", "groovy", "python", "bash"]),
    (
        ComplianceWizard,
        "ComplianceWizard",
        "Compliance",
        ["python", "javascript", "typescript", "java", "go"],
    ),
    (
        DatabaseWizard,
        "DatabaseWizard",
        "Database",
        ["sql", "python", "javascript", "typescript", "java", "go"],
    ),
    (
        DebuggingWizard,
        "DebuggingWizard",
        "Debugging",
        ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
    ),
    (
        DocumentationWizard,
        "DocumentationWizard",
        "Documentation",
        ["python", "javascript", "typescript", "java", "go", "rust", "markdown"],
    ),
    (
        LocalizationWizard,
        "LocalizationWizard",
        "Localization",
        ["python", "javascript", "typescript", "java", "go", "html", "jsx", "tsx"],
    ),
    (
        MigrationWizard,
        "MigrationWizard",
        "Migration",
        ["python", "javascript", "typescript", "java", "go", "rust"],
    ),
    (
        MonitoringWizard,
        "MonitoringWizard",
        "Monitoring",
        ["python", "javascript", "typescript", "java", "go", "yaml"],
    ),
    (
        ObservabilityWizard,
        "ObservabilityWizard",
        "Observability",
        ["python", "javascript", "typescript", "java", "go", "rust"],
    ),
    (
        PerformanceWizard,
        "PerformanceWizard",
        "Performance",
        ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
    ),
    (
        RefactoringWizard,
        "RefactoringWizard",
        "Code Quality",
        ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
    ),
    (
        ScalingWizard,
        "ScalingWizard",
        "Scalability",
        ["python", "javascript", "typescript", "java", "go", "rust"],
    ),
    (
        SecurityWizard,
        "SecurityWizard",
        "Security",
        ["python", "javascript", "typescript", "java", "go", "rust"],
    ),
    (
        TestingWizard,
        "TestingWizard",
        "Testing",
        ["python", "javascript", "typescript", "java", "go", "rust"],
    ),
]


class TestAccessibilityWizard:
    """Tests for AccessibilityWizard"""

    def test_initialization(self):
        """Test AccessibilityWizard initialization"""
        wizard = AccessibilityWizard()
        assert wizard.name == "AccessibilityWizard"
        assert wizard.category == "Accessibility"
        assert wizard.languages == ["html", "jsx", "tsx", "vue", "svelte"]

    def test_analyze_code(self):
        """Test AccessibilityWizard analyze_code method"""
        wizard = AccessibilityWizard()
        code = '<img src="image.png">'
        issues = wizard.analyze_code(code, "test.html", "html")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test AccessibilityWizard predict_future_issues method"""
        wizard = AccessibilityWizard()
        code = '<img src="image.png">'
        context = {"team_size": 5, "deployment_frequency": "daily"}
        predictions = wizard.predict_future_issues(code, "test.html", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test AccessibilityWizard suggest_fixes method"""
        wizard = AccessibilityWizard()
        issue = WizardIssue(
            severity="warning",
            message="Missing alt text",
            file_path="test.html",
            line_number=1,
            code_snippet='<img src="image.png">',
            fix_suggestion="Add alt attribute",
            category="Accessibility",
            confidence=0.95,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestAPIWizard:
    """Tests for APIWizard"""

    def test_initialization(self):
        """Test APIWizard initialization"""
        wizard = APIWizard()
        assert wizard.name == "APIWizard"
        assert wizard.category == "API"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "rust"]

    def test_analyze_code(self):
        """Test APIWizard analyze_code method"""
        wizard = APIWizard()
        code = "def get_user(user_id):\n    return db.query(user_id)"
        issues = wizard.analyze_code(code, "api.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test APIWizard predict_future_issues method"""
        wizard = APIWizard()
        code = "def get_user(user_id):\n    return db.query(user_id)"
        context = {"api_version": "1.0", "clients": 10}
        predictions = wizard.predict_future_issues(code, "api.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test APIWizard suggest_fixes method"""
        wizard = APIWizard()
        issue = WizardIssue(
            severity="error",
            message="Missing input validation",
            file_path="api.py",
            line_number=5,
            code_snippet="def get_user(user_id):",
            fix_suggestion="Add validation",
            category="API",
            confidence=0.92,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestCICDWizard:
    """Tests for CICDWizard"""

    def test_initialization(self):
        """Test CICDWizard initialization"""
        wizard = CICDWizard()
        assert wizard.name == "CICDWizard"
        assert wizard.category == "DevOps"
        assert wizard.languages == ["yaml", "groovy", "python", "bash"]

    def test_analyze_code(self):
        """Test CICDWizard analyze_code method"""
        wizard = CICDWizard()
        code = "pipeline { stages { stage('Test') { steps { sh 'pytest' } } } }"
        issues = wizard.analyze_code(code, "Jenkinsfile", "groovy")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test CICDWizard predict_future_issues method"""
        wizard = CICDWizard()
        code = "pipeline { stages { stage('Test') { steps { sh 'pytest' } } } }"
        context = {"pipeline_duration_minutes": 45, "failure_rate": 0.05}
        predictions = wizard.predict_future_issues(code, "Jenkinsfile", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test CICDWizard suggest_fixes method"""
        wizard = CICDWizard()
        issue = WizardIssue(
            severity="warning",
            message="Pipeline timeout risk",
            file_path="Jenkinsfile",
            line_number=10,
            code_snippet="sh 'slow_test.sh'",
            fix_suggestion="Parallelize jobs",
            category="DevOps",
            confidence=0.88,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestComplianceWizard:
    """Tests for ComplianceWizard"""

    def test_initialization(self):
        """Test ComplianceWizard initialization"""
        wizard = ComplianceWizard()
        assert wizard.name == "ComplianceWizard"
        assert wizard.category == "Compliance"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go"]

    def test_analyze_code(self):
        """Test ComplianceWizard analyze_code method"""
        wizard = ComplianceWizard()
        code = "user_data = request.args.get('pii')"
        issues = wizard.analyze_code(code, "compliance.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test ComplianceWizard predict_future_issues method"""
        wizard = ComplianceWizard()
        code = "user_data = request.args.get('pii')"
        context = {"markets": ["EU", "US"], "data_retention_days": 30}
        predictions = wizard.predict_future_issues(code, "compliance.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test ComplianceWizard suggest_fixes method"""
        wizard = ComplianceWizard()
        issue = WizardIssue(
            severity="error",
            message="GDPR violation: PII stored without consent",
            file_path="compliance.py",
            line_number=15,
            code_snippet="user_data = request.args.get('pii')",
            fix_suggestion="Add encryption and consent check",
            category="Compliance",
            confidence=0.98,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestDatabaseWizard:
    """Tests for DatabaseWizard"""

    def test_initialization(self):
        """Test DatabaseWizard initialization"""
        wizard = DatabaseWizard()
        assert wizard.name == "DatabaseWizard"
        assert wizard.category == "Database"
        assert wizard.languages == ["sql", "python", "javascript", "typescript", "java", "go"]

    def test_analyze_code(self):
        """Test DatabaseWizard analyze_code method"""
        wizard = DatabaseWizard()
        code = "SELECT * FROM users WHERE id = 1;"
        issues = wizard.analyze_code(code, "query.sql", "sql")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test DatabaseWizard predict_future_issues method"""
        wizard = DatabaseWizard()
        code = "SELECT * FROM users WHERE id = 1;"
        context = {"table_size_gb": 100, "query_frequency": "high"}
        predictions = wizard.predict_future_issues(code, "query.sql", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test DatabaseWizard suggest_fixes method"""
        wizard = DatabaseWizard()
        issue = WizardIssue(
            severity="warning",
            message="Missing index on query column",
            file_path="query.sql",
            line_number=1,
            code_snippet="SELECT * FROM users WHERE id = 1;",
            fix_suggestion="CREATE INDEX idx_users_id",
            category="Database",
            confidence=0.91,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestDebuggingWizard:
    """Tests for DebuggingWizard"""

    def test_initialization(self):
        """Test DebuggingWizard initialization"""
        wizard = DebuggingWizard()
        assert wizard.name == "DebuggingWizard"
        assert wizard.category == "Debugging"
        assert wizard.languages == [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "cpp",
        ]

    def test_analyze_code(self):
        """Test DebuggingWizard analyze_code method"""
        wizard = DebuggingWizard()
        code = "result = process(data)\nprint(result.value)"
        issues = wizard.analyze_code(code, "debug.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test DebuggingWizard predict_future_issues method"""
        wizard = DebuggingWizard()
        code = "result = process(data)\nprint(result.value)"
        context = {"error_rate": 0.02, "avg_response_time": 100}
        predictions = wizard.predict_future_issues(code, "debug.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test DebuggingWizard suggest_fixes method"""
        wizard = DebuggingWizard()
        issue = WizardIssue(
            severity="error",
            message="Potential null pointer dereference",
            file_path="debug.py",
            line_number=2,
            code_snippet="print(result.value)",
            fix_suggestion="Add null check",
            category="Debugging",
            confidence=0.89,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestDocumentationWizard:
    """Tests for DocumentationWizard"""

    def test_initialization(self):
        """Test DocumentationWizard initialization"""
        wizard = DocumentationWizard()
        assert wizard.name == "DocumentationWizard"
        assert wizard.category == "Documentation"
        assert wizard.languages == [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "markdown",
        ]

    def test_analyze_code(self):
        """Test DocumentationWizard analyze_code method"""
        wizard = DocumentationWizard()
        code = "def complex_function(a, b):\n    return a + b"
        issues = wizard.analyze_code(code, "utils.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test DocumentationWizard predict_future_issues method"""
        wizard = DocumentationWizard()
        code = "def complex_function(a, b):\n    return a + b"
        context = {"team_turnover": 0.3, "code_age_months": 12}
        predictions = wizard.predict_future_issues(code, "utils.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test DocumentationWizard suggest_fixes method"""
        wizard = DocumentationWizard()
        issue = WizardIssue(
            severity="info",
            message="Missing docstring",
            file_path="utils.py",
            line_number=1,
            code_snippet="def complex_function(a, b):",
            fix_suggestion="Add comprehensive docstring",
            category="Documentation",
            confidence=0.85,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestLocalizationWizard:
    """Tests for LocalizationWizard"""

    def test_initialization(self):
        """Test LocalizationWizard initialization"""
        wizard = LocalizationWizard()
        assert wizard.name == "LocalizationWizard"
        assert wizard.category == "Localization"
        assert wizard.languages == [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "html",
            "jsx",
            "tsx",
        ]

    def test_analyze_code(self):
        """Test LocalizationWizard analyze_code method"""
        wizard = LocalizationWizard()
        code = 'label.text = "Welcome"'
        issues = wizard.analyze_code(code, "ui.js", "javascript")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test LocalizationWizard predict_future_issues method"""
        wizard = LocalizationWizard()
        code = 'label.text = "Welcome"'
        context = {"target_languages": 5, "user_base": "global"}
        predictions = wizard.predict_future_issues(code, "ui.js", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test LocalizationWizard suggest_fixes method"""
        wizard = LocalizationWizard()
        issue = WizardIssue(
            severity="warning",
            message="Hardcoded string",
            file_path="ui.js",
            line_number=1,
            code_snippet='label.text = "Welcome"',
            fix_suggestion='Use i18n.t("welcome")',
            category="Localization",
            confidence=0.93,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestMigrationWizard:
    """Tests for MigrationWizard"""

    def test_initialization(self):
        """Test MigrationWizard initialization"""
        wizard = MigrationWizard()
        assert wizard.name == "MigrationWizard"
        assert wizard.category == "Migration"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "rust"]

    def test_analyze_code(self):
        """Test MigrationWizard analyze_code method"""
        wizard = MigrationWizard()
        code = "from old_lib import deprecated_function"
        issues = wizard.analyze_code(code, "legacy.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test MigrationWizard predict_future_issues method"""
        wizard = MigrationWizard()
        code = "from old_lib import deprecated_function"
        context = {"deprecated_version": "1.0", "support_end_date": "2025-12-01"}
        predictions = wizard.predict_future_issues(code, "legacy.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test MigrationWizard suggest_fixes method"""
        wizard = MigrationWizard()
        issue = WizardIssue(
            severity="warning",
            message="Using deprecated API",
            file_path="legacy.py",
            line_number=1,
            code_snippet="from old_lib import deprecated_function",
            fix_suggestion="Migrate to new_lib.new_function",
            category="Migration",
            confidence=0.94,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestMonitoringWizard:
    """Tests for MonitoringWizard"""

    def test_initialization(self):
        """Test MonitoringWizard initialization"""
        wizard = MonitoringWizard()
        assert wizard.name == "MonitoringWizard"
        assert wizard.category == "Monitoring"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "yaml"]

    def test_analyze_code(self):
        """Test MonitoringWizard analyze_code method"""
        wizard = MonitoringWizard()
        code = "critical_operation()"
        issues = wizard.analyze_code(code, "service.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test MonitoringWizard predict_future_issues method"""
        wizard = MonitoringWizard()
        code = "critical_operation()"
        context = {"incidents_per_month": 2, "detection_time": 15}
        predictions = wizard.predict_future_issues(code, "service.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test MonitoringWizard suggest_fixes method"""
        wizard = MonitoringWizard()
        issue = WizardIssue(
            severity="warning",
            message="No monitoring alerts",
            file_path="service.py",
            line_number=5,
            code_snippet="critical_operation()",
            fix_suggestion="Add alert rules",
            category="Monitoring",
            confidence=0.90,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestObservabilityWizard:
    """Tests for ObservabilityWizard"""

    def test_initialization(self):
        """Test ObservabilityWizard initialization"""
        wizard = ObservabilityWizard()
        assert wizard.name == "ObservabilityWizard"
        assert wizard.category == "Observability"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "rust"]

    def test_analyze_code(self):
        """Test ObservabilityWizard analyze_code method"""
        wizard = ObservabilityWizard()
        code = "result = process(data)\nreturn result"
        issues = wizard.analyze_code(code, "handler.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test ObservabilityWizard predict_future_issues method"""
        wizard = ObservabilityWizard()
        code = "result = process(data)\nreturn result"
        context = {"trace_sampling": 0.1, "log_volume": "high"}
        predictions = wizard.predict_future_issues(code, "handler.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test ObservabilityWizard suggest_fixes method"""
        wizard = ObservabilityWizard()
        issue = WizardIssue(
            severity="warning",
            message="Missing trace context",
            file_path="handler.py",
            line_number=1,
            code_snippet="result = process(data)",
            fix_suggestion="Add trace span",
            category="Observability",
            confidence=0.87,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestPerformanceWizard:
    """Tests for PerformanceWizard"""

    def test_initialization(self):
        """Test PerformanceWizard initialization"""
        wizard = PerformanceWizard()
        assert wizard.name == "PerformanceWizard"
        assert wizard.category == "Performance"
        assert wizard.languages == [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "cpp",
        ]

    def test_analyze_code(self):
        """Test PerformanceWizard analyze_code method"""
        wizard = PerformanceWizard()
        code = "for item in items:\n    db.query(item)"
        issues = wizard.analyze_code(code, "loop.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test PerformanceWizard predict_future_issues method"""
        wizard = PerformanceWizard()
        code = "for item in items:\n    db.query(item)"
        context = {"items_count_growth": 1000, "expected_users": 10000}
        predictions = wizard.predict_future_issues(code, "loop.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test PerformanceWizard suggest_fixes method"""
        wizard = PerformanceWizard()
        issue = WizardIssue(
            severity="error",
            message="N+1 query problem",
            file_path="loop.py",
            line_number=2,
            code_snippet="db.query(item)",
            fix_suggestion="Use batch query or JOIN",
            category="Performance",
            confidence=0.96,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestRefactoringWizard:
    """Tests for RefactoringWizard"""

    def test_initialization(self):
        """Test RefactoringWizard initialization"""
        wizard = RefactoringWizard()
        assert wizard.name == "RefactoringWizard"
        assert wizard.category == "Code Quality"
        assert wizard.languages == [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "cpp",
        ]

    def test_analyze_code(self):
        """Test RefactoringWizard analyze_code method"""
        wizard = RefactoringWizard()
        code = "def big_function():\n    # 500 lines of code"
        issues = wizard.analyze_code(code, "refactor.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test RefactoringWizard predict_future_issues method"""
        wizard = RefactoringWizard()
        code = "def big_function():\n    # 500 lines of code"
        context = {"code_churn": 0.3, "defect_density": 0.05}
        predictions = wizard.predict_future_issues(code, "refactor.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test RefactoringWizard suggest_fixes method"""
        wizard = RefactoringWizard()
        issue = WizardIssue(
            severity="warning",
            message="High cyclomatic complexity",
            file_path="refactor.py",
            line_number=1,
            code_snippet="def big_function():",
            fix_suggestion="Extract methods",
            category="Code Quality",
            confidence=0.91,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestScalingWizard:
    """Tests for ScalingWizard"""

    def test_initialization(self):
        """Test ScalingWizard initialization"""
        wizard = ScalingWizard()
        assert wizard.name == "ScalingWizard"
        assert wizard.category == "Scalability"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "rust"]

    def test_analyze_code(self):
        """Test ScalingWizard analyze_code method"""
        wizard = ScalingWizard()
        code = "global_state = {}\ndef process(data):\n    global_state['key'] = data"
        issues = wizard.analyze_code(code, "scale.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test ScalingWizard predict_future_issues method"""
        wizard = ScalingWizard()
        code = "global_state = {}\ndef process(data):\n    global_state['key'] = data"
        context = {"expected_load_rps": 10000, "current_capacity": 1000}
        predictions = wizard.predict_future_issues(code, "scale.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test ScalingWizard suggest_fixes method"""
        wizard = ScalingWizard()
        issue = WizardIssue(
            severity="error",
            message="Single point of failure",
            file_path="scale.py",
            line_number=2,
            code_snippet="global_state = {}",
            fix_suggestion="Distribute state across nodes",
            category="Scalability",
            confidence=0.97,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestSecurityWizard:
    """Tests for SecurityWizard"""

    def test_initialization(self):
        """Test SecurityWizard initialization"""
        wizard = SecurityWizard()
        assert wizard.name == "SecurityWizard"
        assert wizard.category == "Security"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "rust"]

    def test_analyze_code(self):
        """Test SecurityWizard analyze_code method"""
        wizard = SecurityWizard()
        code = 'query = "SELECT * FROM users WHERE id=" + user_input'
        issues = wizard.analyze_code(code, "security.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test SecurityWizard predict_future_issues method"""
        wizard = SecurityWizard()
        code = 'query = "SELECT * FROM users WHERE id=" + user_input'
        context = {"publicly_exposed": True, "vuln_history": 3}
        predictions = wizard.predict_future_issues(code, "security.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test SecurityWizard suggest_fixes method"""
        wizard = SecurityWizard()
        issue = WizardIssue(
            severity="error",
            message="SQL injection vulnerability",
            file_path="security.py",
            line_number=1,
            code_snippet='query = "SELECT * FROM users WHERE id=" + user_input',
            fix_suggestion="Use parameterized queries",
            category="Security",
            confidence=0.99,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


class TestTestingWizard:
    """Tests for TestingWizard"""

    def test_initialization(self):
        """Test TestingWizard initialization"""
        wizard = TestingWizard()
        assert wizard.name == "TestingWizard"
        assert wizard.category == "Testing"
        assert wizard.languages == ["python", "javascript", "typescript", "java", "go", "rust"]

    def test_analyze_code(self):
        """Test TestingWizard analyze_code method"""
        wizard = TestingWizard()
        code = "def critical_function():\n    return do_something()"
        issues = wizard.analyze_code(code, "untested.py", "python")
        assert isinstance(issues, list)

    def test_predict_future_issues(self):
        """Test TestingWizard predict_future_issues method"""
        wizard = TestingWizard()
        code = "def critical_function():\n    return do_something()"
        context = {"code_coverage": 0.6, "defect_escape_rate": 0.1}
        predictions = wizard.predict_future_issues(code, "untested.py", context)
        assert isinstance(predictions, list)

    def test_suggest_fixes(self):
        """Test TestingWizard suggest_fixes method"""
        wizard = TestingWizard()
        issue = WizardIssue(
            severity="warning",
            message="Low test coverage",
            file_path="untested.py",
            line_number=1,
            code_snippet="def critical_function():",
            fix_suggestion="Add unit and integration tests",
            category="Testing",
            confidence=0.88,
        )
        fix = wizard.suggest_fixes(issue)
        assert isinstance(fix, str)


# Parametrized tests for all wizards
@pytest.mark.parametrize("wizard_spec", WIZARD_SPECS)
class TestAllWizardsInheritance:
    """Parametrized tests verifying all wizards inherit from BaseCoachWizard"""

    def test_wizard_inherits_from_base_coach_wizard(self, wizard_spec):
        """Test that wizard inherits from BaseCoachWizard"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        assert isinstance(wizard, BaseCoachWizard)

    def test_wizard_has_correct_name(self, wizard_spec):
        """Test that wizard has correct name"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        assert wizard.name == name

    def test_wizard_has_correct_category(self, wizard_spec):
        """Test that wizard has correct category"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        assert wizard.category == category

    def test_wizard_has_correct_languages(self, wizard_spec):
        """Test that wizard supports expected languages"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        assert wizard.languages == languages

    def test_wizard_analyze_code_returns_list(self, wizard_spec):
        """Test that analyze_code returns a list"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        code = "# test code"
        result = wizard.analyze_code(code, "test.py", "python")
        assert isinstance(result, list)
        assert all(isinstance(item, WizardIssue) for item in result)

    def test_wizard_predict_future_issues_returns_list(self, wizard_spec):
        """Test that predict_future_issues returns a list"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        code = "# test code"
        context = {"team_size": 5}
        result = wizard.predict_future_issues(code, "test.py", context)
        assert isinstance(result, list)
        assert all(isinstance(item, WizardPrediction) for item in result)

    def test_wizard_suggest_fixes_returns_string(self, wizard_spec):
        """Test that suggest_fixes returns a string"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        issue = WizardIssue(
            severity="warning",
            message="Test issue",
            file_path="test.py",
            line_number=1,
            code_snippet="test",
            fix_suggestion="test fix",
            category=category,
            confidence=0.8,
        )
        result = wizard.suggest_fixes(issue)
        assert isinstance(result, str)

    def test_wizard_run_full_analysis(self, wizard_spec):
        """Test that run_full_analysis returns WizardResult"""
        wizard_class, name, category, languages = wizard_spec
        wizard = wizard_class()
        code = "# test code"
        context = {"team_size": 5}
        result = wizard.run_full_analysis(code, "test.py", "python", context)
        assert result.wizard_name == name
        assert isinstance(result.issues, list)
        assert isinstance(result.predictions, list)
        assert isinstance(result.summary, str)
        assert result.analyzed_files == 1


class TestWizardIssueDataclass:
    """Tests for WizardIssue dataclass"""

    def test_wizard_issue_creation(self):
        """Test creating a WizardIssue"""
        issue = WizardIssue(
            severity="error",
            message="Test issue",
            file_path="test.py",
            line_number=5,
            code_snippet="test code",
            fix_suggestion="fix it",
            category="Testing",
            confidence=0.95,
        )
        assert issue.severity == "error"
        assert issue.message == "Test issue"
        assert issue.file_path == "test.py"
        assert issue.line_number == 5
        assert issue.code_snippet == "test code"
        assert issue.fix_suggestion == "fix it"
        assert issue.category == "Testing"
        assert issue.confidence == 0.95

    def test_wizard_issue_with_none_values(self):
        """Test WizardIssue with None optional values"""
        issue = WizardIssue(
            severity="info",
            message="Test issue",
            file_path="test.py",
            line_number=None,
            code_snippet=None,
            fix_suggestion=None,
            category="Testing",
            confidence=0.5,
        )
        assert issue.line_number is None
        assert issue.code_snippet is None
        assert issue.fix_suggestion is None


class TestWizardPredictionDataclass:
    """Tests for WizardPrediction dataclass"""

    def test_wizard_prediction_creation(self):
        """Test creating a WizardPrediction"""
        prediction = WizardPrediction(
            predicted_date=datetime(2025, 12, 31),
            issue_type="performance_degradation",
            probability=0.85,
            impact="high",
            prevention_steps=["optimize", "refactor"],
            reasoning="Load increasing 10% monthly",
        )
        assert prediction.issue_type == "performance_degradation"
        assert prediction.probability == 0.85
        assert prediction.impact == "high"
        assert len(prediction.prevention_steps) == 2


# Integration test
class TestWizardIntegration:
    """Integration tests for Coach Wizards"""

    def test_multiple_wizards_analysis(self):
        """Test running analysis across multiple wizards"""
        code = "SELECT * FROM users"
        context = {"team_size": 10}

        wizards = [
            SecurityWizard(),
            PerformanceWizard(),
            DocumentationWizard(),
        ]

        for wizard in wizards:
            result = wizard.run_full_analysis(code, "test.sql", "sql", context)
            assert result.wizard_name is not None
            assert isinstance(result.analysis_time, float)
            assert result.analysis_time >= 0

    def test_wizard_issue_with_all_fields(self):
        """Test WizardIssue with all required and optional fields"""
        issue = WizardIssue(
            severity="error",
            message="Critical vulnerability found",
            file_path="/src/auth.py",
            line_number=42,
            code_snippet="password = user_input  # unsafe",
            fix_suggestion="Use bcrypt for hashing",
            category="Security",
            confidence=0.99,
        )

        assert all(
            [
                issue.severity == "error",
                issue.message == "Critical vulnerability found",
                issue.file_path == "/src/auth.py",
                issue.line_number == 42,
                issue.code_snippet == "password = user_input  # unsafe",
                issue.fix_suggestion == "Use bcrypt for hashing",
                issue.category == "Security",
                issue.confidence == 0.99,
            ]
        )
