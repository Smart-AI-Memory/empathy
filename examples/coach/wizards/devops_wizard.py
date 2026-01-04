"""DevOps Wizard

CI/CD pipelines, infrastructure as code, deployment automation, and container orchestration.
Uses Empathy Framework Level 3 (Proactive) for pipeline design and Level 4
(Anticipatory) for predicting deployment issues and infrastructure scaling needs.

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


class DevOpsWizard(BaseWizard):
    """Wizard for CI/CD, infrastructure, and deployment automation

    Uses:
    - Level 2: Guide user through infrastructure decisions
    - Level 3: Proactively generate pipeline configurations
    - Level 4: Anticipate deployment failures and scaling issues
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is a DevOps task"""
        # High-priority DevOps phrases (worth 2 points each)
        devops_phrases = ["ci/cd", "pipeline", "deploy", "deployment", "docker", "kubernetes"]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "terraform",
            "github actions",
            "jenkins",
            "gitlab",
            "k8s",
            "helm",
            "container",
            "orchestration",
            "infrastructure",
            "iac",
            "ansible",
            "build",
            "release",
            "continuous integration",
            "continuous deployment",
        ]

        task_lower = (task.task + " " + task.context).lower()

        # Count high-priority matches (2 points each)
        primary_matches = sum(2 for phrase in devops_phrases if phrase in task_lower)

        # Count secondary matches (1 point each)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)  # 6+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute DevOps workflow"""
        # Step 1: Assess emotional context
        emotional_state = self._assess_emotional_state(task)

        # Step 2: Extract constraints
        self._extract_constraints(task)

        # Step 3: Analyze DevOps requirements
        diagnosis = self._analyze_devops_requirements(task)

        # Step 4: Design CI/CD pipeline (Level 3: Proactive)
        pipeline_design = self._design_pipeline(task)

        # Step 5: Generate infrastructure code
        infrastructure = self._design_infrastructure(task)

        # Step 6: Create deployment strategy
        deployment_strategy = self._create_deployment_strategy(task)

        # Step 7: Generate pipeline configuration
        pipeline_config = self._generate_pipeline_config(task, pipeline_design)

        # Step 8: Generate infrastructure code
        infrastructure_code = self._generate_infrastructure_code(task, infrastructure)

        # Step 9: Predict deployment issues (Level 4: Anticipatory)
        deployment_forecast = self._predict_deployment_issues(task, pipeline_design)

        # Step 10: Identify risks
        risks = self._identify_risks(task, deployment_strategy)

        # Step 11: Create artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="DevOps Strategy Document",
                content=self._generate_strategy_document(diagnosis, deployment_strategy),
            ),
            WizardArtifact(
                type="code",
                title="CI/CD Pipeline (GitHub Actions)",
                content=pipeline_config,
            ),
            WizardArtifact(
                type="code",
                title="Infrastructure as Code (Terraform)",
                content=infrastructure_code,
            ),
            WizardArtifact(
                type="code",
                title="Kubernetes Manifests",
                content=self._generate_kubernetes_manifests(task, infrastructure),
            ),
            WizardArtifact(
                type="doc",
                title="Deployment Guide",
                content=self._create_deployment_guide(task, deployment_strategy),
            ),
            WizardArtifact(type="doc", title="Deployment Forecast", content=deployment_forecast),
        ]

        # Step 12: Generate next actions
        next_actions = [
            "Set up CI/CD pipeline in repository",
            "Test pipeline with feature branch",
            "Deploy to staging environment",
            "Run smoke tests and validation",
            "Create production deployment runbook",
        ] + self._generate_anticipatory_actions(task)

        # Step 13: Create empathy checks
        empathy_checks = EmpathyChecks(
            cognitive=f"Considered {task.role}'s constraints: deployment safety, rollback capabilities, zero-downtime",
            emotional=f"Acknowledged: Deployments are stressful, {emotional_state['urgency']} urgency detected",
            anticipatory=(
                deployment_forecast[:200] + "..."
                if len(deployment_forecast) > 200
                else deployment_forecast
            ),
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=[
                "1. Design CI/CD pipeline stages (build, test, deploy)",
                "2. Create infrastructure as code (Terraform)",
                "3. Set up container orchestration (Kubernetes)",
                "4. Implement deployment automation",
                "5. Configure monitoring and alerting",
                "6. Create rollback procedures",
                "7. Document deployment process",
            ],
            artifacts=artifacts,
            risks=risks,
            handoffs=self._create_handoffs(task),
            next_actions=next_actions,
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_devops_requirements(self, task: WizardTask) -> str:
        """Analyze DevOps requirements from task description"""
        analysis = "# DevOps Requirements Analysis\n\n"
        analysis += f"**Objective**: {task.task}\n\n"

        # Categorize DevOps task
        categories = []
        task_lower = (task.task + " " + task.context).lower()

        if any(kw in task_lower for kw in ["ci/cd", "pipeline", "github actions", "jenkins"]):
            categories.append("CI/CD Pipeline")
        if any(kw in task_lower for kw in ["docker", "container", "kubernetes", "k8s"]):
            categories.append("Container Orchestration")
        if any(kw in task_lower for kw in ["terraform", "infrastructure", "iac", "cloud"]):
            categories.append("Infrastructure as Code")
        if any(kw in task_lower for kw in ["deploy", "deployment", "release"]):
            categories.append("Deployment Automation")
        if any(kw in task_lower for kw in ["monitoring", "observability", "logging"]):
            categories.append("Monitoring & Observability")

        if not categories:
            categories.append("General DevOps")

        analysis += f"**Category**: {', '.join(categories)}\n\n"
        analysis += (
            f"**Context**: {task.context[:300]}...\n"
            if len(task.context) > 300
            else f"**Context**: {task.context}\n"
        )

        return analysis

    def _design_pipeline(self, task: WizardTask) -> dict[str, Any]:
        """Design CI/CD pipeline"""
        pipeline = {"stages": [], "triggers": [], "environments": []}

        # Standard pipeline stages
        pipeline["stages"] = [
            {
                "name": "Build",
                "steps": [
                    "Checkout code",
                    "Install dependencies",
                    "Build application",
                    "Build Docker image",
                ],
            },
            {
                "name": "Test",
                "steps": [
                    "Run unit tests",
                    "Run integration tests",
                    "Run security scans (SAST)",
                    "Check code coverage (target: 80%+)",
                ],
            },
            {
                "name": "Package",
                "steps": [
                    "Tag Docker image",
                    "Push to container registry",
                    "Generate SBOM (Software Bill of Materials)",
                ],
            },
            {
                "name": "Deploy to Staging",
                "steps": ["Deploy to staging environment", "Run smoke tests", "Run E2E tests"],
            },
            {
                "name": "Deploy to Production",
                "steps": [
                    "Manual approval (for production)",
                    "Deploy with blue-green strategy",
                    "Run health checks",
                    "Monitor error rates",
                ],
            },
        ]

        pipeline["triggers"] = [
            "Push to main branch → Deploy to staging",
            "Create release tag → Deploy to production",
            "Pull request → Run tests only",
        ]

        pipeline["environments"] = ["development", "staging", "production"]

        return pipeline

    def _design_infrastructure(self, task: WizardTask) -> dict[str, Any]:
        """Design infrastructure architecture"""
        infrastructure = {
            "cloud_provider": "AWS",  # Default, can be GCP, Azure
            "components": [],
            "scaling": {},
        }

        (task.task + " " + task.context).lower()

        # Determine components
        infrastructure["components"] = [
            {
                "name": "Container Registry",
                "service": "ECR (Elastic Container Registry)",
                "purpose": "Store Docker images",
            },
            {
                "name": "Kubernetes Cluster",
                "service": "EKS (Elastic Kubernetes Service)",
                "purpose": "Orchestrate containers",
            },
            {
                "name": "Load Balancer",
                "service": "ALB (Application Load Balancer)",
                "purpose": "Distribute traffic",
            },
            {
                "name": "Database",
                "service": "RDS (Managed PostgreSQL)",
                "purpose": "Data persistence",
            },
        ]

        infrastructure["scaling"] = {
            "horizontal": "Kubernetes HPA (Horizontal Pod Autoscaler)",
            "min_replicas": 2,
            "max_replicas": 10,
            "target_cpu": "70%",
        }

        return infrastructure

    def _create_deployment_strategy(self, task: WizardTask) -> str:
        """Create deployment strategy"""
        strategy = "## Deployment Strategy\n\n"

        strategy += "### Recommended: Blue-Green Deployment\n\n"
        strategy += "**How it works**:\n"
        strategy += "1. Deploy new version to 'green' environment (parallel to 'blue' production)\n"
        strategy += "2. Run smoke tests on green environment\n"
        strategy += "3. Switch traffic from blue → green (instant cutover)\n"
        strategy += "4. Keep blue environment running for 1 hour (fast rollback if needed)\n"
        strategy += "5. Decommission blue environment after validation period\n\n"

        strategy += "**Advantages**:\n"
        strategy += "- Zero downtime\n"
        strategy += "- Instant rollback (switch traffic back to blue)\n"
        strategy += "- Full testing in production-like environment before cutover\n\n"

        strategy += "**Disadvantages**:\n"
        strategy += "- Requires 2x infrastructure during deployment\n"
        strategy += "- Database migrations require careful planning\n\n"

        strategy += "### Alternative: Canary Deployment\n\n"
        strategy += "**How it works**:\n"
        strategy += "1. Deploy new version to small subset of servers (10% traffic)\n"
        strategy += "2. Monitor error rates, latency for 30 minutes\n"
        strategy += "3. Gradually increase traffic: 10% → 25% → 50% → 100%\n"
        strategy += "4. Rollback if error rate exceeds threshold\n\n"

        strategy += "**Best for**: High-risk changes, gradual rollout\n"

        return strategy

    def _generate_pipeline_config(self, task: WizardTask, pipeline: dict) -> str:
        """Generate CI/CD pipeline configuration"""
        config = "# GitHub Actions CI/CD Pipeline\n\n"

        config += "```yaml\n"
        config += "name: CI/CD Pipeline\n\n"
        config += "on:\n"
        config += "  push:\n"
        config += "    branches: [main, develop]\n"
        config += "  pull_request:\n"
        config += "    branches: [main]\n"
        config += "  release:\n"
        config += "    types: [created]\n\n"

        config += "env:\n"
        config += "  REGISTRY: ghcr.io\n"
        config += "  IMAGE_NAME: ${{ github.repository }}\n\n"

        config += "jobs:\n"
        config += "  build-and-test:\n"
        config += "    runs-on: ubuntu-latest\n"
        config += "    steps:\n"
        config += "      - name: Checkout code\n"
        config += "        uses: actions/checkout@v4\n\n"

        config += "      - name: Set up Python\n"
        config += "        uses: actions/setup-python@v4\n"
        config += "        with:\n"
        config += "          python-version: '3.11'\n\n"

        config += "      - name: Install dependencies\n"
        config += "        run: |\n"
        config += "          pip install -r requirements.txt\n"
        config += "          pip install pytest pytest-cov\n\n"

        config += "      - name: Run tests\n"
        config += "        run: |\n"
        config += "          pytest --cov=. --cov-report=xml\n\n"

        config += "      - name: Check coverage\n"
        config += "        run: |\n"
        config += "          coverage report --fail-under=80\n\n"

        config += "      - name: Build Docker image\n"
        config += "        run: |\n"
        config += "          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .\n\n"

        config += "  deploy-staging:\n"
        config += "    needs: build-and-test\n"
        config += "    if: github.ref == 'refs/heads/main'\n"
        config += "    runs-on: ubuntu-latest\n"
        config += "    environment: staging\n"
        config += "    steps:\n"
        config += "      - name: Deploy to staging\n"
        config += "        run: |\n"
        config += "          kubectl set image deployment/app app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n staging\n\n"

        config += "      - name: Run smoke tests\n"
        config += "        run: |\n"
        config += "          curl -f https://staging.example.com/health || exit 1\n\n"

        config += "  deploy-production:\n"
        config += "    needs: deploy-staging\n"
        config += "    if: github.event_name == 'release'\n"
        config += "    runs-on: ubuntu-latest\n"
        config += "    environment: production\n"
        config += "    steps:\n"
        config += "      - name: Deploy to production (blue-green)\n"
        config += "        run: |\n"
        config += "          # Deploy to green environment\n"
        config += "          kubectl set image deployment/app-green app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n production\n"
        config += "          kubectl rollout status deployment/app-green -n production\n\n"

        config += "      - name: Switch traffic to green\n"
        config += "        run: |\n"
        config += '          kubectl patch service app -n production -p \'{"spec":{"selector":{"version":"green"}}}\'\n\n'

        config += "      - name: Monitor for 5 minutes\n"
        config += "        run: |\n"
        config += "          sleep 300\n"
        config += "          # Check error rates in monitoring system\n\n"

        config += "      - name: Rollback on failure\n"
        config += "        if: failure()\n"
        config += "        run: |\n"
        config += '          kubectl patch service app -n production -p \'{"spec":{"selector":{"version":"blue"}}}\'\n'
        config += "```\n"

        return config

    def _generate_infrastructure_code(self, task: WizardTask, infrastructure: dict) -> str:
        """Generate Terraform infrastructure code"""
        terraform = "# Terraform Infrastructure Configuration\n\n"

        terraform += "```hcl\n"
        terraform += "# main.tf\n\n"
        terraform += "terraform {\n"
        terraform += '  required_version = ">= 1.0"\n'
        terraform += "  required_providers {\n"
        terraform += "    aws = {\n"
        terraform += '      source  = "hashicorp/aws"\n'
        terraform += '      version = "~> 5.0"\n'
        terraform += "    }\n"
        terraform += "  }\n"
        terraform += '  backend "s3" {\n'
        terraform += '    bucket = "terraform-state-bucket"\n'
        terraform += '    key    = "app/terraform.tfstate"\n'
        terraform += '    region = "us-east-1"\n'
        terraform += "  }\n"
        terraform += "}\n\n"

        terraform += 'provider "aws" {\n'
        terraform += "  region = var.aws_region\n"
        terraform += "}\n\n"

        terraform += "# VPC and Networking\n"
        terraform += 'module "vpc" {\n'
        terraform += '  source = "terraform-aws-modules/vpc/aws"\n'
        terraform += '  name = "app-vpc"\n'
        terraform += '  cidr = "10.0.0.0/16"\n'
        terraform += '  azs  = ["us-east-1a", "us-east-1b", "us-east-1c"]\n'
        terraform += '  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]\n'
        terraform += '  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]\n'
        terraform += "  enable_nat_gateway = true\n"
        terraform += "}\n\n"

        terraform += "# EKS Cluster\n"
        terraform += 'module "eks" {\n'
        terraform += '  source  = "terraform-aws-modules/eks/aws"\n'
        terraform += '  cluster_name    = "app-cluster"\n'
        terraform += '  cluster_version = "1.28"\n'
        terraform += "  vpc_id          = module.vpc.vpc_id\n"
        terraform += "  subnet_ids      = module.vpc.private_subnets\n\n"

        terraform += "  eks_managed_node_groups = {\n"
        terraform += "    general = {\n"
        terraform += "      desired_size = 2\n"
        terraform += "      min_size     = 2\n"
        terraform += "      max_size     = 10\n"
        terraform += '      instance_types = ["t3.medium"]\n'
        terraform += "    }\n"
        terraform += "  }\n"
        terraform += "}\n\n"

        terraform += "# RDS Database\n"
        terraform += 'module "db" {\n'
        terraform += '  source  = "terraform-aws-modules/rds/aws"\n'
        terraform += '  identifier = "app-db"\n'
        terraform += '  engine     = "postgres"\n'
        terraform += '  engine_version = "15.4"\n'
        terraform += '  instance_class = "db.t3.medium"\n'
        terraform += "  allocated_storage = 100\n"
        terraform += "  storage_encrypted = true\n"
        terraform += "  multi_az = true\n"
        terraform += "  backup_retention_period = 7\n"
        terraform += "}\n\n"

        terraform += "# Application Load Balancer\n"
        terraform += 'module "alb" {\n'
        terraform += '  source  = "terraform-aws-modules/alb/aws"\n'
        terraform += '  name    = "app-alb"\n'
        terraform += "  vpc_id  = module.vpc.vpc_id\n"
        terraform += "  subnets = module.vpc.public_subnets\n"
        terraform += "  security_groups = [aws_security_group.alb.id]\n\n"

        terraform += "  target_groups = [\n"
        terraform += "    {\n"
        terraform += '      name_prefix      = "app-"\n'
        terraform += '      backend_protocol = "HTTP"\n'
        terraform += "      backend_port     = 80\n"
        terraform += '      target_type      = "ip"\n'
        terraform += "    }\n"
        terraform += "  ]\n"
        terraform += "}\n"
        terraform += "```\n\n"

        terraform += "```hcl\n"
        terraform += "# variables.tf\n\n"
        terraform += 'variable "aws_region" {\n'
        terraform += '  description = "AWS region"\n'
        terraform += "  type        = string\n"
        terraform += '  default     = "us-east-1"\n'
        terraform += "}\n\n"

        terraform += 'variable "environment" {\n'
        terraform += '  description = "Environment name"\n'
        terraform += "  type        = string\n"
        terraform += '  default     = "production"\n'
        terraform += "}\n"
        terraform += "```\n"

        return terraform

    def _generate_kubernetes_manifests(self, task: WizardTask, infrastructure: dict) -> str:
        """Generate Kubernetes deployment manifests"""
        manifests = "# Kubernetes Deployment Manifests\n\n"

        manifests += "## Deployment\n\n"
        manifests += "```yaml\n"
        manifests += "# deployment.yaml\n"
        manifests += "apiVersion: apps/v1\n"
        manifests += "kind: Deployment\n"
        manifests += "metadata:\n"
        manifests += "  name: app\n"
        manifests += "  namespace: production\n"
        manifests += "spec:\n"
        manifests += "  replicas: 3\n"
        manifests += "  selector:\n"
        manifests += "    matchLabels:\n"
        manifests += "      app: app\n"
        manifests += "  template:\n"
        manifests += "    metadata:\n"
        manifests += "      labels:\n"
        manifests += "        app: app\n"
        manifests += "    spec:\n"
        manifests += "      containers:\n"
        manifests += "      - name: app\n"
        manifests += "        image: ghcr.io/org/app:latest\n"
        manifests += "        ports:\n"
        manifests += "        - containerPort: 8000\n"
        manifests += "        env:\n"
        manifests += "        - name: DATABASE_URL\n"
        manifests += "          valueFrom:\n"
        manifests += "            secretKeyRef:\n"
        manifests += "              name: app-secrets\n"
        manifests += "              key: database-url\n"
        manifests += "        resources:\n"
        manifests += "          requests:\n"
        manifests += '            memory: "256Mi"\n'
        manifests += '            cpu: "250m"\n'
        manifests += "          limits:\n"
        manifests += '            memory: "512Mi"\n'
        manifests += '            cpu: "500m"\n'
        manifests += "        livenessProbe:\n"
        manifests += "          httpGet:\n"
        manifests += "            path: /health\n"
        manifests += "            port: 8000\n"
        manifests += "          initialDelaySeconds: 30\n"
        manifests += "          periodSeconds: 10\n"
        manifests += "        readinessProbe:\n"
        manifests += "          httpGet:\n"
        manifests += "            path: /ready\n"
        manifests += "            port: 8000\n"
        manifests += "          initialDelaySeconds: 5\n"
        manifests += "          periodSeconds: 5\n"
        manifests += "```\n\n"

        manifests += "## Service\n\n"
        manifests += "```yaml\n"
        manifests += "# service.yaml\n"
        manifests += "apiVersion: v1\n"
        manifests += "kind: Service\n"
        manifests += "metadata:\n"
        manifests += "  name: app\n"
        manifests += "  namespace: production\n"
        manifests += "spec:\n"
        manifests += "  selector:\n"
        manifests += "    app: app\n"
        manifests += "  ports:\n"
        manifests += "  - protocol: TCP\n"
        manifests += "    port: 80\n"
        manifests += "    targetPort: 8000\n"
        manifests += "  type: LoadBalancer\n"
        manifests += "```\n\n"

        manifests += "## Horizontal Pod Autoscaler\n\n"
        manifests += "```yaml\n"
        manifests += "# hpa.yaml\n"
        manifests += "apiVersion: autoscaling/v2\n"
        manifests += "kind: HorizontalPodAutoscaler\n"
        manifests += "metadata:\n"
        manifests += "  name: app-hpa\n"
        manifests += "  namespace: production\n"
        manifests += "spec:\n"
        manifests += "  scaleTargetRef:\n"
        manifests += "    apiVersion: apps/v1\n"
        manifests += "    kind: Deployment\n"
        manifests += "    name: app\n"
        manifests += "  minReplicas: 2\n"
        manifests += "  maxReplicas: 10\n"
        manifests += "  metrics:\n"
        manifests += "  - type: Resource\n"
        manifests += "    resource:\n"
        manifests += "      name: cpu\n"
        manifests += "      target:\n"
        manifests += "        type: Utilization\n"
        manifests += "        averageUtilization: 70\n"
        manifests += "```\n"

        return manifests

    def _create_deployment_guide(self, task: WizardTask, strategy: str) -> str:
        """Create deployment guide"""
        guide = "# Deployment Guide\n\n"

        guide += "## Pre-Deployment Checklist\n\n"
        guide += "- [ ] All tests passing in CI/CD pipeline\n"
        guide += "- [ ] Code review approved\n"
        guide += "- [ ] Staging deployment successful\n"
        guide += "- [ ] Database migrations tested\n"
        guide += "- [ ] Rollback plan prepared\n"
        guide += "- [ ] Stakeholders notified\n"
        guide += "- [ ] Monitoring dashboards ready\n\n"

        guide += strategy + "\n"

        guide += "## Deployment Steps\n\n"
        guide += "### 1. Pre-deployment\n"
        guide += "```bash\n"
        guide += "# Tag release\n"
        guide += 'git tag -a v1.0.0 -m "Release v1.0.0"\n'
        guide += "git push origin v1.0.0\n\n"
        guide += "# This triggers the production deployment pipeline\n"
        guide += "```\n\n"

        guide += "### 2. Monitor Deployment\n"
        guide += "```bash\n"
        guide += "# Watch rollout status\n"
        guide += "kubectl rollout status deployment/app -n production\n\n"
        guide += "# Check pod health\n"
        guide += "kubectl get pods -n production -l app=app\n\n"
        guide += "# View logs\n"
        guide += "kubectl logs -f -n production -l app=app\n"
        guide += "```\n\n"

        guide += "### 3. Validation\n"
        guide += "```bash\n"
        guide += "# Health check\n"
        guide += "curl https://api.example.com/health\n\n"
        guide += "# Smoke tests\n"
        guide += "pytest tests/smoke/\n\n"
        guide += "# Monitor error rates (next 30 minutes)\n"
        guide += "# Check dashboards: Grafana, Datadog, etc.\n"
        guide += "```\n\n"

        guide += "## Rollback Procedure\n\n"
        guide += "```bash\n"
        guide += "# Option 1: Rollback to previous version (blue-green)\n"
        guide += 'kubectl patch service app -n production -p \'{"spec":{"selector":{"version":"blue"}}}\'\n\n'
        guide += "# Option 2: Rollback Kubernetes deployment\n"
        guide += "kubectl rollout undo deployment/app -n production\n\n"
        guide += "# Verify rollback\n"
        guide += "kubectl rollout status deployment/app -n production\n"
        guide += "```\n\n"

        guide += "## Post-Deployment\n\n"
        guide += "- [ ] Monitor error rates for 1 hour\n"
        guide += "- [ ] Verify all critical paths working\n"
        guide += "- [ ] Update release notes\n"
        guide += "- [ ] Notify stakeholders of successful deployment\n"
        guide += "- [ ] Schedule post-mortem if issues occurred\n"

        return guide

    def _predict_deployment_issues(self, task: WizardTask, pipeline: dict) -> str:
        """Level 4: Predict deployment and infrastructure issues"""
        forecast = "# Deployment Forecast (Level 4: Anticipatory)\n\n"

        forecast += "## Current State\n"
        forecast += "- Pipeline stages: " + str(len(pipeline.get("stages", []))) + "\n"
        forecast += "- Deployment frequency: Weekly (assumed)\n"
        forecast += "- Rollback capability: Manual\n\n"

        forecast += "## Projected Issues (Next 30-90 Days)\n\n"

        forecast += "### ⚠️ Deployment Failures Increase (30 days)\n"
        forecast += "**Prediction**: As team grows, deployment failures will increase 2x\n"
        forecast += "**Impact**: Blocked releases, frustrated developers, missed deadlines\n"
        forecast += "**Cause**: Manual steps, insufficient testing, configuration drift\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Automate ALL deployment steps (zero manual intervention)\n"
        forecast += "- Add smoke tests to catch issues before production\n"
        forecast += "- Implement configuration management (prevent drift)\n"
        forecast += "- Use infrastructure as code (Terraform) for reproducibility\n\n"

        forecast += "### ⚠️ Slow Deployment Pipeline (45 days)\n"
        forecast += "**Prediction**: As codebase grows, pipeline will exceed 30 minutes\n"
        forecast += "**Impact**: Slow feedback loop, reduced deployment frequency\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Parallelize independent pipeline stages\n"
        forecast += "- Use Docker layer caching to speed up builds\n"
        forecast += "- Split tests into fast unit tests (always) + slow E2E (nightly)\n"
        forecast += "- Consider incremental builds\n\n"

        forecast += "### ⚠️ Infrastructure Scaling Bottleneck (60 days)\n"
        forecast += "**Prediction**: Manual infrastructure changes can't keep up with growth\n"
        forecast += "**Impact**: Developers blocked waiting for infrastructure\n"
        forecast += "**Preventive Action**:\n"
        forecast += "- Implement auto-scaling NOW (HPA in Kubernetes)\n"
        forecast += "- Use infrastructure as code for self-service provisioning\n"
        forecast += "- Set up monitoring alerts BEFORE hitting capacity limits\n\n"

        forecast += "### ⚠️ Configuration Management Chaos (90 days)\n"
        forecast += "**Prediction**: Config differences between environments cause bugs\n"
        forecast += '**Impact**: "Works on my machine" syndrome, production incidents\n'
        forecast += "**Preventive Action**:\n"
        forecast += "- Centralize config management (AWS Secrets Manager, Vault)\n"
        forecast += "- Use environment variables (12-factor app)\n"
        forecast += "- Validate config in CI/CD pipeline\n"
        forecast += "- Document all environment-specific settings\n\n"

        forecast += "## Recommended Timeline\n"
        forecast += "- **Now (Week 1)**: Automate deployment, set up IaC\n"
        forecast += "- **Week 4**: Implement auto-scaling and monitoring\n"
        forecast += "- **Week 8**: Add comprehensive smoke tests\n"
        forecast += "- **Week 12**: Review and optimize pipeline performance\n"

        return forecast

    def _generate_strategy_document(self, diagnosis: str, strategy: str) -> str:
        """Generate comprehensive DevOps strategy document"""
        doc = f"{diagnosis}\n\n"
        doc += strategy + "\n\n"

        doc += "## Infrastructure Philosophy\n\n"
        doc += "- **Infrastructure as Code**: All infrastructure managed through Terraform\n"
        doc += "- **Immutable Infrastructure**: Never modify running servers, always deploy new\n"
        doc += "- **Zero Downtime Deployments**: Blue-green or canary deployments\n"
        doc += "- **Automated Testing**: CI/CD pipeline catches issues before production\n"
        doc += "- **Observability First**: Monitoring, logging, tracing built in from day 1\n"

        return doc

    def _identify_risks(self, task: WizardTask, strategy: str) -> list[WizardRisk]:
        """Identify deployment and infrastructure risks"""
        risks = []

        # Deployment failure risk
        risks.append(
            WizardRisk(
                risk="Deployment may fail and cause downtime",
                mitigation="Use blue-green deployment for zero-downtime. Keep previous version running for fast rollback.",
                severity="high",
            ),
        )

        # Configuration drift risk
        risks.append(
            WizardRisk(
                risk="Manual infrastructure changes cause configuration drift",
                mitigation="Use Terraform for ALL infrastructure changes. Enable drift detection in CI/CD.",
                severity="medium",
            ),
        )

        # Security vulnerability risk
        risks.append(
            WizardRisk(
                risk="Docker images may contain security vulnerabilities",
                mitigation="Add container scanning to CI/CD (Trivy, Snyk). Fail builds on high/critical vulnerabilities.",
                severity="high",
            ),
        )

        # Cost overrun risk
        risks.append(
            WizardRisk(
                risk="Auto-scaling may cause unexpected cloud costs",
                mitigation="Set up cost monitoring alerts. Configure maximum scaling limits. Review costs weekly.",
                severity="medium",
            ),
        )

        return risks

    def _create_handoffs(self, task: WizardTask) -> list[WizardHandoff]:
        """Create handoffs for DevOps work"""
        handoffs = []

        if task.role == "developer":
            handoffs.append(
                WizardHandoff(
                    owner="DevOps / Platform Team",
                    what="Review infrastructure code, set up monitoring, configure secrets management",
                    when="Before production deployment",
                ),
            )
            handoffs.append(
                WizardHandoff(
                    owner="Security Team",
                    what="Review security configurations, approve container images, validate network policies",
                    when="Before production deployment",
                ),
            )

        return handoffs
