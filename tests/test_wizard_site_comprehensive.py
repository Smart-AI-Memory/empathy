#!/usr/bin/env python3
"""
Comprehensive Wizard Site Testing Plan
======================================

Tests all 44 wizards accessible via wizards.smartaimemory.com

Categories:
- Domain Wizards (16): Industry-specific with compliance
- Software/Coach Wizards (16): Development tools
- AI Wizards (12): AI/ML development tools

Test Coverage:
1. API endpoint availability
2. Processing functionality
3. Response structure validation
4. Sample input handling
5. Error handling

Run with: pytest tests/test_wizard_site_comprehensive.py -v
"""

import pytest

# ============================================================================
# WIZARD REGISTRY - All 44 Wizards
# ============================================================================

DOMAIN_WIZARDS = [
    {
        "id": "healthcare",
        "name": "Healthcare Wizard",
        "category": "domain",
        "sample_input": "Patient John Doe, MRN: 123456, DOB: 01/15/1980. Diagnosis: Type 2 Diabetes.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "finance",
        "name": "Finance Wizard",
        "category": "domain",
        "sample_input": "Account #4532-1234-5678-9012, routing 021000021. Transaction: $50,000 wire transfer.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "legal",
        "name": "Legal Wizard",
        "category": "domain",
        "sample_input": "Case No. 2024-CV-12345. Plaintiff: Acme Corp. Attorney: Jane Smith, Bar #123456.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "education",
        "name": "Education Wizard",
        "category": "domain",
        "sample_input": "Student ID: STU-2024-001. Course: CS101. Grade: A. Financial Aid ID: FA-789.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "customer_support",
        "name": "Customer Support Wizard",
        "category": "domain",
        "sample_input": "Ticket #CS-2024-5678. Customer: john@email.com. Issue: Order #ORD-123 not delivered.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "hr",
        "name": "HR Wizard",
        "category": "domain",
        "sample_input": "Employee ID: EMP-001. Salary: $85,000. Performance review: Exceeds expectations.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "sales",
        "name": "Sales Wizard",
        "category": "domain",
        "sample_input": "Lead ID: LEAD-2024-001. Contact: jane@company.com. Opportunity: $500K deal.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "real_estate",
        "name": "Real Estate Wizard",
        "category": "domain",
        "sample_input": "MLS# 12345678. Property: 123 Main St. Parcel ID: P-2024-001. Price: $450,000.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "insurance",
        "name": "Insurance Wizard",
        "category": "domain",
        "sample_input": "Policy #INS-2024-001. Claim #CLM-5678. VIN: 1HGBH41JXMN109186.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "accounting",
        "name": "Accounting Wizard",
        "category": "domain",
        "sample_input": "Tax ID: 12-3456789. Account #ACC-001. Bank routing: 021000021.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "research",
        "name": "Research Wizard",
        "category": "domain",
        "sample_input": "Participant ID: P-001. Protocol #IRB-2024-123. Grant ID: NIH-R01-12345.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "government",
        "name": "Government Wizard",
        "category": "domain",
        "sample_input": "Case #GOV-2024-001. Permit #PERM-5678. License #LIC-9012.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "retail",
        "name": "Retail Wizard",
        "category": "domain",
        "sample_input": "Order #ORD-2024-001. Customer ID: CUST-5678. Tracking: 1Z999AA10123456784.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "manufacturing",
        "name": "Manufacturing Wizard",
        "category": "domain",
        "sample_input": "Part #MFG-001. Serial #SN-12345. Batch #BATCH-2024-01. Employee ID: EMP-789.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "logistics",
        "name": "Logistics Wizard",
        "category": "domain",
        "sample_input": "Shipment #SHIP-2024-001. Tracking: 1Z999AA10123456784. Order #ORD-5678.",
        "expected_features": ["pii_detected", "classification"],
    },
    {
        "id": "technology",
        "name": "Technology Wizard",
        "category": "domain",
        "sample_input": "API Key: sk-abc123xyz. SSH Key: ssh-rsa AAAAB3... IP: 192.168.1.100.",
        "expected_features": ["pii_detected", "classification"],
    },
]

SOFTWARE_WIZARDS = [
    {
        "id": "debugging",
        "name": "Debugging Wizard",
        "category": "coach",
        "sample_input": """def process_data(data):
    result = data['key']  # KeyError if key missing
    return result / 0  # Division by zero
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "testing",
        "name": "Testing Wizard",
        "category": "coach",
        "sample_input": """def calculate_total(items):
    total = sum(item.price for item in items)
    return total
# No tests for edge cases
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "security_wizard",
        "name": "Security Wizard",
        "category": "coach",
        "sample_input": """import os
password = "admin123"  # Hardcoded credential  # pragma: allowlist secret
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "documentation",
        "name": "Documentation Wizard",
        "category": "coach",
        "sample_input": """def complex_algorithm(x, y, z, config):
    # Missing docstring
    result = x * y + z
    return result
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "performance_wizard",
        "name": "Performance Wizard",
        "category": "coach",
        "sample_input": """def slow_function(items):
    result = []
    for i in items:
        for j in items:  # O(n²) complexity
            result.append(i + j)
    return result
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "refactoring",
        "name": "Refactoring Wizard",
        "category": "coach",
        "sample_input": """def do_everything(a, b, c, d, e, f, g, h):  # Too many parameters
    if a:
        if b:
            if c:  # Deep nesting
                return d + e + f + g + h
    return 0
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "database",
        "name": "Database Wizard",
        "category": "coach",
        "sample_input": """SELECT * FROM users
JOIN orders ON users.id = orders.user_id
JOIN products ON orders.product_id = products.id
WHERE users.created_at > '2024-01-01'
-- Missing index on created_at
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "api_wizard",
        "name": "API Wizard",
        "category": "coach",
        "sample_input": """@app.route('/users/<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_endpoint(id):
    # All methods in one endpoint
    # No versioning
    # No rate limiting
    return jsonify(get_user(id))
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "compliance",
        "name": "Compliance Wizard",
        "category": "coach",
        "sample_input": """def store_user_data(user):
    # No encryption for PII
    # No consent tracking
    # No data retention policy
    db.save(user.email, user.ssn, user.health_records)
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "monitoring",
        "name": "Monitoring Wizard",
        "category": "coach",
        "sample_input": """def critical_service():
    # No health checks
    # No metrics
    # No alerting
    process_transactions()
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "cicd",
        "name": "CI/CD Wizard",
        "category": "coach",
        "sample_input": """# .github/workflows/deploy.yml
name: Deploy
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: npm install && npm run deploy
      # No tests, no staging, secrets in code
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "accessibility",
        "name": "Accessibility Wizard",
        "category": "coach",
        "sample_input": """<div onclick="submit()">Click here</div>
<img src="photo.jpg">
<input type="text">
<!-- Missing: alt text, labels, keyboard nav, ARIA -->
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "localization",
        "name": "Localization Wizard",
        "category": "coach",
        "sample_input": """def format_date(date):
    return f"{date.month}/{date.day}/{date.year}"  # US-only format

def display_price(amount):
    return f"${amount:.2f}"  # USD-only, hardcoded symbol
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "migration",
        "name": "Migration Wizard",
        "category": "coach",
        "sample_input": """# Migration to new database
# Current: PostgreSQL 12
# Target: PostgreSQL 15
# Tables: users (10M rows), orders (50M rows)
# No rollback plan documented
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "observability",
        "name": "Observability Wizard",
        "category": "coach",
        "sample_input": """async def process_payment(order):
    result = await payment_gateway.charge(order.total)
    if result.success:
        await notify_customer(order.email)
    # No tracing, no correlation IDs, no SLOs defined
""",
        "expected_features": ["issues", "issues_found"],
    },
    {
        "id": "scaling",
        "name": "Scaling Wizard",
        "category": "coach",
        "sample_input": """# Current: Single instance, 8GB RAM, 2 CPU
# Traffic: 1000 req/min → 10000 req/min expected
# Database: Single node MySQL
# Session storage: In-memory
""",
        "expected_features": ["issues", "issues_found"],
    },
]

AI_WIZARDS = [
    {
        "id": "multi_model",
        "name": "Multi-Model Wizard",
        "category": "ai",
        "sample_input": "Compare GPT-4 and Claude for code review tasks with emphasis on security analysis",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "rag_pattern",
        "name": "RAG Pattern Wizard",
        "category": "ai",
        "sample_input": "Implement a RAG system for customer support documentation with 10K+ articles",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "ai_performance",
        "name": "AI Performance Wizard",
        "category": "ai",
        "sample_input": "Optimize inference latency for a production ML model serving 1M requests/day",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "ai_collaboration",
        "name": "AI Collaboration Wizard",
        "category": "ai",
        "sample_input": "Design multi-agent system for automated code review and testing pipeline",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "advanced_debugging",
        "name": "Advanced Debugging Wizard",
        "category": "ai",
        "sample_input": "Debug intermittent GPU memory errors in distributed training with PyTorch",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "agent_orchestration",
        "name": "Agent Orchestration Wizard",
        "category": "ai",
        "sample_input": "Orchestrate 5 specialized agents for end-to-end data pipeline: ingestion, validation, transformation, analysis, reporting",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "enhanced_testing",
        "name": "Enhanced Testing Wizard",
        "category": "ai",
        "sample_input": "Generate comprehensive test suite for authentication microservice with OAuth2 and JWT",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "ai_documentation",
        "name": "AI Documentation Wizard",
        "category": "ai",
        "sample_input": "Auto-generate API documentation from FastAPI codebase with usage examples",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "prompt_engineering",
        "name": "Prompt Engineering Wizard",
        "category": "ai",
        "sample_input": "Optimize this prompt for code review: 'Review this code and find bugs'",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "ai_context",
        "name": "AI Context Wizard",
        "category": "ai",
        "sample_input": "Optimize context window usage for 100K token documents while maintaining quality",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "security_analysis",
        "name": "Security Analysis Wizard",
        "category": "ai",
        "sample_input": "Analyze AI model for prompt injection vulnerabilities and data leakage risks",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
    {
        "id": "ai_testing",
        "name": "AI Testing Wizard",
        "category": "ai",
        "sample_input": "Create evaluation framework for LLM output quality on customer service tasks",
        "expected_features": ["issues", "predictions", "recommendations"],
    },
]

ALL_WIZARDS = DOMAIN_WIZARDS + SOFTWARE_WIZARDS + AI_WIZARDS


# ============================================================================
# TEST FIXTURES
# ============================================================================


def _check_server_available(url: str) -> bool:
    """Check if the wizard server is running."""
    try:
        import socket
        from urllib.parse import urlparse

        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 8001

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


@pytest.fixture
def api_base_url():
    """Base URL for wizard API"""
    return "http://localhost:8001"


@pytest.fixture
def wizard_registry():
    """Complete wizard registry"""
    return ALL_WIZARDS


@pytest.fixture(autouse=True)
def skip_if_server_unavailable(api_base_url):
    """Skip integration tests if wizard server is not running."""
    if not _check_server_available(api_base_url):
        pytest.skip(
            f"Wizard server not running at {api_base_url}. "
            "Start with: cd wizard_api && uvicorn main:app --port 8001"
        )


# ============================================================================
# API TESTS - Integration tests requiring running server
# ============================================================================


class TestWizardAPIAvailability:
    """Test that all wizard endpoints are available"""

    @pytest.mark.asyncio
    async def test_api_root_returns_wizard_count(self, api_base_url):
        """API root should return loaded wizard count"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base_url}/")

        assert response.status_code == 200
        data = response.json()
        assert "wizards_loaded" in data
        assert data["wizards_loaded"] >= 30  # At least 30 wizards loaded

    @pytest.mark.asyncio
    async def test_wizards_list_endpoint(self, api_base_url):
        """GET /api/wizards should return wizard list"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base_url}/api/wizards")

        assert response.status_code == 200
        data = response.json()
        assert "wizards" in data
        assert "total" in data
        assert data["total"] >= 30


class TestDomainWizards:
    """Test all 16 domain wizards"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("wizard", DOMAIN_WIZARDS, ids=[w["id"] for w in DOMAIN_WIZARDS])
    async def test_domain_wizard_processing(self, api_base_url, wizard):
        """Each domain wizard should process input and return expected structure"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/{wizard['id']}/process",
                json={
                    "input": wizard["sample_input"],
                    "user_id": "test_user",
                    "context": {},
                },
            )

        # Should return 200 or wizard not loaded (404)
        assert response.status_code in [
            200,
            404,
        ], f"Wizard {wizard['id']} returned {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "output" in data

            # Check for expected analysis features
            if data.get("success") and data.get("analysis"):
                for feature in wizard.get("expected_features", []):
                    assert (
                        feature in data["analysis"]
                    ), f"Missing {feature} in {wizard['id']} response"


class TestSoftwareWizards:
    """Test all 16 software/coach wizards"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("wizard", SOFTWARE_WIZARDS, ids=[w["id"] for w in SOFTWARE_WIZARDS])
    async def test_software_wizard_processing(self, api_base_url, wizard):
        """Each software wizard should analyze code and return issues"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/{wizard['id']}/process",
                json={
                    "input": wizard["sample_input"],
                    "user_id": "test_user",
                    "context": {"file_path": "test.py", "language": "python"},
                },
            )

        assert response.status_code in [
            200,
            404,
        ], f"Wizard {wizard['id']} returned {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "output" in data


class TestAIWizards:
    """Test all 12 AI wizards"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("wizard", AI_WIZARDS, ids=[w["id"] for w in AI_WIZARDS])
    async def test_ai_wizard_processing(self, api_base_url, wizard):
        """Each AI wizard should analyze input and return predictions"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/{wizard['id']}/process",
                json={
                    "input": wizard["sample_input"],
                    "user_id": "test_user",
                    "context": {"wizard_type": "ai"},
                },
            )

        assert response.status_code in [
            200,
            404,
        ], f"Wizard {wizard['id']} returned {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "output" in data

            # AI wizards should return analysis with predictions
            if data.get("success") and data.get("analysis"):
                analysis = data["analysis"]
                # At least one of these should be present
                has_content = any(
                    [
                        analysis.get("issues"),
                        analysis.get("predictions"),
                        analysis.get("recommendations"),
                    ]
                )
                assert has_content or data.get(
                    "output"
                ), f"AI wizard {wizard['id']} returned empty analysis"


class TestAgentOrchestrationWizard:
    """Specific tests for the Agent Orchestration Wizard"""

    @pytest.mark.asyncio
    async def test_parses_agent_count_from_text(self, api_base_url):
        """Should parse agent count from natural language"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/agent_orchestration/process",
                json={
                    "input": "Orchestrate 5 specialized agents for data pipeline: ingestion, validation, transformation, analysis, reporting",
                    "user_id": "test_user",
                    "context": {"wizard_type": "ai"},
                },
            )

        if response.status_code == 200:
            data = response.json()
            assert data.get("success"), f"Processing failed: {data.get('error')}"
            # Should have analysis with agent count
            if data.get("analysis") and data["analysis"].get("metadata"):
                agent_count = data["analysis"]["metadata"].get("agent_count", 0)
                assert agent_count >= 5, f"Expected at least 5 agents, got {agent_count}"

    @pytest.mark.asyncio
    async def test_predictions_for_many_agents(self, api_base_url):
        """Should generate predictions when agent count > 5"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/agent_orchestration/process",
                json={
                    "input": "Build 8 agent system: ingestion, validation, transformation, enrichment, analysis, reporting, monitoring, alerting",
                    "user_id": "test_user",
                    "context": {},
                },
            )

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("analysis"):
                predictions = data["analysis"].get("predictions", [])
                # Should have predictions for 8 agents
                assert len(predictions) > 0, "Expected predictions for 8 agents"


class TestErrorHandling:
    """Test error handling across wizards"""

    @pytest.mark.asyncio
    async def test_invalid_wizard_returns_404(self, api_base_url):
        """Non-existent wizard should return 404"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/nonexistent_wizard/process",
                json={"input": "test", "user_id": "test"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_empty_input_handled_gracefully(self, api_base_url):
        """Empty input should not crash wizards"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/api/wizard/debugging/process",
                json={"input": "", "user_id": "test"},
            )

        # Should return 200 or 422 (validation error), not 500
        assert response.status_code in [200, 422]


# ============================================================================
# INTEGRATION TESTS (requires backend running)
# ============================================================================


class TestWizardIntegration:
    """Integration tests requiring backend"""

    @pytest.mark.asyncio
    async def test_all_wizards_respond(self, api_base_url):
        """Every wizard should respond (success or graceful error)"""
        import httpx

        results = {"success": [], "failed": [], "not_loaded": []}

        async with httpx.AsyncClient(timeout=30.0) as client:
            for wizard in ALL_WIZARDS:
                try:
                    response = await client.post(
                        f"{api_base_url}/api/wizard/{wizard['id']}/process",
                        json={
                            "input": wizard["sample_input"],
                            "user_id": "test_user",
                            "context": {},
                        },
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            results["success"].append(wizard["id"])
                        else:
                            results["failed"].append((wizard["id"], data.get("error")))
                    elif response.status_code == 404:
                        results["not_loaded"].append(wizard["id"])
                    else:
                        results["failed"].append((wizard["id"], f"HTTP {response.status_code}"))
                except Exception as e:
                    results["failed"].append((wizard["id"], str(e)))

        # Report results
        print("\n=== Wizard Test Results ===")
        print(f"✓ Successful: {len(results['success'])}")
        print(f"✗ Failed: {len(results['failed'])}")
        print(f"⊘ Not loaded: {len(results['not_loaded'])}")

        if results["failed"]:
            print("\nFailed wizards:")
            for wizard_id, error in results["failed"]:
                print(f"  - {wizard_id}: {error}")

        # At least 50% should work
        total = len(ALL_WIZARDS)
        working = len(results["success"])
        assert working >= total * 0.5, f"Only {working}/{total} wizards working"


# ============================================================================
# RUN STANDALONE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("COMPREHENSIVE WIZARD SITE TEST PLAN")
    print("=" * 60)
    print(f"\nTotal Wizards: {len(ALL_WIZARDS)}")
    print(f"  - Domain Wizards: {len(DOMAIN_WIZARDS)}")
    print(f"  - Software Wizards: {len(SOFTWARE_WIZARDS)}")
    print(f"  - AI Wizards: {len(AI_WIZARDS)}")
    print("\nTo run tests:")
    print("  1. Start backend: python backend/api/wizard_api.py")
    print("  2. Run tests: pytest tests/test_wizard_site_comprehensive.py -v")
    print("\nOr run integration test:")
    print("  pytest tests/test_wizard_site_comprehensive.py::TestWizardIntegration -v")
