"""Onboarding Wizard

Knowledge transfer, new developer ramp-up, codebase tours, and learning paths.
Uses Empathy Framework Level 3 (Proactive) for knowledge gap detection and Level 4
(Anticipatory) for predicting onboarding bottlenecks and learning challenges.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from typing import Any

from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)


class OnboardingWizard(BaseWizard):
    """Wizard for developer onboarding and knowledge transfer

    Uses:
    - Level 2: Guide new developers through codebase
    - Level 3: Proactively identify knowledge gaps
    - Level 4: Anticipate onboarding challenges and learning curve issues
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is an onboarding task"""
        # High-priority onboarding phrases (worth 2 points each)
        onboarding_phrases = [
            "onboarding",
            "onboard",
            "new developer",
            "ramp up",
            "knowledge transfer",
        ]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "learning",
            "documentation",
            "training",
            "tutorial",
            "getting started",
            "setup",
            "introduction",
            "new hire",
            "new team member",
            "codebase tour",
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Count high-priority matches (2 points each)
        primary_matches = sum(2 for phrase in onboarding_phrases if phrase in task_lower)

        # Count secondary matches (1 point each)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)  # 6+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute onboarding workflow"""
        # Step 1: Assess emotional context
        self._assess_emotional_state(task)

        # Step 2: Extract constraints
        self._extract_constraints(task)

        # Step 3: Analyze onboarding requirements
        diagnosis = self._analyze_onboarding_requirements(task)

        # Step 4: Detect knowledge gaps (Level 3: Proactive)
        knowledge_gaps = self._detect_knowledge_gaps(task)

        # Step 5: Create learning path
        learning_path = self._create_learning_path(task, knowledge_gaps)

        # Step 6: Generate codebase tour
        codebase_tour = self._generate_codebase_tour(task)

        # Step 7: Create glossary
        glossary = self._create_glossary(task)

        # Step 8: Generate interactive tutorials
        tutorials = self._generate_tutorials(task, knowledge_gaps)

        # Step 9: Predict onboarding challenges (Level 4: Anticipatory)
        onboarding_forecast = self._predict_onboarding_challenges(task, knowledge_gaps)

        # Step 10: Identify risks
        risks = self._identify_risks(task, learning_path)

        # Step 11: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Onboarding Guide",
                content=self._generate_onboarding_guide(diagnosis, learning_path),
            ),
            WizardArtifact(type="doc", title="Codebase Architecture Tour", content=codebase_tour),
            WizardArtifact(type="doc", title="Project Glossary", content=glossary),
            WizardArtifact(type="doc", title="Interactive Tutorials", content=tutorials),
            WizardArtifact(
                type="checklist",
                title="30-60-90 Day Onboarding Checklist",
                content=self._create_onboarding_checklist(task),
            ),
            WizardArtifact(
                type="doc",
                title="Onboarding Success Forecast",
                content=onboarding_forecast,
            ),
        ]

        # Step 12: Generate next actions
        next_actions = learning_path[:5] + self._generate_anticipatory_actions(task)

        # Step 13: Create empathy checks
        empathy_checks = EmpathyChecks(
            cognitive="Considered new developer constraints: learning curve, unfamiliar tech stack, information overload",
            emotional="Acknowledged: Starting a new role is stressful and overwhelming",
            anticipatory=(
                onboarding_forecast[:200] + "..."
                if len(onboarding_forecast) > 200
                else onboarding_forecast
            ),
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=learning_path,
            artifacts=artifacts,
            risks=risks,
            handoffs=self._create_handoffs(task),
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_onboarding_requirements(self, task: WizardTask) -> str:
        """Analyze onboarding requirements"""
        analysis = "# Onboarding Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        # Categorize onboarding needs
        categories = []
        task_lower = (task.task + " " + task.context).lower()

        if any(kw in task_lower for kw in ["codebase", "architecture", "code"]):
            categories.append("Codebase Understanding")
        if any(kw in task_lower for kw in ["setup", "environment", "install"]):
            categories.append("Development Environment Setup")
        if any(kw in task_lower for kw in ["process", "workflow", "git", "deploy"]):
            categories.append("Development Workflows")
        if any(kw in task_lower for kw in ["team", "culture", "communication"]):
            categories.append("Team Integration")
        if any(kw in task_lower for kw in ["domain", "business", "product"]):
            categories.append("Domain Knowledge")

        if not categories:
            categories.append("General Onboarding")

        analysis += f"**Category**: {', '.join(categories)}\n\n"
        analysis += f"**Target Role**: {task.role}\n"
        analysis += (
            f"**Context**: {task.context[:300]}...\n"
            if len(task.context) > 300
            else f"**Context**: {task.context}\n"
        )

        return analysis

    def _detect_knowledge_gaps(self, task: WizardTask) -> list[dict[str, Any]]:
        """Detect knowledge gaps (Level 3: Proactive)"""
        gaps = []

        task_lower = (task.task + " " + task.context).lower()

        # Technical knowledge gaps
        if any(kw in task_lower for kw in ["python", "backend", "api"]):
            gaps.append(
                {
                    "area": "Python Backend Development",
                    "priority": "high",
                    "description": "Understanding FastAPI, async patterns, database ORM",
                    "resources": [
                        "Read: FastAPI documentation (https://fastapi.tiangolo.com)",
                        "Tutorial: Build a simple REST API",
                        "Code review: Review existing API endpoints",
                    ],
                },
            )

        if any(kw in task_lower for kw in ["react", "frontend", "ui"]):
            gaps.append(
                {
                    "area": "React Frontend Development",
                    "priority": "high",
                    "description": "Understanding React hooks, state management, component patterns",
                    "resources": [
                        "Read: React documentation (https://react.dev)",
                        "Tutorial: Build a simple component",
                        "Pair programming: Work with senior frontend dev",
                    ],
                },
            )

        # Architecture knowledge gaps
        gaps.append(
            {
                "area": "System Architecture",
                "priority": "high",
                "description": "Understanding how services communicate, data flow, deployment",
                "resources": [
                    "Review: Architecture diagram (C4 model)",
                    "Read: Architecture Decision Records (ADRs)",
                    "Meeting: Architecture walkthrough with tech lead",
                ],
            },
        )

        # Process knowledge gaps
        gaps.append(
            {
                "area": "Development Workflow",
                "priority": "medium",
                "description": "Git workflow, code review process, deployment pipeline",
                "resources": [
                    "Read: CONTRIBUTING.md",
                    "Shadow: Watch a complete feature development cycle",
                    "Practice: Submit first PR with guidance",
                ],
            },
        )

        # Domain knowledge gaps
        gaps.append(
            {
                "area": "Business Domain",
                "priority": "medium",
                "description": "Understanding business model, user personas, key features",
                "resources": [
                    "Read: Product documentation",
                    "Meeting: Product manager overview session",
                    "Hands-on: Use the product as an end-user",
                ],
            },
        )

        return gaps

    def _create_learning_path(self, task: WizardTask, gaps: list[dict]) -> list[str]:
        """Create structured learning path"""
        path = ["## 30-60-90 Day Learning Path\n"]

        path.append("\n### Days 1-30: Foundation")
        path.append("1. **Environment Setup** (Days 1-2)")
        path.append("   - Install development tools")
        path.append("   - Clone repositories")
        path.append("   - Run application locally")
        path.append("   - Deploy to personal dev environment")

        path.append("\n2. **Codebase Familiarization** (Days 3-10)")
        path.append("   - Read architecture documentation")
        path.append("   - Walk through main code paths")
        path.append("   - Run and debug tests")
        path.append("   - Make small documentation fixes")

        path.append("\n3. **First Contribution** (Days 11-20)")
        path.append("   - Pick up 'good first issue' ticket")
        path.append("   - Submit first PR with mentor support")
        path.append("   - Participate in code review")
        path.append("   - Fix a small bug")

        path.append("\n4. **Domain Learning** (Days 21-30)")
        path.append("   - Shadow customer support tickets")
        path.append("   - Meet with product team")
        path.append("   - Review user analytics")
        path.append("   - Use product from end-user perspective")

        path.append("\n\n### Days 31-60: Building Competence")
        path.append("5. **Independent Feature Work** (Days 31-45)")
        path.append("   - Own a small feature end-to-end")
        path.append("   - Write tests for your code")
        path.append("   - Deploy to staging")
        path.append("   - Participate in planning meetings")

        path.append("\n6. **Deep Dive Areas** (Days 46-60)")
        for gap in gaps[:2]:  # Focus on top 2 priority gaps
            path.append(f"   - Study: {gap['area']}")
            path.append(f"     - {gap['resources'][0]}")

        path.append("\n\n### Days 61-90: Full Contribution")
        path.append("7. **Complex Feature Ownership** (Days 61-80)")
        path.append("   - Lead a medium-sized feature")
        path.append("   - Collaborate with cross-functional team")
        path.append("   - Present work in team demo")

        path.append("\n8. **Knowledge Sharing** (Days 81-90)")
        path.append("   - Update documentation based on learnings")
        path.append("   - Help next new hire with onboarding")
        path.append("   - Present learnings to team")

        return path

    def _generate_codebase_tour(self, task: WizardTask) -> str:
        """Generate interactive codebase tour"""
        tour = "# Codebase Architecture Tour\n\n"

        tour += "## Project Structure\n\n"
        tour += "```\n"
        tour += "project/\n"
        tour += "├── src/                    # Source code\n"
        tour += "│   ├── api/               # API endpoints (REST/GraphQL)\n"
        tour += "│   ├── models/            # Database models (ORM)\n"
        tour += "│   ├── services/          # Business logic layer\n"
        tour += "│   ├── utils/             # Shared utilities\n"
        tour += "│   └── config.py          # Configuration management\n"
        tour += "├── tests/                 # Test suite\n"
        tour += "│   ├── unit/              # Unit tests (fast)\n"
        tour += "│   ├── integration/       # Integration tests\n"
        tour += "│   └── e2e/               # End-to-end tests\n"
        tour += "├── docs/                  # Documentation\n"
        tour += "│   ├── architecture/      # Architecture Decision Records\n"
        tour += "│   ├── api/               # API documentation\n"
        tour += "│   └── guides/            # How-to guides\n"
        tour += "├── .github/               # GitHub Actions CI/CD\n"
        tour += "├── docker/                # Docker configurations\n"
        tour += "└── requirements.txt       # Python dependencies\n"
        tour += "```\n\n"

        tour += "## Key Components\n\n"

        tour += "### 1. API Layer (`src/api/`)\n"
        tour += "**Purpose**: HTTP request handling, input validation, response formatting\n\n"
        tour += "**Key files**:\n"
        tour += "- `src/api/routes/users.py`: User management endpoints\n"
        tour += "- `src/api/routes/auth.py`: Authentication endpoints\n"
        tour += "- `src/api/middleware.py`: Request/response middleware\n\n"
        tour += "**Start here**: `src/api/main.py` (application entry point)\n\n"

        tour += "### 2. Service Layer (`src/services/`)\n"
        tour += "**Purpose**: Business logic, orchestration, external integrations\n\n"
        tour += "**Key files**:\n"
        tour += "- `src/services/user_service.py`: User-related business logic\n"
        tour += "- `src/services/email_service.py`: Email notification handling\n"
        tour += "- `src/services/payment_service.py`: Payment processing\n\n"
        tour += "**Pattern**: Controllers call services, services contain business logic\n\n"

        tour += "### 3. Data Layer (`src/models/`)\n"
        tour += "**Purpose**: Database schema, ORM models, data access\n\n"
        tour += "**Key files**:\n"
        tour += "- `src/models/user.py`: User model and database schema\n"
        tour += "- `src/models/database.py`: Database connection management\n\n"
        tour += "**ORM**: SQLAlchemy (or Django ORM, depending on framework)\n\n"

        tour += "## Data Flow Example\n\n"
        tour += "**User Registration Flow**:\n"
        tour += "1. **Request**: `POST /api/v1/users` → `src/api/routes/users.py`\n"
        tour += "2. **Validation**: Pydantic model validates input\n"
        tour += "3. **Business Logic**: `src/services/user_service.py::create_user()`\n"
        tour += "   - Hash password\n"
        tour += "   - Check if email already exists\n"
        tour += "   - Create user in database\n"
        tour += "   - Send welcome email\n"
        tour += "4. **Data Access**: `src/models/user.py::User.create()`\n"
        tour += "5. **Response**: Return user object (201 Created)\n\n"

        tour += "## Important Patterns\n\n"

        tour += "### Dependency Injection\n"
        tour += "```python\n"
        tour += "# Services are injected, not instantiated directly\n"
        tour += "def create_user(user_data: UserCreate, user_service: UserService = Depends()):\n"
        tour += "    return user_service.create(user_data)\n"
        tour += "```\n\n"

        tour += "### Error Handling\n"
        tour += "```python\n"
        tour += "# Custom exceptions are caught by middleware\n"
        tour += "from src.exceptions import UserAlreadyExistsError\n\n"
        tour += "if user_exists:\n"
        tour += '    raise UserAlreadyExistsError(f"User {email} already exists")\n'
        tour += "```\n\n"

        tour += "### Configuration\n"
        tour += "```python\n"
        tour += "# Environment-based config (12-factor app)\n"
        tour += "from src.config import settings\n\n"
        tour += "DATABASE_URL = settings.DATABASE_URL\n"
        tour += "API_KEY = settings.API_KEY\n"
        tour += "```\n\n"

        tour += "## Next Steps\n"
        tour += "1. Run the app locally: `python -m src.api.main`\n"
        tour += "2. Read the API docs: `http://localhost:8000/docs`\n"
        tour += "3. Run tests: `pytest tests/`\n"
        tour += "4. Make a small change: Add a log statement and see it in action\n"

        return tour

    def _create_glossary(self, task: WizardTask) -> str:
        """Create project-specific glossary"""
        glossary = "# Project Glossary\n\n"
        glossary += "Common terms, acronyms, and concepts used in this codebase.\n\n"

        glossary += "## Technical Terms\n\n"
        glossary += "| Term | Definition |\n"
        glossary += "|------|------------|\n"
        glossary += "| **API** | Application Programming Interface - HTTP endpoints for client communication |\n"
        glossary += "| **ORM** | Object-Relational Mapping - Database abstraction layer (e.g., SQLAlchemy) |\n"
        glossary += "| **JWT** | JSON Web Token - Authentication token format |\n"
        glossary += "| **CRUD** | Create, Read, Update, Delete - Basic database operations |\n"
        glossary += (
            "| **DTO** | Data Transfer Object - Object for transferring data between layers |\n"
        )
        glossary += "| **Middleware** | Code that runs before/after request handling (auth, logging, etc.) |\n"
        glossary += "| **Migration** | Database schema change script (versioned) |\n"
        glossary += "| **Serializer** | Converts objects to/from JSON |\n\n"

        glossary += "## Project-Specific Terms\n\n"
        glossary += "| Term | Definition |\n"
        glossary += "|------|------------|\n"
        glossary += "| **User** | End-user account in the system |\n"
        glossary += "| **Tenant** | Multi-tenant isolation unit (organization) |\n"
        glossary += "| **Workspace** | User's project or collaboration space |\n"
        glossary += "| **Session** | Authenticated user session (managed via JWT) |\n"
        glossary += "| **Webhook** | Event callback to external system |\n\n"

        glossary += "## Acronyms\n\n"
        glossary += "| Acronym | Meaning |\n"
        glossary += "|---------|----------|\n"
        glossary += "| **ADR** | Architecture Decision Record |\n"
        glossary += "| **CI/CD** | Continuous Integration / Continuous Deployment |\n"
        glossary += "| **PR** | Pull Request |\n"
        glossary += "| **TDD** | Test-Driven Development |\n"
        glossary += "| **RBAC** | Role-Based Access Control |\n"
        glossary += "| **SLA** | Service Level Agreement |\n"
        glossary += "| **SLO** | Service Level Objective |\n\n"

        glossary += "## Code Conventions\n\n"
        glossary += "- **Snake_case**: Variables and functions (`user_service`, `create_user`)\n"
        glossary += "- **PascalCase**: Classes and models (`UserService`, `UserModel`)\n"
        glossary += "- **UPPER_CASE**: Constants (`DATABASE_URL`, `MAX_RETRIES`)\n"
        glossary += "- **Async functions**: Prefix with `async def` for async operations\n"
        glossary += "- **Private methods**: Prefix with `_` (e.g., `_validate_email`)\n"

        return glossary

    def _generate_tutorials(self, task: WizardTask, gaps: list[dict]) -> str:
        """Generate interactive tutorials"""
        tutorials = "# Interactive Tutorials\n\n"

        tutorials += "## Tutorial 1: Your First Code Change\n\n"
        tutorials += "**Goal**: Make a small change, test it, and submit a PR\n\n"
        tutorials += "**Steps**:\n"
        tutorials += "1. Create a feature branch\n"
        tutorials += "   ```bash\n"
        tutorials += "   git checkout -b tutorial/my-first-change\n"
        tutorials += "   ```\n\n"

        tutorials += "2. Make a small change (add a log statement)\n"
        tutorials += "   ```python\n"
        tutorials += "   # src/api/routes/users.py\n"
        tutorials += "   import logging\n"
        tutorials += "   logger = logging.getLogger(__name__)\n\n"
        tutorials += "   def get_user(user_id: str):\n"
        tutorials += '       logger.info(f"Fetching user {user_id}")  # <- Add this line\n'
        tutorials += "       return user_service.get(user_id)\n"
        tutorials += "   ```\n\n"

        tutorials += "3. Run tests to verify\n"
        tutorials += "   ```bash\n"
        tutorials += "   pytest tests/api/test_users.py\n"
        tutorials += "   ```\n\n"

        tutorials += "4. Commit and push\n"
        tutorials += "   ```bash\n"
        tutorials += "   git add src/api/routes/users.py\n"
        tutorials += '   git commit -m "Add logging to get_user endpoint"\n'
        tutorials += "   git push origin tutorial/my-first-change\n"
        tutorials += "   ```\n\n"

        tutorials += "5. Create a pull request on GitHub\n"
        tutorials += "6. Request review from your mentor\n\n"

        tutorials += "## Tutorial 2: Add a New API Endpoint\n\n"
        tutorials += "**Goal**: Create a simple GET endpoint from scratch\n\n"
        tutorials += "**Steps**:\n"
        tutorials += "1. Define the route\n"
        tutorials += "   ```python\n"
        tutorials += "   # src/api/routes/users.py\n"
        tutorials += "   from fastapi import APIRouter, HTTPException\n"
        tutorials += "   \n"
        tutorials += "   router = APIRouter()\n"
        tutorials += "   \n"
        tutorials += '   @router.get("/users/{user_id}/profile")\n'
        tutorials += "   async def get_user_profile(user_id: str):\n"
        tutorials += '       """Get user profile information"""\n'
        tutorials += "       # Start with a simple stub that returns the structure\n"
        tutorials += "       return {\n"
        tutorials += '           "user_id": user_id,\n'
        tutorials += '           "email": "user@example.com",\n'
        tutorials += '           "name": "Example User"\n'
        tutorials += "       }\n"
        tutorials += "   ```\n\n"

        tutorials += "2. Write a test FIRST (TDD)\n"
        tutorials += "   ```python\n"
        tutorials += "   # tests/api/test_users.py\n"
        tutorials += "   def test_get_user_profile():\n"
        tutorials += '       response = client.get("/api/v1/users/123/profile")\n'
        tutorials += "       assert response.status_code == 200\n"
        tutorials += '       assert "email" in response.json()\n'
        tutorials += "   ```\n\n"

        tutorials += "3. Implement the endpoint\n"
        tutorials += "   ```python\n"
        tutorials += '   @router.get("/users/{user_id}/profile")\n'
        tutorials += "   async def get_user_profile(user_id: str):\n"
        tutorials += "       user = await user_service.get(user_id)\n"
        tutorials += "       if not user:\n"
        tutorials += '           raise HTTPException(status_code=404, detail="User not found")\n'
        tutorials += '       return {"email": user.email, "name": user.name}\n'
        tutorials += "   ```\n\n"

        tutorials += "4. Run tests and verify\n"
        tutorials += "5. Submit PR with test + implementation\n\n"

        tutorials += "## Tutorial 3: Debug a Failing Test\n\n"
        tutorials += "**Goal**: Use debugging tools to fix a broken test\n\n"
        tutorials += "**Steps**:\n"
        tutorials += "1. Run a specific test\n"
        tutorials += "   ```bash\n"
        tutorials += "   pytest tests/api/test_users.py::test_create_user -v\n"
        tutorials += "   ```\n\n"

        tutorials += "2. Add breakpoint in code\n"
        tutorials += "   ```python\n"
        tutorials += "   import pdb; pdb.set_trace()  # Python debugger\n"
        tutorials += "   ```\n\n"

        tutorials += "3. Inspect variables, step through code\n"
        tutorials += "4. Fix the issue\n"
        tutorials += "5. Remove breakpoint and verify test passes\n\n"

        tutorials += "## Tutorial 4: Deploy to Staging\n\n"
        tutorials += "**Goal**: Deploy your code to the staging environment\n\n"
        tutorials += "**Steps**:\n"
        tutorials += "1. Merge your PR to `main` branch\n"
        tutorials += "2. CI/CD pipeline automatically deploys to staging\n"
        tutorials += "3. Monitor deployment in GitHub Actions\n"
        tutorials += "4. Test your changes in staging: `https://staging.example.com`\n"
        tutorials += "5. Verify logs in monitoring dashboard\n"

        return tutorials

    def _create_onboarding_checklist(self, task: WizardTask) -> str:
        """Create 30-60-90 day checklist"""
        checklist = "# 30-60-90 Day Onboarding Checklist\n\n"

        checklist += "## First 30 Days: Foundation\n\n"
        checklist += "### Week 1: Setup & Orientation\n"
        checklist += "- [ ] Complete HR onboarding\n"
        checklist += "- [ ] Set up development environment\n"
        checklist += "- [ ] Get access to all systems (GitHub, AWS, Slack, etc.)\n"
        checklist += "- [ ] Meet with manager (1:1 kickoff)\n"
        checklist += "- [ ] Meet the team (team intro meeting)\n"
        checklist += "- [ ] Run application locally\n"
        checklist += "- [ ] Read architecture documentation\n\n"

        checklist += "### Week 2-4: Learning & First Contributions\n"
        checklist += "- [ ] Complete codebase tour\n"
        checklist += "- [ ] Shadow a code review session\n"
        checklist += "- [ ] Fix a documentation typo or error\n"
        checklist += "- [ ] Complete 'good first issue' ticket\n"
        checklist += "- [ ] Submit first PR (with mentor support)\n"
        checklist += "- [ ] Participate in team standup\n"
        checklist += "- [ ] Attend sprint planning meeting\n"
        checklist += "- [ ] Read product documentation\n"
        checklist += "- [ ] Use product as end-user\n\n"

        checklist += "## Days 31-60: Building Competence\n\n"
        checklist += "### Week 5-6: Independent Work\n"
        checklist += "- [ ] Own a small bug fix end-to-end\n"
        checklist += "- [ ] Write tests for your code\n"
        checklist += "- [ ] Deploy code to staging\n"
        checklist += "- [ ] Review another developer's PR\n"
        checklist += "- [ ] Pair program with senior developer\n"
        checklist += "- [ ] Attend architecture meeting\n\n"

        checklist += "### Week 7-8: Feature Ownership\n"
        checklist += "- [ ] Own a small feature end-to-end\n"
        checklist += "- [ ] Collaborate with designer/PM\n"
        checklist += "- [ ] Present work in team demo\n"
        checklist += "- [ ] Participate in retrospective\n"
        checklist += "- [ ] Update documentation based on learnings\n\n"

        checklist += "## Days 61-90: Full Contribution\n\n"
        checklist += "### Week 9-12: Advanced Work\n"
        checklist += "- [ ] Lead a medium-complexity feature\n"
        checklist += "- [ ] Participate in on-call rotation (shadowing)\n"
        checklist += "- [ ] Contribute to architecture discussion\n"
        checklist += "- [ ] Mentor next new hire\n"
        checklist += "- [ ] Give a technical presentation to team\n"
        checklist += "- [ ] Complete 30-60-90 day review with manager\n\n"

        checklist += "## Continuous Activities\n"
        checklist += "- [ ] Daily standup participation\n"
        checklist += "- [ ] Weekly 1:1 with manager\n"
        checklist += "- [ ] Monthly learning goal review\n"
        checklist += "- [ ] Regular code reviews (give and receive)\n"

        return checklist

    def _predict_onboarding_challenges(self, task: WizardTask, gaps: list[dict]) -> str:
        """Level 4: Predict onboarding challenges"""
        forecast = "# Onboarding Success Forecast (Level 4: Anticipatory)\n\n"

        forecast += "## Current State\n"
        forecast += f"- Knowledge gaps identified: {len(gaps)}\n"
        forecast += f"- Target role: {task.role}\n"
        forecast += "- Expected ramp-up time: 60-90 days (standard)\n\n"

        forecast += "## Projected Challenges (Next 30-90 Days)\n\n"

        forecast += "### ⚠️ Information Overload (Week 1-2)\n"
        forecast += "**Prediction**: New hire will feel overwhelmed by volume of information\n"
        forecast += "**Impact**: Slower learning, retention issues, increased stress\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Break learning into small, digestible chunks (one concept per day)\n"
        forecast += "- Prioritize: Focus on 20% that delivers 80% value\n"
        forecast += "- Regular check-ins: Daily 15-minute sync with mentor\n"
        forecast += "- Encourage questions: Create safe space for 'dumb questions'\n\n"

        forecast += "### ⚠️ Imposter Syndrome (Week 3-6)\n"
        forecast += "**Prediction**: New hire will doubt their abilities and fit\n"
        forecast += "**Impact**: Reduced confidence, hesitation to ask questions, slower progress\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Normalize the learning curve: 'Everyone struggles at first'\n"
        forecast += "- Celebrate small wins: Acknowledge every PR merged\n"
        forecast += "- Provide positive feedback: Highlight what they're doing well\n"
        forecast += "- Share your own onboarding struggles: 'I was confused too'\n\n"

        forecast += "### ⚠️ Context Switching Fatigue (Week 4-8)\n"
        forecast += "**Prediction**: Too many concurrent learning threads will slow progress\n"
        forecast += "**Impact**: Shallow understanding, difficulty retaining knowledge\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Focus on one area at a time (depth over breadth)\n"
        forecast += "- Block dedicated learning time (no meetings, no interruptions)\n"
        forecast += "- Assign a single 'learning buddy' (not rotating mentors)\n"
        forecast += "- Limit WIP: Work on one ticket at a time\n\n"

        forecast += "### ⚠️ Plateau at 60 Days (Week 8-10)\n"
        forecast += "**Prediction**: Progress will slow as easy wins are exhausted\n"
        forecast += "**Impact**: Frustration, feeling stuck, potential attrition risk\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Set clear 60-90 day goals BEFORE the plateau hits\n"
        forecast += "- Gradually increase complexity (scaffolding approach)\n"
        forecast += "- Provide stretch assignments to maintain engagement\n"
        forecast += "- Recognize this is normal: 'The plateau is part of mastery'\n\n"

        forecast += "## Success Indicators (Check These Weekly)\n\n"
        forecast += "**Week 1-2**:\n"
        forecast += "- [ ] Development environment working\n"
        forecast += "- [ ] Can run tests locally\n"
        forecast += "- [ ] Has submitted first PR (even if trivial)\n\n"

        forecast += "**Week 3-6**:\n"
        forecast += "- [ ] Completing tickets independently (with some guidance)\n"
        forecast += "- [ ] Asking good questions (specific, actionable)\n"
        forecast += "- [ ] Comfortable with git workflow\n\n"

        forecast += "**Week 7-12**:\n"
        forecast += "- [ ] Contributing to code reviews\n"
        forecast += "- [ ] Proposing solutions (not just implementing specs)\n"
        forecast += "- [ ] Building team relationships\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Week 1**: Environment setup, orientation\n"
        forecast += "- **Week 2**: First code change merged\n"
        forecast += "- **Week 4**: First solo ticket completed\n"
        forecast += "- **Week 8**: First feature owned end-to-end\n"
        forecast += "- **Week 12**: Fully ramped, contributing at full capacity\n"

        return forecast

    def _generate_onboarding_guide(self, diagnosis: str, learning_path: list[str]) -> str:
        """Generate comprehensive onboarding guide"""
        guide = f"{diagnosis}\n\n"

        guide += "## Welcome!\n\n"
        guide += (
            "We're excited to have you on the team! This guide will help you get up to speed.\n\n"
        )

        guide += "## Philosophy\n\n"
        guide += "- **Ask questions early and often**: There are no dumb questions\n"
        guide += "- **Learning over output**: Focus on understanding, not shipping fast\n"
        guide += "- **Mistakes are learning opportunities**: We all make them\n"
        guide += "- **Progress over perfection**: Small steps forward every day\n\n"

        guide += "## Your Mentor\n\n"
        guide += "You've been assigned a mentor who will:\n"
        guide += "- Guide you through your first 90 days\n"
        guide += "- Answer questions (technical and cultural)\n"
        guide += "- Review your code\n"
        guide += "- Provide feedback and coaching\n\n"
        guide += "**Schedule**: Daily 15-minute check-ins for first 2 weeks, then as needed\n\n"

        guide += "\n".join(learning_path)

        return guide

    def _identify_risks(self, task: WizardTask, learning_path: list[str]) -> list[WizardRisk]:
        """Identify onboarding risks"""
        risks = []

        # Information overload risk
        risks.append(
            WizardRisk(
                risk="New hire may feel overwhelmed by information volume",
                mitigation="Break learning into small chunks. Prioritize essential knowledge. Daily check-ins with mentor.",
                severity="medium",
            ),
        )

        # Insufficient mentorship risk
        risks.append(
            WizardRisk(
                risk="Mentor may not have sufficient time to support new hire",
                mitigation="Allocate 20% of mentor's time to onboarding support. Adjust their workload accordingly.",
                severity="high",
            ),
        )

        # Slow ramp-up risk
        risks.append(
            WizardRisk(
                risk="New hire may take longer than expected to become productive",
                mitigation="Set realistic expectations (60-90 days). Measure progress weekly. Provide additional support if needed.",
                severity="low",
            ),
        )

        # Cultural fit risk
        risks.append(
            WizardRisk(
                risk="New hire may struggle with team culture or communication style",
                mitigation="Pair with 'culture buddy' for informal questions. Regular 1:1s with manager to surface concerns early.",
                severity="medium",
            ),
        )

        return risks

    def _create_handoffs(self, task: WizardTask) -> list[WizardHandoff]:
        """Create handoffs for onboarding"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(
                WizardHandoff(
                    owner="Assigned Mentor (Senior Developer)",
                    what="Daily check-ins, code review, technical guidance for first 90 days",
                    when="Throughout onboarding period",
                ),
            )
            handoffs.append(
                WizardHandoff(
                    owner="Engineering Manager",
                    what="Weekly 1:1s, progress tracking, career development discussions",
                    when="Throughout onboarding and beyond",
                ),
            )
            handoffs.append(
                WizardHandoff(
                    owner="HR / People Ops",
                    what="Administrative onboarding, benefits setup, equipment provisioning",
                    when="First week",
                ),
            )

        return handoffs
