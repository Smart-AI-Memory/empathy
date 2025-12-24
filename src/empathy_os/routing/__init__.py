"""
Empathy Framework Routing Module

Intelligent request routing to wizards using LLM classification.

Usage:
    from empathy_os.routing import SmartRouter, quick_route

    # Full router
    router = SmartRouter()
    decision = await router.route("Fix security issue in auth.py")
    print(f"Use: {decision.primary_wizard}")

    # Quick helper
    decision = await quick_route("Optimize database queries")

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .chain_executor import ChainConfig, ChainExecution, ChainExecutor, ChainStep, ChainTrigger
from .classifier import ClassificationResult, HaikuClassifier
from .smart_router import RoutingDecision, SmartRouter, quick_route
from .wizard_registry import WIZARD_REGISTRY, WizardInfo, WizardRegistry

__all__ = [
    # Smart Router
    "SmartRouter",
    "RoutingDecision",
    "quick_route",
    # Classifier
    "HaikuClassifier",
    "ClassificationResult",
    # Wizard Registry
    "WizardRegistry",
    "WizardInfo",
    "WIZARD_REGISTRY",
    # Chain Executor
    "ChainExecutor",
    "ChainConfig",
    "ChainExecution",
    "ChainStep",
    "ChainTrigger",
]
