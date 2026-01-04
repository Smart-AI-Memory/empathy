"""Code Review Wizard API

Pattern-based code review against historical bug patterns.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/wizards/code-review", tags=["Code Review"])


class CodeReviewRequest(BaseModel):
    """Request model for code review."""

    code: str | None = Field(default=None, description="Code to review directly")
    diff: str | None = Field(default=None, description="Git diff to review")
    file_paths: list[str] = Field(default_factory=list, description="Files to review")
    severity_threshold: str = Field(
        default="info",
        description="Minimum severity (info/warning/error)",
    )


class DiffReviewRequest(BaseModel):
    """Request to review a git diff."""

    diff: str = Field(..., description="Git diff content")
    severity_threshold: str = Field(default="info", description="Minimum severity")


@router.post("/review")
async def review_code(request: CodeReviewRequest):
    """Review code against historical bug patterns.

    This wizard analyzes code using patterns learned from past bugs,
    catching issues before they become production problems.

    Features:
    - Anti-pattern detection (null_reference, async_timing, error_handling)
    - Historical bug correlation
    - Confidence-scored findings
    - Actionable fix suggestions
    - Level 4 predictions about recurring issues
    """
    try:
        from empathy_software_plugin.wizards.code_review_wizard import CodeReviewWizard

        wizard = CodeReviewWizard()

        result = await wizard.analyze(
            {
                "files": request.file_paths,
                "diff": request.diff,
                "severity_threshold": request.severity_threshold,
            },
        )

        return {
            "success": True,
            "wizard": "Code Review Wizard",
            "level": 4,
            "result": result,
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Wizard not available: {e!s}. Install empathy-framework[full]",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review-diff")
async def review_diff(request: DiffReviewRequest):
    """Review a git diff for anti-patterns.

    Quick review of changed code without file system access.
    Perfect for CI/CD integration or pre-commit hooks.
    """
    try:
        from empathy_software_plugin.wizards.code_review_wizard import CodeReviewWizard

        wizard = CodeReviewWizard()

        result = await wizard.analyze(
            {
                "diff": request.diff,
                "severity_threshold": request.severity_threshold,
            },
        )

        return {
            "success": True,
            "wizard": "Code Review Wizard",
            "level": 4,
            "result": result,
            "terminal_output": wizard.format_terminal_output(result),
        }

    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Wizard not available: {e!s}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo")
async def demo_review():
    """Demo endpoint showing code review with sample diff."""
    sample_diff = """diff --git a/src/api.js b/src/api.js
--- a/src/api.js
+++ b/src/api.js
@@ -10,6 +10,12 @@ async function fetchUsers() {
+  const response = await fetch('/api/users');
+  const data = response.json();  // Missing await!
+  return data.users.map(u => u.name);  // Potential null reference
+}
+
+function processData(items) {
+  items.forEach(item => {
+    console.log(item.value);  // No null check
+  });
}"""

    request = DiffReviewRequest(diff=sample_diff, severity_threshold="info")
    return await review_diff(request)
