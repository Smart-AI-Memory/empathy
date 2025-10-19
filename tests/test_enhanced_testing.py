"""
Tests for Enhanced Testing Wizard

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
import tempfile
import os
from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard


class TestEnhancedTestingWizard:
    """Test Enhanced Testing Wizard"""

    @pytest.mark.asyncio
    async def test_basic_initialization(self):
        """Test wizard initializes correctly"""
        wizard = EnhancedTestingWizard()

        assert wizard.name == "Enhanced Testing Wizard"
        assert wizard.level == 4
        assert len(wizard.high_risk_patterns) > 0

    @pytest.mark.asyncio
    async def test_coverage_analysis(self):
        """Test coverage metrics analysis"""
        wizard = EnhancedTestingWizard()

        coverage_data = {
            "/test/file1.py": {
                "lines_total": 100,
                "lines_covered": 80,
                "branches_total": 20,
                "branches_covered": 15
            },
            "/test/file2.py": {
                "lines_total": 50,
                "lines_covered": 25,
                "branches_total": 10,
                "branches_covered": 5
            }
        }

        result = await wizard.analyze({
            'project_path': '/test',
            'coverage_report': coverage_data,
            'test_files': [],
            'source_files': []
        })

        coverage = result['coverage']

        assert 'line_coverage' in coverage
        assert 'branch_coverage' in coverage
        assert 'overall_coverage' in coverage

        # Check calculations
        # Lines: (80+25)/(100+50) = 70%
        assert coverage['line_coverage'] == 70.0

        # Branches: (15+5)/(20+10) = 66.67%
        assert abs(coverage['branch_coverage'] - 66.67) < 0.1

    @pytest.mark.asyncio
    async def test_high_risk_pattern_detection(self):
        """Test detection of high-risk untested code"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with high-risk patterns
            auth_file = os.path.join(tmpdir, "auth.py")
            with open(auth_file, 'w') as f:
                f.write('''
def authenticate_user(username, password):
    try:
        # SQL query - high risk!
        result = db.execute(f"SELECT * FROM users WHERE name='{username}'")
        return result
    except Exception as e:
        # Error handling - high risk!
        return None
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},  # No coverage = untested
                'source_files': [auth_file]
            })

            risk_gaps = result['risk_gaps']

            # Should detect both error_handling and user_input patterns
            assert len(risk_gaps) > 0

            # Check for CRITICAL risk level (user_input)
            critical_gaps = [g for g in risk_gaps if g['risk_level'] == 'CRITICAL']
            assert len(critical_gaps) > 0

    @pytest.mark.asyncio
    async def test_test_quality_analysis(self):
        """Test quality scoring"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files with assertions
            test_file1 = os.path.join(tmpdir, "test_module.py")
            with open(test_file1, 'w') as f:
                f.write('''
def test_something():
    assert foo == bar
    assert baz == qux
''')

            test_file2 = os.path.join(tmpdir, "test_another.py")
            with open(test_file2, 'w') as f:
                f.write('''
def test_no_assertions():
    # This test has no assertions - low quality!
    foo = bar()
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},
                'test_files': [test_file1, test_file2],
                'source_files': []
            })

            quality = result['test_quality']

            assert quality['total_test_files'] == 2
            assert quality['tests_with_assertions'] == 1  # Only test_file1
            assert quality['total_assertions'] == 2
            assert 'quality_score' in quality

    @pytest.mark.asyncio
    async def test_brittle_test_detection(self):
        """Test detection of brittle tests"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create brittle test file
            brittle_test = os.path.join(tmpdir, "test_brittle.py")
            with open(brittle_test, 'w') as f:
                f.write('''
def test_with_sleep():
    import time
    time.sleep(5)  # Timing-based - brittle!
    assert result == expected
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},
                'test_files': [brittle_test],
                'source_files': []
            })

            brittle_tests = result['brittle_tests']

            assert len(brittle_tests) > 0
            assert any('sleep' in t['pattern'] for t in brittle_tests)

    @pytest.mark.asyncio
    async def test_predictions_generated(self):
        """Test Level 4 predictions"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create critical untested code
            critical_file = os.path.join(tmpdir, "payment.py")
            with open(critical_file, 'w') as f:
                f.write('''
def process_payment(card_number, amount):
    # User input + financial - CRITICAL!
    result = gateway.charge(card_number, amount)
    return result
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},
                'source_files': [critical_file]
            })

            predictions = result['predictions']

            assert len(predictions) > 0

            # Should have production_bug_risk prediction
            bug_risk_preds = [p for p in predictions if p['type'] == 'production_bug_risk']
            assert len(bug_risk_preds) > 0

            # Check prediction structure
            pred = bug_risk_preds[0]
            assert 'severity' in pred
            assert 'description' in pred
            assert 'prevention_steps' in pred
            assert pred['severity'] == 'critical'

    @pytest.mark.asyncio
    async def test_recommendations_generated(self):
        """Test recommendations are actionable"""
        wizard = EnhancedTestingWizard()

        result = await wizard.analyze({
            'project_path': '/test',
            'coverage_report': {
                "/test/file.py": {
                    "lines_total": 100,
                    "lines_covered": 40,  # Low coverage
                    "branches_total": 20,
                    "branches_covered": 5
                }
            },
            'test_files': [],
            'source_files': ['/test/file.py']
        })

        recommendations = result['recommendations']

        assert len(recommendations) > 0
        assert any('coverage' in r.lower() for r in recommendations)

    @pytest.mark.asyncio
    async def test_test_suggestions(self):
        """Test smart test suggestions"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_with_error_handling = os.path.join(tmpdir, "module.py")
            with open(file_with_error_handling, 'w') as f:
                f.write('''
def risky_function():
    try:
        result = dangerous_operation()
        return result
    except ValueError as e:
        return None
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},
                'source_files': [file_with_error_handling]
            })

            suggestions = result['test_suggestions']

            assert len(suggestions) > 0

            # Check suggestion structure
            suggestion = suggestions[0]
            assert 'priority' in suggestion
            assert 'file' in suggestion
            assert 'test_type' in suggestion
            assert 'rationale' in suggestion
            assert 'suggested_tests' in suggestion
            assert len(suggestion['suggested_tests']) > 0

    @pytest.mark.asyncio
    async def test_standard_wizard_interface(self):
        """Test wizard follows BaseWizard interface"""
        wizard = EnhancedTestingWizard()

        result = await wizard.analyze({
            'project_path': '/test',
            'coverage_report': {},
            'test_files': [],
            'source_files': []
        })

        # Check standard wizard outputs
        assert 'predictions' in result
        assert 'recommendations' in result
        assert 'confidence' in result

        # Confidence should be between 0 and 1
        assert 0 <= result['confidence'] <= 1

    @pytest.mark.asyncio
    async def test_empty_project(self):
        """Test handling of empty project"""
        wizard = EnhancedTestingWizard()

        result = await wizard.analyze({
            'project_path': '/test',
            'coverage_report': {},
            'test_files': [],
            'source_files': []
        })

        # Should handle gracefully
        assert 'coverage' in result
        assert 'test_quality' in result
        assert 'predictions' in result


class TestRiskPatterns:
    """Test high-risk pattern detection"""

    @pytest.mark.asyncio
    async def test_authentication_pattern(self):
        """Test detection of authentication code"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = os.path.join(tmpdir, "auth.py")
            with open(auth_file, 'w') as f:
                f.write('''
def login_user(username, password):
    # Authentication logic
    return authenticate(username, password)
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},
                'source_files': [auth_file]
            })

            risk_gaps = result['risk_gaps']
            auth_gaps = [g for g in risk_gaps if 'authentication' in g['pattern']]

            assert len(auth_gaps) > 0
            assert auth_gaps[0]['risk_level'] == 'CRITICAL'

    @pytest.mark.asyncio
    async def test_financial_calculation_pattern(self):
        """Test detection of financial calculations"""
        wizard = EnhancedTestingWizard()

        with tempfile.TemporaryDirectory() as tmpdir:
            payment_file = os.path.join(tmpdir, "payment.py")
            with open(payment_file, 'w') as f:
                f.write('''
def calculate_total(items):
    total = 0
    for item in items:
        price = item.price
        total = total + price
    return round(total, 2)
''')

            result = await wizard.analyze({
                'project_path': tmpdir,
                'coverage_report': {},
                'source_files': [payment_file]
            })

            risk_gaps = result['risk_gaps']
            financial_gaps = [g for g in risk_gaps if 'financial' in g['pattern']]

            assert len(financial_gaps) > 0
            assert financial_gaps[0]['risk_level'] == 'HIGH'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
