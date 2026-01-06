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
    AdvancedDebuggingWizard,  # noqa: E402
)
from empathy_software_plugin.wizards.agent_orchestration_wizard import (
    AgentOrchestrationWizard,  # noqa: E402
)
from empathy_software_plugin.wizards.ai_collaboration_wizard import (
    AICollaborationWizard,  # noqa: E402
)
from empathy_software_plugin.wizards.ai_context_wizard import AIContextWindowWizard  # noqa: E402
from empathy_software_plugin.wizards.ai_documentation_wizard import (
    AIDocumentationWizard,  # noqa: E402
)
from empathy_software_plugin.wizards.enhanced_testing_wizard import (
    EnhancedTestingWizard,  # noqa: E402
)

# AI wizards (12 total)
from empathy_software_plugin.wizards.multi_model_wizard import MultiModelWizard  # noqa: E402
from empathy_software_plugin.wizards.performance_profiling_wizard import (
    PerformanceProfilingWizard as AIPerformanceWizard,  # noqa: E402
)
from empathy_software_plugin.wizards.prompt_engineering_wizard import (
    PromptEngineeringWizard,  # noqa: E402
)
from empathy_software_plugin.wizards.rag_pattern_wizard import RAGPatternWizard  # noqa: E402
from empathy_software_plugin.wizards.security_analysis_wizard import (
    SecurityAnalysisWizard,  # noqa: E402
)

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


def register_wizard(wizard_id: str, wizard_class: type, *args, **kwargs) -> bool:
    """Register a wizard with proper exception handling.

    This function uses broad exception handling intentionally for graceful degradation.
    Wizards are optional features - the API should start even if some wizards fail.

    Args:
        wizard_id: Unique identifier for the wizard
        wizard_class: Wizard class to instantiate
        *args: Positional arguments for wizard constructor
        **kwargs: Keyword arguments for wizard constructor

    Returns:
        True if wizard was successfully initialized, False otherwise

    Note:
        Uses broad Exception handling for graceful degradation of optional features.
        Full exception context is preserved via logger.exception() for debugging.
    """
    try:
        WIZARDS[wizard_id] = wizard_class(*args, **kwargs)
        logger.info(f"✓ {wizard_class.__name__} initialized as '{wizard_id}'")
        return True
    except ImportError as e:
        # Missing dependencies - common for optional wizards
        logger.warning(f"{wizard_class.__name__} init failed (missing dependency): {e}")
        return False
    except ValueError as e:
        # Configuration errors - invalid arguments, missing API keys, etc.
        logger.warning(f"{wizard_class.__name__} init failed (config error): {e}")
        return False
    except OSError as e:
        # File system errors - missing resources, permission issues
        logger.warning(f"{wizard_class.__name__} init failed (file system error): {e}")
        return False
    except Exception:
        # Catch-all for unexpected wizard initialization errors
        # INTENTIONAL: Ensures API starts even if individual wizards fail
        # Full traceback preserved for debugging
        logger.exception(f"{wizard_class.__name__} init failed (unexpected error)")
        return False


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
    """Initialize all wizard instances with proper exception handling.

    Uses the register_wizard() helper for centralized exception handling.
    Wizards are optional features - API starts even if some wizards fail to initialize.
    """
    global WIZARDS

    # Get shared LLM instance for domain wizards
    try:
        llm = get_llm_instance()
        logger.info("✓ EmpathyLLM instance created")
    except ValueError as e:
        # Missing API key - expected in some environments
        logger.warning(f"EmpathyLLM not available (missing API key): {e}")
        llm = None
    except ImportError as e:
        # Missing dependencies
        logger.warning(f"EmpathyLLM not available (missing dependency): {e}")
        llm = None
    except Exception:
        # Unexpected errors during LLM initialization
        logger.exception("EmpathyLLM initialization failed (unexpected error)")
        llm = None

    # Domain wizards (16 total - require LLM instance)
    if llm:
        register_wizard("healthcare", HealthcareWizard, llm)
        register_wizard("finance", FinanceWizard, llm)
        register_wizard("legal", LegalWizard, llm)
        register_wizard("education", EducationWizard, llm)
        register_wizard("customer_support", CustomerSupportWizard, llm)
        register_wizard("hr", HRWizard, llm)
        register_wizard("sales", SalesWizard, llm)
        register_wizard("real_estate", RealEstateWizard, llm)
        register_wizard("insurance", InsuranceWizard, llm)
        register_wizard("accounting", AccountingWizard, llm)
        register_wizard("research", ResearchWizard, llm)
        register_wizard("government", GovernmentWizard, llm)
        register_wizard("retail", RetailWizard, llm)
        register_wizard("manufacturing", ManufacturingWizard, llm)
        register_wizard("logistics", LogisticsWizard, llm)
        register_wizard("technology", TechnologyWizard, llm)

    # Coach/Software wizards (16 total)
    register_wizard("debugging", DebuggingWizard)
    register_wizard("testing", TestingWizard)
    register_wizard("security_wizard", SecurityWizard)
    register_wizard("documentation", DocumentationWizard)
    register_wizard("performance_wizard", PerformanceWizard)
    register_wizard("refactoring", RefactoringWizard)
    register_wizard("database", DatabaseWizard)
    register_wizard("api_wizard", APIWizard)
    register_wizard("compliance", ComplianceWizard)
    register_wizard("monitoring", MonitoringWizard)
    register_wizard("cicd", CICDWizard)
    register_wizard("accessibility", AccessibilityWizard)
    register_wizard("localization", LocalizationWizard)
    register_wizard("migration", MigrationWizard)
    register_wizard("observability", ObservabilityWizard)
    register_wizard("scaling", ScalingWizard)

    # AI wizards (12 total)
    register_wizard("prompt_engineering", PromptEngineeringWizard)
    register_wizard("multi_model", MultiModelWizard)
    register_wizard("rag_pattern", RAGPatternWizard)
    register_wizard("ai_performance", AIPerformanceWizard)
    register_wizard("ai_collaboration", AICollaborationWizard)
    register_wizard("advanced_debugging", AdvancedDebuggingWizard)
    register_wizard("agent_orchestration", AgentOrchestrationWizard)
    register_wizard("enhanced_testing", EnhancedTestingWizard)
    register_wizard("ai_documentation", AIDocumentationWizard)
    register_wizard("ai_context", AIContextWindowWizard)
    register_wizard("security_analysis", SecurityAnalysisWizard)

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
