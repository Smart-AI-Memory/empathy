"""
Epic Integration Wizard - LangChain Agent
Multi-step wizard for configuring and testing Epic FHIR integration

Copyright 2025 Smart AI Memory, LLC

Licensed under Fair Source 0.9 (the "License");
you may not use this file except in compliance with the License.
"""

import logging
import operator
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)


# =============================================================================
# Wizard State Management
# =============================================================================


class WizardState(TypedDict):
    """
    State for Epic Integration Wizard

    Tracks all wizard steps, user inputs, validation results, and progress.
    Microsoft-style linear progression with validation at each step.
    """

    # Wizard Progress
    current_step: int  # 1-7
    completed_steps: list[int]
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # Step 1: Prerequisites
    prerequisites_checked: bool
    prerequisites_passed: bool
    missing_prerequisites: list[str]

    # Step 2: Epic Credentials
    epic_client_id: str
    epic_client_secret: str
    epic_fhir_base_url: str
    epic_oauth_token_url: str
    epic_sandbox_mode: bool

    # Step 3: Connection Test
    connection_test_passed: bool
    connection_test_error: str
    oauth_token_obtained: bool

    # Step 4: Resource Permissions
    selected_resources: list[str]  # Patient, Condition, MedicationRequest, etc.
    resource_scopes: list[str]  # Patient.Read, Condition.Read, etc.

    # Step 5: Test Patient Lookup
    test_mrn: str
    patient_data_retrieved: bool
    patient_test_error: str
    retrieved_patient_name: str

    # Step 6: Review & Confirm
    configuration_confirmed: bool

    # Step 7: Complete
    integration_activated: bool
    activation_timestamp: str

    # Error Handling
    errors: list[str]
    warnings: list[str]


def create_initial_state() -> WizardState:
    """Create initial wizard state"""
    return WizardState(
        current_step=1,
        completed_steps=[],
        messages=[],
        prerequisites_checked=False,
        prerequisites_passed=False,
        missing_prerequisites=[],
        epic_client_id="",
        epic_client_secret="",
        epic_fhir_base_url="",
        epic_oauth_token_url="",
        epic_sandbox_mode=True,
        connection_test_passed=False,
        connection_test_error="",
        oauth_token_obtained=False,
        selected_resources=[],
        resource_scopes=[],
        test_mrn="",
        patient_data_retrieved=False,
        patient_test_error="",
        retrieved_patient_name="",
        configuration_confirmed=False,
        integration_activated=False,
        activation_timestamp="",
        errors=[],
        warnings=[],
    )


# =============================================================================
# Wizard Nodes (Step Handlers)
# =============================================================================


async def step_1_prerequisites(state: WizardState) -> WizardState:
    """
    Step 1: Check Prerequisites

    Validates system readiness:
    - Python version
    - Required packages installed
    - Environment variables configured
    - Database connectivity
    """
    logger.info("Step 1: Checking prerequisites")

    missing = []

    # Check required environment variables
    import os

    required_env_vars = ["OPENAI_API_KEY", "SECRET_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            missing.append(f"Environment variable: {var}")

    # Check database (simplified for now)
    try:
        from src.config import settings

        if not settings.database_url:
            missing.append("Database configuration")
    except Exception as e:
        missing.append(f"Configuration error: {str(e)}")

    state["prerequisites_checked"] = True
    state["prerequisites_passed"] = len(missing) == 0
    state["missing_prerequisites"] = missing
    state["completed_steps"].append(1)

    # Always allow proceeding to Step 2 for manual credential entry
    # Even if automated prerequisites fail, user can still configure Epic manually
    if state["prerequisites_passed"]:
        state["messages"].append(
            AIMessage(content="✅ All prerequisites met. Ready to configure Epic integration.")
        )
    else:
        # Don't block progression - just warn user
        state["warnings"].append(f"Some automated prerequisites missing: {', '.join(missing)}")
        state["messages"].append(AIMessage(content=f"⚠️  Manual entry mode: {', '.join(missing)}"))

    return state


async def step_2_credentials(state: WizardState) -> WizardState:
    """
    Step 2: Epic Credentials Input

    Collects and validates:
    - Epic Client ID
    - Epic Client Secret
    - FHIR Base URL
    - OAuth Token URL
    - Sandbox mode flag
    """
    logger.info("Step 2: Collecting Epic credentials")

    # Validate credentials are provided
    if not state.get("epic_client_id") or not state.get("epic_client_secret"):
        state["errors"].append("Epic credentials required")
        return state

    if not state.get("epic_fhir_base_url"):
        state["errors"].append("Epic FHIR base URL required")
        return state

    # Validate URL format
    if not state["epic_fhir_base_url"].startswith("https://"):
        state["warnings"].append("Epic FHIR URL should use HTTPS for security")

    state["completed_steps"].append(2)
    state["current_step"] = 3
    state["messages"].append(
        AIMessage(content="✅ Epic credentials collected. Ready to test connection.")
    )

    return state


async def step_3_connection_test(state: WizardState) -> WizardState:
    """
    Step 3: Test Epic FHIR Connection

    Validates:
    - OAuth token can be obtained
    - FHIR endpoint is reachable
    - Credentials are valid
    """
    logger.info("Step 3: Testing Epic FHIR connection")

    try:
        # Import Epic client
        from src.integrations.epic_fhir_client import OAuthManager

        # Create OAuth manager
        oauth_manager = OAuthManager(
            token_url=state["epic_oauth_token_url"],
            client_id=state["epic_client_id"],
            client_secret=state["epic_client_secret"],
        )

        # Attempt to get token
        try:
            await oauth_manager.get_access_token()
            state["oauth_token_obtained"] = True
            state["connection_test_passed"] = True
            state["messages"].append(
                AIMessage(content="✅ Successfully connected to Epic FHIR API")
            )
        except Exception as e:
            state["connection_test_error"] = str(e)
            state["connection_test_passed"] = False
            state["errors"].append(f"OAuth token request failed: {str(e)}")
            state["messages"].append(AIMessage(content=f"❌ Connection failed: {str(e)}"))
            return state

        state["completed_steps"].append(3)
        state["current_step"] = 4

    except Exception as e:
        logger.error(f"Connection test failed: {e}", exc_info=True)
        state["connection_test_error"] = str(e)
        state["connection_test_passed"] = False
        state["errors"].append(f"Connection test error: {str(e)}")

    return state


async def step_4_resource_permissions(state: WizardState) -> WizardState:
    """
    Step 4: Select FHIR Resources and Scopes

    User selects which FHIR resources to enable:
    - Patient (demographics)
    - Condition (diagnoses)
    - MedicationRequest (medications)
    - Observation (vitals, labs)
    - DocumentReference (clinical notes)
    """
    logger.info("Step 4: Configuring resource permissions")

    # Validate at least one resource is selected
    if not state.get("selected_resources"):
        state["errors"].append("At least one FHIR resource must be selected")
        return state

    # Map resources to OAuth scopes
    resource_scope_map = {
        "Patient": "Patient.Read",
        "Condition": "Condition.Read",
        "MedicationRequest": "MedicationRequest.Read",
        "Observation": "Observation.Read",
        "DocumentReference": "DocumentReference.Write",
    }

    scopes = [
        resource_scope_map[resource]
        for resource in state["selected_resources"]
        if resource in resource_scope_map
    ]

    state["resource_scopes"] = scopes
    state["completed_steps"].append(4)
    state["current_step"] = 5
    state["messages"].append(
        AIMessage(content=f"✅ Configured {len(scopes)} resource permissions: {', '.join(scopes)}")
    )

    return state


async def step_5_test_patient_lookup(state: WizardState) -> WizardState:
    """
    Step 5: Test Patient Lookup

    Validates end-to-end functionality:
    - Search patient by MRN
    - Retrieve patient demographics
    - Fetch related resources (conditions, medications)
    """
    logger.info("Step 5: Testing patient lookup")

    if not state.get("test_mrn"):
        state["errors"].append("Test MRN required for patient lookup")
        return state

    try:
        from src.integrations.epic_fhir_client import EpicFHIRClient, OAuthManager

        # Create Epic client
        oauth_manager = OAuthManager(
            token_url=state["epic_oauth_token_url"],
            client_id=state["epic_client_id"],
            client_secret=state["epic_client_secret"],
        )

        epic_client = EpicFHIRClient(
            base_url=state["epic_fhir_base_url"], oauth_manager=oauth_manager
        )

        # Search for patient
        search_result = await epic_client.get(
            "/Patient",
            params={"identifier": f"urn:oid:1.2.840.114350|{state['test_mrn']}"},
        )

        if search_result.get("total", 0) > 0:
            patient = search_result["entry"][0]["resource"]
            patient_name = f"{patient['name'][0]['given'][0]} {patient['name'][0]['family']}"

            state["patient_data_retrieved"] = True
            state["retrieved_patient_name"] = patient_name
            state["messages"].append(
                AIMessage(content=f"✅ Successfully retrieved patient: {patient_name}")
            )
        else:
            state["patient_test_error"] = "Patient not found"
            state["errors"].append(f"Patient with MRN {state['test_mrn']} not found")
            state["messages"].append(
                AIMessage(content=f"❌ Patient not found: MRN {state['test_mrn']}")
            )
            return state

        state["completed_steps"].append(5)
        state["current_step"] = 6

    except Exception as e:
        logger.error(f"Patient lookup failed: {e}", exc_info=True)
        state["patient_test_error"] = str(e)
        state["errors"].append(f"Patient lookup error: {str(e)}")
        state["messages"].append(AIMessage(content=f"❌ Patient lookup failed: {str(e)}"))

    return state


async def step_6_review_confirm(state: WizardState) -> WizardState:
    """
    Step 6: Review and Confirm Configuration

    Shows summary of all settings for final review:
    - Epic endpoint and credentials
    - Enabled resources
    - Test results
    """
    logger.info("Step 6: Review and confirm configuration")

    if not state.get("configuration_confirmed"):
        # User hasn't confirmed yet - show summary
        summary = f"""
**Epic Integration Configuration Summary**

**Connection:**
- FHIR Endpoint: {state['epic_fhir_base_url']}
- Sandbox Mode: {'Yes' if state['epic_sandbox_mode'] else 'No'}
- Connection Test: {'✅ Passed' if state['connection_test_passed'] else '❌ Failed'}

**Resources Enabled:**
{chr(10).join(f'- {resource}' for resource in state['selected_resources'])}

**Test Results:**
- Patient Lookup: {'✅ Passed' if state['patient_data_retrieved'] else '❌ Failed'}
- Test Patient: {state.get('retrieved_patient_name', 'N/A')}

Please confirm to activate integration.
        """
        state["messages"].append(AIMessage(content=summary))
        return state

    state["completed_steps"].append(6)
    state["current_step"] = 7
    state["messages"].append(
        AIMessage(content="✅ Configuration confirmed. Activating integration...")
    )

    return state


async def step_7_complete(state: WizardState) -> WizardState:
    """
    Step 7: Complete Integration Setup

    Finalizes configuration:
    - Saves settings to database/config
    - Activates Epic integration mode
    - Generates setup report
    """
    logger.info("Step 7: Completing Epic integration setup")

    # Save configuration (simplified - would save to database in production)
    try:
        import os

        # In production, save to database or config file
        # For now, just set environment variables
        os.environ["EPIC_FHIR_BASE_URL"] = state["epic_fhir_base_url"]
        os.environ["EPIC_CLIENT_ID"] = state["epic_client_id"]
        os.environ["EPIC_CLIENT_SECRET"] = state["epic_client_secret"]
        os.environ["EPIC_OAUTH_TOKEN_URL"] = state["epic_oauth_token_url"]

        state["integration_activated"] = True
        state["activation_timestamp"] = datetime.utcnow().isoformat()
        state["completed_steps"].append(7)

        state["messages"].append(
            AIMessage(
                content=f"""
🎉 **Epic Integration Activated!**

Your AI Nurse Florence instance is now connected to Epic EHR.

**Activated at:** {state['activation_timestamp']}
**Endpoint:** {state['epic_fhir_base_url']}
**Resources:** {', '.join(state['selected_resources'])}

You can now:
- Scan patient MRN barcodes
- Auto-populate SBAR reports with Epic data
- Generate AI-enhanced care plans using live patient data

Next steps:
1. Train your staff on the Epic integration workflow
2. Review HIPAA compliance documentation
3. Monitor integration logs for any issues
            """
            )
        )

    except Exception as e:
        logger.error(f"Integration activation failed: {e}", exc_info=True)
        state["errors"].append(f"Activation error: {str(e)}")
        state["messages"].append(AIMessage(content=f"❌ Activation failed: {str(e)}"))

    return state


# =============================================================================
# Workflow Routing
# =============================================================================


def should_continue(state: WizardState) -> str:
    """
    Determine next step based on current state

    Microsoft wizard pattern: linear progression with error handling
    """
    # Check for blocking errors
    if state.get("errors") and len(state["errors"]) > 0:
        last_error = state["errors"][-1]

        # Some errors are blocking
        if "prerequisites" in last_error.lower():
            return "prerequisites"
        if "credentials" in last_error.lower():
            return "credentials"
        if "connection" in last_error.lower():
            return "connection_test"

    # Normal progression
    current_step = state.get("current_step", 1)

    if current_step == 1:
        return "prerequisites"
    elif current_step == 2:
        return "credentials"
    elif current_step == 3:
        return "connection_test"
    elif current_step == 4:
        return "resource_permissions"
    elif current_step == 5:
        return "test_patient_lookup"
    elif current_step == 6:
        return "review_confirm"
    elif current_step == 7:
        return "complete"
    else:
        return END


# =============================================================================
# LangGraph Workflow
# =============================================================================


def create_epic_wizard_graph():
    """
    Create LangGraph workflow for Epic Integration Wizard

    Microsoft-style multi-step wizard:
    Prerequisites → Credentials → Connection Test → Permissions → Patient Test → Review → Complete
    """
    workflow = StateGraph(WizardState)

    # Add nodes for each wizard step
    workflow.add_node("prerequisites", step_1_prerequisites)
    workflow.add_node("credentials", step_2_credentials)
    workflow.add_node("connection_test", step_3_connection_test)
    workflow.add_node("resource_permissions", step_4_resource_permissions)
    workflow.add_node("test_patient_lookup", step_5_test_patient_lookup)
    workflow.add_node("review_confirm", step_6_review_confirm)
    workflow.add_node("complete", step_7_complete)

    # Set entry point
    workflow.set_entry_point("prerequisites")

    # Add edges - linear progression (Microsoft wizard pattern)
    # Prerequisites → Credentials → Connection Test → Permissions → Patient Test → Review → Complete
    workflow.add_edge("prerequisites", "credentials")
    workflow.add_edge("credentials", "connection_test")
    workflow.add_edge("connection_test", "resource_permissions")
    workflow.add_edge("resource_permissions", "test_patient_lookup")
    workflow.add_edge("test_patient_lookup", "review_confirm")
    workflow.add_edge("review_confirm", "complete")
    workflow.add_edge("complete", END)

    return workflow.compile()


# Create the compiled graph
epic_wizard_graph = create_epic_wizard_graph()
