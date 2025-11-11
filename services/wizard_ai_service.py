"""
Wizard AI Service using LangChain
Provides AI-powered assistance for clinical wizards
"""

import logging
import os
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Pydantic models for structured outputs
class SepsisAssessment(BaseModel):
    """Structured output for sepsis screening suggestions"""

    suspected_infection_source: str = Field(description="Most likely source of infection")
    risk_factors_present: list[str] = Field(description="List of identified risk factors")
    qsofa_prediction: dict[str, Any] = Field(description="Predicted qSOFA score components")
    recommended_interventions: list[str] = Field(
        description="Recommended sepsis bundle interventions"
    )
    clinical_reasoning: str = Field(description="Brief clinical reasoning for suggestions")


class StrokeAssessment(BaseModel):
    """Structured output for stroke assessment suggestions"""

    cincinnati_findings: dict[str, str] = Field(description="Cincinnati Stroke Scale findings")
    nihss_predictions: dict[str, int] = Field(description="Predicted NIHSS component scores")
    tpa_eligible: bool = Field(description="Whether patient appears tPA eligible")
    contraindications: list[str] = Field(description="Any tPA contraindications identified")
    time_critical_actions: list[str] = Field(description="Immediate actions needed")
    clinical_reasoning: str = Field(description="Brief clinical reasoning")


class CardiacAssessment(BaseModel):
    """Structured output for cardiac assessment suggestions"""

    heart_score_components: dict[str, int] = Field(description="HEART score component predictions")
    ecg_findings: dict[str, Any] = Field(description="Predicted ECG findings")
    stemi_alert: bool = Field(description="Whether STEMI criteria may be met")
    recommended_interventions: list[str] = Field(description="Recommended cardiac interventions")
    disposition_recommendation: str = Field(description="Suggested disposition")
    clinical_reasoning: str = Field(description="Brief clinical reasoning")


class WizardAIService:
    """
    Service for providing AI-powered assistance to clinical wizards using LangChain
    """

    def __init__(self):
        """Initialize the wizard AI service with LangChain"""
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3,  # Lower temperature for clinical accuracy
            max_tokens=2000,
        )

    async def suggest_sepsis_assessment(
        self,
        patient_context: dict[str, Any],
        current_vitals: dict[str, Any] | None = None,
        recent_labs: dict[str, Any] | None = None,
    ) -> SepsisAssessment:
        """
        Provide AI-powered suggestions for sepsis screening wizard

        Args:
            patient_context: Patient demographics, history, medications
            current_vitals: Current vital signs
            recent_labs: Recent laboratory values

        Returns:
            SepsisAssessment with AI-generated suggestions
        """
        parser = JsonOutputParser(pydantic_object=SepsisAssessment)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert clinical nurse assistant specializing in sepsis recognition.
Analyze the patient information and provide structured suggestions for the sepsis screening wizard.

Focus on:
- Identifying likely infection sources based on symptoms and history
- Predicting qSOFA score components (respiratory rate, mental status, blood pressure)
- Recommending appropriate sepsis bundle interventions
- Providing clear clinical reasoning

{format_instructions}""",
                ),
                (
                    "human",
                    """Patient Context:
{patient_context}

Current Vitals:
{current_vitals}

Recent Labs:
{recent_labs}

Provide sepsis screening suggestions with clear clinical reasoning.""",
                ),
            ]
        )

        chain = prompt | self.llm | parser

        try:
            result = await chain.ainvoke(
                {
                    "patient_context": str(patient_context),
                    "current_vitals": str(current_vitals or "Not provided"),
                    "recent_labs": str(recent_labs or "Not provided"),
                    "format_instructions": parser.get_format_instructions(),
                }
            )

            return SepsisAssessment(**result)

        except Exception as e:
            logger.error(f"Error in sepsis assessment: {e}")
            # Return safe default
            return SepsisAssessment(
                suspected_infection_source="Unknown - manual assessment required",
                risk_factors_present=[],
                qsofa_prediction={
                    "respiratory_rate": 0,
                    "mental_status": 0,
                    "systolic_bp": 0,
                },
                recommended_interventions=["Manual clinical assessment recommended"],
                clinical_reasoning="AI suggestion unavailable - proceed with manual assessment",
            )

    async def suggest_stroke_assessment(
        self,
        patient_context: dict[str, Any],
        symptom_onset_time: str,
        current_symptoms: dict[str, Any],
    ) -> StrokeAssessment:
        """
        Provide AI-powered suggestions for stroke assessment wizard

        Args:
            patient_context: Patient demographics and history
            symptom_onset_time: When symptoms began
            current_symptoms: Current neurological symptoms

        Returns:
            StrokeAssessment with AI-generated suggestions
        """
        parser = JsonOutputParser(pydantic_object=StrokeAssessment)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert stroke nurse specialist.
Analyze the patient information and provide structured suggestions for the stroke assessment wizard.

Focus on:
- Cincinnati Stroke Scale assessment (facial droop, arm drift, speech)
- Predicting NIHSS score components based on symptoms
- Evaluating tPA eligibility based on time window and contraindications
- Identifying time-critical actions

{format_instructions}""",
                ),
                (
                    "human",
                    """Patient Context:
{patient_context}

Symptom Onset Time:
{symptom_onset_time}

Current Symptoms:
{current_symptoms}

Provide stroke assessment suggestions with focus on tPA eligibility.""",
                ),
            ]
        )

        chain = prompt | self.llm | parser

        try:
            result = await chain.ainvoke(
                {
                    "patient_context": str(patient_context),
                    "symptom_onset_time": symptom_onset_time,
                    "current_symptoms": str(current_symptoms),
                    "format_instructions": parser.get_format_instructions(),
                }
            )

            return StrokeAssessment(**result)

        except Exception as e:
            logger.error(f"Error in stroke assessment: {e}")
            return StrokeAssessment(
                cincinnati_findings={},
                nihss_predictions={},
                tpa_eligible=False,
                contraindications=["Manual assessment required"],
                time_critical_actions=["Complete manual Cincinnati and NIHSS assessment"],
                clinical_reasoning="AI suggestion unavailable - proceed with manual assessment",
            )

    async def suggest_cardiac_assessment(
        self,
        patient_context: dict[str, Any],
        chest_pain_characteristics: dict[str, Any],
        vital_signs: dict[str, Any],
    ) -> CardiacAssessment:
        """
        Provide AI-powered suggestions for cardiac assessment wizard

        Args:
            patient_context: Patient demographics, history, risk factors
            chest_pain_characteristics: Description of chest pain
            vital_signs: Current vital signs

        Returns:
            CardiacAssessment with AI-generated suggestions
        """
        parser = JsonOutputParser(pydantic_object=CardiacAssessment)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert cardiac care nurse.
Analyze the patient information and provide structured suggestions for the cardiac assessment wizard.

Focus on:
- Calculating HEART score components (History, ECG, Age, Risk factors, Troponin)
- Predicting ECG findings based on symptoms
- Identifying STEMI criteria
- Recommending appropriate cardiac interventions
- Suggesting disposition based on risk stratification

{format_instructions}""",
                ),
                (
                    "human",
                    """Patient Context:
{patient_context}

Chest Pain Characteristics:
{chest_pain_characteristics}

Vital Signs:
{vital_signs}

Provide cardiac assessment suggestions with HEART score and disposition recommendation.""",
                ),
            ]
        )

        chain = prompt | self.llm | parser

        try:
            result = await chain.ainvoke(
                {
                    "patient_context": str(patient_context),
                    "chest_pain_characteristics": str(chest_pain_characteristics),
                    "vital_signs": str(vital_signs),
                    "format_instructions": parser.get_format_instructions(),
                }
            )

            return CardiacAssessment(**result)

        except Exception as e:
            logger.error(f"Error in cardiac assessment: {e}")
            return CardiacAssessment(
                heart_score_components={},
                ecg_findings={},
                stemi_alert=False,
                recommended_interventions=["Complete manual cardiac assessment"],
                disposition_recommendation="Manual risk stratification required",
                clinical_reasoning="AI suggestion unavailable - proceed with manual assessment",
            )

    async def suggest_wizard_field(
        self,
        wizard_type: str,
        field_name: str,
        patient_context: dict[str, Any],
        current_wizard_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Provide AI suggestion for a specific wizard field

        Args:
            wizard_type: Type of wizard (sepsis, stroke, cardiac, etc.)
            field_name: Name of the field to suggest value for
            patient_context: Full patient context
            current_wizard_data: Data already entered in wizard

        Returns:
            Dict with suggested value and reasoning
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a clinical nurse assistant helping with documentation.
Provide a concise, evidence-based suggestion for the requested field.
Return JSON with 'suggested_value' and 'reasoning' keys.""",
                ),
                (
                    "human",
                    """Wizard Type: {wizard_type}
Field: {field_name}
Patient Context: {patient_context}
Current Data: {current_wizard_data}

Suggest an appropriate value for this field with brief clinical reasoning.""",
                ),
            ]
        )

        chain = prompt | self.llm | JsonOutputParser()

        try:
            result = await chain.ainvoke(
                {
                    "wizard_type": wizard_type,
                    "field_name": field_name,
                    "patient_context": str(patient_context),
                    "current_wizard_data": str(current_wizard_data),
                }
            )

            return result

        except Exception as e:
            logger.error(f"Error suggesting wizard field: {e}")
            return {
                "suggested_value": None,
                "reasoning": "AI suggestion unavailable - manual entry recommended",
            }


# Singleton instance
_wizard_ai_service: WizardAIService | None = None


def get_wizard_ai_service() -> WizardAIService:
    """Get or create singleton wizard AI service instance"""
    global _wizard_ai_service
    if _wizard_ai_service is None:
        _wizard_ai_service = WizardAIService()
    return _wizard_ai_service
