/**
 * Empathy Dashboard Panel - Activity Bar Webview
 *
 * Replaces tree views with a rich webview dashboard featuring:
 * - Tabbed interface (Patterns, Health, Costs, Workflows)
 * - Interactive charts using Chart.js
 * - Real-time updates via file watchers
 * - One-click actions for common tasks
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';

export class EmpathyDashboardProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'empathy-dashboard';

    private _view?: vscode.WebviewView;
    private _extensionUri: vscode.Uri;
    private _fileWatcher?: vscode.FileSystemWatcher;

    constructor(extensionUri: vscode.Uri) {
        this._extensionUri = extensionUri;
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
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'runCommand':
                    try {
                        const cmdName = `empathy.${message.command}`;
                        // Check if command exists before executing
                        const allCommands = await vscode.commands.getCommands(true);
                        if (allCommands.includes(cmdName)) {
                            await vscode.commands.executeCommand(cmdName);
                        } else {
                            vscode.window.showWarningMessage(`Command not found: ${cmdName}`);
                        }
                    } catch (err) {
                        vscode.window.showErrorMessage(`Command failed: ${err}`);
                    }
                    break;
                case 'refresh':
                    await this._updateData();
                    break;
                case 'openFile':
                    await this._openFile(message.filePath, message.line);
                    break;
                case 'fixIssue':
                    await this._fixIssue(message.issueType);
                    break;
                case 'runWorkflow':
                    try {
                        await this._runWorkflow(message.workflow, message.input);
                    } catch (err) {
                        vscode.window.showErrorMessage(`Workflow failed: ${err}`);
                    }
                    break;
                case 'getCosts':
                    this._sendCostsData();
                    break;
                case 'showFilePicker':
                    await this._showFilePicker(message.workflow);
                    break;
                case 'showFolderPicker':
                    await this._showFolderPicker(message.workflow);
                    break;
                case 'showDropdown':
                    await this._showDropdown(message.workflow, message.options);
                    break;
                case 'getActiveFile':
                    this._sendActiveFile(message.workflow);
                    break;
            }
        });

        // Set up file watcher for data files
        this._setupFileWatcher();

        // Initial data load
        this._updateData();
    }

    private _setupFileWatcher() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        // Watch for changes to empathy data files
        this._fileWatcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(workspaceFolder, '**/.empathy/*.json')
        );

        const debouncedUpdate = this._debounce(() => this._updateData(), 1000);

        this._fileWatcher.onDidChange(debouncedUpdate);
        this._fileWatcher.onDidCreate(debouncedUpdate);
        this._fileWatcher.onDidDelete(debouncedUpdate);
    }

    private _debounce(fn: () => void, delay: number) {
        let timeout: NodeJS.Timeout;
        return () => {
            clearTimeout(timeout);
            timeout = setTimeout(fn, delay);
        };
    }

    public refresh() {
        this._updateData();
    }

    private async _updateData() {
        if (!this._view) {
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const patternsDir = path.join(workspaceFolder, config.get<string>('patternsDir', './patterns'));
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

        const data = {
            patterns: this._loadPatterns(patternsDir),
            health: this._loadHealth(empathyDir, patternsDir),
            costs: this._loadCosts(empathyDir),
            workflows: this._loadWorkflows(empathyDir),
        };

        this._view.webview.postMessage({ type: 'update', data });
    }

    private _loadPatterns(patternsDir: string): PatternData[] {
        const patterns: PatternData[] = [];

        try {
            const debuggingFile = path.join(patternsDir, 'debugging.json');
            if (fs.existsSync(debuggingFile)) {
                const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
                for (const p of (data.patterns || []).slice(-20)) {
                    patterns.push({
                        id: p.pattern_id || 'unknown',
                        type: p.bug_type || 'unknown',
                        status: p.status || 'investigating',
                        rootCause: p.root_cause || '',
                        fix: p.fix || '',
                        files: p.files_affected || [],
                        timestamp: p.timestamp || '',
                    });
                }
            }
        } catch { /* ignore */ }

        return patterns.reverse();
    }

    private _loadHealth(empathyDir: string, patternsDir: string): HealthData {
        const health: HealthData = {
            score: 0,
            patterns: 0,
            lint: { errors: 0, warnings: 0 },
            types: { errors: 0 },
            security: { high: 0, medium: 0, low: 0 },
            tests: { passed: 0, failed: 0, total: 0, coverage: 0 },
            techDebt: { total: 0, todos: 0, fixmes: 0, hacks: 0 },
            lastUpdated: null,
        };

        try {
            const debuggingFile = path.join(patternsDir, 'debugging.json');
            if (fs.existsSync(debuggingFile)) {
                const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
                health.patterns = data.patterns?.length || 0;
            }
        } catch { /* ignore */ }

        try {
            const healthFile = path.join(empathyDir, 'health.json');
            if (fs.existsSync(healthFile)) {
                const data = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
                health.score = data.score || 0;
                health.lint = data.lint || health.lint;
                health.types = data.types || health.types;
                health.security = data.security || health.security;
                health.tests = data.tests || health.tests;
                health.techDebt = data.tech_debt || health.techDebt;
                health.lastUpdated = data.timestamp || null;
            }
        } catch { /* ignore */ }

        try {
            const debtFile = path.join(patternsDir, 'tech_debt.json');
            if (fs.existsSync(debtFile)) {
                const data = JSON.parse(fs.readFileSync(debtFile, 'utf8'));
                if (data.snapshots && data.snapshots.length > 0) {
                    const latest = data.snapshots[data.snapshots.length - 1];
                    health.techDebt.total = latest.total_items || 0;
                    if (latest.by_type) {
                        health.techDebt.todos = latest.by_type.todo || 0;
                        health.techDebt.fixmes = latest.by_type.fixme || 0;
                        health.techDebt.hacks = latest.by_type.hack || 0;
                    }
                }
            }
        } catch { /* ignore */ }

        // Calculate score if not set
        if (health.score === 0 && health.patterns > 0) {
            let score = 100;
            score -= health.lint.errors * 2;
            score -= health.types.errors * 3;
            score -= health.security.high * 10;
            score -= health.tests.failed * 5;
            health.score = Math.max(0, Math.min(100, Math.round(score)));
        }

        return health;
    }

    private _loadCosts(empathyDir: string): CostData {
        const costs: CostData = {
            totalCost: 0,
            totalSavings: 0,
            requests: 0,
            dailyCosts: [],
            byProvider: {},
        };

        try {
            const costsFile = path.join(empathyDir, 'costs.json');
            if (fs.existsSync(costsFile)) {
                const data = JSON.parse(fs.readFileSync(costsFile, 'utf8'));

                for (const [dateStr, daily] of Object.entries(data.daily_totals || {})) {
                    const d = daily as any;
                    costs.totalCost += d.actual_cost || 0;
                    costs.totalSavings += d.savings || 0;
                    costs.requests += d.requests || 0;

                    costs.dailyCosts.push({
                        date: dateStr,
                        cost: d.actual_cost || 0,
                        savings: d.savings || 0,
                    });
                }

                // By provider
                for (const [provider, providerData] of Object.entries(data.by_provider || {})) {
                    costs.byProvider[provider] = {
                        requests: (providerData as any).requests || 0,
                        cost: (providerData as any).actual_cost || 0,
                    };
                }

                // Sort daily costs by date
                costs.dailyCosts.sort((a, b) => a.date.localeCompare(b.date));
            }
        } catch { /* ignore */ }

        return costs;
    }

    private _sendCostsData() {
        if (!this._view) {
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            this._view.webview.postMessage({
                type: 'costsData',
                data: { requests: [], totalSavings: 0, totalCost: 0, savingsPercent: 0 }
            });
            return;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

        try {
            const costsFile = path.join(empathyDir, 'costs.json');
            if (!fs.existsSync(costsFile)) {
                this._view.webview.postMessage({
                    type: 'costsData',
                    data: { requests: [], totalSavings: 0, totalCost: 0, savingsPercent: 0 }
                });
                return;
            }

            const data = JSON.parse(fs.readFileSync(costsFile, 'utf8'));

            // Get last 10 requests
            const requests = (data.requests || []).slice(-10).reverse();

            // Calculate 7-day totals
            let totalSavings = 0;
            let totalCost = 0;
            let baselineCost = 0;

            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - 7);
            const cutoffStr = cutoff.toISOString().split('T')[0];

            for (const [dateStr, daily] of Object.entries(data.daily_totals || {})) {
                if (dateStr >= cutoffStr) {
                    const d = daily as any;
                    totalCost += d.actual_cost || 0;
                    totalSavings += d.savings || 0;
                    baselineCost += d.baseline_cost || 0;
                }
            }

            const savingsPercent = baselineCost > 0 ? Math.round((totalSavings / baselineCost) * 100) : 0;

            this._view.webview.postMessage({
                type: 'costsData',
                data: {
                    requests,
                    totalSavings,
                    totalCost,
                    savingsPercent
                }
            });
        } catch {
            this._view.webview.postMessage({
                type: 'costsData',
                data: { requests: [], totalSavings: 0, totalCost: 0, savingsPercent: 0 }
            });
        }
    }

    private _loadWorkflows(empathyDir: string): WorkflowData {
        const workflows: WorkflowData = {
            totalRuns: 0,
            successfulRuns: 0,
            totalCost: 0,
            totalSavings: 0,
            recentRuns: [],
            byWorkflow: {},
        };

        try {
            const runsFile = path.join(empathyDir, 'workflow_runs.json');
            if (fs.existsSync(runsFile)) {
                const runs = JSON.parse(fs.readFileSync(runsFile, 'utf8')) as any[];

                workflows.totalRuns = runs.length;
                workflows.successfulRuns = runs.filter(r => r.success).length;

                for (const run of runs) {
                    workflows.totalCost += run.cost || 0;
                    workflows.totalSavings += run.savings || 0;

                    const wfName = run.workflow || 'unknown';
                    if (!workflows.byWorkflow[wfName]) {
                        workflows.byWorkflow[wfName] = { runs: 0, cost: 0, savings: 0 };
                    }
                    workflows.byWorkflow[wfName].runs++;
                    workflows.byWorkflow[wfName].cost += run.cost || 0;
                    workflows.byWorkflow[wfName].savings += run.savings || 0;
                }

                workflows.recentRuns = runs.slice(-10).reverse().map(r => ({
                    workflow: r.workflow || 'unknown',
                    success: r.success || false,
                    cost: r.cost || 0,
                    savings: r.savings || 0,
                    timestamp: r.started_at || '',
                }));
            }
        } catch { /* ignore */ }

        return workflows;
    }

    private async _openFile(filePath: string, line?: number) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder || !filePath) {
            return;
        }

        const fullPath = path.isAbsolute(filePath) ? filePath : path.join(workspaceFolder, filePath);

        try {
            const doc = await vscode.workspace.openTextDocument(fullPath);
            const editor = await vscode.window.showTextDocument(doc);
            if (line && line > 0) {
                const position = new vscode.Position(line - 1, 0);
                editor.selection = new vscode.Selection(position, position);
                editor.revealRange(new vscode.Range(position, position));
            }
        } catch {
            vscode.window.showErrorMessage(`Could not open file: ${filePath}`);
        }
    }

    private async _fixIssue(issueType: string) {
        switch (issueType) {
            case 'lint':
                vscode.commands.executeCommand('empathy.fixLint');
                break;
            case 'format':
                vscode.commands.executeCommand('empathy.fixFormat');
                break;
            case 'all':
                vscode.commands.executeCommand('empathy.fixAll');
                break;
        }
    }

    private async _runWorkflow(workflowName: string, input?: string) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        // Send "running" state to webview
        this._view?.webview.postMessage({
            type: 'workflowStatus',
            data: { workflow: workflowName, status: 'running', output: '' }
        });

        // Execute workflow and capture output - pass input as JSON with workflow-specific key
        const inputKeys: Record<string, string> = {
            'research': 'question',
            'code-review': 'target',
            'doc-gen': 'target',
            'bug-predict': 'target',
            'security-audit': 'target',
            'perf-audit': 'target',
            'test-gen': 'target',
            'refactor-plan': 'target',
            'dependency-check': 'scope',
            'release-prep': 'version'
        };
        const inputKey = inputKeys[workflowName] || 'query';
        const inputJson = input ? JSON.stringify({ [inputKey]: input }) : '';
        const escapedJson = inputJson.replace(/'/g, "'\\''"); // Escape single quotes for shell
        const command = `python -m empathy_os.cli workflow run ${workflowName}${input ? ` --input '${escapedJson}'` : ''}`;

        cp.exec(command, { cwd: workspaceFolder, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
            const output = stdout || stderr || (error ? error.message : 'No output');
            const success = !error;

            this._view?.webview.postMessage({
                type: 'workflowStatus',
                data: {
                    workflow: workflowName,
                    status: success ? 'complete' : 'error',
                    output: output,
                    error: error ? error.message : null
                }
            });
        });
    }

    private async _showFilePicker(workflow: string) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri;

        const result = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            defaultUri: workspaceFolder,
            title: `Select file for ${workflow}`,
            openLabel: 'Select'
        });

        if (result && result[0]) {
            const relativePath = vscode.workspace.asRelativePath(result[0]);
            this._view?.webview.postMessage({
                type: 'pickerResult',
                data: { workflow, path: relativePath, cancelled: false }
            });
        } else {
            this._view?.webview.postMessage({
                type: 'pickerResult',
                data: { workflow, path: '', cancelled: true }
            });
        }
    }

    private async _showFolderPicker(workflow: string) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri;

        const result = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            defaultUri: workspaceFolder,
            title: `Select folder for ${workflow}`,
            openLabel: 'Select Folder'
        });

        if (result && result[0]) {
            const relativePath = vscode.workspace.asRelativePath(result[0]);
            this._view?.webview.postMessage({
                type: 'pickerResult',
                data: { workflow, path: relativePath, cancelled: false }
            });
        } else {
            this._view?.webview.postMessage({
                type: 'pickerResult',
                data: { workflow, path: '', cancelled: true }
            });
        }
    }

    private async _showDropdown(workflow: string, options: string[]) {
        const result = await vscode.window.showQuickPick(options, {
            placeHolder: `Select option for ${workflow}`,
            title: workflow
        });

        this._view?.webview.postMessage({
            type: 'pickerResult',
            data: { workflow, path: result || '', cancelled: !result }
        });
    }

    private _sendActiveFile(workflow: string) {
        const activeEditor = vscode.window.activeTextEditor;
        let activePath = '';

        if (activeEditor) {
            activePath = vscode.workspace.asRelativePath(activeEditor.document.uri);
        }

        this._view?.webview.postMessage({
            type: 'activeFile',
            data: { workflow, path: activePath }
        });
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Empathy Dashboard</title>
    <style>
        :root {
            --bg: var(--vscode-sideBar-background);
            --fg: var(--vscode-sideBar-foreground);
            --border: var(--vscode-panel-border);
            --button-bg: var(--vscode-button-background);
            --button-fg: var(--vscode-button-foreground);
            --tab-active: var(--vscode-tab-activeBackground);
            --tab-inactive: var(--vscode-tab-inactiveBackground);
            --success: var(--vscode-testing-iconPassed);
            --error: var(--vscode-testing-iconFailed);
            --warning: var(--vscode-editorWarning-foreground);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: var(--vscode-font-family);
            font-size: 12px;
            color: var(--fg);
            background: var(--bg);
            height: 100vh;
            overflow: hidden;
        }

        /* Tab Bar */
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border);
            background: var(--tab-inactive);
        }

        .tab {
            padding: 8px 12px;
            cursor: pointer;
            border: none;
            background: transparent;
            color: var(--fg);
            opacity: 0.7;
            font-size: 11px;
            border-bottom: 2px solid transparent;
        }

        .tab:hover { opacity: 1; }

        .tab.active {
            opacity: 1;
            background: var(--tab-active);
            border-bottom-color: var(--button-bg);
        }

        /* Tab Content */
        .tab-content {
            display: none;
            padding: 12px;
            height: calc(100vh - 36px);
            overflow-y: auto;
        }

        .tab-content.active { display: block; }

        /* Cards */
        .card {
            background: var(--vscode-input-background);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
        }

        .card-title {
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Health Score Circle */
        .score-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px;
        }

        .score-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .score-circle.good { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .score-circle.warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .score-circle.bad { background: rgba(239, 68, 68, 0.2); color: var(--error); }

        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .metric {
            background: var(--vscode-input-background);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 8px;
            text-align: center;
        }

        .metric-value {
            font-size: 16px;
            font-weight: 600;
        }

        .metric-value.success { color: var(--success); }
        .metric-value.warning { color: var(--warning); }
        .metric-value.error { color: var(--error); }

        .metric-label {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 2px;
        }

        /* List Items */
        .list-item {
            display: flex;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid var(--border);
            gap: 8px;
        }

        .list-item:last-child { border-bottom: none; }

        .list-item-icon {
            width: 16px;
            text-align: center;
        }

        .list-item-content { flex: 1; min-width: 0; }
        .list-item-title { font-weight: 500; }
        .list-item-desc { font-size: 10px; opacity: 0.7; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

        /* Buttons */
        .btn {
            padding: 6px 12px;
            background: var(--button-bg);
            color: var(--button-fg);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }

        .btn:hover { opacity: 0.9; }

        .btn-row {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        /* Status Badge */
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 500;
        }

        .badge.success { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .badge.warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .badge.error { background: rgba(239, 68, 68, 0.2); color: var(--error); }
        .badge.info { background: rgba(99, 102, 241, 0.2); color: #6366f1; }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 20px;
            opacity: 0.5;
        }

        /* Progress Bars */
        .progress-bar {
            height: 6px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 4px;
        }

        .progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s;
        }

        .progress-fill.success { background: var(--success); }
        .progress-fill.warning { background: var(--warning); }
        .progress-fill.error { background: var(--error); }

        /* Action Buttons Grid */
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
        }

        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 10px 6px;
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: 1px solid var(--border);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.15s;
            font-size: 11px;
        }

        .action-btn:hover {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-color: var(--vscode-button-background);
        }

        .action-icon {
            font-size: 18px;
            margin-bottom: 4px;
        }

        /* Health Tree View */
        .health-tree {
            padding: 0 8px;
        }

        .tree-item {
            display: flex;
            align-items: center;
            padding: 6px 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.15s;
        }

        .tree-item:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .tree-icon {
            width: 20px;
            text-align: center;
            margin-right: 8px;
        }

        .tree-icon.ok { color: var(--success); }
        .tree-icon.warning { color: var(--warning); }
        .tree-icon.error { color: var(--error); }

        .tree-label {
            flex: 1;
            font-size: 12px;
        }

        .tree-value {
            font-size: 11px;
            opacity: 0.8;
            padding: 2px 6px;
            background: var(--vscode-input-background);
            border-radius: 3px;
        }

        /* Workflow Selector */
        .workflow-selector {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .workflow-dropdown {
            flex: 1;
            padding: 6px 8px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }

        .workflow-dropdown:focus {
            outline: 1px solid var(--vscode-focusBorder);
        }

        .workflow-run-btn {
            padding: 6px 12px;
            white-space: nowrap;
        }

        /* Workflow grid - 2 columns for longer labels */
        .workflow-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .workflow-btn {
            flex-direction: row;
            justify-content: flex-start;
            gap: 8px;
            padding: 8px 10px;
        }

        .workflow-btn .action-icon {
            margin-bottom: 0;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="tabs">
        <button class="tab active" data-tab="power">Power</button>
        <button class="tab" data-tab="health">Health</button>
        <button class="tab" data-tab="workflows">Workflows</button>
    </div>

    <!-- Power Tab -->
    <div id="tab-power" class="tab-content active">
        <div class="card">
            <div class="card-title">Quick Actions</div>
            <div class="actions-grid workflow-grid">
                <button class="action-btn workflow-btn" data-cmd="morning" data-title="Morning Briefing">
                    <span class="action-icon">&#x2600;</span>
                    <span>Get Briefing</span>
                </button>
                <button class="action-btn workflow-btn" data-cmd="ship" data-title="Pre-Ship Check">
                    <span class="action-icon">&#x1F680;</span>
                    <span>Run Ship</span>
                </button>
                <button class="action-btn workflow-btn" data-cmd="fix-all" data-title="Fix All Issues">
                    <span class="action-icon">&#x1F527;</span>
                    <span>Fix Issues</span>
                </button>
                <button class="action-btn workflow-btn" data-cmd="learn" data-title="Learn Patterns">
                    <span class="action-icon">&#x1F4DA;</span>
                    <span>Learn Patterns</span>
                </button>
                <button class="action-btn workflow-btn" data-cmd="health" data-title="Health Check">
                    <span class="action-icon">&#x2764;</span>
                    <span>Check Health</span>
                </button>
                <button class="action-btn workflow-btn" id="view-costs-btn" data-title="View Costs">
                    <span class="action-icon">&#x1F4B0;</span>
                    <span>View Costs</span>
                </button>
            </div>
        </div>

        <div class="card" style="margin-top: 12px">
            <div class="card-title">Quick Stats</div>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value" id="power-patterns">--</div>
                    <div class="metric-label">Patterns</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="power-health">--</div>
                    <div class="metric-label">Health</div>
                </div>
                <div class="metric">
                    <div class="metric-value success" id="power-savings">--</div>
                    <div class="metric-label">Savings</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="power-requests">--</div>
                    <div class="metric-label">Requests</div>
                </div>
            </div>
        </div>

        <!-- Cost Details Panel (hidden by default) -->
        <div id="costs-panel" class="card" style="margin-top: 12px; display: none;">
            <div class="card-title" style="display: flex; justify-content: space-between; align-items: center;">
                <span>&#x1F4B0; Cost Details (7 days)</span>
                <button id="close-costs" style="background: none; border: none; cursor: pointer; font-size: 14px; opacity: 0.7;">&#x2715;</button>
            </div>
            <div id="costs-summary" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; text-align: center;">
                <div>
                    <div style="font-size: 18px; font-weight: bold; color: var(--vscode-charts-green);" id="costs-saved">$0.00</div>
                    <div style="font-size: 10px; opacity: 0.7;">Saved</div>
                </div>
                <div>
                    <div style="font-size: 18px; font-weight: bold;" id="costs-percent">0%</div>
                    <div style="font-size: 10px; opacity: 0.7;">Reduction</div>
                </div>
                <div>
                    <div style="font-size: 18px; font-weight: bold;" id="costs-total">$0.00</div>
                    <div style="font-size: 10px; opacity: 0.7;">Actual</div>
                </div>
            </div>
            <div style="font-size: 11px; font-weight: bold; margin-bottom: 6px; opacity: 0.8;">Recent Requests</div>
            <div id="costs-list" style="max-height: 200px; overflow-y: auto;">
                <div style="text-align: center; padding: 20px; opacity: 0.5;">Loading...</div>
            </div>
        </div>

        <div class="card" style="margin-top: 12px">
            <div class="card-title">Workflows <span style="font-size: 9px; color: #a855f7; font-weight: normal; opacity: 0.9;">(New Beta Feature)</span></div>
            <div class="actions-grid workflow-grid">
                <button class="action-btn workflow-btn" data-workflow="research">
                    <span class="action-icon">&#x1F50D;</span>
                    <span>Research Topic</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="code-review">
                    <span class="action-icon">&#x1F4DD;</span>
                    <span>Review Code</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="doc-gen">
                    <span class="action-icon">&#x1F4DA;</span>
                    <span>Generate Docs</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="bug-predict">
                    <span class="action-icon">&#x1F41B;</span>
                    <span>Predict Bugs</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="security-audit">
                    <span class="action-icon">&#x1F512;</span>
                    <span>Security Audit</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="perf-audit">
                    <span class="action-icon">&#x26A1;</span>
                    <span>Perf Audit</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="test-gen">
                    <span class="action-icon">&#x1F9EA;</span>
                    <span>Generate Tests</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="refactor-plan">
                    <span class="action-icon">&#x1F3D7;</span>
                    <span>Refactor Plan</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="dependency-check">
                    <span class="action-icon">&#x1F4E6;</span>
                    <span>Check Deps</span>
                </button>
                <button class="action-btn workflow-btn" data-workflow="release-prep">
                    <span class="action-icon">&#x1F3C1;</span>
                    <span>Release Prep</span>
                </button>
            </div>
        </div>

        <!-- Workflow Results Panel (hidden by default) -->
        <div id="workflow-results" class="card" style="margin-top: 12px; display: none;">
            <div class="card-title" style="display: flex; justify-content: space-between; align-items: center;">
                <span id="workflow-results-title">&#x2699; Workflow Results</span>
                <button id="close-workflow-results" style="background: none; border: none; cursor: pointer; font-size: 14px; opacity: 0.7;">&#x2715;</button>
            </div>
            <!-- Input Section -->
            <div id="workflow-input-section" style="margin-bottom: 10px;">
                <div id="workflow-input-label" style="font-size: 11px; margin-bottom: 4px; opacity: 0.8;">Enter your query:</div>
                <div id="workflow-text-input" style="display: block;">
                    <textarea id="workflow-input" placeholder="e.g., What are the best practices for error handling?" style="width: 100%; height: 60px; padding: 8px; font-size: 11px; font-family: var(--vscode-font-family); background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--border); border-radius: 4px; resize: vertical;"></textarea>
                </div>
                <div id="workflow-file-input" style="display: none;">
                    <div style="display: flex; gap: 6px;">
                        <input id="workflow-path" type="text" placeholder="Click Browse..." readonly style="flex: 1; padding: 8px; font-size: 11px; font-family: var(--vscode-font-family); background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--border); border-radius: 4px;">
                        <button id="workflow-browse-btn" class="btn" style="white-space: nowrap;">&#x1F4C2; Browse</button>
                    </div>
                </div>
                <div id="workflow-dropdown-input" style="display: none; text-align: center; padding: 10px;">
                    <button id="workflow-select-btn" class="btn" style="width: 100%;">&#x25BC; Select Option</button>
                </div>
                <button id="workflow-run-btn" class="btn" style="margin-top: 8px; width: 100%;">&#x25B6; Run Workflow</button>
            </div>
            <div id="workflow-results-status" style="margin-bottom: 8px; padding: 6px 10px; border-radius: 4px; font-size: 11px; display: none;">
                Running...
            </div>
            <div id="workflow-results-content" style="max-height: 300px; overflow-y: auto; font-family: var(--vscode-editor-font-family); font-size: 11px; line-height: 1.5; white-space: pre-wrap; background: var(--vscode-editor-background); padding: 10px; border-radius: 4px; border: 1px solid var(--border); display: none;">
            </div>
        </div>

        <div style="margin-top: 12px; text-align: center;">
            <button class="btn" data-cmd="dashboard" style="opacity: 0.7; font-size: 10px;">Open Web Dashboard</button>
        </div>
    </div>

    <!-- Health Tab - Tree View Style -->
    <div id="tab-health" class="tab-content">
        <div class="score-container" style="padding: 12px;">
            <div class="score-circle good" id="health-score">--</div>
            <div style="opacity: 0.7; font-size: 11px;">Health Score</div>
        </div>

        <div class="health-tree">
            <div class="tree-item" data-cmd="learn">
                <span class="tree-icon" id="patterns-icon">&#x2714;</span>
                <span class="tree-label">Patterns Learned</span>
                <span class="tree-value" id="metric-patterns">--</span>
            </div>
            <div class="tree-item" data-cmd="fixLint">
                <span class="tree-icon" id="lint-icon">&#x2714;</span>
                <span class="tree-label">Lint</span>
                <span class="tree-value" id="metric-lint">--</span>
            </div>
            <div class="tree-item" data-cmd="fixAll">
                <span class="tree-icon" id="types-icon">&#x2714;</span>
                <span class="tree-label">Types</span>
                <span class="tree-value" id="metric-types">--</span>
            </div>
            <div class="tree-item">
                <span class="tree-icon" id="security-icon">&#x2714;</span>
                <span class="tree-label">Security</span>
                <span class="tree-value" id="metric-security">0 high</span>
            </div>
            <div class="tree-item" data-cmd="runTests">
                <span class="tree-icon" id="tests-icon">&#x2714;</span>
                <span class="tree-label">Tests</span>
                <span class="tree-value" id="metric-tests">--</span>
            </div>
            <div class="tree-item">
                <span class="tree-icon">&#x1F4DD;</span>
                <span class="tree-label">Tech Debt</span>
                <span class="tree-value" id="metric-debt">--</span>
            </div>
        </div>

        <div class="card" style="margin-top: 10px;">
            <div class="card-title">Coverage</div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div class="progress-bar" style="flex: 1">
                    <div class="progress-fill success" id="coverage-bar" style="width: 0%"></div>
                </div>
                <span id="coverage-value">--%</span>
            </div>
        </div>

        <div class="btn-row">
            <button class="btn" data-cmd="runScan">Scan</button>
            <button class="btn" data-cmd="fixAll">Fix All</button>
        </div>
    </div>

    <!-- Workflows Tab -->
    <div id="tab-workflows" class="tab-content">
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-value" id="wf-runs">0</div>
                <div class="metric-label">Total Runs</div>
            </div>
            <div class="metric">
                <div class="metric-value success" id="wf-success">0%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="wf-cost">$0.00</div>
                <div class="metric-label">Total Cost</div>
            </div>
            <div class="metric">
                <div class="metric-value success" id="wf-savings">$0.00</div>
                <div class="metric-label">Savings</div>
            </div>
        </div>

        <div class="card" style="margin-top: 12px">
            <div class="card-title">Recent Runs</div>
            <div id="workflows-list">
                <div class="empty-state">No workflow runs yet</div>
            </div>
        </div>

        <div class="btn-row">
            <button class="btn" data-cmd="workflow">List Workflows</button>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
            });
        });

        // Track running actions to prevent duplicate clicks
        const runningActions = new Set();

        // Button click handlers - use event delegation for CSP compliance
        document.querySelectorAll('button[data-cmd]').forEach(btn => {
            btn.addEventListener('click', function() {
                const cmd = this.dataset.cmd;

                // Prevent duplicate action
                if (runningActions.has(cmd)) {
                    return;
                }
                runningActions.add(cmd);

                // Store original content and show running state
                const iconSpan = this.querySelector('.action-icon');
                const textSpan = this.querySelector('span:not(.action-icon)');
                const originalIcon = iconSpan ? iconSpan.innerHTML : '';
                const originalText = textSpan ? textSpan.textContent : this.textContent;

                this.disabled = true;
                this.style.opacity = '0.7';
                if (iconSpan) iconSpan.innerHTML = '&#x23F3;'; // Hourglass
                if (textSpan) textSpan.textContent = 'Running...';
                else this.textContent = 'Running...';

                vscode.postMessage({ type: 'runCommand', command: cmd });

                // Restore after timeout (command execution happens in terminal)
                setTimeout(() => {
                    this.disabled = false;
                    this.style.opacity = '1';
                    if (iconSpan) iconSpan.innerHTML = originalIcon;
                    if (textSpan) textSpan.textContent = originalText;
                    runningActions.delete(cmd);
                }, 3000);
            });
        });

        // Tree item click handlers
        document.querySelectorAll('.tree-item[data-cmd]').forEach(item => {
            item.addEventListener('click', function() {
                const cmd = this.dataset.cmd;
                if (runningActions.has('tree-' + cmd)) return;
                runningActions.add('tree-' + cmd);

                this.style.opacity = '0.5';
                vscode.postMessage({ type: 'runCommand', command: cmd });

                setTimeout(() => {
                    this.style.opacity = '1';
                    runningActions.delete('tree-' + cmd);
                }, 3000);
            });
        });

        // Store original button content for restoration
        const workflowButtonState = new Map();
        let currentWorkflow = null;

        // Workflow input configuration - defines input type and UI for each workflow
        const workflowConfig = {
            'research': {
                type: 'text',
                label: 'What would you like to research?',
                placeholder: 'e.g., Best practices for error handling in Python'
            },
            'code-review': {
                type: 'file',
                label: 'Select file to review',
                placeholder: 'Click Browse or type path...',
                allowText: true  // hybrid - allows manual path entry too
            },
            'doc-gen': {
                type: 'file',
                label: 'Select file/module to document',
                placeholder: 'Click Browse or describe what to document...',
                allowText: true
            },
            'bug-predict': {
                type: 'folder',
                label: 'Select folder to analyze for bugs',
                placeholder: 'Click Browse to select folder...'
            },
            'security-audit': {
                type: 'folder',
                label: 'Select folder to audit',
                placeholder: 'Click Browse to select folder...'
            },
            'perf-audit': {
                type: 'folder',
                label: 'Select folder to profile',
                placeholder: 'Click Browse to select folder...'
            },
            'test-gen': {
                type: 'file',
                label: 'Select file to generate tests for',
                placeholder: 'Click Browse to select file...'
            },
            'refactor-plan': {
                type: 'folder',
                label: 'Select folder to plan refactoring',
                placeholder: 'Click Browse to select folder...'
            },
            'dependency-check': {
                type: 'dropdown',
                label: 'Select dependency check scope',
                options: ['All dependencies', 'Security-critical only', 'Outdated only', 'Direct dependencies only']
            },
            'release-prep': {
                type: 'text',
                label: 'Enter release version',
                placeholder: 'e.g., v2.3.0'
            }
        };

        // Helper to show the appropriate input type
        function showInputType(type, config) {
            const textInput = document.getElementById('workflow-text-input');
            const fileInput = document.getElementById('workflow-file-input');
            const dropdownInput = document.getElementById('workflow-dropdown-input');
            const pathField = document.getElementById('workflow-path');
            const textField = document.getElementById('workflow-input');

            // Hide all first
            textInput.style.display = 'none';
            fileInput.style.display = 'none';
            dropdownInput.style.display = 'none';

            if (type === 'text') {
                textInput.style.display = 'block';
                textField.placeholder = config.placeholder || 'Enter your query...';
                textField.value = '';
                textField.focus();
            } else if (type === 'file' || type === 'folder') {
                fileInput.style.display = 'block';
                pathField.placeholder = config.placeholder || 'Click Browse...';
                pathField.value = '';
                // If hybrid (allowText), make editable
                pathField.readOnly = !config.allowText;
                // Request active file for pre-population
                vscode.postMessage({ type: 'getActiveFile', workflow: currentWorkflow });
            } else if (type === 'dropdown') {
                dropdownInput.style.display = 'block';
            }
        }

        // Workflow button click handlers - show input panel first
        document.querySelectorAll('.action-btn[data-workflow]').forEach(btn => {
            const workflow = btn.dataset.workflow;
            const iconSpan = btn.querySelector('.action-icon');
            const textSpan = btn.querySelector('span:not(.action-icon)');
            workflowButtonState.set(workflow, {
                icon: iconSpan ? iconSpan.innerHTML : '',
                text: textSpan ? textSpan.textContent : '',
                btn: btn
            });

            btn.addEventListener('click', function() {
                const wf = this.dataset.workflow;
                currentWorkflow = wf;

                // Show input panel
                const resultsPanel = document.getElementById('workflow-results');
                const resultsTitle = document.getElementById('workflow-results-title');
                const inputSection = document.getElementById('workflow-input-section');
                const inputLabel = document.getElementById('workflow-input-label');
                const resultsStatus = document.getElementById('workflow-results-status');
                const resultsContent = document.getElementById('workflow-results-content');

                const config = workflowConfig[wf] || { type: 'text', label: 'Enter your query:', placeholder: 'Describe what you need...' };

                resultsPanel.style.display = 'block';
                resultsTitle.innerHTML = '&#x2699; ' + wf;
                inputSection.style.display = 'block';
                inputLabel.textContent = config.label;
                resultsStatus.style.display = 'none';
                resultsContent.style.display = 'none';
                resultsContent.textContent = '';

                // Show correct input type
                showInputType(config.type, config);
            });
        });

        // Browse button click handler
        const browseBtn = document.getElementById('workflow-browse-btn');
        if (browseBtn) {
            browseBtn.addEventListener('click', function() {
                if (!currentWorkflow) return;
                const config = workflowConfig[currentWorkflow];
                if (config && config.type === 'folder') {
                    vscode.postMessage({ type: 'showFolderPicker', workflow: currentWorkflow });
                } else {
                    vscode.postMessage({ type: 'showFilePicker', workflow: currentWorkflow });
                }
            });
        }

        // Select option button click handler (for dropdown)
        const selectBtn = document.getElementById('workflow-select-btn');
        if (selectBtn) {
            selectBtn.addEventListener('click', function() {
                if (!currentWorkflow) return;
                const config = workflowConfig[currentWorkflow];
                if (config && config.options) {
                    vscode.postMessage({ type: 'showDropdown', workflow: currentWorkflow, options: config.options });
                }
            });
        }

        // Track selected dropdown value
        let selectedDropdownValue = '';

        // Run workflow button handler
        const workflowRunBtn = document.getElementById('workflow-run-btn');
        if (workflowRunBtn) {
            workflowRunBtn.addEventListener('click', function() {
                if (!currentWorkflow) return;

                const config = workflowConfig[currentWorkflow] || { type: 'text' };
                let inputValue = '';

                // Get input value from appropriate field
                if (config.type === 'text') {
                    const inputField = document.getElementById('workflow-input');
                    inputValue = inputField.value.trim();
                    if (!inputValue) {
                        inputField.style.borderColor = 'var(--vscode-inputValidation-errorBorder)';
                        inputField.focus();
                        return;
                    }
                    inputField.style.borderColor = 'var(--border)';
                } else if (config.type === 'file' || config.type === 'folder') {
                    const pathField = document.getElementById('workflow-path');
                    inputValue = pathField.value.trim();
                    if (!inputValue) {
                        pathField.style.borderColor = 'var(--vscode-inputValidation-errorBorder)';
                        return;
                    }
                    pathField.style.borderColor = 'var(--border)';
                } else if (config.type === 'dropdown') {
                    inputValue = selectedDropdownValue;
                    if (!inputValue) {
                        const selectBtn = document.getElementById('workflow-select-btn');
                        selectBtn.style.borderColor = 'var(--vscode-inputValidation-errorBorder)';
                        return;
                    }
                }

                // Prevent duplicate action
                if (runningActions.has('wf-' + currentWorkflow)) {
                    return;
                }
                runningActions.add('wf-' + currentWorkflow);

                // Update button state
                const state = workflowButtonState.get(currentWorkflow);
                if (state) {
                    state.btn.disabled = true;
                    state.btn.style.opacity = '0.7';
                    const icon = state.btn.querySelector('.action-icon');
                    const text = state.btn.querySelector('span:not(.action-icon)');
                    if (icon) icon.innerHTML = '&#x23F3;';
                    if (text) text.textContent = 'Running...';
                }

                // Show running state
                const inputSection = document.getElementById('workflow-input-section');
                const resultsStatus = document.getElementById('workflow-results-status');
                const resultsContent = document.getElementById('workflow-results-content');

                inputSection.style.display = 'none';
                resultsStatus.style.display = 'block';
                resultsStatus.style.background = 'rgba(99, 102, 241, 0.2)';
                resultsStatus.style.color = '#6366f1';
                resultsStatus.innerHTML = '&#x23F3; Running workflow...';
                resultsContent.style.display = 'block';
                resultsContent.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.5;">Executing workflow with: ' + inputValue.substring(0, 50) + (inputValue.length > 50 ? '...' : '') + '</div>';

                vscode.postMessage({ type: 'runWorkflow', workflow: currentWorkflow, input: inputValue });
            });
        }

        // Close workflow results panel
        const closeWorkflowResults = document.getElementById('close-workflow-results');
        if (closeWorkflowResults) {
            closeWorkflowResults.addEventListener('click', function() {
                document.getElementById('workflow-results').style.display = 'none';
                currentWorkflow = null;
            });
        }

        // View Costs button - show panel and request data
        const viewCostsBtn = document.getElementById('view-costs-btn');
        const costsPanel = document.getElementById('costs-panel');
        const closeCostsBtn = document.getElementById('close-costs');

        if (viewCostsBtn) {
            viewCostsBtn.addEventListener('click', function() {
                costsPanel.style.display = 'block';
                vscode.postMessage({ type: 'getCosts' });
            });
        }

        if (closeCostsBtn) {
            closeCostsBtn.addEventListener('click', function() {
                costsPanel.style.display = 'none';
            });
        }

        // Handle data updates
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'update') {
                updateHealth(message.data.health);
                updateWorkflows(message.data.workflows);
            } else if (message.type === 'costsData') {
                updateCostsPanel(message.data);
            } else if (message.type === 'workflowStatus') {
                updateWorkflowResults(message.data);
            } else if (message.type === 'pickerResult') {
                // Handle file/folder picker or dropdown result
                const data = message.data;
                if (data.cancelled) return;

                if (data.path) {
                    const config = workflowConfig[data.workflow];
                    if (config && config.type === 'dropdown') {
                        // Dropdown selection
                        selectedDropdownValue = data.path;
                        const selectBtn = document.getElementById('workflow-select-btn');
                        selectBtn.textContent = data.path;
                        selectBtn.style.borderColor = 'var(--border)';
                    } else {
                        // File or folder picker
                        const pathField = document.getElementById('workflow-path');
                        pathField.value = data.path;
                        pathField.style.borderColor = 'var(--border)';
                    }
                }
            } else if (message.type === 'activeFile') {
                // Pre-populate with active file if applicable
                const data = message.data;
                if (data.path && data.workflow === currentWorkflow) {
                    const config = workflowConfig[currentWorkflow];
                    // Only pre-populate for file pickers, not folders
                    if (config && config.type === 'file') {
                        const pathField = document.getElementById('workflow-path');
                        if (!pathField.value) {
                            pathField.value = data.path;
                        }
                    }
                }
            }
        });

        function updateWorkflowResults(data) {
            const resultsPanel = document.getElementById('workflow-results');
            const resultsTitle = document.getElementById('workflow-results-title');
            const resultsStatus = document.getElementById('workflow-results-status');
            const resultsContent = document.getElementById('workflow-results-content');

            // Restore button state only on complete/error
            if (data.status !== 'running') {
                const state = workflowButtonState.get(data.workflow);
                if (state) {
                    state.btn.disabled = false;
                    state.btn.style.opacity = '1';
                    const icon = state.btn.querySelector('.action-icon');
                    const text = state.btn.querySelector('span:not(.action-icon)');
                    if (icon) icon.innerHTML = state.icon;
                    if (text) text.textContent = state.text;
                    runningActions.delete('wf-' + data.workflow);
                }
            }

            if (data.status === 'running') {
                resultsPanel.style.display = 'block';
                resultsTitle.innerHTML = '&#x2699; ' + data.workflow;
                resultsStatus.style.display = 'block';
                resultsStatus.style.background = 'rgba(99, 102, 241, 0.2)';
                resultsStatus.style.color = '#6366f1';
                resultsStatus.innerHTML = '&#x23F3; Running workflow...';
                resultsContent.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.5;">Executing workflow...</div>';
            } else if (data.status === 'complete') {
                resultsStatus.style.display = 'block';
                resultsStatus.style.background = 'rgba(16, 185, 129, 0.2)';
                resultsStatus.style.color = 'var(--vscode-testing-iconPassed)';
                resultsStatus.innerHTML = '&#x2714; Complete';
                resultsContent.textContent = data.output || 'Workflow completed successfully.';
            } else if (data.status === 'error') {
                resultsStatus.style.display = 'block';
                resultsStatus.style.background = 'rgba(239, 68, 68, 0.2)';
                resultsStatus.style.color = 'var(--vscode-testing-iconFailed)';
                resultsStatus.innerHTML = '&#x2718; Error';
                resultsContent.textContent = data.output || data.error || 'An error occurred.';
            }
        }

        function updateCostsPanel(data) {
            // Update summary
            document.getElementById('costs-saved').textContent = '$' + (data.totalSavings || 0).toFixed(2);
            document.getElementById('costs-percent').textContent = (data.savingsPercent || 0) + '%';
            document.getElementById('costs-total').textContent = '$' + (data.totalCost || 0).toFixed(2);

            // Update requests list
            const listEl = document.getElementById('costs-list');
            if (!data.requests || data.requests.length === 0) {
                listEl.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.5;">No requests yet</div>';
                return;
            }

            const tierColors = {
                cheap: '#22c55e',
                capable: '#3b82f6',
                premium: '#a855f7'
            };

            listEl.innerHTML = data.requests.map(req => {
                const tierColor = tierColors[req.tier] || '#888';
                const timeAgo = formatTimeAgo(req.timestamp);
                return '<div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--vscode-widget-border); font-size: 11px;">' +
                    '<div style="flex: 1;">' +
                        '<div style="font-weight: 500;">' + (req.task_type || 'unknown').replace(/_/g, ' ') + '</div>' +
                        '<div style="display: flex; gap: 8px; opacity: 0.7; font-size: 10px;">' +
                            '<span style="color: ' + tierColor + ';">' + (req.tier || 'capable') + '</span>' +
                            '<span>' + timeAgo + '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div style="text-align: right;">' +
                        '<div style="color: var(--vscode-charts-green); font-weight: 500;">+$' + (req.savings || 0).toFixed(4) + '</div>' +
                        '<div style="opacity: 0.7; font-size: 10px;">$' + (req.actual_cost || 0).toFixed(4) + '</div>' +
                    '</div>' +
                '</div>';
            }).join('');
        }

        function formatTimeAgo(timestamp) {
            if (!timestamp) return '';
            const now = new Date();
            const date = new Date(timestamp);
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            if (diffMins < 1) return 'just now';
            if (diffMins < 60) return diffMins + 'm ago';
            if (diffHours < 24) return diffHours + 'h ago';
            return diffDays + 'd ago';
        }

        function updateHealth(health) {
            const scoreEl = document.getElementById('health-score');
            scoreEl.textContent = health.score + '%';
            scoreEl.className = 'score-circle ' + (health.score >= 80 ? 'good' : health.score >= 50 ? 'warning' : 'bad');

            // Update tree items with icons and values
            updateTreeItem('patterns', health.patterns, health.patterns > 0);
            updateTreeItem('lint', health.lint.errors + ' errors', health.lint.errors === 0);
            updateTreeItem('types', health.types.errors + ' errors', health.types.errors === 0);
            updateTreeItem('security', (health.security?.high || 0) + ' high', (health.security?.high || 0) === 0);
            updateTreeItem('tests', health.tests.passed + '/' + health.tests.total, health.tests.failed === 0);
            document.getElementById('metric-debt').textContent = (health.techDebt?.total || 0) + ' items';

            const coverage = health.tests.coverage || 0;
            document.getElementById('coverage-bar').style.width = coverage + '%';
            document.getElementById('coverage-bar').className = 'progress-fill ' + (coverage >= 70 ? 'success' : coverage >= 50 ? 'warning' : 'error');
            document.getElementById('coverage-value').textContent = coverage + '%';

            // Update Power tab stats
            document.getElementById('power-patterns').textContent = health.patterns;
            const powerHealthEl = document.getElementById('power-health');
            powerHealthEl.textContent = health.score + '%';
            powerHealthEl.className = 'metric-value ' + (health.score >= 80 ? 'success' : health.score >= 50 ? 'warning' : 'error');
        }

        function updateTreeItem(id, value, isOk) {
            const valueEl = document.getElementById('metric-' + id);
            const iconEl = document.getElementById(id + '-icon');
            if (valueEl) valueEl.textContent = value;
            if (iconEl) {
                iconEl.textContent = isOk ? '\\u2714' : '\\u2718';
                iconEl.className = 'tree-icon ' + (isOk ? 'ok' : 'error');
            }
        }

        function updateWorkflows(workflows) {
            // Update Power tab stats from workflow data
            if (workflows.costs) {
                document.getElementById('power-savings').textContent = '$' + (workflows.costs.totalSavings || 0).toFixed(2);
                document.getElementById('power-requests').textContent = workflows.costs.requests || 0;
            }

            document.getElementById('wf-runs').textContent = workflows.totalRuns;
            document.getElementById('wf-success').textContent = workflows.totalRuns > 0 ? Math.round((workflows.successfulRuns / workflows.totalRuns) * 100) + '%' : '0%';
            document.getElementById('wf-cost').textContent = '$' + workflows.totalCost.toFixed(4);
            document.getElementById('wf-savings').textContent = '$' + workflows.totalSavings.toFixed(4);

            const list = document.getElementById('workflows-list');
            if (workflows.recentRuns.length === 0) {
                list.innerHTML = '<div class="empty-state">No workflow runs yet</div>';
                return;
            }

            list.innerHTML = workflows.recentRuns.slice(0, 5).map(run => \`
                <div class="list-item">
                    <span class="list-item-icon">\${run.success ? '&#x2714;' : '&#x2718;'}</span>
                    <div class="list-item-content">
                        <div class="list-item-title">\${run.workflow}</div>
                        <div class="list-item-desc">Saved $\${run.savings.toFixed(4)}</div>
                    </div>
                    <span class="badge \${run.success ? 'success' : 'error'}">\${run.success ? 'OK' : 'Failed'}</span>
                </div>
            \`).join('');
        }

        // Request initial data
        vscode.postMessage({ type: 'refresh' });
    </script>
</body>
</html>`;
    }

    public dispose() {
        if (this._fileWatcher) {
            this._fileWatcher.dispose();
        }
    }
}

interface PatternData {
    id: string;
    type: string;
    status: string;
    rootCause: string;
    fix: string;
    files: string[];
    timestamp: string;
}

interface HealthData {
    score: number;
    patterns: number;
    lint: { errors: number; warnings: number };
    types: { errors: number };
    security: { high: number; medium: number; low: number };
    tests: { passed: number; failed: number; total: number; coverage: number };
    techDebt: { total: number; todos: number; fixmes: number; hacks: number };
    lastUpdated: string | null;
}

interface CostData {
    totalCost: number;
    totalSavings: number;
    requests: number;
    dailyCosts: Array<{ date: string; cost: number; savings: number }>;
    byProvider: Record<string, { requests: number; cost: number }>;
}

interface WorkflowData {
    totalRuns: number;
    successfulRuns: number;
    totalCost: number;
    totalSavings: number;
    recentRuns: Array<{ workflow: string; success: boolean; cost: number; savings: number; timestamp: string }>;
    byWorkflow: Record<string, { runs: number; cost: number; savings: number }>;
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
