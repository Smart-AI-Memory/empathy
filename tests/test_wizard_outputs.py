#!/usr/bin/env python3
"""
Wizard Output Testing and Saving - ALL 44 WIZARDS
==================================================

Tests all wizards and saves outputs for user review.

Outputs saved to: tests/wizard_outputs/

Run: python tests/test_wizard_outputs.py
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

import pytest

# Skip entire module if httpx is not available
httpx = pytest.importorskip("httpx", reason="httpx required for wizard output tests")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "wizard_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

API_BASE_URL = os.getenv("WIZARD_API_URL", "http://localhost:8001")

# ============================================================================
# ALL 44 WIZARDS - Complete Registry
# ============================================================================

# Domain Wizards (16 total)
DOMAIN_WIZARDS = [
    {
        "id": "healthcare",
        "name": "Healthcare Wizard",
        "priority": "low",  # Well tested
        "sample_input": "Patient John Doe, MRN: 123456, DOB: 01/15/1980. Diagnosis: Type 2 Diabetes. A1C: 8.5%. Recommend insulin adjustment.",
    },
    {
        "id": "finance",
        "name": "Finance Wizard",
        "priority": "high",
        "sample_input": "Account #4532-1234-5678-9012, routing 021000021. Transaction: $50,000 wire transfer to offshore account.",
    },
    {
        "id": "legal",
        "name": "Legal Wizard",
        "priority": "high",
        "sample_input": "Case No. 2024-CV-12345. Plaintiff: Acme Corp vs. XYZ Inc. Breach of contract. Settlement discussions pending.",
    },
    {
        "id": "education",
        "name": "Education Wizard",
        "priority": "high",
        "sample_input": "Student ID: STU-2024-001. Academic probation notice. GPA: 1.8. Financial aid at risk.",
    },
    {
        "id": "customer_support",
        "name": "Customer Support Wizard",
        "priority": "medium",
        "sample_input": "Ticket #CS-2024-5678. Angry customer. Order delayed 2 weeks. Requesting full refund and compensation.",
    },
    {
        "id": "hr",
        "name": "HR Wizard",
        "priority": "high",
        "sample_input": "Employee termination review. EMP-001. Performance issues documented. Legal review recommended before proceeding.",
    },
    {
        "id": "sales",
        "name": "Sales Wizard",
        "priority": "medium",
        "sample_input": "Q4 Pipeline review. $2.5M at risk. Key deal slipping. Competitor offering 30% discount.",
    },
    {
        "id": "real_estate",
        "name": "Real Estate Wizard",
        "priority": "medium",
        "sample_input": "MLS# 12345678. Property: 123 Main St. Parcel ID: P-2024-001. Listed: $450,000. Multiple offers received.",
    },
    {
        "id": "insurance",
        "name": "Insurance Wizard",
        "priority": "high",
        "sample_input": "Claim #CLM-5678. Vehicle total loss. Policy limits: $50K. Claimant requesting $75K. Fraud indicators present.",
    },
    {
        "id": "accounting",
        "name": "Accounting Wizard",
        "priority": "medium",
        "sample_input": "Q4 Audit preparation. Tax ID: 12-3456789. Discrepancy found: $25,000 unreconciled transactions.",
    },
    {
        "id": "research",
        "name": "Research Wizard",
        "priority": "medium",
        "sample_input": "IRB Protocol #2024-123. Participant consent forms. Grant ID: NIH-R01-12345. Data handling procedures.",
    },
    {
        "id": "government",
        "name": "Government Wizard",
        "priority": "high",
        "sample_input": "FOIA Request #GOV-2024-001. Sensitive documents requested. Redaction review needed. 20-day deadline.",
    },
    {
        "id": "retail",
        "name": "Retail Wizard",
        "priority": "medium",
        "sample_input": "Holiday inventory planning. SKU: RET-2024-001. Current stock: 500 units. Projected demand: 2000 units.",
    },
    {
        "id": "manufacturing",
        "name": "Manufacturing Wizard",
        "priority": "medium",
        "sample_input": "Production line issue. Part #MFG-001 defect rate: 5%. Quality control alert. Batch #BATCH-2024-01 quarantined.",
    },
    {
        "id": "logistics",
        "name": "Logistics Wizard",
        "priority": "medium",
        "sample_input": "Supply chain disruption. Shipment #SHIP-2024-001 delayed 7 days. Alternative routing needed. Cost impact: $15K.",
    },
    {
        "id": "technology",
        "name": "Technology Wizard",
        "priority": "high",
        "sample_input": "Security audit findings. API Key exposure detected: sk-abc123xyz. SSH credentials in repo. IP whitelist needed.",
    },
]

# Software/Coach Wizards (16 total)
SOFTWARE_WIZARDS = [
    {
        "id": "debugging",
        "name": "Debugging Wizard",
        "priority": "critical",
        "sample_input": """def process_payment(order):
    total = order['total']  # KeyError if missing
    tax = total * 0.08  # Assumes US tax rate
    user = get_user(order['user_id'])  # N+1 query
    result = charge_card(user.card, total + tax)
    if result:
        send_email(user.email)  # No error handling
    return result
""",
    },
    {
        "id": "testing",
        "name": "Testing Wizard",
        "priority": "high",
        "sample_input": """class PaymentProcessor:
    def process(self, amount, card):
        if amount <= 0:
            raise ValueError("Invalid amount")
        if not card.is_valid():
            raise CardError("Invalid card")
        result = self.gateway.charge(card, amount)
        return result

# No tests for edge cases, failures, concurrency
""",
    },
    {
        "id": "security_wizard",
        "name": "Security Wizard",
        "priority": "critical",
        "sample_input": """import os
from flask import Flask, request

app = Flask(__name__)
SECRET_KEY = "production_secret_key_123"  # Hardcoded

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    query = f"SELECT * FROM users WHERE username='{username}'"  # SQL injection
    return db.execute(query)
""",
    },
    {
        "id": "documentation",
        "name": "Documentation Wizard",
        "priority": "medium",
        "sample_input": """def calculate_risk_score(portfolio, market_conditions, user_preferences, historical_data, risk_tolerance):
    # Complex algorithm with no documentation
    result = sum([p.value * m.volatility for p, m in zip(portfolio, market_conditions)])
    return result * risk_tolerance
""",
    },
    {
        "id": "performance_wizard",
        "name": "Performance Wizard",
        "priority": "high",
        "sample_input": """def get_recommendations(user_id):
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user)
    recommendations = []
    for order in orders:  # N+1 problem
        for item in order.items.all():  # Another N+1
            similar = Product.objects.filter(category=item.category)[:10]
            recommendations.extend(similar)
    return recommendations
""",
    },
    {
        "id": "refactoring",
        "name": "Refactoring Wizard",
        "priority": "medium",
        "sample_input": """def do_everything(a, b, c, d, e, f, g, h, i, j):  # Too many params
    if a:
        if b:
            if c:
                if d:  # Deep nesting
                    result = e + f + g + h + i + j
                    print(result)  # Side effect
                    return result
    return 0
""",
    },
    {
        "id": "database",
        "name": "Database Wizard",
        "priority": "high",
        "sample_input": """SELECT u.*, o.*, p.*, r.*
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON o.product_id = p.id
JOIN reviews r ON p.id = r.product_id
WHERE u.created_at > '2024-01-01'
AND o.status = 'completed'
-- Missing indexes, cartesian product risk
""",
    },
    {
        "id": "api_wizard",
        "name": "API Wizard",
        "priority": "high",
        "sample_input": """@app.get("/users/{user_id}")
def get_user(user_id: str):
    # No auth, no rate limit, no validation
    return db.users.find_one({"_id": user_id})

@app.post("/users")
def create_user(data: dict):
    # No schema, no duplicate check
    return db.users.insert_one(data)
""",
    },
    {
        "id": "compliance",
        "name": "Compliance Wizard",
        "priority": "high",
        "sample_input": """def store_user_data(user):
    # GDPR/CCPA violations
    db.save(user.email, user.ssn, user.health_records)
    third_party_analytics.track(user)  # No consent
    # No data retention policy
    # No deletion capability
""",
    },
    {
        "id": "monitoring",
        "name": "Monitoring Wizard",
        "priority": "medium",
        "sample_input": """def process_critical_transaction(data):
    # No health checks, metrics, or alerting
    result = external_service.call(data)
    database.save(result)
    return result
    # What if external_service fails? Database fails?
""",
    },
    {
        "id": "cicd",
        "name": "CI/CD Wizard",
        "priority": "medium",
        "sample_input": """# deploy.yml
name: Deploy
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: npm install && npm run deploy
      # No tests, no staging, no rollback, secrets in code
""",
    },
    {
        "id": "accessibility",
        "name": "Accessibility Wizard",
        "priority": "medium",
        "sample_input": """<div onclick="submit()">Click here</div>
<img src="photo.jpg">
<input type="text">
<table><tr><td>Data</td></tr></table>
<!-- Missing: alt, labels, ARIA, keyboard nav, focus mgmt -->
""",
    },
    {
        "id": "localization",
        "name": "Localization Wizard",
        "priority": "low",
        "sample_input": """def format_data(date, amount, name):
    return f"Hello {name}, on {date.month}/{date.day}/{date.year} you paid ${amount:.2f}"
    # US-only format, hardcoded strings, no RTL support
""",
    },
    {
        "id": "migration",
        "name": "Migration Wizard",
        "priority": "medium",
        "sample_input": """# Database Migration Plan
# From: PostgreSQL 12 → PostgreSQL 15
# Tables: users (10M), orders (50M), products (1M)
# Downtime window: 4 hours
# No rollback plan, no data validation, no performance testing
""",
    },
    {
        "id": "observability",
        "name": "Observability Wizard",
        "priority": "medium",
        "sample_input": """async def multi_step_workflow(request):
    user = await fetch_user(request.user_id)
    order = await create_order(user, request.items)
    payment = await process_payment(order)
    notification = await send_notification(user, order)
    # No tracing, no correlation IDs, no SLOs
    return {"order": order.id}
""",
    },
    {
        "id": "scaling",
        "name": "Scaling Wizard",
        "priority": "medium",
        "sample_input": """# Current Architecture
# - Single instance: 8GB RAM, 2 CPU
# - MySQL single node
# - Session storage: in-memory
# - Expected growth: 10x traffic in 6 months
# - Current: 1000 req/min, Target: 10000 req/min
""",
    },
]

# AI Wizards (12 total)
AI_WIZARDS = [
    {
        "id": "multi_model",
        "name": "Multi-Model Wizard",
        "priority": "high",
        "sample_input": "Design a multi-model architecture using Claude for reasoning, GPT-4 for code generation, and Gemini for multimodal tasks. Need to handle fallbacks, cost optimization, and consistency checking.",
    },
    {
        "id": "rag_pattern",
        "name": "RAG Pattern Wizard",
        "priority": "high",
        "sample_input": "Build RAG system for 50,000 technical documents. Requirements: semantic search, hybrid retrieval, reranking, chunk optimization. Current issues: low relevance scores, high latency, 2s response time.",
    },
    {
        "id": "ai_performance",
        "name": "AI Performance Wizard",
        "priority": "high",
        "sample_input": "Optimize LLM inference for production. Current: 2s latency, $0.10/request. Target: 500ms, $0.03/request. Volume: 100K requests/day. Using GPT-4 for all tasks.",
    },
    {
        "id": "ai_collaboration",
        "name": "AI Collaboration Wizard",
        "priority": "high",
        "sample_input": "Design multi-agent system for code review. Agents: style checker, security scanner, performance analyzer, documentation reviewer. Need shared context and conflict resolution.",
    },
    {
        "id": "advanced_debugging",
        "name": "Advanced Debugging Wizard",
        "priority": "high",
        "sample_input": "Debug intermittent failures in LLM application. Symptoms: random timeouts, inconsistent outputs, memory growth. Stack: FastAPI + LangChain + GPT-4. 5% of requests fail.",
    },
    {
        "id": "agent_orchestration",
        "name": "Agent Orchestration Wizard",
        "priority": "critical",
        "sample_input": "Orchestrate 8 specialized agents for enterprise data pipeline: ingestion agent, validation agent, transformation agent, enrichment agent, analysis agent, reporting agent, monitoring agent, alerting agent. Need to handle failures gracefully and maintain data consistency.",
    },
    {
        "id": "enhanced_testing",
        "name": "Enhanced Testing Wizard",
        "priority": "high",
        "sample_input": "Create comprehensive test suite for LLM-powered customer service bot. Test: response quality, safety filters, edge cases, adversarial inputs, performance under load, cost tracking.",
    },
    {
        "id": "ai_documentation",
        "name": "AI Documentation Wizard",
        "priority": "medium",
        "sample_input": "Auto-generate documentation for AI system. Components: 3 LLM models, 5 RAG pipelines, 12 prompt templates, 8 evaluation metrics. Need model cards, prompt docs, and API reference.",
    },
    {
        "id": "prompt_engineering",
        "name": "Prompt Engineering Wizard",
        "priority": "high",
        "sample_input": """Analyze and improve this prompt:
'You are a code reviewer. Review this code and find bugs.'

Current issues: Low consistency, missing security checks, variable output format, no structured response.""",
    },
    {
        "id": "ai_context",
        "name": "AI Context Wizard",
        "priority": "medium",
        "sample_input": "Optimize context window for legal document analysis. Documents: 50-100 pages. Current approach: full doc in context. Issues: hitting 128K limit, slow processing, high cost.",
    },
    {
        "id": "security_analysis",
        "name": "AI Security Analysis Wizard",
        "priority": "critical",
        "sample_input": "Security audit for customer service AI. Capabilities: account lookup, order modifications, refund processing. Concerns: prompt injection, data exfiltration, unauthorized actions, jailbreaking.",
    },
    {
        "id": "ai_testing",
        "name": "AI Testing Wizard",
        "priority": "high",
        "sample_input": "Build evaluation framework for LLM outputs. Tasks: summarization, Q&A, code generation. Metrics needed: accuracy, relevance, safety, latency, cost. Dataset: 1000 test cases.",
    },
]

# Combine all wizards
ALL_WIZARDS = DOMAIN_WIZARDS + SOFTWARE_WIZARDS + AI_WIZARDS


async def _test_single_wizard(client: httpx.AsyncClient, wizard: dict) -> dict:
    """Test a single wizard and return results (internal helper, not a pytest test)"""
    wizard_id = wizard["id"]
    sample_input = wizard.get("sample_input", f"Sample input for {wizard['name']} testing.")

    result = {
        "wizard_id": wizard_id,
        "wizard_name": wizard["name"],
        "priority": wizard.get("priority", "medium"),
        "timestamp": datetime.now().isoformat(),
        "input": sample_input,
        "success": False,
        "output": None,
        "analysis": None,
        "error": None,
    }

    try:
        response = await client.post(
            f"{API_BASE_URL}/api/wizard/{wizard_id}/process",
            json={
                "input": sample_input,
                "user_id": "test_user",
                "context": {"file_path": "test.py", "language": "python"},
            },
        )

        result["http_status"] = response.status_code

        if response.status_code == 200:
            data = response.json()
            result["success"] = data.get("success", False)
            result["output"] = data.get("output", "")
            result["analysis"] = data.get("analysis", {})
            if not result["success"]:
                result["error"] = data.get("error", "Unknown error")
        elif response.status_code == 404:
            result["error"] = "Wizard not loaded"
        else:
            result["error"] = f"HTTP {response.status_code}"

    except Exception as e:
        result["error"] = str(e)

    return result


async def run_all_tests():
    """Run tests on all wizards and save outputs"""
    print("=" * 60)
    print("WIZARD OUTPUT TESTING - ALL 44 WIZARDS")
    print("=" * 60)
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("\nWizard Categories:")
    print(f"  - Domain Wizards: {len(DOMAIN_WIZARDS)}")
    print(f"  - Software Wizards: {len(SOFTWARE_WIZARDS)}")
    print(f"  - AI Wizards: {len(AI_WIZARDS)}")
    print(f"  - TOTAL: {len(ALL_WIZARDS)}")
    print()

    results = []
    summary = {"success": 0, "failed": 0, "not_loaded": 0}

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check API availability
        try:
            health = await client.get(f"{API_BASE_URL}/")
            if health.status_code != 200:
                print("ERROR: API not responding. Start with: python backend/api/wizard_api.py")
                return
            api_info = health.json()
            print(f"API Status: {api_info.get('wizards_loaded', 0)} wizards loaded\n")
        except Exception as e:
            print(f"ERROR: Cannot connect to API at {API_BASE_URL}")
            print("Start backend: python backend/api/wizard_api.py")
            print(f"Error: {e}")
            return

        # Test Domain Wizards
        print("=" * 40)
        print("DOMAIN WIZARDS")
        print("=" * 40)
        for i, wizard in enumerate(DOMAIN_WIZARDS, 1):
            await _run_single_test(client, wizard, i, len(DOMAIN_WIZARDS), results, summary)

        # Test Software Wizards
        print("\n" + "=" * 40)
        print("SOFTWARE WIZARDS")
        print("=" * 40)
        for i, wizard in enumerate(SOFTWARE_WIZARDS, 1):
            await _run_single_test(client, wizard, i, len(SOFTWARE_WIZARDS), results, summary)

        # Test AI Wizards
        print("\n" + "=" * 40)
        print("AI WIZARDS")
        print("=" * 40)
        for i, wizard in enumerate(AI_WIZARDS, 1):
            await _run_single_test(client, wizard, i, len(AI_WIZARDS), results, summary)

    # Save summary
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "api_url": API_BASE_URL,
        "total_tested": len(ALL_WIZARDS),
        "summary": summary,
        "results": results,
    }

    summary_file = OUTPUT_DIR / "test_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2, default=str)

    # Generate markdown report
    report = generate_markdown_report(summary_data)
    report_file = OUTPUT_DIR / "test_report.md"
    with open(report_file, "w") as f:
        f.write(report)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Successful: {summary['success']}/{len(ALL_WIZARDS)}")
    print(f"✗ Failed: {summary['failed']}")
    print(f"⊘ Not loaded: {summary['not_loaded']}")
    print(f"\nOutputs saved to: {OUTPUT_DIR}/")
    print("  - Individual: <wizard_id>_output.json")
    print("  - Summary: test_summary.json")
    print("  - Report: test_report.md")

    # List failed wizards
    if summary["failed"] > 0:
        print("\n⚠️  Failed wizards requiring attention:")
        for r in results:
            if not r["success"] and r.get("error") != "Wizard not loaded":
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(
                    r.get("priority", "medium"), "⚪"
                )
                print(f"  {priority_icon} {r['wizard_name']}: {r.get('error', 'Unknown')[:60]}")


async def _run_single_test(client, wizard, index, total, results, summary):
    """Run a single wizard test"""
    priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
        wizard.get("priority", "medium"), "⚪"
    )

    print(f"[{index}/{total}] {priority_icon} {wizard['name']}...", end=" ", flush=True)

    result = await _test_single_wizard(client, wizard)
    results.append(result)

    if result["success"]:
        summary["success"] += 1
        output_preview = str(result.get("output", ""))[:50].replace("\n", " ")
        print(f"✓ {output_preview}...")
    elif result.get("error") == "Wizard not loaded":
        summary["not_loaded"] += 1
        print("⊘ Not loaded")
    else:
        summary["failed"] += 1
        print(f"✗ {result.get('error', 'Unknown')[:50]}")

    # Save individual wizard output
    output_file = OUTPUT_DIR / f"{wizard['id']}_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, default=str)


def generate_markdown_report(data: dict) -> str:
    """Generate a markdown report of test results"""
    summary = data["summary"]
    results = data["results"]

    report = f"""# Wizard Test Report - All 44 Wizards

**Generated:** {data["timestamp"]}
**API URL:** {data["api_url"]}
**Total Tested:** {data["total_tested"]}

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ✓ Successful | {summary["success"]} | {summary["success"] * 100 // data["total_tested"]}% |
| ✗ Failed | {summary["failed"]} | {summary["failed"] * 100 // data["total_tested"]}% |
| ⊘ Not Loaded | {summary["not_loaded"]} | {summary["not_loaded"] * 100 // data["total_tested"]}% |

## Results by Category

### Domain Wizards ({len(DOMAIN_WIZARDS)})
"""

    for r in results:
        if r["wizard_id"] in [w["id"] for w in DOMAIN_WIZARDS]:
            status = "✓" if r["success"] else "✗" if r.get("error") != "Wizard not loaded" else "⊘"
            report += f"- {status} **{r['wizard_name']}**"
            if not r["success"] and r.get("error"):
                report += f": {r['error'][:50]}"
            report += "\n"

    report += f"\n### Software Wizards ({len(SOFTWARE_WIZARDS)})\n"
    for r in results:
        if r["wizard_id"] in [w["id"] for w in SOFTWARE_WIZARDS]:
            status = "✓" if r["success"] else "✗" if r.get("error") != "Wizard not loaded" else "⊘"
            report += f"- {status} **{r['wizard_name']}**"
            if not r["success"] and r.get("error"):
                report += f": {r['error'][:50]}"
            report += "\n"

    report += f"\n### AI Wizards ({len(AI_WIZARDS)})\n"
    for r in results:
        if r["wizard_id"] in [w["id"] for w in AI_WIZARDS]:
            status = "✓" if r["success"] else "✗" if r.get("error") != "Wizard not loaded" else "⊘"
            report += f"- {status} **{r['wizard_name']}**"
            if not r["success"] and r.get("error"):
                report += f": {r['error'][:50]}"
            report += "\n"

    report += "\n## Sample Outputs\n\n"

    # Include sample successful outputs from each category
    samples_shown = 0
    for r in results:
        if r["success"] and r.get("output") and samples_shown < 6:
            report += f"### {r['wizard_name']}\n\n"
            report += "**Input:**\n```\n"
            report += r["input"][:300]
            if len(r["input"]) > 300:
                report += "..."
            report += "\n```\n\n"
            report += "**Output:**\n```\n"
            output_str = str(r["output"])[:800]
            report += output_str
            if len(str(r["output"])) > 800:
                report += "..."
            report += "\n```\n\n"
            samples_shown += 1

    return report


if __name__ == "__main__":
    asyncio.run(run_all_tests())
