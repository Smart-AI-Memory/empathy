"""Code Inspection Pipeline API

Wraps the CodeInspectionAgent for web access.
Unified code analysis with parallel execution and cross-tool intelligence.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/wizards/inspect", tags=["Code Inspection"])


class InspectRequest(BaseModel):
    """Request model for code inspection."""

    project_path: str = Field(default=".", description="Project root to inspect")
    target_mode: str = Field(
        default="all",
        description="Target mode: all, staged, changed, or paths",
    )
    target_paths: list[str] = Field(default_factory=list, description="Specific paths to inspect")
    exclude_patterns: list[str] = Field(
        default_factory=list,
        description="Glob patterns to exclude",
    )
    output_format: str = Field(
        default="json",
        description="Output format: json, terminal, markdown, sarif, html",
    )
    parallel_mode: bool = Field(default=True, description="Run analysis in parallel")
    learning_enabled: bool = Field(default=True, description="Enable pattern learning")
    baseline_enabled: bool = Field(default=True, description="Apply baseline suppression")


class QuickScanRequest(BaseModel):
    """Request for quick project scan."""

    project_path: str = Field(..., description="Project root to scan")
    output_format: str = Field(default="json", description="Output format")


@router.post("/run")
async def run_inspection(request: InspectRequest):
    """Run the full code inspection pipeline.

    This is the main empathy-inspect command as an API.

    Pipeline phases:
    1. Static Analysis (parallel): lint, security, tech debt, test quality
    2. Dynamic Analysis (conditional): code review, debugging triggers
    3. Cross-Analysis: correlate findings across tools
    4. Learning: extract patterns for future use
    5. Reporting: unified health score and recommendations

    Output formats:
    - json: Machine-readable results
    - terminal: Human-readable CLI output
    - markdown: Documentation-friendly format
    - sarif: GitHub Actions / CI integration
    - html: Professional dashboard report
    """
    try:
        from agents.code_inspection import CodeInspectionAgent

        agent = CodeInspectionAgent(
            parallel_mode=request.parallel_mode,
            learning_enabled=request.learning_enabled,
            baseline_enabled=request.baseline_enabled,
        )

        state = await agent.inspect(
            project_path=request.project_path,
            target_mode=request.target_mode,
            target_paths=request.target_paths or None,
            exclude_patterns=request.exclude_patterns or None,
            output_format=request.output_format,
        )

        # Format report
        report = agent.format_report(state, request.output_format)

        return {
            "success": True,
            "wizard": "Code Inspection Pipeline",
            "health_score": state.get("overall_health_score", 0),
            "health_status": state.get("health_status", "unknown"),
            "total_findings": state.get("total_findings", 0),
            "categories": {
                "lint": state.get("lint_results", {}).get("findings_count", 0),
                "security": state.get("security_results", {}).get("findings_count", 0),
                "tech_debt": state.get("tech_debt_results", {}).get("findings_count", 0),
                "test_quality": state.get("test_quality_results", {}).get("findings_count", 0),
            },
            "report": report,
            "format": request.output_format,
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Inspection agent not available: {e!s}. Install empathy-framework[full]",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick")
async def quick_scan(request: QuickScanRequest):
    """Quick project health scan.

    Runs a fast inspection with default settings.
    Good for quick health checks.
    """
    full_request = InspectRequest(
        project_path=request.project_path,
        output_format=request.output_format,
        parallel_mode=True,
        learning_enabled=False,  # Skip learning for speed
    )
    return await run_inspection(full_request)


@router.get("/formats")
async def list_formats():
    """List available output formats."""
    return {
        "formats": [
            {
                "name": "json",
                "description": "Machine-readable JSON output",
                "use_case": "API integration, programmatic access",
            },
            {
                "name": "terminal",
                "description": "Human-readable CLI output with colors",
                "use_case": "Command line usage, quick review",
            },
            {
                "name": "markdown",
                "description": "Markdown-formatted report",
                "use_case": "Documentation, PR comments",
            },
            {
                "name": "sarif",
                "description": "Static Analysis Results Interchange Format",
                "use_case": "GitHub Actions, Azure DevOps, GitLab CI",
            },
            {
                "name": "html",
                "description": "Professional HTML dashboard",
                "use_case": "Stakeholder reports, sprint reviews",
            },
        ],
    }


@router.get("/demo")
async def demo_inspection():
    """Demo endpoint showing inspection capabilities.

    Returns sample output showing what a full inspection looks like.
    """
    return {
        "success": True,
        "wizard": "Code Inspection Pipeline",
        "demo": True,
        "sample_output": {
            "health_score": 85,
            "health_status": "pass",
            "total_findings": 12,
            "categories": {
                "lint": {"findings": 5, "severity": {"warning": 4, "info": 1}},
                "security": {"findings": 2, "severity": {"high": 1, "medium": 1}},
                "tech_debt": {"findings": 3, "items": {"todo": 2, "fixme": 1}},
                "test_quality": {"findings": 2, "coverage_gaps": 2},
            },
            "predictions": [
                {
                    "type": "security_priority",
                    "description": "1 high-severity security finding needs immediate attention",
                },
            ],
            "recommendations": [
                "Fix SQL injection in api/users.py:42",
                "Add null check in components/UserList.tsx:15",
                "Resolve 3 TODO items before next release",
            ],
        },
    }
