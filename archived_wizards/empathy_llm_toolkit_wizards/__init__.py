"""
Empathy LLM Wizards - Security-Aware AI Assistants

Specialized AI wizards built on EmpathyLLM with integrated security controls.
Each wizard is optimized for specific domains with appropriate security policies.

Available Wizards (16 total):
1. HealthcareWizard - HIPAA-compliant medical assistant
2. FinanceWizard - SOX/PCI-DSS banking and finance
3. LegalWizard - Attorney-client privilege legal services
4. EducationWizard - FERPA-compliant academic support
5. CustomerSupportWizard - Customer service and help desk
6. HRWizard - Employee privacy compliant HR
7. SalesWizard - CRM privacy compliant sales and marketing
8. RealEstateWizard - Property data privacy compliant
9. InsuranceWizard - Policy data privacy compliant
10. AccountingWizard - SOX/IRS compliant accounting and tax
11. ResearchWizard - IRB-compliant academic research
12. GovernmentWizard - FISMA-compliant government services
13. RetailWizard - PCI-DSS compliant retail and e-commerce
14. ManufacturingWizard - Production data privacy compliant
15. LogisticsWizard - Shipment data privacy compliant
16. TechnologyWizard - IT security compliant operations

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .accounting_wizard import AccountingWizard
from .base_wizard import BaseWizard, WizardConfig
from .customer_support_wizard import CustomerSupportWizard
from .education_wizard import EducationWizard
from .finance_wizard import FinanceWizard
from .government_wizard import GovernmentWizard
from .healthcare_wizard import HealthcareWizard
from .hr_wizard import HRWizard
from .insurance_wizard import InsuranceWizard
from .legal_wizard import LegalWizard
from .logistics_wizard import LogisticsWizard
from .manufacturing_wizard import ManufacturingWizard
from .real_estate_wizard import RealEstateWizard
from .research_wizard import ResearchWizard
from .retail_wizard import RetailWizard
from .sales_wizard import SalesWizard
from .technology_wizard import TechnologyWizard

__all__ = [
    # Base classes
    "BaseWizard",
    "WizardConfig",
    # Domain-specific wizards (alphabetical)
    "AccountingWizard",
    "CustomerSupportWizard",
    "EducationWizard",
    "FinanceWizard",
    "GovernmentWizard",
    "HealthcareWizard",
    "HRWizard",
    "InsuranceWizard",
    "LegalWizard",
    "LogisticsWizard",
    "ManufacturingWizard",
    "RealEstateWizard",
    "ResearchWizard",
    "RetailWizard",
    "SalesWizard",
    "TechnologyWizard",
]
