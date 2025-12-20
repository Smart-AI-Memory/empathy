"""
Security Analysis Wizard API

Wraps the SecurityAnalysisWizard for web access.
OWASP pattern detection with exploitability assessment.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/wizards/security", tags=["Security"])


class SecurityScanRequest(BaseModel):
    """Request model for security scanning."""

    code: str | None = Field(default=None, description="Code to scan directly")
    file_paths: list[str] = Field(default_factory=list, description="File paths to scan")
    project_path: str = Field(default=".", description="Project root path")
    exclude_patterns: list[str] = Field(
        default_factory=list, description="Patterns to exclude from scanning"
    )


class CodeSnippetRequest(BaseModel):
    """Request to scan a code snippet."""

    code: str = Field(..., description="Code snippet to analyze")
    language: str = Field(default="python", description="Programming language")
    filename: str = Field(default="snippet.py", description="Virtual filename")


@router.post("/scan")
async def scan_security(request: SecurityScanRequest):
    """
    Scan code for security vulnerabilities.

    This wizard detects OWASP Top 10 vulnerabilities and assesses
    their real-world exploitability, not just theoretical risk.

    Features:
    - OWASP pattern detection (injection, XSS, SSRF, etc.)
    - Exploitability assessment (CRITICAL/HIGH/MEDIUM/LOW)
    - Attack complexity analysis
    - Prioritized recommendations
    - Level 4 predictions about imminent risks
    """
    try:
        from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

        wizard = SecurityAnalysisWizard()

        result = await wizard.analyze(
            {
                "source_files": request.file_paths,
                "project_path": request.project_path,
                "exclude_patterns": request.exclude_patterns,
            }
        )

        return {
            "success": True,
            "wizard": "Security Analysis Wizard",
            "level": 4,
            "result": result,
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Wizard not available: {str(e)}. Install empathy-framework[full]",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-snippet")
async def scan_snippet(request: CodeSnippetRequest):
    """
    Scan a code snippet for security issues.

    Quick analysis of a code snippet without file system access.
    Useful for code review or paste-and-check workflows.
    """
    try:
        from empathy_software_plugin.wizards.security.exploit_analyzer import ExploitAnalyzer
        from empathy_software_plugin.wizards.security.owasp_patterns import OWASPPatternDetector

        detector = OWASPPatternDetector()
        analyzer = ExploitAnalyzer()

        # Detect vulnerabilities
        vulnerabilities = detector.detect_vulnerabilities(request.code, request.filename)

        # Assess exploitability
        assessments = []
        for vuln in vulnerabilities:
            assessment = analyzer.assess_exploitability(vuln, {})
            assessments.append(
                {
                    "vulnerability": vuln,
                    "exploitability": assessment.exploitability,
                    "accessibility": assessment.accessibility,
                    "attack_complexity": assessment.attack_complexity,
                    "exploit_likelihood": assessment.exploit_likelihood,
                    "reasoning": assessment.reasoning,
                    "mitigation_urgency": assessment.mitigation_urgency,
                }
            )

        return {
            "success": True,
            "vulnerabilities_found": len(vulnerabilities),
            "assessments": assessments,
            "language": request.language,
        }

    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Wizard not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo")
async def demo_scan():
    """
    Demo endpoint showing security wizard with vulnerable code sample.
    """
    vulnerable_code = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability!
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

def render_html(user_input):
    # XSS vulnerability!
    return f"<div>{user_input}</div>"
"""

    request = CodeSnippetRequest(code=vulnerable_code, language="python", filename="vulnerable.py")
    return await scan_snippet(request)
