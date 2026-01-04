"""Empathy Healthcare Plugin

Clinical protocol monitoring using the empathy framework.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

__version__ = "1.0.0"

from .monitors.clinical_protocol_monitor import ClinicalProtocolMonitor

__all__ = ["ClinicalProtocolMonitor"]
