/**
 * Workflow Wizard Panel - Interactive Workflow Creation Wizard
 *
 * A guided wizard for creating new workflows:
 * 1. Select Pattern - Choose Crew, Base, or Compose with inline guidance
 * 2. Name & Configure - Enter workflow name and output directory
 * 3. Preview & Create - Review generated template and create file
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { getFilePickerService, FilePickerService } from '../services/FilePickerService';

// =============================================================================
// Types
// =============================================================================

interface WorkflowPattern {
    id: 'crew' | 'base' | 'compose';
    name: string;
    description: string;
    bestFor: string[];
    tradeoffs: {
        cost: string;
        speed: string;
        thoroughness: string;
    };
}

interface AgentConfig {
    id: string;
    role: string;
    goal: string;
    backstory: string;
    expertiseLevel: 'novice' | 'intermediate' | 'expert' | 'world-class';
}

interface TaskConfig {
    id: string;
    description: string;
    expectedOutput: string;
    assignedAgentId: string;
}

type WizardStep = 'pattern' | 'overview' | 'agents' | 'tasks' | 'preview';

interface WizardSession {
    step: WizardStep;
    selectedPattern: WorkflowPattern['id'] | null;
    workflowName: string;
    description: string;
    outputDir: string;
    generatedCode: string;
    className: string;
    // Crew-specific fields
    numAgents: number;
    processType: 'sequential' | 'hierarchical';
    agents: AgentConfig[];
    tasks: TaskConfig[];
}

// Default agent templates
const DEFAULT_AGENTS: AgentConfig[] = [
    {
        id: 'agent-1',
        role: 'Analyst',
        goal: 'Analyze the target and gather comprehensive findings',
        backstory: 'Expert analyst with deep domain knowledge and attention to detail',
        expertiseLevel: 'expert'
    },
    {
        id: 'agent-2',
        role: 'Reviewer',
        goal: 'Cross-check findings and validate accuracy',
        backstory: 'Experienced reviewer focused on quality and correctness',
        expertiseLevel: 'expert'
    },
    {
        id: 'agent-3',
        role: 'Synthesizer',
        goal: 'Combine findings into actionable recommendations',
        backstory: 'Strategic thinker who excels at synthesis and prioritization',
        expertiseLevel: 'expert'
    }
];

// Default task templates
const DEFAULT_TASKS: TaskConfig[] = [
    {
        id: 'task-1',
        description: 'Analyze the target and identify key findings',
        expectedOutput: 'Structured list of findings with severity and details',
        assignedAgentId: 'agent-1'
    },
    {
        id: 'task-2',
        description: 'Review and validate the analysis findings',
        expectedOutput: 'Validated findings with confidence scores',
        assignedAgentId: 'agent-2'
    },
    {
        id: 'task-3',
        description: 'Synthesize findings into recommendations',
        expectedOutput: 'Prioritized list of actionable recommendations',
        assignedAgentId: 'agent-3'
    }
];

// =============================================================================
// Pattern Definitions
// =============================================================================

const WORKFLOW_PATTERNS: WorkflowPattern[] = [
    {
        id: 'crew',
        name: 'Crew Pattern',
        description: 'Multiple specialized AI agents collaborate on the task',
        bestFor: ['Security audits', 'Code reviews', 'Research synthesis', 'Quality-critical analysis'],
        tradeoffs: {
            cost: 'Higher',
            speed: 'Slower',
            thoroughness: 'High'
        }
    },
    {
        id: 'base',
        name: 'Base Pattern',
        description: 'Sequential stages with automatic model tier routing',
        bestFor: ['Cost-sensitive tasks', 'Batch operations', 'Clear stage progression', 'Speed-critical'],
        tradeoffs: {
            cost: 'Low-Medium',
            speed: 'Fast',
            thoroughness: 'Medium'
        }
    },
    {
        id: 'compose',
        name: 'Compose Pattern',
        description: 'Orchestrate multiple existing workflows together',
        bestFor: ['Combining capabilities', 'Parallel execution', 'Meta-workflows', 'Pipeline automation'],
        tradeoffs: {
            cost: 'Varies',
            speed: 'Varies',
            thoroughness: 'Depends on composed workflows'
        }
    }
];

// =============================================================================
// Utility Functions
// =============================================================================

function getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}

function toClassName(name: string, pattern: string): string {
    // Convert kebab-case, spaces, and underscores to PascalCase
    const base = name.replace(/[-\s]+/g, '_').split('_')
        .filter(word => word.length > 0)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join('');

    // Add appropriate suffix
    if (!base.endsWith('Workflow') && !base.endsWith('Crew') && !base.endsWith('Pipeline')) {
        if (pattern === 'crew') return base + 'Crew';
        if (pattern === 'compose') return base + 'Pipeline';
        return base + 'Workflow';
    }
    return base;
}

function toFileName(name: string): string {
    return name.replace(/[-\s]+/g, '_').toLowerCase() + '.py';
}

// =============================================================================
// Template Generators
// =============================================================================

function generateCrewTemplate(className: string, workflowName: string, description: string): string {
    const desc = description || 'Multi-agent analysis crew';
    return `"""
${workflowName} - Multi-Agent Workflow

${description ? description + '\n\n' : ''}Pattern: Crew (default)
- Multiple specialized AI agents collaborate on the task
- Best for: thorough analysis, multiple perspectives, quality-critical tasks

Generated with: empathy workflow new ${workflowName}
See: docs/guides/WORKFLOW_PATTERNS.md

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ${className}Result:
    """Result from ${className} execution."""
    success: bool
    findings: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    cost: float = 0.0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "cost": self.cost,
        }


class ${className}:
    """
    ${workflowName} - ${desc}

    Agents:
    - Analyst: Primary analysis of the target
    - Reviewer: Cross-checks and validates findings
    - Synthesizer: Combines perspectives into recommendations

    Usage:
        crew = ${className}()
        result = await crew.execute(path="./src", context={})
    """

    name = "${workflowName}"
    description = "${desc}"

    def __init__(self, num_agents: int = 3, **kwargs: Any):
        """
        Initialize the crew.

        Args:
            num_agents: Number of agents to use (affects cost/quality tradeoff)
            **kwargs: Additional configuration
        """
        self.num_agents = num_agents
        self.config = kwargs

    async def execute(
        self,
        path: str = ".",
        context: dict | None = None,
        **kwargs: Any,
    ) -> ${className}Result:
        """
        Execute the crew analysis.

        Args:
            path: Path to analyze
            context: Additional context for agents
            **kwargs: Additional arguments

        Returns:
            ${className}Result with findings and recommendations
        """
        context = context or {}

        # TODO: Implement agent logic
        # Example structure:
        #
        # async def analyst_task():
        #     # Primary analysis
        #     return analysis_result
        #
        # async def reviewer_task(analysis):
        #     # Cross-check findings
        #     return reviewed_result
        #
        # async def synthesizer_task(analysis, review):
        #     # Combine into recommendations
        #     return recommendations
        #
        # analysis = await analyst_task()
        # review = await reviewer_task(analysis)
        # recommendations = await synthesizer_task(analysis, review)

        return ${className}Result(
            success=True,
            findings=[],
            recommendations=["Implement agent logic"],
            confidence=0.0,
            cost=0.0,
        )
`;
}

function generateBaseTemplate(className: string, workflowName: string, description: string): string {
    const desc = description || 'Sequential workflow with tier routing';
    return `"""
${workflowName} - Sequential Stage Workflow

${description ? description + '\n\n' : ''}Pattern: Base
- Sequential stages with automatic model tier routing
- Best for: cost-sensitive tasks, clear stage progression, single-purpose tools

Generated with: empathy workflow new ${workflowName} --base
See: docs/guides/WORKFLOW_PATTERNS.md

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from typing import Any

from empathy_os.workflows.base import BaseWorkflow, ModelTier, WorkflowResult
from empathy_os.workflows.step_config import WorkflowStepConfig


class ${className}(BaseWorkflow):
    """
    ${workflowName} - ${desc}

    Stages:
    1. Analyze (CAPABLE tier) - Initial analysis
    2. Process (CHEAP tier) - Data processing
    3. Format (CHEAP tier) - Output formatting

    Usage:
        workflow = ${className}()
        result = await workflow.execute(path="./src")
    """

    name = "${workflowName}"
    description = "${desc}"

    def define_steps(self) -> list[WorkflowStepConfig]:
        """
        Define workflow stages with model tier routing.

        Tier guide:
        - CHEAP: Haiku/GPT-4o-mini ($0.25-1.25/M tokens) - summarization, formatting
        - CAPABLE: Sonnet/GPT-4o ($3-15/M tokens) - analysis, code review
        - PREMIUM: Opus/o1 ($15-75/M tokens) - architecture decisions, complex reasoning
        """
        return [
            WorkflowStepConfig(
                name="analyze",
                tier=ModelTier.CAPABLE,
                prompt_template="""Analyze the following:

{input}

Provide a structured analysis with key findings.""",
                description="Initial analysis using capable model",
            ),
            WorkflowStepConfig(
                name="process",
                tier=ModelTier.CHEAP,
                prompt_template="""Process these analysis results:

{previous_output}

Extract the key points and organize them.""",
                description="Process results using cheap model",
            ),
            WorkflowStepConfig(
                name="format",
                tier=ModelTier.CHEAP,
                prompt_template="""Format the following for output:

{previous_output}

Create a clear, actionable summary.""",
                description="Format output using cheap model",
            ),
        ]

    async def execute(self, path: str = ".", **kwargs: Any) -> WorkflowResult:
        """
        Execute the workflow.

        Args:
            path: Path to analyze
            **kwargs: Additional arguments

        Returns:
            WorkflowResult with analysis output
        """
        # Read input (customize based on your needs)
        input_data = f"Path: {path}"

        # Run the defined steps
        return await self.run_steps(input_data, **kwargs)
`;
}

function generateComposeTemplate(className: string, workflowName: string, description: string): string {
    const desc = description || 'Pipeline composing multiple workflows';
    return `"""
${workflowName} - Workflow Composition Pipeline

${description ? description + '\n\n' : ''}Pattern: Compose
- Orchestrates multiple existing workflows
- Best for: combining capabilities, parallel execution, meta-workflows

Generated with: empathy workflow new ${workflowName} --compose
See: docs/guides/WORKFLOW_PATTERNS.md

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ${className}Result:
    """Combined result from pipeline execution."""
    success: bool
    go_no_go: str  # "GO", "NO_GO", "CONDITIONAL"

    # Individual workflow results
    workflow_results: dict = field(default_factory=dict)

    # Aggregated metrics
    total_findings: int = 0
    total_cost: float = 0.0
    total_duration_ms: int = 0

    # Recommendations
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "go_no_go": self.go_no_go,
            "total_findings": self.total_findings,
            "total_cost": self.total_cost,
            "total_duration_ms": self.total_duration_ms,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


class ${className}:
    """
    ${workflowName} - ${desc}

    Composed workflows:
    - WorkflowA (parallel)
    - WorkflowB (parallel)
    - WorkflowC (sequential, after A and B)

    Usage:
        pipeline = ${className}(mode="full")
        result = await pipeline.execute(path="./src")
    """

    name = "${workflowName}"
    description = "${desc}"

    def __init__(
        self,
        mode: str = "full",  # "full", "quick"
        parallel: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize the pipeline.

        Args:
            mode: Execution mode ("full" runs all, "quick" runs subset)
            parallel: Run independent workflows in parallel
            **kwargs: Additional configuration
        """
        self.mode = mode
        self.parallel = parallel
        self.config = kwargs

    async def execute(
        self,
        path: str = ".",
        **kwargs: Any,
    ) -> ${className}Result:
        """
        Execute the composed pipeline.

        Args:
            path: Path to analyze
            **kwargs: Additional arguments

        Returns:
            ${className}Result with combined analysis
        """
        started_at = datetime.now()
        workflow_results = {}
        total_cost = 0.0
        blockers = []
        warnings = []
        recommendations = []

        try:
            # TODO: Import and instantiate your workflows
            # from .workflow_a import WorkflowA
            # from .workflow_b import WorkflowB
            # workflow_a = WorkflowA()
            # workflow_b = WorkflowB()

            if self.parallel:
                # Run workflows in parallel
                # results = await asyncio.gather(
                #     workflow_a.execute(path=path),
                #     workflow_b.execute(path=path),
                # )
                # workflow_results["workflow_a"] = results[0]
                # workflow_results["workflow_b"] = results[1]
                pass
            else:
                # Run workflows sequentially
                # workflow_results["workflow_a"] = await workflow_a.execute(path=path)
                # workflow_results["workflow_b"] = await workflow_b.execute(path=path)
                pass

            # TODO: Aggregate results
            # for name, result in workflow_results.items():
            #     total_cost += result.cost
            #     blockers.extend(result.blockers)
            #     warnings.extend(result.warnings)

            # Determine go/no-go
            if blockers:
                go_no_go = "NO_GO"
            elif warnings:
                go_no_go = "CONDITIONAL"
            else:
                go_no_go = "GO"

            recommendations.append("Implement workflow composition logic")

        except Exception as e:
            return ${className}Result(
                success=False,
                go_no_go="NO_GO",
                blockers=[str(e)],
            )

        duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)

        return ${className}Result(
            success=True,
            go_no_go=go_no_go,
            workflow_results=workflow_results,
            total_findings=0,
            total_cost=total_cost,
            total_duration_ms=duration_ms,
            blockers=blockers,
            warnings=warnings,
            recommendations=recommendations,
        )
`;
}

function generateTemplate(pattern: string, className: string, workflowName: string, description: string): string {
    switch (pattern) {
        case 'crew': return generateCrewTemplate(className, workflowName, description);
        case 'base': return generateBaseTemplate(className, workflowName, description);
        case 'compose': return generateComposeTemplate(className, workflowName, description);
        default: return generateCrewTemplate(className, workflowName, description);
    }
}

function generateCrewTemplateWithAgents(
    className: string,
    workflowName: string,
    description: string,
    agents: AgentConfig[],
    tasks: TaskConfig[],
    processType: 'sequential' | 'hierarchical'
): string {
    const desc = description || 'Multi-agent analysis crew';

    // Generate agent definitions
    const agentDefs = agents.map(agent => {
        const varName = agent.role.toLowerCase().replace(/\s+/g, '_');
        return `        self.${varName} = Agent(
            role="${agent.role}",
            goal="${agent.goal}",
            backstory="${agent.backstory}",
            expertise_level="${agent.expertiseLevel}",
        )`;
    }).join('\n\n');

    // Generate task definitions
    const taskDefs = tasks.map(task => {
        const agent = agents.find(a => a.id === task.assignedAgentId);
        const agentVar = agent ? agent.role.toLowerCase().replace(/\s+/g, '_') : 'analyst';
        return `        Task(
            description="${task.description}",
            expected_output="${task.expectedOutput}",
            agent=self.${agentVar},
        )`;
    }).join(',\n');

    // Generate agent list for docstring
    const agentList = agents.map(a => `    - ${a.role}: ${a.goal}`).join('\n');

    return `"""
${workflowName} - Multi-Agent Workflow

${description ? description + '\n\n' : ''}Pattern: Crew
- Multiple specialized AI agents collaborate on the task
- Process Type: ${processType}
- Agents: ${agents.length}

Generated with: empathy workflow new ${workflowName}
See: docs/guides/WORKFLOW_PATTERNS.md

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass, field
from typing import Any

# Note: Import your Agent and Task classes from your framework
# from crewai import Agent, Task, Crew
# or from your custom implementation


@dataclass
class ${className}Result:
    """Result from ${className} execution."""
    success: bool
    findings: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    cost: float = 0.0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "cost": self.cost,
        }


class Agent:
    """Placeholder Agent class - replace with your framework's Agent."""
    def __init__(self, role: str, goal: str, backstory: str, expertise_level: str = "expert"):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.expertise_level = expertise_level


class Task:
    """Placeholder Task class - replace with your framework's Task."""
    def __init__(self, description: str, expected_output: str, agent: Agent):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent


class ${className}:
    """
    ${workflowName} - ${desc}

    Process Type: ${processType}

    Agents:
${agentList}

    Usage:
        crew = ${className}()
        result = await crew.execute(path="./src", context={})
    """

    name = "${workflowName}"
    description = "${desc}"
    process_type = "${processType}"

    def __init__(self, **kwargs: Any):
        """Initialize the crew with configured agents."""
        # Define agents
${agentDefs}

        # Store all agents
        self.agents = [${agents.map(a => 'self.' + a.role.toLowerCase().replace(/\s+/g, '_')).join(', ')}]

    def define_tasks(self) -> list:
        """Define the tasks for this crew."""
        return [
${taskDefs}
        ]

    async def execute(
        self,
        path: str = ".",
        context: dict | None = None,
        **kwargs: Any,
    ) -> ${className}Result:
        """
        Execute the crew analysis.

        Args:
            path: Path to analyze
            context: Additional context for agents
            **kwargs: Additional arguments

        Returns:
            ${className}Result with findings and recommendations
        """
        context = context or {}
        tasks = self.define_tasks()

        # TODO: Implement crew execution logic
        # Example using CrewAI:
        # crew = Crew(
        #     agents=self.agents,
        #     tasks=tasks,
        #     process=Process.${processType.toUpperCase()},
        # )
        # result = crew.kickoff()

        return ${className}Result(
            success=True,
            findings=[],
            recommendations=["Implement crew execution logic"],
            confidence=0.0,
            cost=0.0,
        )
`;
}

// =============================================================================
// WorkflowWizardPanel Class
// =============================================================================

export class WorkflowWizardPanel implements vscode.WebviewViewProvider {
    public static readonly viewType = 'workflow-wizard';

    private _view?: vscode.WebviewView;
    private _extensionUri: vscode.Uri;
    private _context: vscode.ExtensionContext;
    private _session: WizardSession;
    private _disposables: vscode.Disposable[] = [];
    private _defaultPattern: 'crew' | 'base' | 'compose' = 'crew';
    private _filePickerService: FilePickerService;

    constructor(extensionUri: vscode.Uri, context: vscode.ExtensionContext) {
        this._extensionUri = extensionUri;
        this._context = context;
        this._filePickerService = getFilePickerService();
        this._session = this._createEmptySession();
        this._loadConfigDefault();
    }

    private _createEmptySession(): WizardSession {
        return {
            step: 'pattern',
            selectedPattern: null,
            workflowName: '',
            description: '',
            outputDir: 'src/empathy_os/workflows',
            generatedCode: '',
            className: '',
            // Crew-specific defaults
            numAgents: 3,
            processType: 'sequential',
            agents: JSON.parse(JSON.stringify(DEFAULT_AGENTS)), // Deep copy
            tasks: JSON.parse(JSON.stringify(DEFAULT_TASKS))    // Deep copy
        };
    }

    private _loadConfigDefault(): void {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) return;

        const configPath = path.join(workspaceFolder, 'empathy.config.yml');
        if (fs.existsSync(configPath)) {
            try {
                const configContent = fs.readFileSync(configPath, 'utf8');
                // Simple regex to extract default_pattern value
                const match = configContent.match(/default_pattern:\s*(crew|base|compose)/);
                if (match && (match[1] === 'crew' || match[1] === 'base' || match[1] === 'compose')) {
                    this._defaultPattern = match[1] as 'crew' | 'base' | 'compose';
                }
            } catch (e) {
                // Fall back to 'crew'
            }
        }
    }

    public dispose() {
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from webview
        const messageDisposable = webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'selectPattern':
                    this._selectPattern(message.pattern);
                    break;
                case 'setName':
                    this._setName(message.name);
                    break;
                case 'setDescription':
                    this._setDescription(message.description);
                    break;
                case 'setOutputDir':
                    this._setOutputDir(message.outputDir);
                    break;
                case 'goToStep':
                    this._goToStep(message.step);
                    break;
                case 'generatePreview':
                    this._generatePreview();
                    break;
                case 'createWorkflow':
                    await this._createWorkflow();
                    break;
                case 'reset':
                    this._reset();
                    break;
                case 'getInitialState':
                    this._sendState();
                    break;
                case 'browseOutputDir':
                    await this._browseOutputDir();
                    break;
                case 'setNumAgents':
                    this._setNumAgents(message.num);
                    break;
                case 'setProcessType':
                    this._setProcessType(message.processType);
                    break;
                case 'updateAgent':
                    this._updateAgent(message.agentId, message.field, message.value);
                    break;
                case 'addTask':
                    this._addTask();
                    break;
                case 'updateTask':
                    this._updateTask(message.taskId, message.field, message.value);
                    break;
                case 'removeTask':
                    this._removeTask(message.taskId);
                    break;
            }
        });

        this._disposables.push(messageDisposable);
    }

    // =========================================================================
    // State Management
    // =========================================================================

    private _selectPattern(pattern: 'crew' | 'base' | 'compose'): void {
        this._session.selectedPattern = pattern;
        this._session.step = 'overview';
        this._sendState();
    }

    private _setName(name: string): void {
        this._session.workflowName = name;
        if (this._session.selectedPattern) {
            this._session.className = toClassName(name, this._session.selectedPattern);
        }
        this._sendState();
    }

    private _setDescription(description: string): void {
        this._session.description = description;
        this._sendState();
    }

    private _setOutputDir(outputDir: string): void {
        this._session.outputDir = outputDir;
        this._sendState();
    }

    private _setNumAgents(num: number): void {
        this._session.numAgents = Math.max(2, Math.min(5, num));
        // Adjust agents array to match
        while (this._session.agents.length < this._session.numAgents) {
            const idx = this._session.agents.length;
            this._session.agents.push({
                id: `agent-${idx + 1}`,
                role: `Agent ${idx + 1}`,
                goal: 'Define the goal for this agent',
                backstory: 'Describe the agent\'s expertise and approach',
                expertiseLevel: 'expert'
            });
        }
        while (this._session.agents.length > this._session.numAgents) {
            this._session.agents.pop();
        }
        this._sendState();
    }

    private _setProcessType(processType: 'sequential' | 'hierarchical'): void {
        this._session.processType = processType;
        this._sendState();
    }

    private _updateAgent(agentId: string, field: string, value: string): void {
        const agent = this._session.agents.find(a => a.id === agentId);
        if (agent) {
            (agent as any)[field] = value;
        }
        this._sendState();
    }

    private _addTask(): void {
        const idx = this._session.tasks.length;
        this._session.tasks.push({
            id: `task-${idx + 1}`,
            description: 'Describe what this task should accomplish',
            expectedOutput: 'Describe the expected output format',
            assignedAgentId: this._session.agents[0]?.id || 'agent-1'
        });
        this._sendState();
    }

    private _updateTask(taskId: string, field: string, value: string): void {
        const task = this._session.tasks.find(t => t.id === taskId);
        if (task) {
            (task as any)[field] = value;
        }
        this._sendState();
    }

    private _removeTask(taskId: string): void {
        this._session.tasks = this._session.tasks.filter(t => t.id !== taskId);
        this._sendState();
    }

    private _goToStep(step: WizardStep): void {
        this._session.step = step;
        this._sendState();
    }

    private _generatePreview(): void {
        if (!this._session.selectedPattern || !this._session.workflowName) {
            return;
        }

        this._session.className = toClassName(
            this._session.workflowName,
            this._session.selectedPattern
        );

        // For crew pattern, use the enhanced template with agents/tasks
        if (this._session.selectedPattern === 'crew') {
            this._session.generatedCode = generateCrewTemplateWithAgents(
                this._session.className,
                this._session.workflowName,
                this._session.description,
                this._session.agents,
                this._session.tasks,
                this._session.processType
            );
        } else {
            this._session.generatedCode = generateTemplate(
                this._session.selectedPattern,
                this._session.className,
                this._session.workflowName,
                this._session.description
            );
        }
        this._session.step = 'preview';
        this._sendState();
    }

    private async _createWorkflow(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const fileName = toFileName(this._session.workflowName);
        const outputDir = path.join(workspaceFolder, this._session.outputDir);
        const filePath = path.join(outputDir, fileName);

        // Create directory if needed
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Check if file exists
        if (fs.existsSync(filePath)) {
            const answer = await vscode.window.showWarningMessage(
                `File ${fileName} already exists. Overwrite?`,
                'Yes', 'No'
            );
            if (answer !== 'Yes') {
                return;
            }
        }

        // Write file
        try {
            fs.writeFileSync(filePath, this._session.generatedCode);
            vscode.window.showInformationMessage(`Created ${fileName}`);

            // Open the file
            const doc = await vscode.workspace.openTextDocument(filePath);
            await vscode.window.showTextDocument(doc);

            // Reset session
            this._reset();
        } catch (err) {
            vscode.window.showErrorMessage(`Failed to create file: ${(err as Error).message}`);
        }
    }

    private async _browseOutputDir(): Promise<void> {
        const result = await this._filePickerService.showFolderPicker({
            title: 'Select Output Directory',
            openLabel: 'Select'
        });

        if (result) {
            this._session.outputDir = result.path;
            this._sendState();
        }
    }

    private _reset(): void {
        this._session = this._createEmptySession();
        this._sendState();
    }

    private _sendState(): void {
        const patterns = WORKFLOW_PATTERNS.map(p => ({
            ...p,
            isDefault: p.id === this._defaultPattern
        }));

        this._view?.webview.postMessage({
            type: 'state',
            session: this._session,
            patterns,
            defaultPattern: this._defaultPattern
        });
    }

    // =========================================================================
    // WebView HTML
    // =========================================================================

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Workflow Wizard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-sideBar-background);
            padding: 12px;
        }
        .hidden { display: none !important; }

        /* Header */
        .header {
            margin-bottom: 16px;
        }
        .header h1 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .header p {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }

        /* Steps indicator */
        .steps {
            display: flex;
            gap: 4px;
            margin-bottom: 16px;
        }
        .step-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--vscode-input-border);
        }
        .step-dot.active { background: var(--vscode-button-background); }
        .step-dot.completed { background: #22c55e; }

        /* Pattern Cards */
        .pattern-grid {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .pattern-card {
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 12px;
            cursor: pointer;
            transition: border-color 0.2s;
        }
        .pattern-card:hover {
            border-color: var(--vscode-button-background);
        }
        .pattern-card.selected {
            border-color: var(--vscode-button-background);
            background: rgba(var(--vscode-button-background), 0.1);
        }
        .pattern-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        .pattern-name {
            font-weight: 600;
            font-size: 12px;
        }
        .pattern-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
        }
        .pattern-badge.default {
            background: #22c55e;
            color: white;
        }
        .pattern-desc {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
        }
        .pattern-best-for {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }
        .pattern-best-for strong {
            color: var(--vscode-foreground);
        }
        .pattern-tradeoffs {
            display: flex;
            gap: 8px;
            margin-top: 6px;
            font-size: 10px;
        }
        .tradeoff {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .tradeoff-label {
            color: var(--vscode-descriptionForeground);
        }

        /* Form */
        .form-group {
            margin-bottom: 14px;
        }
        .form-label {
            display: block;
            font-size: 11px;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .form-input {
            width: 100%;
            padding: 6px 10px;
            border: 1px solid var(--vscode-input-border);
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border-radius: 4px;
            font-size: 12px;
        }
        .form-input:focus {
            outline: 1px solid var(--vscode-focusBorder);
        }
        .form-hint {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
        }
        .input-group {
            display: flex;
            gap: 6px;
        }
        .input-group .form-input {
            flex: 1;
        }

        /* Preview */
        .preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .preview-file {
            font-size: 12px;
            font-weight: 500;
        }
        .preview-pattern {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
        }
        .preview-code {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            padding: 10px;
            font-family: var(--vscode-editor-font-family);
            font-size: 11px;
            line-height: 1.4;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre;
        }

        /* Syntax Highlighting */
        .keyword { color: var(--vscode-symbolIcon-keywordForeground, #569cd6); }
        .string { color: var(--vscode-symbolIcon-stringForeground, #ce9178); }
        .comment { color: var(--vscode-symbolIcon-commentForeground, #6a9955); }
        .function { color: var(--vscode-symbolIcon-functionForeground, #dcdcaa); }
        .decorator { color: var(--vscode-symbolIcon-eventForeground, #c586c0); }
        .class-name { color: var(--vscode-symbolIcon-classForeground, #4ec9b0); }

        /* Buttons */
        .button-row {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }
        .button {
            padding: 6px 14px;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .button:hover { background: var(--vscode-button-hoverBackground); }
        .button:disabled { opacity: 0.5; cursor: not-allowed; }
        .button-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        .button-secondary:hover { background: var(--vscode-button-secondaryHoverBackground); }
        .button-success {
            background: #22c55e;
            color: white;
        }
        .button-success:hover { background: #16a34a; }
        .button-small {
            padding: 4px 8px;
            font-size: 11px;
        }

        /* Section */
        .section { margin-bottom: 20px; }
        .section-title {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        /* Agent/Task Cards */
        .agent-card, .task-card {
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .agent-card-header, .task-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .agent-card-title, .task-card-title {
            font-weight: 500;
            font-size: 11px;
        }
        .card-remove {
            background: none;
            border: none;
            color: var(--vscode-descriptionForeground);
            cursor: pointer;
            font-size: 14px;
            padding: 0 4px;
        }
        .card-remove:hover { color: var(--vscode-errorForeground); }
        .card-field {
            margin-bottom: 8px;
        }
        .card-field:last-child { margin-bottom: 0; }
        .card-field label {
            display: block;
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 2px;
        }
        .card-field input, .card-field textarea, .card-field select {
            width: 100%;
            padding: 4px 8px;
            font-size: 11px;
            border: 1px solid var(--vscode-input-border);
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border-radius: 3px;
        }
        .card-field textarea { resize: vertical; min-height: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Workflow Wizard</h1>
        <p>Create a new workflow from template</p>
    </div>

    <!-- Steps indicator (dynamic based on pattern) -->
    <div class="steps" id="steps-container"></div>

    <!-- Step 1: Pattern Selection -->
    <div id="view-pattern" class="section">
        <div class="section-title">Select Pattern</div>
        <div id="patterns-container" class="pattern-grid"></div>
    </div>

    <!-- Step 2: Overview (for all patterns) -->
    <div id="view-overview" class="section hidden">
        <div class="section-title">Workflow Overview</div>
        <div class="form-group">
            <label class="form-label">Workflow Name</label>
            <input type="text" id="input-name" class="form-input" placeholder="my-workflow">
            <div class="form-hint">Use kebab-case (e.g., security-scanner, code-reviewer)</div>
        </div>
        <div class="form-group">
            <label class="form-label">Goal / Description</label>
            <textarea id="input-description" class="form-input" rows="2" placeholder="What is the goal of this workflow?"></textarea>
        </div>
        <!-- Crew-specific fields -->
        <div id="crew-fields" class="hidden">
            <div class="form-group">
                <label class="form-label">Number of Agents</label>
                <select id="input-num-agents" class="form-input">
                    <option value="2">2 agents</option>
                    <option value="3" selected>3 agents</option>
                    <option value="4">4 agents</option>
                    <option value="5">5 agents</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Process Type</label>
                <select id="input-process-type" class="form-input">
                    <option value="sequential" selected>Sequential - Tasks run in order</option>
                    <option value="hierarchical">Hierarchical - Manager coordinates agents</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Output Directory</label>
            <div class="input-group">
                <input type="text" id="input-output" class="form-input" value="src/empathy_os/workflows">
                <button class="button button-secondary button-small" id="btn-browse">Browse</button>
            </div>
        </div>
        <div id="class-preview" class="form-hint" style="margin-top: 8px;"></div>
        <div class="button-row">
            <button class="button button-secondary" id="btn-back-pattern">Back</button>
            <button class="button" id="btn-next-overview">Next</button>
        </div>
    </div>

    <!-- Step 3: Define Agents (Crew pattern only) -->
    <div id="view-agents" class="section hidden">
        <div class="section-title">Define Agents</div>
        <div class="form-hint" style="margin-bottom: 12px;">Configure each agent's role, goal, and backstory. The 80/20 rule: well-designed tasks matter more than perfect agents.</div>
        <div id="agents-container"></div>
        <div class="button-row">
            <button class="button button-secondary" id="btn-back-overview">Back</button>
            <button class="button" id="btn-next-agents">Next: Define Tasks</button>
        </div>
    </div>

    <!-- Step 4: Define Tasks (Crew pattern only) -->
    <div id="view-tasks" class="section hidden">
        <div class="section-title">Define Tasks</div>
        <div class="form-hint" style="margin-bottom: 12px;">Tasks are the most important part (80/20 rule). Define clear descriptions and expected outputs.</div>
        <div id="tasks-container"></div>
        <button class="button button-secondary button-small" id="btn-add-task" style="margin-top: 8px;">+ Add Task</button>
        <div class="button-row">
            <button class="button button-secondary" id="btn-back-agents">Back</button>
            <button class="button" id="btn-next-tasks">Preview</button>
        </div>
    </div>

    <!-- Step 5: Preview -->
    <div id="view-preview" class="section hidden">
        <div class="preview-header">
            <span class="preview-file" id="preview-filename"></span>
            <span class="preview-pattern" id="preview-pattern"></span>
        </div>
        <div id="preview-code" class="preview-code"></div>
        <div class="button-row">
            <button class="button button-secondary" id="btn-back-tasks">Back</button>
            <button class="button button-success" id="btn-create">Create Workflow</button>
        </div>
    </div>

    <!-- CLI Hint -->
    <div class="cli-hint" style="margin-top: 16px; padding: 8px; background: var(--vscode-textBlockQuote-background); border-radius: 4px; font-size: 11px;">
        <span style="opacity: 0.7;">CLI:</span>
        <code style="font-family: var(--vscode-editor-font-family); background: var(--vscode-editor-background); padding: 2px 6px; border-radius: 3px; margin-left: 4px;">empathy workflow new &lt;name&gt;</code>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();

        // State
        let currentSession = null;
        let previousStep = null;
        let previousAgentCount = 0;
        let previousTaskCount = 0;
        let patterns = [];
        let defaultPattern = 'crew';

        // Elements
        const viewPattern = document.getElementById('view-pattern');
        const viewOverview = document.getElementById('view-overview');
        const viewAgents = document.getElementById('view-agents');
        const viewTasks = document.getElementById('view-tasks');
        const viewPreview = document.getElementById('view-preview');
        const patternsContainer = document.getElementById('patterns-container');
        const stepsContainer = document.getElementById('steps-container');
        const crewFields = document.getElementById('crew-fields');
        const agentsContainer = document.getElementById('agents-container');
        const tasksContainer = document.getElementById('tasks-container');
        const inputName = document.getElementById('input-name');
        const inputDescription = document.getElementById('input-description');
        const inputOutput = document.getElementById('input-output');
        const inputNumAgents = document.getElementById('input-num-agents');
        const inputProcessType = document.getElementById('input-process-type');
        const classPreview = document.getElementById('class-preview');
        const previewFilename = document.getElementById('preview-filename');
        const previewPattern = document.getElementById('preview-pattern');
        const previewCode = document.getElementById('preview-code');
        const btnNextOverview = document.getElementById('btn-next-overview');

        // Event handlers - Overview step
        document.getElementById('btn-browse').addEventListener('click', () => {
            vscode.postMessage({ type: 'browseOutputDir' });
        });

        document.getElementById('btn-back-pattern').addEventListener('click', () => {
            vscode.postMessage({ type: 'goToStep', step: 'pattern' });
        });

        document.getElementById('btn-next-overview').addEventListener('click', () => {
            if (currentSession?.selectedPattern === 'crew') {
                vscode.postMessage({ type: 'goToStep', step: 'agents' });
            } else {
                vscode.postMessage({ type: 'generatePreview' });
            }
        });

        // Event handlers - Agents step
        document.getElementById('btn-back-overview').addEventListener('click', () => {
            vscode.postMessage({ type: 'goToStep', step: 'overview' });
        });

        document.getElementById('btn-next-agents').addEventListener('click', () => {
            vscode.postMessage({ type: 'goToStep', step: 'tasks' });
        });

        // Event handlers - Tasks step
        document.getElementById('btn-back-agents').addEventListener('click', () => {
            vscode.postMessage({ type: 'goToStep', step: 'agents' });
        });

        document.getElementById('btn-next-tasks').addEventListener('click', () => {
            vscode.postMessage({ type: 'generatePreview' });
        });

        document.getElementById('btn-add-task').addEventListener('click', () => {
            vscode.postMessage({ type: 'addTask' });
        });

        // Event handlers - Preview step
        document.getElementById('btn-back-tasks').addEventListener('click', () => {
            if (currentSession?.selectedPattern === 'crew') {
                vscode.postMessage({ type: 'goToStep', step: 'tasks' });
            } else {
                vscode.postMessage({ type: 'goToStep', step: 'overview' });
            }
        });

        document.getElementById('btn-create').addEventListener('click', () => {
            vscode.postMessage({ type: 'createWorkflow' });
        });

        // Input handlers
        inputName.addEventListener('input', (e) => {
            const name = e.target.value;
            vscode.postMessage({ type: 'setName', name });
            updateClassPreview(name);
            updateNextButton();
        });

        inputDescription.addEventListener('input', (e) => {
            vscode.postMessage({ type: 'setDescription', description: e.target.value });
        });

        inputOutput.addEventListener('input', (e) => {
            vscode.postMessage({ type: 'setOutputDir', outputDir: e.target.value });
        });

        inputNumAgents.addEventListener('change', (e) => {
            vscode.postMessage({ type: 'setNumAgents', num: parseInt(e.target.value) });
        });

        inputProcessType.addEventListener('change', (e) => {
            vscode.postMessage({ type: 'setProcessType', processType: e.target.value });
        });

        function updateNextButton() {
            btnNextOverview.disabled = !inputName.value.trim();
        }

        function updateClassPreview(name) {
            if (!name || !currentSession?.selectedPattern) {
                classPreview.textContent = '';
                return;
            }
            const base = name.replace(/-/g, '_').split('_')
                .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
                .join('');
            let className = base;
            if (!base.endsWith('Workflow') && !base.endsWith('Crew') && !base.endsWith('Pipeline')) {
                if (currentSession.selectedPattern === 'crew') className += 'Crew';
                else if (currentSession.selectedPattern === 'compose') className += 'Pipeline';
                else className += 'Workflow';
            }
            const fileName = name.replace(/-/g, '_').toLowerCase() + '.py';
            classPreview.textContent = 'Class: ' + className + ' | File: ' + fileName;
        }

        // Render step indicators
        function renderSteps() {
            const isCrew = currentSession?.selectedPattern === 'crew';
            const stepCount = isCrew ? 5 : 3;
            const stepMap = isCrew
                ? ['pattern', 'overview', 'agents', 'tasks', 'preview']
                : ['pattern', 'overview', 'preview'];
            const currentStepIdx = stepMap.indexOf(currentSession?.step || 'pattern');

            let html = '';
            for (let i = 0; i < stepCount; i++) {
                let classes = 'step-dot';
                if (i < currentStepIdx) classes += ' completed';
                else if (i === currentStepIdx) classes += ' active';
                html += '<div class="' + classes + '"></div>';
            }
            stepsContainer.innerHTML = html;
        }

        // Render patterns
        function renderPatterns() {
            patternsContainer.innerHTML = '';
            patterns.forEach(p => {
                const card = document.createElement('div');
                card.className = 'pattern-card' + (currentSession?.selectedPattern === p.id ? ' selected' : '');
                card.innerHTML = \`
                    <div class="pattern-header">
                        <span class="pattern-name">\${p.name}</span>
                        \${p.isDefault ? '<span class="pattern-badge default">default</span>' : ''}
                    </div>
                    <div class="pattern-desc">\${p.description}</div>
                    <div class="pattern-best-for">
                        <strong>Best for:</strong> \${p.bestFor.join(', ')}
                    </div>
                    <div class="pattern-tradeoffs">
                        <div class="tradeoff">
                            <span class="tradeoff-label">Cost:</span> \${p.tradeoffs.cost}
                        </div>
                        <div class="tradeoff">
                            <span class="tradeoff-label">Speed:</span> \${p.tradeoffs.speed}
                        </div>
                        <div class="tradeoff">
                            <span class="tradeoff-label">Thoroughness:</span> \${p.tradeoffs.thoroughness}
                        </div>
                    </div>
                \`;
                card.addEventListener('click', () => {
                    vscode.postMessage({ type: 'selectPattern', pattern: p.id });
                });
                patternsContainer.appendChild(card);
            });
        }

        // Render agents
        function renderAgents() {
            if (!currentSession?.agents) return;
            let html = '';
            currentSession.agents.forEach((agent, idx) => {
                html += \`
                <div class="agent-card" data-agent-id="\${agent.id}">
                    <div class="agent-card-header">
                        <span class="agent-card-title">Agent \${idx + 1}</span>
                    </div>
                    <div class="card-field">
                        <label>Role</label>
                        <input type="text" class="agent-role" value="\${escapeHtml(agent.role)}" placeholder="e.g., Senior Security Analyst">
                    </div>
                    <div class="card-field">
                        <label>Goal</label>
                        <input type="text" class="agent-goal" value="\${escapeHtml(agent.goal)}" placeholder="What is this agent trying to achieve?">
                    </div>
                    <div class="card-field">
                        <label>Backstory</label>
                        <textarea class="agent-backstory" rows="2" placeholder="Describe expertise and approach">\${escapeHtml(agent.backstory)}</textarea>
                    </div>
                    <div class="card-field">
                        <label>Expertise Level</label>
                        <select class="agent-expertise">
                            <option value="novice" \${agent.expertiseLevel === 'novice' ? 'selected' : ''}>Novice</option>
                            <option value="intermediate" \${agent.expertiseLevel === 'intermediate' ? 'selected' : ''}>Intermediate</option>
                            <option value="expert" \${agent.expertiseLevel === 'expert' ? 'selected' : ''}>Expert</option>
                            <option value="world-class" \${agent.expertiseLevel === 'world-class' ? 'selected' : ''}>World-class</option>
                        </select>
                    </div>
                </div>\`;
            });
            agentsContainer.innerHTML = html;

            // Add event listeners
            document.querySelectorAll('.agent-card').forEach(card => {
                const agentId = card.dataset.agentId;
                card.querySelector('.agent-role').addEventListener('input', (e) => {
                    vscode.postMessage({ type: 'updateAgent', agentId, field: 'role', value: e.target.value });
                });
                card.querySelector('.agent-goal').addEventListener('input', (e) => {
                    vscode.postMessage({ type: 'updateAgent', agentId, field: 'goal', value: e.target.value });
                });
                card.querySelector('.agent-backstory').addEventListener('input', (e) => {
                    vscode.postMessage({ type: 'updateAgent', agentId, field: 'backstory', value: e.target.value });
                });
                card.querySelector('.agent-expertise').addEventListener('change', (e) => {
                    vscode.postMessage({ type: 'updateAgent', agentId, field: 'expertiseLevel', value: e.target.value });
                });
            });
        }

        // Render tasks
        function renderTasks() {
            if (!currentSession?.tasks || !currentSession?.agents) return;
            let html = '';
            currentSession.tasks.forEach((task, idx) => {
                const agentOptions = currentSession.agents.map(a =>
                    '<option value="' + a.id + '"' + (task.assignedAgentId === a.id ? ' selected' : '') + '>' + escapeHtml(a.role) + '</option>'
                ).join('');

                html += \`
                <div class="task-card" data-task-id="\${task.id}">
                    <div class="task-card-header">
                        <span class="task-card-title">Task \${idx + 1}</span>
                        \${currentSession.tasks.length > 1 ? '<button class="card-remove task-remove">&times;</button>' : ''}
                    </div>
                    <div class="card-field">
                        <label>Description</label>
                        <textarea class="task-description" rows="2" placeholder="What should be done?">\${escapeHtml(task.description)}</textarea>
                    </div>
                    <div class="card-field">
                        <label>Expected Output</label>
                        <input type="text" class="task-output" value="\${escapeHtml(task.expectedOutput)}" placeholder="What format/structure should the result have?">
                    </div>
                    <div class="card-field">
                        <label>Assigned Agent</label>
                        <select class="task-agent">\${agentOptions}</select>
                    </div>
                </div>\`;
            });
            tasksContainer.innerHTML = html;

            // Add event listeners
            document.querySelectorAll('.task-card').forEach(card => {
                const taskId = card.dataset.taskId;
                card.querySelector('.task-description').addEventListener('input', (e) => {
                    vscode.postMessage({ type: 'updateTask', taskId, field: 'description', value: e.target.value });
                });
                card.querySelector('.task-output').addEventListener('input', (e) => {
                    vscode.postMessage({ type: 'updateTask', taskId, field: 'expectedOutput', value: e.target.value });
                });
                card.querySelector('.task-agent').addEventListener('change', (e) => {
                    vscode.postMessage({ type: 'updateTask', taskId, field: 'assignedAgentId', value: e.target.value });
                });
                const removeBtn = card.querySelector('.task-remove');
                if (removeBtn) {
                    removeBtn.addEventListener('click', () => {
                        vscode.postMessage({ type: 'removeTask', taskId });
                    });
                }
            });
        }

        function escapeHtml(text) {
            if (!text) return '';
            return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }

        // Syntax highlighting
        function highlightCode(code) {
            if (!code) return '';
            let escaped = code
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');

            const kwPattern = /\\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|async|await|yield|lambda|pass|break|continue|raise|in|is|not|and|or|True|False|None)\\b/g;

            escaped = escaped
                .replace(/(#[^\\n]*)/g, '<span class="comment">$1</span>')
                .replace(/(@\\w+)/g, '<span class="decorator">$1</span>')
                .replace(/("""[\\s\\S]*?""")/g, '<span class="string">$1</span>')
                .replace(/('[^'\\n]*'|"[^"\\n]*")/g, '<span class="string">$1</span>')
                .replace(kwPattern, '<span class="keyword">$1</span>')
                .replace(/\\bclass\\s+(\\w+)/g, 'class <span class="class-name">$1</span>')
                .replace(/\\bdef\\s+(\\w+)/g, 'def <span class="function">$1</span>');

            return escaped;
        }

        // Update view based on current step
        function updateView() {
            if (!currentSession) return;

            const stepChanged = previousStep !== currentSession.step;
            const agentCountChanged = previousAgentCount !== (currentSession.agents?.length || 0);
            const taskCountChanged = previousTaskCount !== (currentSession.tasks?.length || 0);

            // Only update visibility and render when step changes
            if (stepChanged) {
                // Hide all views
                viewPattern.classList.add('hidden');
                viewOverview.classList.add('hidden');
                viewAgents.classList.add('hidden');
                viewTasks.classList.add('hidden');
                viewPreview.classList.add('hidden');

                // Render steps indicator
                renderSteps();

                const isCrew = currentSession.selectedPattern === 'crew';

                switch (currentSession.step) {
                    case 'pattern':
                        viewPattern.classList.remove('hidden');
                        renderPatterns();
                        break;

                    case 'overview':
                        viewOverview.classList.remove('hidden');
                        inputName.value = currentSession.workflowName;
                        inputDescription.value = currentSession.description;
                        inputOutput.value = currentSession.outputDir;
                        inputNumAgents.value = currentSession.numAgents;
                        inputProcessType.value = currentSession.processType;
                        updateClassPreview(currentSession.workflowName);
                        updateNextButton();
                        // Show/hide crew-specific fields
                        if (isCrew) {
                            crewFields.classList.remove('hidden');
                            btnNextOverview.textContent = 'Next: Define Agents';
                        } else {
                            crewFields.classList.add('hidden');
                            btnNextOverview.textContent = 'Preview';
                        }
                        break;

                    case 'agents':
                        viewAgents.classList.remove('hidden');
                        renderAgents();
                        break;

                    case 'tasks':
                        viewTasks.classList.remove('hidden');
                        renderTasks();
                        break;

                    case 'preview':
                        viewPreview.classList.remove('hidden');
                        const fileName = currentSession.workflowName.replace(/-/g, '_').toLowerCase() + '.py';
                        previewFilename.textContent = fileName;
                        previewPattern.textContent = currentSession.selectedPattern;
                        previewCode.innerHTML = highlightCode(currentSession.generatedCode);
                        break;
                }

                previousStep = currentSession.step;
            } else {
                // Step didn't change - only re-render if agent/task counts changed
                if (currentSession.step === 'agents' && agentCountChanged) {
                    renderAgents();
                }
                if (currentSession.step === 'tasks' && taskCountChanged) {
                    renderTasks();
                }
            }

            // Always update counts
            previousAgentCount = currentSession.agents?.length || 0;
            previousTaskCount = currentSession.tasks?.length || 0;
        }

        // Message handler
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'state') {
                currentSession = message.session;
                patterns = message.patterns;
                defaultPattern = message.defaultPattern;
                updateView();
            }
        });

        // Request initial state
        vscode.postMessage({ type: 'getInitialState' });
    </script>
</body>
</html>`;
    }
}
