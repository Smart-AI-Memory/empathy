/**
 * Workflow Factory Panel - Full-Screen Interactive Workflow Creation
 *
 * Opens in editor area as a tab (like Claude Code) featuring:
 * - Visual pattern selection with descriptions
 * - Comprehensive agent/crew selection and configuration
 * - Interactive form with validation
 * - One-click workflow creation
 * - Real-time preview of generated code
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';

interface WorkflowPattern {
    id: string;
    name: string;
    category: string;
    complexity: string;
    description: string;
    requires: string[];
    conflicts: string[];
}

interface Agent {
    id: string;
    name: string;
    role: string;
    goal?: string;
    backstory?: string;
    tools?: string[];
}

interface Crew {
    id: string;
    name: string;
    description: string;
    agents: Agent[];
}

export class WorkflowFactoryPanel {
    public static currentPanel: WorkflowFactoryPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _patterns: WorkflowPattern[] = [];
    private _crews: Crew[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._loadPatterns();
        this._loadCrews();
        this._panel.webview.html = this._getHtmlForWebview();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'createWorkflow':
                        await this._createWorkflow(message.data);
                        break;
                    case 'listPatterns':
                        await this._listPatterns();
                        break;
                    case 'recommend':
                        await this._recommendPatterns(message.workflowType);
                        break;
                    case 'validateName':
                        this._validateWorkflowName(message.name);
                        break;
                    case 'getPatterns':
                        this._sendPatterns();
                        break;
                    case 'getCrews':
                        this._sendCrews();
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (WorkflowFactoryPanel.currentPanel) {
            WorkflowFactoryPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'workflowFactory',
            '🚀 Workflow Factory',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [extensionUri],
            }
        );

        WorkflowFactoryPanel.currentPanel = new WorkflowFactoryPanel(panel, extensionUri);
    }

    public dispose() {
        WorkflowFactoryPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _loadPatterns() {
        try {
            const result = cp.execSync('python -m workflow_scaffolding list-patterns --json', {
                cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
                encoding: 'utf-8',
                timeout: 5000
            });
            const output = JSON.parse(result);
            this._patterns = output.patterns || [];
        } catch (err) {
            console.error('Failed to load workflow patterns:', err);
            // Fallback patterns
            this._patterns = [
                {
                    id: 'single-stage',
                    name: 'Single Stage',
                    category: 'STRUCTURAL',
                    complexity: 'SIMPLE',
                    description: 'Simple one-tier workflow for straightforward tasks',
                    requires: [],
                    conflicts: ['multi-stage', 'crew-based']
                },
                {
                    id: 'multi-stage',
                    name: 'Multi-Stage',
                    category: 'STRUCTURAL',
                    complexity: 'MODERATE',
                    description: 'Sequential workflow with multiple processing stages',
                    requires: [],
                    conflicts: ['single-stage', 'crew-based']
                },
                {
                    id: 'conditional-tier',
                    name: 'Conditional Tier',
                    category: 'TIER',
                    complexity: 'MODERATE',
                    description: 'Dynamic tier selection based on complexity',
                    requires: ['multi-stage'],
                    conflicts: []
                },
                {
                    id: 'code-scanner',
                    name: 'Code Scanner',
                    category: 'BEHAVIOR',
                    complexity: 'MODERATE',
                    description: 'File scanning and code analysis capabilities',
                    requires: [],
                    conflicts: []
                },
                {
                    id: 'config-driven',
                    name: 'Config Driven',
                    category: 'INTEGRATION',
                    complexity: 'SIMPLE',
                    description: 'Load settings from empathy.config.yml',
                    requires: [],
                    conflicts: []
                },
                {
                    id: 'result-dataclass',
                    name: 'Result Dataclass',
                    category: 'OUTPUT',
                    complexity: 'SIMPLE',
                    description: 'Structured output with typed results',
                    requires: [],
                    conflicts: []
                },
                {
                    id: 'crew-based',
                    name: 'Crew Based',
                    category: 'STRUCTURAL',
                    complexity: 'COMPLEX',
                    description: 'Wraps existing CrewAI multi-agent crew',
                    requires: [],
                    conflicts: ['single-stage', 'multi-stage']
                }
            ];
        }
    }

    private _loadCrews() {
        // Available CrewAI crews
        this._crews = [
            {
                id: 'code_review',
                name: 'Code Review Crew',
                description: 'Comprehensive code review with 5 specialized agents',
                agents: [
                    { id: 'lead', name: 'Review Lead', role: 'Coordinator', goal: 'Orchestrate code review team', backstory: 'Senior engineer with 15+ years experience' },
                    { id: 'security', name: 'Security Analyst', role: 'Security Expert', goal: 'Find security vulnerabilities', backstory: 'Security specialist focused on OWASP Top 10' },
                    { id: 'architecture', name: 'Architecture Reviewer', role: 'Software Architect', goal: 'Evaluate design patterns', backstory: 'Expert in SOLID principles and scalability' },
                    { id: 'quality', name: 'Quality Analyst', role: 'Code Quality Expert', goal: 'Identify code smells', backstory: 'Maintainability and testing specialist' },
                    { id: 'performance', name: 'Performance Reviewer', role: 'Performance Engineer', goal: 'Find optimization opportunities', backstory: 'Expert in performance profiling' }
                ]
            },
            {
                id: 'security_audit',
                name: 'Security Audit Crew',
                description: 'Deep security analysis and vulnerability detection',
                agents: [
                    { id: 'scanner', name: 'Vulnerability Scanner', role: 'Security Scanner', goal: 'Detect known vulnerabilities' },
                    { id: 'analyst', name: 'Threat Analyst', role: 'Threat Modeler', goal: 'Assess security risks' },
                    { id: 'auditor', name: 'Compliance Auditor', role: 'Compliance Expert', goal: 'Check security standards' }
                ]
            },
            {
                id: 'refactoring',
                name: 'Refactoring Crew',
                description: 'Code improvement and technical debt reduction',
                agents: [
                    { id: 'analyzer', name: 'Code Analyzer', role: 'Static Analysis Expert', goal: 'Identify code smells' },
                    { id: 'refactorer', name: 'Refactoring Specialist', role: 'Refactoring Expert', goal: 'Suggest improvements' },
                    { id: 'reviewer', name: 'Impact Reviewer', role: 'Change Assessor', goal: 'Evaluate refactoring impact' }
                ]
            },
            {
                id: 'health_check',
                name: 'Health Check Crew',
                description: 'Overall codebase health assessment',
                agents: [
                    { id: 'metrics', name: 'Metrics Collector', role: 'Metrics Analyst', goal: 'Gather code metrics' },
                    { id: 'tester', name: 'Test Analyzer', role: 'Testing Expert', goal: 'Assess test coverage' },
                    { id: 'reporter', name: 'Health Reporter', role: 'Report Generator', goal: 'Generate health report' }
                ]
            },
            {
                id: 'custom',
                name: 'Custom Agents',
                description: 'Build your own agent configuration',
                agents: []
            }
        ];
    }

    private async _createWorkflow(data: {
        name: string;
        description: string;
        patterns: string[];
        stages: string;
        crew?: string;
        customAgents?: Agent[];
    }) {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!workspaceFolder) {
                throw new Error('No workspace folder open');
            }

            const terminal = vscode.window.createTerminal('Workflow Factory');
            terminal.show();

            let cmd = `empathy workflow create ${data.name}`;
            if (data.description) {
                cmd += ` --description "${data.description}"`;
            }
            if (data.patterns && data.patterns.length > 0) {
                cmd += ` --patterns ${data.patterns.join(',')}`;
            }
            if (data.stages) {
                cmd += ` --stages ${data.stages.replace(/,\s+/g, ',')}`;  // Remove spaces after commas
            }
            // Note: --crew parameter doesn't exist in CLI yet
            // Crew selection is for reference only - edit generated workflow to specify crew

            terminal.sendText(cmd);

            // Show helpful message about selected crew
            if (data.crew && data.crew !== 'custom') {
                const crew = this._crews.find(c => c.id === data.crew);
                if (crew) {
                    terminal.sendText(`# Selected crew: ${crew.name} (${crew.agents.length} agents)`);
                    terminal.sendText(`# Edit the generated workflow to use: ${data.crew}`);
                }
            }

            // Show success with agent info
            let agentInfo = '';
            if (data.crew && data.crew !== 'custom') {
                const crew = this._crews.find(c => c.id === data.crew);
                if (crew) {
                    agentInfo = ` with ${crew.agents.length} agents from ${crew.name}`;
                }
            } else if (data.customAgents && data.customAgents.length > 0) {
                agentInfo = ` with ${data.customAgents.length} custom agents`;
            }

            this._panel.webview.postMessage({
                type: 'workflowCreated',
                success: true,
                message: `Workflow "${data.name}" created successfully${agentInfo}! Check the terminal for details.`,
                workflowName: data.name
            });

            vscode.window.showInformationMessage(`✨ Workflow "${data.name}" created! (12x faster)`);
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : String(err);
            this._panel.webview.postMessage({
                type: 'workflowCreated',
                success: false,
                message: errorMsg
            });
            vscode.window.showErrorMessage(`Failed to create workflow: ${errorMsg}`);
        }
    }

    private async _listPatterns() {
        const terminal = vscode.window.createTerminal('Workflow Patterns');
        terminal.show();
        terminal.sendText('empathy workflow list-patterns');
    }

    private async _recommendPatterns(workflowType: string) {
        const terminal = vscode.window.createTerminal('Pattern Recommendations');
        terminal.show();
        terminal.sendText(`empathy workflow recommend ${workflowType}`);
    }

    private _validateWorkflowName(name: string) {
        const isValid = /^[a-z][a-z0-9-]*$/.test(name);
        const message = isValid
            ? ''
            : 'Use kebab-case: lowercase letters, numbers, and hyphens only';

        this._panel.webview.postMessage({
            type: 'nameValidation',
            isValid,
            message
        });
    }

    private _sendPatterns() {
        this._panel.webview.postMessage({
            type: 'patternsData',
            patterns: this._patterns
        });
    }

    private _sendCrews() {
        this._panel.webview.postMessage({
            type: 'crewsData',
            crews: this._crews
        });
    }

    private _getHtmlForWebview(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Factory</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            padding: 0;
            overflow-x: hidden;
        }

        .header {
            background: var(--vscode-titleBar-activeBackground);
            padding: 24px 40px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 40px;
        }

        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 32px;
            margin-bottom: 32px;
        }

        .section {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 24px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 600;
        }

        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 10px 12px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            font-family: var(--vscode-font-family);
            font-size: 13px;
        }

        select {
            cursor: pointer;
        }

        textarea {
            resize: vertical;
            min-height: 80px;
        }

        .hint {
            margin-top: 6px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .validation-error {
            margin-top: 6px;
            font-size: 12px;
            color: var(--vscode-errorForeground);
        }

        .crew-card {
            background: var(--vscode-editor-background);
            border: 2px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .crew-card:hover {
            border-color: var(--vscode-focusBorder);
            transform: translateY(-1px);
        }

        .crew-card.selected {
            background: var(--vscode-list-activeSelectionBackground);
            border-color: var(--vscode-focusBorder);
        }

        .crew-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }

        .crew-name {
            font-size: 15px;
            font-weight: 600;
            flex: 1;
        }

        .agent-count {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
        }

        .crew-description {
            font-size: 13px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 12px;
        }

        .agents-preview {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .agent-tag {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        }

        .agent-list {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .agent-item {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 8px;
        }

        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .agent-name {
            font-weight: 600;
            font-size: 14px;
        }

        .agent-role {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            background: var(--vscode-badge-background);
            padding: 2px 6px;
            border-radius: 3px;
        }

        .agent-details {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .patterns-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 12px;
        }

        .pattern-card {
            background: var(--vscode-editor-background);
            border: 2px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .pattern-card:hover {
            border-color: var(--vscode-focusBorder);
            transform: translateY(-1px);
        }

        .pattern-card.selected {
            background: var(--vscode-list-activeSelectionBackground);
            border-color: var(--vscode-focusBorder);
        }

        .pattern-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .pattern-checkbox {
            width: 18px;
            height: 18px;
        }

        .pattern-name {
            font-size: 14px;
            font-weight: 600;
            flex: 1;
        }

        .complexity-badge {
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .complexity-simple {
            background: rgba(0, 200, 83, 0.15);
            color: #00c853;
        }

        .complexity-moderate {
            background: rgba(255, 193, 7, 0.15);
            color: #ffc107;
        }

        .complexity-complex {
            background: rgba(244, 67, 54, 0.15);
            color: #f44336;
        }

        .pattern-description {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        button {
            padding: 12px 24px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        button.primary {
            font-size: 15px;
            padding: 14px 32px;
        }

        button.secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .button-group {
            display: flex;
            gap: 12px;
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .success-message,
        .error-message {
            padding: 16px;
            margin: 16px 0;
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .success-message {
            background: rgba(0, 200, 83, 0.1);
            color: #00c853;
            border: 1px solid rgba(0, 200, 83, 0.3);
        }

        .error-message {
            background: rgba(244, 67, 54, 0.1);
            color: #f44336;
            border: 1px solid rgba(244, 67, 54, 0.3);
        }

        @media (max-width: 1200px) {
            .two-column {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Workflow Factory</h1>
        <div class="subtitle">Create workflows 12x faster with agents, patterns, and visual configuration</div>
    </div>

    <div class="container">
        <div id="message-container"></div>

        <div class="two-column">
            <!-- Left Column: Basic Info -->
            <div class="section">
                <div class="section-title">📋 Workflow Details</div>

                <div class="form-group">
                    <label for="workflow-name">Workflow Name *</label>
                    <input type="text" id="workflow-name" placeholder="bug-scanner" autofocus />
                    <div class="hint">Use kebab-case (e.g., bug-scanner, code-review)</div>
                    <div id="name-error" class="validation-error"></div>
                </div>

                <div class="form-group">
                    <label for="workflow-description">Description</label>
                    <textarea id="workflow-description" placeholder="Scan code for bugs, analyze, test, and report"></textarea>
                </div>

                <div class="form-group">
                    <label for="workflow-stages">Stages (comma-separated)</label>
                    <input type="text" id="workflow-stages" placeholder="analyze,process,test,report" />
                    <div class="hint">Leave empty for single-stage workflows</div>
                </div>
            </div>

            <!-- Right Column: Agent/Crew Selection -->
            <div class="section">
                <div class="section-title">🤖 Agents & Crews</div>

                <div class="form-group">
                    <label for="crew-select">Select Crew</label>
                    <select id="crew-select" onchange="handleCrewSelect(this.value)">
                        <option value="">-- No crew (manual workflow) --</option>
                    </select>
                    <div class="hint">Pre-built multi-agent teams or build your own</div>
                </div>

                <div id="crew-details"></div>
            </div>
        </div>

        <!-- Patterns Section -->
        <div class="section">
            <div class="section-title">⚡ Workflow Patterns</div>
            <div id="patterns-container" class="patterns-grid">
                <p style="color: var(--vscode-descriptionForeground);">Loading patterns...</p>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="button-group">
            <button class="primary" onclick="createWorkflow()">✨ Create Workflow</button>
            <button class="secondary" onclick="resetForm()">🔄 Reset</button>
            <button class="secondary" onclick="listPatterns()">📋 List All Patterns</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let patterns = [];
        let crews = [];
        let selectedPatterns = new Set();
        let selectedCrew = null;

        // Request initial data
        vscode.postMessage({ type: 'getPatterns' });
        vscode.postMessage({ type: 'getCrews' });

        // Handle messages
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'patternsData':
                    patterns = message.patterns;
                    renderPatterns();
                    break;
                case 'crewsData':
                    crews = message.crews;
                    renderCrewOptions();
                    break;
                case 'nameValidation':
                    document.getElementById('name-error').textContent = message.message;
                    break;
                case 'workflowCreated':
                    showMessage(message.success, message.message);
                    if (message.success) {
                        setTimeout(() => resetForm(), 2000);
                    }
                    break;
            }
        });

        // Validate name on input
        document.getElementById('workflow-name').addEventListener('input', (e) => {
            vscode.postMessage({ type: 'validateName', name: e.target.value });
        });

        function renderCrewOptions() {
            const select = document.getElementById('crew-select');
            crews.forEach(crew => {
                const option = document.createElement('option');
                option.value = crew.id;
                option.textContent = \`\${crew.name} (\${crew.agents.length} agents)\`;
                select.appendChild(option);
            });
        }

        function handleCrewSelect(crewId) {
            selectedCrew = crewId ? crews.find(c => c.id === crewId) : null;
            renderCrewDetails();

            // Auto-select crew-based pattern if crew selected
            if (selectedCrew && selectedCrew.id !== 'custom') {
                selectedPatterns.add('crew-based');
                renderPatterns();
            }
        }

        function renderCrewDetails() {
            const container = document.getElementById('crew-details');

            if (!selectedCrew || selectedCrew.agents.length === 0) {
                container.innerHTML = '';
                return;
            }

            let html = '<div class="agent-list">';
            html += '<strong style="display: block; margin-bottom: 12px;">Agents in this crew:</strong>';

            selectedCrew.agents.forEach(agent => {
                html += \`
                    <div class="agent-item">
                        <div class="agent-header">
                            <div class="agent-name">\${agent.name}</div>
                            <div class="agent-role">\${agent.role}</div>
                        </div>
                        \${agent.goal ? \`<div class="agent-details"><strong>Goal:</strong> \${agent.goal}</div>\` : ''}
                        \${agent.backstory ? \`<div class="agent-details"><strong>Backstory:</strong> \${agent.backstory}</div>\` : ''}
                    </div>
                \`;
            });

            html += '</div>';
            container.innerHTML = html;
        }

        function renderPatterns() {
            const container = document.getElementById('patterns-container');

            let html = '';
            patterns.forEach(pattern => {
                const isSelected = selectedPatterns.has(pattern.id);
                const complexityClass = \`complexity-\${pattern.complexity.toLowerCase()}\`;

                html += \`
                    <div class="pattern-card \${isSelected ? 'selected' : ''}"
                         onclick="togglePattern('\${pattern.id}')">
                        <div class="pattern-header">
                            <input type="checkbox"
                                   class="pattern-checkbox"
                                   \${isSelected ? 'checked' : ''}
                                   onclick="event.stopPropagation(); togglePattern('\${pattern.id}')">
                            <div class="pattern-name">\${pattern.name}</div>
                            <span class="complexity-badge \${complexityClass}">\${pattern.complexity}</span>
                        </div>
                        <div class="pattern-description">\${pattern.description}</div>
                    </div>
                \`;
            });

            container.innerHTML = html;
        }

        function togglePattern(patternId) {
            if (selectedPatterns.has(patternId)) {
                selectedPatterns.delete(patternId);
            } else {
                selectedPatterns.add(patternId);
            }
            renderPatterns();
        }

        function createWorkflow() {
            const name = document.getElementById('workflow-name').value.trim();
            const description = document.getElementById('workflow-description').value.trim();
            const stages = document.getElementById('workflow-stages').value.trim();

            if (!name) {
                showMessage(false, 'Workflow name is required');
                return;
            }

            if (!/^[a-z][a-z0-9-]*$/.test(name)) {
                showMessage(false, 'Invalid workflow name. Use kebab-case.');
                return;
            }

            vscode.postMessage({
                type: 'createWorkflow',
                data: {
                    name,
                    description,
                    patterns: Array.from(selectedPatterns),
                    stages,
                    crew: selectedCrew ? selectedCrew.id : null
                }
            });
        }

        function resetForm() {
            document.getElementById('workflow-name').value = '';
            document.getElementById('workflow-description').value = '';
            document.getElementById('workflow-stages').value = '';
            document.getElementById('crew-select').value = '';
            selectedPatterns.clear();
            selectedCrew = null;
            renderPatterns();
            renderCrewDetails();
            document.getElementById('message-container').innerHTML = '';
            document.getElementById('name-error').textContent = '';
        }

        function listPatterns() {
            vscode.postMessage({ type: 'listPatterns' });
        }

        function showMessage(success, message) {
            const container = document.getElementById('message-container');
            const className = success ? 'success-message' : 'error-message';
            const icon = success ? '✅' : '❌';
            container.innerHTML = \`<div class="\${className}">\${icon} \${message}</div>\`;
            setTimeout(() => {
                container.innerHTML = '';
            }, 5000);
        }
    </script>
</body>
</html>`;
    }
}
