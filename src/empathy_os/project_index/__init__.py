"""Project Index - Codebase Intelligence Layer

Tracks metadata about all files in a project to enable:
- Test coverage gap analysis
- Staleness detection (code changed, tests didn't)
- Dependency mapping
- Project health reports
- Workflow intelligence

Storage:
- Primary: .empathy/project_index.json
- Real-time: Redis (when short-term memory enabled)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .index import ProjectIndex
from .models import FileRecord, IndexConfig, ProjectSummary
from .reports import ReportGenerator
from .scanner import ProjectScanner

__all__ = [
    "FileRecord",
    "IndexConfig",
    "ProjectIndex",
    "ProjectScanner",
    "ProjectSummary",
    "ReportGenerator",
]
