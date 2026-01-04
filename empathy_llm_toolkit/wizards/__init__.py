"""Empathy LLM Wizards - Canonical Examples

Core wizard base class and canonical domain examples demonstrating
the Empathy Framework's capabilities across different use cases.

Included Wizards (3 canonical examples):
1. HealthcareWizard - HIPAA-compliant medical assistant
2. CustomerSupportWizard - Customer service and help desk
3. TechnologyWizard - IT and software development operations

Additional Wizards Available:
For specialized domain wizards, install separate packages:
- Healthcare (23 wizards): pip install empathy-healthcare-wizards
- Tech & AI (16 wizards): pip install empathy-software-wizards
- Business (12+ wizards): pip install empathy-business-wizards

Or try the live dashboards:
- Healthcare: https://healthcare.smartaimemory.com/static/dashboard.html
- Tech & AI: https://wizards.smartaimemory.com/

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .base_wizard import BaseWizard, WizardConfig
from .customer_support_wizard import CustomerSupportWizard
from .healthcare_wizard import HealthcareWizard
from .technology_wizard import TechnologyWizard

__all__ = [
    # Base classes
    "BaseWizard",
    # Canonical domain examples
    "CustomerSupportWizard",
    "HealthcareWizard",
    "TechnologyWizard",
    "WizardConfig",
]
