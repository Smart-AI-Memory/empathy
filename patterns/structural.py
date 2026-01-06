"""Structural patterns for wizard architecture.

Structural patterns define the overall flow and organization of a wizard:
- Linear Flow: Step-by-step wizard with review and approval
- Phased Processing: Multi-phase pipeline for complex analysis
- Session-Based: State management with session storage

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from typing import Literal

from pydantic import BaseModel, Field

from .core import BasePattern, CodeGeneratorMixin, PatternCategory


class StepConfig(BaseModel):
    """Configuration for a single wizard step."""

    step: int = Field(..., description="Step number (1-indexed)", ge=1)
    title: str = Field(..., description="Step title displayed to user")
    prompt: str = Field(..., description="Instructional prompt for this step")
    fields: list[str] = Field(..., description="List of field names to collect")
    help_text: str = Field(..., description="Help text explaining the step")
    is_review_step: bool = Field(
        default=False,
        description="Whether this is a review/approval step",
    )


class LinearFlowPattern(BasePattern, CodeGeneratorMixin):
    """Linear multi-step wizard pattern.

    **Description:**
    A wizard that guides users through a fixed sequence of steps, culminating
    in a review step where they can preview and approve the final output.

    **Usage:** 16 wizards (SOAP Note, SBAR, Care Plan, etc.)
    **Reusability:** 0.9 (highly reusable)

    **Key Features:**
    - Fixed step sequence (no branching)
    - Session-based state management
    - Preview before finalization
    - Explicit user approval required

    **Generated Endpoints:**
    - POST /start - Initialize wizard session
    - POST /{wizard_id}/step - Submit step data
    - POST /{wizard_id}/preview - Generate preview
    - POST /{wizard_id}/save - Finalize with approval
    - GET /{wizard_id}/report - Retrieve completed report
    """

    category: Literal[PatternCategory.STRUCTURAL] = PatternCategory.STRUCTURAL
    total_steps: int = Field(..., description="Total number of steps", ge=2)
    steps: dict[int, StepConfig] = Field(
        ..., description="Step configurations keyed by step number"
    )
    requires_approval: bool = Field(
        default=True,
        description="Whether final step requires user approval",
    )
    session_storage: Literal["redis", "memory"] = Field(
        default="redis",
        description="Session storage backend (redis preferred, memory fallback)",
    )

    def generate_endpoint_list(self) -> list[str]:
        """Generate list of FastAPI endpoints for this wizard."""
        return [
            "POST /start",
            "POST /{wizard_id}/step",
            "POST /{wizard_id}/preview",
            "POST /{wizard_id}/save",
            "GET /{wizard_id}/report",
        ]

    def generate_code(self) -> str:
        """Generate FastAPI router skeleton for linear flow wizard."""
        endpoints = "\n".join(f"    - {endpoint}" for endpoint in self.generate_endpoint_list())

        return f'''
"""Linear Flow Wizard - Generated from LinearFlowPattern

Total Steps: {self.total_steps}
Requires Approval: {self.requires_approval}
Session Storage: {self.session_storage}

Endpoints:
{endpoints}
"""

from fastapi import APIRouter, HTTPException
from typing import Any
from uuid import uuid4
from datetime import datetime

router = APIRouter()

# Step configuration
WIZARD_STEPS = {{
{self._generate_step_configs()}
}}


@router.post("/start")
async def start_wizard():
    """Initialize wizard session"""
    wizard_id = str(uuid4())

    session_data = {{
        "wizard_id": wizard_id,
        "current_step": 1,
        "total_steps": {self.total_steps},
        "collected_data": {{}},
        "created_at": datetime.now().isoformat(),
    }}

    # Store session (implement _store_session)
    await _store_session(wizard_id, session_data)

    return {{"wizard_id": wizard_id, "current_step": WIZARD_STEPS[1]}}


@router.post("/{{wizard_id}}/step")
async def submit_step(wizard_id: str, step_data: dict[str, Any]):
    """Submit data for current step"""
    session = await _get_session(wizard_id)
    if not session:
        raise HTTPException(404, "Wizard session not found")

    current_step = session["current_step"]
    submitted_step = step_data.get("step", current_step)

    # Validate step sequence
    if submitted_step != current_step:
        raise HTTPException(
            422,
            f"Expected step {{current_step}}, got step {{submitted_step}}"
        )

    # Store data and advance
    session["collected_data"].update(step_data.get("data", {{}}))
    if current_step < {self.total_steps}:
        session["current_step"] = current_step + 1

    await _store_session(wizard_id, session)

    return {{"current_step": WIZARD_STEPS[session["current_step"]]}}


@router.post("/{{wizard_id}}/preview")
async def preview_report(wizard_id: str):
    """Generate preview without finalizing"""
    session = await _get_session(wizard_id)
    if not session:
        raise HTTPException(404, "Wizard session not found")

    if session["current_step"] != {self.total_steps}:
        raise HTTPException(400, "Complete all steps before preview")

    preview = _generate_report(session["collected_data"])
    session["preview_report"] = preview
    await _store_session(wizard_id, session)

    return {{"preview": preview}}


@router.post("/{{wizard_id}}/save")
async def save_report(wizard_id: str, approval: dict[str, Any]):
    """Finalize report with user approval"""
    session = await _get_session(wizard_id)
    if not session:
        raise HTTPException(404, "Wizard session not found")

    if "preview_report" not in session:
        raise HTTPException(400, "Must generate preview first")

    if not approval.get("user_approved", False):
        raise HTTPException(400, "User approval required")

    session["completed"] = True
    session["completed_at"] = datetime.now().isoformat()
    session["final_report"] = session["preview_report"]

    await _store_session(wizard_id, session)

    return {{"report": session["final_report"], "completed": True}}


@router.get("/{{wizard_id}}/report")
async def get_report(wizard_id: str):
    """Retrieve completed report"""
    session = await _get_session(wizard_id)
    if not session:
        raise HTTPException(404, "Wizard session not found")

    if not session.get("completed", False):
        raise HTTPException(422, "Wizard not yet completed")

    return {{"report": _generate_report(session["collected_data"])}}


# Helper functions (implement these)
async def _store_session(wizard_id: str, session_data: dict):
    """Store wizard session in {self.session_storage}"""
    pass


async def _get_session(wizard_id: str) -> dict | None:
    """Retrieve wizard session from {self.session_storage}"""
    pass


def _generate_report(collected_data: dict) -> dict:
    """Generate final report from collected data"""
    pass
'''

    def _generate_step_configs(self) -> str:
        """Generate Python dict literal for step configurations."""
        lines = []
        for step_num, step_config in sorted(self.steps.items()):
            lines.append(f"    {step_num}: {{")
            lines.append(f'        "step": {step_config.step},')
            lines.append(f'        "title": "{step_config.title}",')
            lines.append(f'        "prompt": "{step_config.prompt}",')
            lines.append(f'        "fields": {step_config.fields},')
            lines.append(f'        "help_text": "{step_config.help_text}",')
            if step_config.is_review_step:
                lines.append('        "is_review_step": True,')
            lines.append("    },")
        return "\n".join(lines)


class PhaseConfig(BaseModel):
    """Configuration for a processing phase."""

    name: str = Field(..., description="Phase name (e.g., 'parse', 'analyze')")
    description: str = Field(..., description="What this phase does")
    required: bool = Field(
        default=True,
        description="Whether this phase is required",
    )
    parallel_with: list[str] = Field(
        default_factory=list,
        description="Phases that can run in parallel with this one",
    )


class PhasedProcessingPattern(BasePattern, CodeGeneratorMixin):
    """Multi-phase processing pipeline pattern.

    **Description:**
    A wizard that processes input through multiple sequential or parallel phases,
    where each phase performs a specific transformation or analysis step.

    **Usage:** 12 wizards (Advanced Debugging, Security Analysis, Performance Profiling)
    **Reusability:** 0.85

    **Key Features:**
    - Sequential phase execution
    - Optional parallel phases
    - Context passed between phases
    - Comprehensive result aggregation

    **Common Phases:**
    - Parse: Extract structured data from input
    - Load Config: Load wizard/tool configuration
    - Analyze: Perform core analysis
    - Fix/Transform: Apply changes
    - Verify: Confirm results

    **Generated Method:**
    async def analyze(context: dict) -> dict
    """

    category: Literal[PatternCategory.STRUCTURAL] = PatternCategory.STRUCTURAL
    phases: list[PhaseConfig] = Field(..., description="List of processing phases in order")

    def generate_code(self) -> str:
        """Generate analyze() method skeleton with phases."""
        phase_implementations = []

        for i, phase in enumerate(self.phases, 1):
            parallel_info = ""
            if phase.parallel_with:
                parallel_info = f"  # Can run in parallel with: {', '.join(phase.parallel_with)}"

            phase_implementations.append(
                f"""
        # Phase {i}: {phase.description}{parallel_info}
        logger.info("Phase {i}: {phase.name}")
        {phase.name}_result = await self._{phase.name}(context)
        context["{phase.name}_result"] = {phase.name}_result
"""
            )

        phases_code = "".join(phase_implementations)

        return f'''
"""Phased Processing Wizard - Generated from PhasedProcessingPattern

Phases:
{self._generate_phase_list()}
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PhasedWizard:
    """Multi-phase processing wizard"""

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute all processing phases.

        Args:
            context: Input context with wizard-specific data

        Returns:
            Comprehensive analysis results from all phases
        """
{phases_code}

        # Aggregate results
        return {{
            "success": True,
{self._generate_result_fields()}
            "metadata": {{
                "phases_executed": {len(self.phases)},
                "context_keys": list(context.keys()),
            }},
        }}

{self._generate_phase_methods()}
'''

    def _generate_phase_list(self) -> str:
        """Generate formatted list of phases."""
        lines = []
        for i, phase in enumerate(self.phases, 1):
            required = "REQUIRED" if phase.required else "OPTIONAL"
            lines.append(f"  {i}. {phase.name} ({required}): {phase.description}")
        return "\n".join(lines)

    def _generate_result_fields(self) -> str:
        """Generate result dictionary fields."""
        lines = []
        for phase in self.phases:
            lines.append(f'            "{phase.name}": {phase.name}_result,')
        return "\n".join(lines)

    def _generate_phase_methods(self) -> str:
        """Generate stub methods for each phase."""
        methods = []
        for phase in self.phases:
            methods.append(
                f'''
    async def _{phase.name}(self, context: dict[str, Any]) -> dict[str, Any]:
        """Phase: {phase.description}

        Args:
            context: Shared context from previous phases

        Returns:
            Phase-specific results
        """
        # TODO: Implement {phase.name} phase
        return {{"status": "not_implemented"}}
'''
            )
        return "\n".join(methods)


class SessionBasedPattern(BasePattern):
    """Session-based wizard with state management.

    **Description:**
    Wizards that maintain state across multiple requests using session storage
    (Redis preferred, memory fallback).

    **Usage:** 16 wizards (all healthcare wizards)
    **Reusability:** 0.95

    **Key Features:**
    - Session ID generation (UUID)
    - State persistence (Redis + memory fallback)
    - TTL management (auto-expiration)
    - State recovery

    **Session Data Structure:**
    - wizard_id: Unique session identifier
    - current_step: Current step number
    - collected_data: User input data
    - created_at/updated_at: Timestamps
    - preview_report: Generated preview (optional)
    - completed: Boolean flag
    """

    category: Literal[PatternCategory.STRUCTURAL] = PatternCategory.STRUCTURAL
    session_ttl_seconds: int = Field(
        default=7200,
        description="Session TTL in seconds (default: 2 hours)",
        ge=60,
    )
    storage_backend: Literal["redis", "memory", "both"] = Field(
        default="both",
        description="Session storage backend",
    )
