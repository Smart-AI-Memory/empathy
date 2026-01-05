#!/usr/bin/env python3
"""Empathy Wizard API - Real Wizard Integration
Connects React dashboard to actual wizard implementations.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging  # noqa: E402
from typing import Any  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from coach_wizards.accessibility_wizard import AccessibilityWizard  # noqa: E402
from coach_wizards.api_wizard import APIWizard  # noqa: E402
from coach_wizards.cicd_wizard import CICDWizard  # noqa: E402
from coach_wizards.compliance_wizard import ComplianceWizard  # noqa: E402
from coach_wizards.database_wizard import DatabaseWizard  # noqa: E402

# Coach/Software wizards (16 total)
from coach_wizards.debugging_wizard import DebuggingWizard  # noqa: E402
from coach_wizards.documentation_wizard import DocumentationWizard  # noqa: E402
from coach_wizards.localization_wizard import LocalizationWizard  # noqa: E402
from coach_wizards.migration_wizard import MigrationWizard  # noqa: E402
from coach_wizards.monitoring_wizard import MonitoringWizard  # noqa: E402
from coach_wizards.observability_wizard import ObservabilityWizard  # noqa: E402
from coach_wizards.performance_wizard import PerformanceWizard  # noqa: E402
from coach_wizards.refactoring_wizard import RefactoringWizard  # noqa: E402
from coach_wizards.scaling_wizard import ScalingWizard  # noqa: E402
from coach_wizards.security_wizard import SecurityWizard  # noqa: E402
from coach_wizards.testing_wizard import TestingWizard  # noqa: E402

# Import wizard implementations
from empathy_llm_toolkit import EmpathyLLM  # noqa: E402
from empathy_llm_toolkit.wizards.accounting_wizard import AccountingWizard  # noqa: E402
from empathy_llm_toolkit.wizards.customer_support_wizard import CustomerSupportWizard  # noqa: E402
from empathy_llm_toolkit.wizards.education_wizard import EducationWizard  # noqa: E402
from empathy_llm_toolkit.wizards.finance_wizard import FinanceWizard  # noqa: E402
from empathy_llm_toolkit.wizards.government_wizard import GovernmentWizard  # noqa: E402

# Domain wizards (16 total)
from empathy_llm_toolkit.wizards.healthcare_wizard import HealthcareWizard  # noqa: E402
from empathy_llm_toolkit.wizards.hr_wizard import HRWizard  # noqa: E402
from empathy_llm_toolkit.wizards.insurance_wizard import InsuranceWizard  # noqa: E402
from empathy_llm_toolkit.wizards.legal_wizard import LegalWizard  # noqa: E402
from empathy_llm_toolkit.wizards.logistics_wizard import LogisticsWizard  # noqa: E402
from empathy_llm_toolkit.wizards.manufacturing_wizard import ManufacturingWizard  # noqa: E402
from empathy_llm_toolkit.wizards.real_estate_wizard import RealEstateWizard  # noqa: E402
from empathy_llm_toolkit.wizards.research_wizard import ResearchWizard  # noqa: E402
from empathy_llm_toolkit.wizards.retail_wizard import RetailWizard  # noqa: E402
from empathy_llm_toolkit.wizards.sales_wizard import SalesWizard  # noqa: E402
from empathy_llm_toolkit.wizards.technology_wizard import TechnologyWizard  # noqa: E402
from empathy_software_plugin.wizards.advanced_debugging_wizard import (
    AdvancedDebuggingWizard,
)  # noqa: E402
from empathy_software_plugin.wizards.agent_orchestration_wizard import (
    AgentOrchestrationWizard,
)  # noqa: E402
from empathy_software_plugin.wizards.ai_collaboration_wizard import (
    AICollaborationWizard,
)  # noqa: E402
from empathy_software_plugin.wizards.ai_context_wizard import AIContextWindowWizard  # noqa: E402
from empathy_software_plugin.wizards.ai_documentation_wizard import (
    AIDocumentationWizard,
)  # noqa: E402
from empathy_software_plugin.wizards.enhanced_testing_wizard import (
    EnhancedTestingWizard,
)  # noqa: E402

# AI wizards (12 total)
from empathy_software_plugin.wizards.multi_model_wizard import MultiModelWizard  # noqa: E402
from empathy_software_plugin.wizards.performance_profiling_wizard import (
    PerformanceProfilingWizard as AIPerformanceWizard,
)  # noqa: E402
from empathy_software_plugin.wizards.prompt_engineering_wizard import (
    PromptEngineeringWizard,
)  # noqa: E402
from empathy_software_plugin.wizards.rag_pattern_wizard import RAGPatternWizard  # noqa: E402
from empathy_software_plugin.wizards.security_analysis_wizard import (
    SecurityAnalysisWizard,
)  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize shared LLM instance for domain wizards
def get_llm_instance():
    """Get or create EmpathyLLM instance.

    Raises:
        ValueError: If ANTHROPIC_API_KEY environment variable is not set.

    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is required. "
            "Set it in your .env file or environment before starting the API.",
        )

    return EmpathyLLM(
        provider="anthropic",
        api_key=api_key,
        enable_security=True,
        enable_audit_logging=True,
    )


app = FastAPI(title="Empathy Wizard API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class WizardRequest(BaseModel):
    input: str
    context: dict[str, Any] | None = None
    user_id: str | None = "demo_user"


class WizardResponse(BaseModel):
    success: bool
    output: str
    analysis: dict[str, Any] | None = None
    error: str | None = None


# Initialize wizards
WIZARDS = {}


def init_wizards():
    """Initialize all wizard instances"""
    global WIZARDS

    # Get shared LLM instance for domain wizards
    try:
        llm = get_llm_instance()
        logger.info("✓ EmpathyLLM instance created")
    except Exception as e:
        logger.error(f"Failed to create EmpathyLLM: {e}")
        llm = None

    # Domain wizards (16 total - require LLM instance)
    if llm:
        # Healthcare domain
        try:
            WIZARDS["healthcare"] = HealthcareWizard(llm)
            logger.info("✓ Healthcare Wizard initialized")
        except Exception as e:
            logger.warning(f"Healthcare Wizard init failed: {e}")

        try:
            WIZARDS["finance"] = FinanceWizard(llm)
            logger.info("✓ Finance Wizard initialized")
        except Exception as e:
            logger.warning(f"Finance Wizard init failed: {e}")

        try:
            WIZARDS["legal"] = LegalWizard(llm)
            logger.info("✓ Legal Wizard initialized")
        except Exception as e:
            logger.warning(f"Legal Wizard init failed: {e}")

        try:
            WIZARDS["education"] = EducationWizard(llm)
            logger.info("✓ Education Wizard initialized")
        except Exception as e:
            logger.warning(f"Education Wizard init failed: {e}")

        try:
            WIZARDS["customer_support"] = CustomerSupportWizard(llm)
            logger.info("✓ Customer Support Wizard initialized")
        except Exception as e:
            logger.warning(f"Customer Support Wizard init failed: {e}")

        try:
            WIZARDS["hr"] = HRWizard(llm)
            logger.info("✓ HR Wizard initialized")
        except Exception as e:
            logger.warning(f"HR Wizard init failed: {e}")

        try:
            WIZARDS["sales"] = SalesWizard(llm)
            logger.info("✓ Sales Wizard initialized")
        except Exception as e:
            logger.warning(f"Sales Wizard init failed: {e}")

        try:
            WIZARDS["real_estate"] = RealEstateWizard(llm)
            logger.info("✓ Real Estate Wizard initialized")
        except Exception as e:
            logger.warning(f"Real Estate Wizard init failed: {e}")

        try:
            WIZARDS["insurance"] = InsuranceWizard(llm)
            logger.info("✓ Insurance Wizard initialized")
        except Exception as e:
            logger.warning(f"Insurance Wizard init failed: {e}")

        try:
            WIZARDS["accounting"] = AccountingWizard(llm)
            logger.info("✓ Accounting Wizard initialized")
        except Exception as e:
            logger.warning(f"Accounting Wizard init failed: {e}")

        try:
            WIZARDS["research"] = ResearchWizard(llm)
            logger.info("✓ Research Wizard initialized")
        except Exception as e:
            logger.warning(f"Research Wizard init failed: {e}")

        try:
            WIZARDS["government"] = GovernmentWizard(llm)
            logger.info("✓ Government Wizard initialized")
        except Exception as e:
            logger.warning(f"Government Wizard init failed: {e}")

        try:
            WIZARDS["retail"] = RetailWizard(llm)
            logger.info("✓ Retail Wizard initialized")
        except Exception as e:
            logger.warning(f"Retail Wizard init failed: {e}")

        try:
            WIZARDS["manufacturing"] = ManufacturingWizard(llm)
            logger.info("✓ Manufacturing Wizard initialized")
        except Exception as e:
            logger.warning(f"Manufacturing Wizard init failed: {e}")

        try:
            WIZARDS["logistics"] = LogisticsWizard(llm)
            logger.info("✓ Logistics Wizard initialized")
        except Exception as e:
            logger.warning(f"Logistics Wizard init failed: {e}")

        try:
            WIZARDS["technology"] = TechnologyWizard(llm)
            logger.info("✓ Technology Wizard initialized")
        except Exception as e:
            logger.warning(f"Technology Wizard init failed: {e}")

    # Coach/Software wizards (16 total)
    try:
        WIZARDS["debugging"] = DebuggingWizard()
        logger.info("✓ Debugging Wizard initialized")
    except Exception as e:
        logger.warning(f"Debugging Wizard init failed: {e}")

    try:
        WIZARDS["testing"] = TestingWizard()
        logger.info("✓ Testing Wizard initialized")
    except Exception as e:
        logger.warning(f"Testing Wizard init failed: {e}")

    try:
        WIZARDS["security_wizard"] = SecurityWizard()
        logger.info("✓ Security Wizard initialized")
    except Exception as e:
        logger.warning(f"Security Wizard init failed: {e}")

    try:
        WIZARDS["documentation"] = DocumentationWizard()
        logger.info("✓ Documentation Wizard initialized")
    except Exception as e:
        logger.warning(f"Documentation Wizard init failed: {e}")

    try:
        WIZARDS["performance_wizard"] = PerformanceWizard()
        logger.info("✓ Performance Wizard initialized")
    except Exception as e:
        logger.warning(f"Performance Wizard init failed: {e}")

    try:
        WIZARDS["refactoring"] = RefactoringWizard()
        logger.info("✓ Refactoring Wizard initialized")
    except Exception as e:
        logger.warning(f"Refactoring Wizard init failed: {e}")

    try:
        WIZARDS["database"] = DatabaseWizard()
        logger.info("✓ Database Wizard initialized")
    except Exception as e:
        logger.warning(f"Database Wizard init failed: {e}")

    try:
        WIZARDS["api_wizard"] = APIWizard()
        logger.info("✓ API Wizard initialized")
    except Exception as e:
        logger.warning(f"API Wizard init failed: {e}")

    try:
        WIZARDS["compliance"] = ComplianceWizard()
        logger.info("✓ Compliance Wizard initialized")
    except Exception as e:
        logger.warning(f"Compliance Wizard init failed: {e}")

    try:
        WIZARDS["monitoring"] = MonitoringWizard()
        logger.info("✓ Monitoring Wizard initialized")
    except Exception as e:
        logger.warning(f"Monitoring Wizard init failed: {e}")

    try:
        WIZARDS["cicd"] = CICDWizard()
        logger.info("✓ CI/CD Wizard initialized")
    except Exception as e:
        logger.warning(f"CI/CD Wizard init failed: {e}")

    try:
        WIZARDS["accessibility"] = AccessibilityWizard()
        logger.info("✓ Accessibility Wizard initialized")
    except Exception as e:
        logger.warning(f"Accessibility Wizard init failed: {e}")

    try:
        WIZARDS["localization"] = LocalizationWizard()
        logger.info("✓ Localization Wizard initialized")
    except Exception as e:
        logger.warning(f"Localization Wizard init failed: {e}")

    try:
        WIZARDS["migration"] = MigrationWizard()
        logger.info("✓ Migration Wizard initialized")
    except Exception as e:
        logger.warning(f"Migration Wizard init failed: {e}")

    try:
        WIZARDS["observability"] = ObservabilityWizard()
        logger.info("✓ Observability Wizard initialized")
    except Exception as e:
        logger.warning(f"Observability Wizard init failed: {e}")

    try:
        WIZARDS["scaling"] = ScalingWizard()
        logger.info("✓ Scaling Wizard initialized")
    except Exception as e:
        logger.warning(f"Scaling Wizard init failed: {e}")

    # AI wizards (12 total)
    try:
        WIZARDS["prompt_engineering"] = PromptEngineeringWizard()
        logger.info("✓ Prompt Engineering Wizard initialized")
    except Exception as e:
        logger.warning(f"Prompt Engineering Wizard init failed: {e}")

    try:
        WIZARDS["multi_model"] = MultiModelWizard()
        logger.info("✓ Multi-Model Wizard initialized")
    except Exception as e:
        logger.warning(f"Multi-Model Wizard init failed: {e}")

    try:
        WIZARDS["rag_pattern"] = RAGPatternWizard()
        logger.info("✓ RAG Pattern Wizard initialized")
    except Exception as e:
        logger.warning(f"RAG Pattern Wizard init failed: {e}")

    try:
        WIZARDS["ai_performance"] = AIPerformanceWizard()
        logger.info("✓ AI Performance Wizard initialized")
    except Exception as e:
        logger.warning(f"AI Performance Wizard init failed: {e}")

    try:
        WIZARDS["ai_collaboration"] = AICollaborationWizard()
        logger.info("✓ AI Collaboration Wizard initialized")
    except Exception as e:
        logger.warning(f"AI Collaboration Wizard init failed: {e}")

    try:
        WIZARDS["advanced_debugging"] = AdvancedDebuggingWizard()
        logger.info("✓ Advanced Debugging Wizard initialized")
    except Exception as e:
        logger.warning(f"Advanced Debugging Wizard init failed: {e}")

    try:
        WIZARDS["agent_orchestration"] = AgentOrchestrationWizard()
        logger.info("✓ Agent Orchestration Wizard initialized")
    except Exception as e:
        logger.warning(f"Agent Orchestration Wizard init failed: {e}")

    try:
        WIZARDS["enhanced_testing"] = EnhancedTestingWizard()
        logger.info("✓ Enhanced Testing Wizard initialized")
    except Exception as e:
        logger.warning(f"Enhanced Testing Wizard init failed: {e}")

    try:
        WIZARDS["ai_documentation"] = AIDocumentationWizard()
        logger.info("✓ AI Documentation Wizard initialized")
    except Exception as e:
        logger.warning(f"AI Documentation Wizard init failed: {e}")

    try:
        WIZARDS["ai_context"] = AIContextWindowWizard()
        logger.info("✓ AI Context Window Wizard initialized")
    except Exception as e:
        logger.warning(f"AI Context Window Wizard init failed: {e}")

    try:
        WIZARDS["security_analysis"] = SecurityAnalysisWizard()
        logger.info("✓ Security Analysis Wizard initialized")
    except Exception as e:
        logger.warning(f"Security Analysis Wizard init failed: {e}")

    logger.info(f"🧙 Initialized {len(WIZARDS)} wizards")


@app.on_event("startup")
async def startup_event():
    """Initialize wizards on startup"""
    init_wizards()


@app.get("/")
async def root():
    return {
        "service": "Empathy Wizard API",
        "version": "2.0.0",
        "wizards_loaded": len(WIZARDS),
        "available_wizards": list(WIZARDS.keys()),
    }


@app.post("/api/wizard/{wizard_id}/process")
async def process_wizard(wizard_id: str, request: WizardRequest) -> WizardResponse:
    """Process input with specified wizard"""
    if wizard_id not in WIZARDS:
        raise HTTPException(
            status_code=404,
            detail=f"Wizard '{wizard_id}' not found. Available: {list(WIZARDS.keys())}",
        )

    wizard = WIZARDS[wizard_id]

    try:
        # Call wizard with input
        if hasattr(wizard, "process"):
            # Domain wizards (healthcare, finance, legal, education, etc.)
            result = await wizard.process(
                user_input=request.input,
                user_id=request.user_id,
                context=request.context or {},
            )

            return WizardResponse(
                success=True,
                output=result.get("response", ""),
                analysis={
                    "classification": result.get("classification"),
                    "pii_detected": result.get("pii_detected", []),
                    "compliance": result.get("compliance", []),
                    "confidence": result.get("confidence", 0.0),
                },
            )

        if hasattr(wizard, "analyze_code"):
            # Coach wizards (debugging, security, api, testing, etc.)
            issues = wizard.analyze_code(
                code=request.input,
                file_path=(
                    request.context.get("file_path", "demo.py") if request.context else "demo.py"
                ),
                language=request.context.get("language", "python") if request.context else "python",
            )

            # Format issues
            output_lines = []
            for issue in issues:
                output_lines.append(
                    f"[{issue.severity.upper()}] Line {issue.line}: {issue.message}",
                )
                if issue.suggestion:
                    output_lines.append(f"  💡 {issue.suggestion}")

            return WizardResponse(
                success=True,
                output="\n".join(output_lines) if output_lines else "✓ No issues found",
                analysis={
                    "issues_found": len(issues),
                    "issues": [
                        {
                            "severity": issue.severity,
                            "line": issue.line,
                            "message": issue.message,
                            "suggestion": issue.suggestion,
                        }
                        for issue in issues
                    ],
                },
            )

        if hasattr(wizard, "analyze"):
            # AI wizards (prompt_engineering, multi_model, rag_pattern, etc.)
            context = request.context or {}
            context["user_input"] = request.input

            result = await wizard.analyze(context)

            # Format AI wizard output
            output_parts = []

            if result.get("issues"):
                output_parts.append("Issues:")
                for issue in result["issues"][:5]:  # Top 5
                    output_parts.append(
                        f"  - [{issue.get('severity', 'info').upper()}] {issue.get('message', 'N/A')}",
                    )

            if result.get("recommendations"):
                output_parts.append("\nRecommendations:")
                for rec in result["recommendations"][:5]:  # Top 5
                    output_parts.append(f"  - {rec}")

            if result.get("predictions"):
                output_parts.append("\nPredictions:")
                for pred in result["predictions"][:3]:  # Top 3
                    output_parts.append(f"  - {pred.get('alert', pred.get('type', 'N/A'))}")

            return WizardResponse(
                success=True,
                output="\n".join(output_parts) if output_parts else "Analysis complete",
                analysis={
                    "issues": result.get("issues", []),
                    "predictions": result.get("predictions", []),
                    "recommendations": result.get("recommendations", []),
                    "confidence": result.get("confidence", 0.0),
                    "patterns": result.get("patterns", []),
                },
            )

        raise HTTPException(
            status_code=500,
            detail=f"Wizard '{wizard_id}' has unknown interface",
        )

    except Exception as e:
        logger.error(f"Error processing with {wizard_id}: {e}", exc_info=True)
        return WizardResponse(success=False, output="", error=str(e))


@app.get("/api/wizards")
async def get_wizards():
    """Get list of available wizards"""
    return {
        "wizards": [
            {
                "id": wizard_id,
                "name": wizard.__class__.__name__,
                "loaded": True,
                "type": "domain" if hasattr(wizard, "process") else "coach",
            }
            for wizard_id, wizard in WIZARDS.items()
        ],
        "total": len(WIZARDS),
    }


if __name__ == "__main__":
    import uvicorn

    print("🧙 Starting Empathy Wizard API at http://localhost:8001")
    print(f"📁 Project root: {project_root}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
