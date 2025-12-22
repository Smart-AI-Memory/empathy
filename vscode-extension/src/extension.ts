/**
 * Empathy Framework VS Code Extension
 *
 * Provides integration with Empathy Framework including:
 * - Status bar showing health score and cost savings
 * - Command palette for all CLI commands
 * - Sidebar with pattern browser
 * - Inline diagnostics from inspection
 * - Quick fix actions and auto-scan on save
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { PowerPanel } from './panels/PowerPanel';
import { EmpathyDashboardProvider } from './panels/EmpathyDashboardPanel';

// Status bar item
let statusBarItem: vscode.StatusBarItem;

// Health provider (used for diagnostics)
let healthProvider: HealthTreeProvider;

// Extension path (for accessing bundled scripts)
let extensionPath: string;

// Refresh timer
let refreshTimer: NodeJS.Timeout | undefined;

// Diagnostics collection for Problem Panel (Feature F)
let diagnosticCollection: vscode.DiagnosticCollection;

// File watcher for auto-scan (Feature E)
let fileWatcher: vscode.FileSystemWatcher | undefined;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Empathy Framework extension activated');

    // Store extension path for accessing bundled scripts
    extensionPath = context.extensionPath;

    // Create status bar
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.command = 'empathy.status';
    context.subscriptions.push(statusBarItem);

    // Create diagnostics collection (Feature F)
    diagnosticCollection = vscode.languages.createDiagnosticCollection('empathy');
    context.subscriptions.push(diagnosticCollection);

    // Create health provider (for diagnostics support)
    healthProvider = new HealthTreeProvider(diagnosticCollection);

    // Register dashboard webview provider (with context for persistence)
    const dashboardProvider = new EmpathyDashboardProvider(context.extensionUri, context);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            EmpathyDashboardProvider.viewType,
            dashboardProvider
        )
    );

    // Register commands - existing
    const commands = [
        { name: 'empathy.morning', handler: cmdMorning },
        { name: 'empathy.ship', handler: cmdShip },
        { name: 'empathy.fixAll', handler: cmdFixAll },
        { name: 'empathy.learn', handler: cmdLearn },
        { name: 'empathy.costs', handler: cmdCosts },
        { name: 'empathy.dashboard', handler: cmdDashboard },
        { name: 'empathy.syncClaude', handler: cmdSyncClaude },
        { name: 'empathy.status', handler: cmdStatus },
        // New commands for Health view actions (Features A, B, C, D)
        { name: 'empathy.refreshHealth', handler: cmdRefreshHealth },
        { name: 'empathy.runScan', handler: cmdRunScan },
        { name: 'empathy.fixLint', handler: cmdFixLint },
        { name: 'empathy.fixFormat', handler: cmdFixFormat },
        { name: 'empathy.runTests', handler: cmdRunTests },
        { name: 'empathy.viewDetails', handler: cmdViewDetails },
        { name: 'empathy.openFile', handler: cmdOpenFile },
        { name: 'empathy.ignoreIssue', handler: cmdIgnoreIssue },
        { name: 'empathy.openWebDashboard', handler: cmdOpenWebDashboard },
    ];

    for (const cmd of commands) {
        context.subscriptions.push(
            vscode.commands.registerCommand(cmd.name, cmd.handler)
        );
    }

    // Register Power Panel command (needs extensionUri)
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.openPowerPanel', () => {
            PowerPanel.createOrShow(context.extensionUri);
        })
    );

    // Initialize
    updateStatusBar();
    startAutoRefresh(context);
    setupAutoScanOnSave(context); // Feature E

    // Show welcome message on first activation
    showWelcomeIfNeeded(context);

    // Load initial diagnostics (Feature F)
    healthProvider.updateDiagnostics();
}

/**
 * Extension deactivation
 */
export function deactivate() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    if (fileWatcher) {
        fileWatcher.dispose();
    }
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
}

// ============================================================================
// Command Handlers
// ============================================================================

async function cmdMorning() {
    runEmpathyCommand('morning', 'Morning Briefing');
}

async function cmdShip() {
    runEmpathyCommand('ship', 'Pre-Ship Check');
}

async function cmdFixAll() {
    await runEmpathyCommandWithProgress('fix-all', 'Fixing all issues...');
    healthProvider.refresh();
}

async function cmdLearn() {
    runEmpathyCommand('learn --analyze 20', 'Learning Patterns');
}

async function cmdCosts() {
    runEmpathyCommand('costs', 'API Costs');
}

async function cmdDashboard() {
    runEmpathyCommand('dashboard', 'Dashboard', { background: true });
    vscode.window.showInformationMessage(
        'Empathy Dashboard started. Check your browser.'
    );
}

async function cmdSyncClaude() {
    runEmpathyCommand('sync-claude', 'Sync to Claude Code');
}

async function cmdStatus() {
    const data = await getStatusData();
    if (data) {
        const message = [
            `Patterns: ${data.patterns} learned`,
            `Health: ${data.health}`,
            `Costs: $${data.savings.toFixed(2)} saved`,
        ].join(' | ');
        vscode.window.showInformationMessage(`Empathy Status: ${message}`);
    }
}

// Feature A: Quick Fix for Lint
async function cmdFixLint() {
    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Fixing lint issues...',
            cancellable: false,
        },
        async () => {
            await runEmpathyCommandSilent('fix-all --lint-only');
            healthProvider.refresh();
            vscode.window.showInformationMessage('Lint issues fixed!');
        }
    );
}

// Feature A: Quick Fix for Format
async function cmdFixFormat() {
    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Formatting code...',
            cancellable: false,
        },
        async () => {
            await runEmpathyCommandSilent('fix-all --format-only');
            healthProvider.refresh();
            vscode.window.showInformationMessage('Code formatted!');
        }
    );
}

// Feature B: Refresh Health / Run Scan
async function cmdRefreshHealth() {
    healthProvider.refresh();
    healthProvider.updateDiagnostics();
    vscode.window.showInformationMessage('Health data refreshed');
}

async function cmdRunScan() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Empathy: Running health scan...',
            cancellable: false,
        },
        async () => {
            // Run actual health checks via bundled Python script
            const config = vscode.workspace.getConfiguration('empathy');
            const pythonPath = config.get<string>('pythonPath', 'python');
            const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

            // Ensure .empathy directory exists
            if (!fs.existsSync(empathyDir)) {
                fs.mkdirSync(empathyDir, { recursive: true });
            }

            // Path to bundled health scan script (safe - no shell interpolation)
            const healthScriptPath = path.join(extensionPath, 'scripts', 'health_scan.py');

            return new Promise<void>((resolve) => {
                // Use execFile with array arguments to prevent command injection
                cp.execFile(pythonPath, [healthScriptPath, workspaceFolder, empathyDir],
                    { cwd: workspaceFolder, timeout: 60000 },
                    (error) => {
                        healthProvider.refresh();
                        healthProvider.updateDiagnostics();
                        updateStatusBar();
                        if (error) {
                            vscode.window.showWarningMessage('Health scan completed with warnings');
                        } else {
                            vscode.window.showInformationMessage('Health scan complete!');
                        }
                        resolve();
                    }
                );
            });
        }
    );
}

// Feature C: Run Tests
async function cmdRunTests() {
    runEmpathyCommand('ship --tests-only', 'Running Tests');
}

// Feature C: Open file at location
async function cmdOpenFile(filePath?: string, line?: number) {
    if (!filePath) {
        return;
    }
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        return;
    }

    const fullPath = path.isAbsolute(filePath)
        ? filePath
        : path.join(workspaceFolder, filePath);

    try {
        const doc = await vscode.workspace.openTextDocument(fullPath);
        const editor = await vscode.window.showTextDocument(doc);
        if (line && line > 0) {
            const position = new vscode.Position(line - 1, 0);
            editor.selection = new vscode.Selection(position, position);
            editor.revealRange(new vscode.Range(position, position));
        }
    } catch (err) {
        vscode.window.showErrorMessage(`Could not open file: ${filePath}`);
    }
}

// Feature D: View Details
async function cmdViewDetails(item?: HealthItem) {
    if (!item) {
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        return;
    }

    // Show quick pick with options based on item type
    const options: string[] = [];
    if (item.label === 'Lint' || item.label === 'Types') {
        options.push('Fix Issues', 'Show in Terminal', 'View Report');
    } else if (item.label === 'Security') {
        options.push('View Report', 'Run Security Scan');
    } else if (item.label === 'Tests') {
        options.push('Run Tests', 'View Coverage Report');
    } else if (item.label === 'Tech Debt') {
        options.push('View Hotspots', 'Search TODOs');
    } else {
        options.push('Refresh', 'Open Dashboard');
    }

    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: `Actions for ${item.label}`,
    });

    if (!selected) {
        return;
    }

    switch (selected) {
        case 'Fix Issues':
            cmdFixAll();
            break;
        case 'Show in Terminal':
            runEmpathyCommand('ship --verbose', 'Health Check');
            break;
        case 'View Report':
            runEmpathyCommand('dashboard', 'Dashboard', { background: true });
            break;
        case 'Run Security Scan':
            runEmpathyCommand('ship --security-only', 'Security Scan');
            break;
        case 'Run Tests':
            cmdRunTests();
            break;
        case 'View Coverage Report':
            const coverageFile = path.join(workspaceFolder, 'htmlcov', 'index.html');
            if (fs.existsSync(coverageFile)) {
                vscode.env.openExternal(vscode.Uri.file(coverageFile));
            } else {
                vscode.window.showWarningMessage('No coverage report found. Run tests first.');
            }
            break;
        case 'View Hotspots':
            runEmpathyCommand('patterns hotspots', 'Tech Debt Hotspots');
            break;
        case 'Search TODOs':
            vscode.commands.executeCommand('workbench.action.findInFiles', {
                query: 'TODO|FIXME|HACK',
                isRegex: true,
            });
            break;
        case 'Refresh':
            cmdRefreshHealth();
            break;
        case 'Open Dashboard':
            cmdDashboard();
            break;
    }
}

// Feature D: Ignore Issue (add to baseline)
async function cmdIgnoreIssue(item?: HealthItem) {
    if (!item) {
        return;
    }

    const reason = await vscode.window.showInputBox({
        prompt: 'Reason for ignoring this issue (optional)',
        placeHolder: 'e.g., False positive, Will fix in Q2',
    });

    if (reason === undefined) {
        return; // Cancelled
    }

    vscode.window.showInformationMessage(
        `Issue "${item.label}" would be added to baseline. (Feature coming soon)`
    );
}

// Open Full Web Dashboard
async function cmdOpenWebDashboard() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');

    // Check if dashboard server is already running
    try {
        const http = await import('http');
        const isRunning = await new Promise<boolean>((resolve) => {
            const req = http.request(
                { host: 'localhost', port: 8765, path: '/api/health', timeout: 1000 },
                (res) => resolve(res.statusCode === 200)
            );
            req.on('error', () => resolve(false));
            req.on('timeout', () => { req.destroy(); resolve(false); });
            req.end();
        });

        if (isRunning) {
            vscode.env.openExternal(vscode.Uri.parse('http://localhost:8765'));
            return;
        }
    } catch {
        // Server not running, continue to start it
    }

    // Start the dashboard server
    vscode.window.showInformationMessage('Starting Empathy Web Dashboard...');

    const proc = cp.spawn(pythonPath, ['-m', 'empathy_os.cli', 'dashboard', '--no-browser'], {
        cwd: workspaceFolder.uri.fsPath,
        detached: true,
        stdio: 'ignore'
    });
    proc.unref();

    // Wait for server to start, then open browser
    setTimeout(() => {
        vscode.env.openExternal(vscode.Uri.parse('http://localhost:8765'));
    }, 2500);
}

// ============================================================================
// Empathy Command Runner
// ============================================================================

interface RunOptions {
    background?: boolean;
}

async function runEmpathyCommand(
    command: string,
    title: string,
    options: RunOptions = {}
): Promise<void> {
    const config = vscode.workspace.getConfiguration('empathy');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    // Build arguments as array for safe execution (no shell interpolation)
    const args = ['-m', 'empathy_os.cli', ...command.split(/\s+/)];

    if (options.background) {
        // Use execFile with array arguments to prevent command injection
        cp.execFile(pythonPath, args, { cwd: workspaceFolder });
        return;
    }

    // Show in terminal (terminal.sendText is safe - no shell injection risk)
    const terminal = vscode.window.createTerminal({
        name: `Empathy: ${title}`,
        cwd: workspaceFolder,
    });
    terminal.show();
    terminal.sendText(`${pythonPath} -m empathy_os.cli ${command}`);
}

async function runEmpathyCommandSilent(command: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        if (!workspaceFolder) {
            reject(new Error('No workspace folder open'));
            return;
        }

        // Build arguments as array for safe execution (no shell interpolation)
        const args = ['-m', 'empathy_os.cli', ...command.split(/\s+/)];

        // Use execFile with array arguments to prevent command injection
        cp.execFile(pythonPath, args, { cwd: workspaceFolder }, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else {
                resolve(stdout);
            }
        });
    });
}

async function runEmpathyCommandWithProgress(command: string, message: string): Promise<void> {
    return vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: `Empathy: ${message}`,
            cancellable: false,
        },
        async () => {
            await runEmpathyCommandSilent(command);
        }
    );
}

// ============================================================================
// Feature E: Auto-Scan on Save
// ============================================================================

function setupAutoScanOnSave(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration('empathy');
    const autoScanEnabled = config.get<boolean>('autoScanOnSave', false);

    if (!autoScanEnabled) {
        return;
    }

    // Watch for Python file saves
    fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.py');

    // Debounce mechanism
    let scanTimeout: NodeJS.Timeout | undefined;

    const debouncedScan = () => {
        if (scanTimeout) {
            clearTimeout(scanTimeout);
        }
        scanTimeout = setTimeout(async () => {
            try {
                await runEmpathyCommandSilent('ship --quick --silent');
                healthProvider.refresh();
                healthProvider.updateDiagnostics();
            } catch {
                // Ignore errors in background scan
            }
        }, 2000); // Wait 2 seconds after last save
    };

    fileWatcher.onDidChange(debouncedScan);
    fileWatcher.onDidCreate(debouncedScan);

    context.subscriptions.push(fileWatcher);
}

// ============================================================================
// Status Bar
// ============================================================================

interface StatusData {
    patterns: number;
    health: string;
    savings: number;
}

async function getStatusData(): Promise<StatusData | null> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceFolder) {
        return null;
    }

    const config = vscode.workspace.getConfiguration('empathy');
    const patternsDir = path.join(
        workspaceFolder,
        config.get<string>('patternsDir', './patterns')
    );
    const empathyDir = path.join(
        workspaceFolder,
        config.get<string>('empathyDir', '.empathy')
    );

    let patterns = 0;
    let savings = 0;

    // Count patterns
    try {
        const debuggingFile = path.join(patternsDir, 'debugging.json');
        if (fs.existsSync(debuggingFile)) {
            const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
            patterns = data.patterns?.length || 0;
        }
    } catch {
        // Ignore errors
    }

    // Get cost savings
    try {
        const costsFile = path.join(empathyDir, 'costs.json');
        if (fs.existsSync(costsFile)) {
            const data = JSON.parse(fs.readFileSync(costsFile, 'utf8'));
            // Sum up daily savings
            for (const daily of Object.values(data.daily_totals || {})) {
                savings += (daily as any).savings || 0;
            }
        }
    } catch {
        // Ignore errors
    }

    return {
        patterns,
        health: patterns > 0 ? 'OK' : 'Setup needed',
        savings,
    };
}

async function updateStatusBar(): Promise<void> {
    const config = vscode.workspace.getConfiguration('empathy');
    if (!config.get<boolean>('showStatusBar', true)) {
        statusBarItem.hide();
        return;
    }

    const data = await getStatusData();
    if (!data) {
        statusBarItem.text = '$(pulse) Empathy';
        statusBarItem.tooltip = 'No workspace open';
    } else if (data.patterns === 0) {
        statusBarItem.text = '$(pulse) Empathy: Setup';
        statusBarItem.tooltip = 'Run "empathy learn" to get started';
    } else {
        statusBarItem.text = `$(pulse) ${data.patterns} patterns | $${data.savings.toFixed(2)} saved`;
        statusBarItem.tooltip = `Empathy Framework\nPatterns: ${data.patterns}\nSavings: $${data.savings.toFixed(2)}`;
    }
    statusBarItem.show();
}

function startAutoRefresh(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration('empathy');
    const autoRefresh = config.get<boolean>('autoRefresh', true);
    const interval = config.get<number>('refreshInterval', 300) * 1000;

    if (autoRefresh && interval > 0) {
        refreshTimer = setInterval(() => {
            updateStatusBar();
            healthProvider.refresh();
        }, interval);
    }
}

// ============================================================================
// Health Provider (for diagnostics)
// ============================================================================

class HealthTreeProvider implements vscode.TreeDataProvider<HealthItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HealthItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private cachedHealth: HealthData | null = null;
    private diagnosticCollection: vscode.DiagnosticCollection;

    constructor(diagnosticCollection: vscode.DiagnosticCollection) {
        this.diagnosticCollection = diagnosticCollection;
    }

    refresh(): void {
        this.cachedHealth = null;
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: HealthItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: HealthItem): Promise<HealthItem[]> {
        // If this is a child element, return its details
        if (element && element.children) {
            return element.children;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return [new HealthItem('No workspace', 'Open a folder to inspect', 'unknown')];
        }

        // Get health data from files or cache
        const health = await this.getHealthData(workspaceFolder);

        const items: HealthItem[] = [];

        // Overall Health Score - clickable to run scan
        const scoreIcon = health.score >= 80 ? 'ok' : health.score >= 50 ? 'warning' : 'error';
        const scoreItem = new HealthItem(
            'Health Score',
            `${health.score}%`,
            scoreIcon,
            undefined,
            'Overall code health score - click to scan'
        );
        scoreItem.command = { command: 'empathy.runScan', title: 'Run Scan' };
        scoreItem.contextValue = 'healthScore';
        items.push(scoreItem);

        // Patterns Learned
        const patternsItem = new HealthItem(
            'Patterns Learned',
            `${health.patterns} bugs tracked`,
            health.patterns > 0 ? 'ok' : 'unknown',
            undefined,
            'Bug patterns learned from git history'
        );
        patternsItem.command = { command: 'empathy.learn', title: 'Learn Patterns' };
        patternsItem.contextValue = 'patterns';
        items.push(patternsItem);

        // Lint Issues - with fix action
        const lintStatus = health.lint.errors === 0 ? 'ok' : health.lint.errors > 10 ? 'error' : 'warning';
        const lintItem = new HealthItem(
            'Lint',
            `${health.lint.errors} errors, ${health.lint.warnings} warnings`,
            lintStatus,
            [
                new HealthItem('Errors', health.lint.errors.toString(), health.lint.errors === 0 ? 'ok' : 'error'),
                new HealthItem('Warnings', health.lint.warnings.toString(), health.lint.warnings === 0 ? 'ok' : 'warning'),
            ],
            'Linting issues from ruff/pylint - click to fix'
        );
        lintItem.command = { command: 'empathy.fixLint', title: 'Fix Lint' };
        lintItem.contextValue = 'lint';
        items.push(lintItem);

        // Type Checking
        const typeStatus = health.types.errors === 0 ? 'ok' : 'error';
        const typesItem = new HealthItem(
            'Types',
            health.types.errors === 0 ? 'All types valid' : `${health.types.errors} type errors`,
            typeStatus,
            undefined,
            'MyPy type checking results'
        );
        typesItem.contextValue = 'types';
        items.push(typesItem);

        // Security
        const secStatus = health.security.high === 0 && health.security.medium === 0 ? 'ok' :
                         health.security.high > 0 ? 'error' : 'warning';
        const secItem = new HealthItem(
            'Security',
            `${health.security.high} high, ${health.security.medium} medium`,
            secStatus,
            [
                new HealthItem('High Severity', health.security.high.toString(), health.security.high === 0 ? 'ok' : 'error'),
                new HealthItem('Medium Severity', health.security.medium.toString(), health.security.medium === 0 ? 'ok' : 'warning'),
                new HealthItem('Low Severity', health.security.low.toString(), 'ok'),
            ],
            'Security vulnerabilities from bandit'
        );
        secItem.contextValue = 'security';
        items.push(secItem);

        // Tests - with run action
        const testStatus = health.tests.failed === 0 ? 'ok' : 'error';
        const testItem = new HealthItem(
            'Tests',
            `${health.tests.passed}/${health.tests.total} passing`,
            testStatus,
            [
                new HealthItem('Passed', health.tests.passed.toString(), 'ok'),
                new HealthItem('Failed', health.tests.failed.toString(), health.tests.failed === 0 ? 'ok' : 'error'),
                new HealthItem('Coverage', `${health.tests.coverage}%`, health.tests.coverage >= 70 ? 'ok' : 'warning'),
            ],
            'Test suite status and coverage - click to run'
        );
        testItem.command = { command: 'empathy.runTests', title: 'Run Tests' };
        testItem.contextValue = 'tests';
        items.push(testItem);

        // Tech Debt
        const debtStatus = health.techDebt.total < 50 ? 'ok' : health.techDebt.total < 200 ? 'warning' : 'error';
        const debtItem = new HealthItem(
            'Tech Debt',
            `${health.techDebt.total} items`,
            debtStatus,
            [
                new HealthItem('TODOs', health.techDebt.todos.toString(), 'info'),
                new HealthItem('FIXMEs', health.techDebt.fixmes.toString(), health.techDebt.fixmes === 0 ? 'ok' : 'warning'),
                new HealthItem('HACKs', health.techDebt.hacks.toString(), health.techDebt.hacks === 0 ? 'ok' : 'error'),
            ],
            'Technical debt from code annotations'
        );
        debtItem.contextValue = 'techDebt';
        items.push(debtItem);

        // Last Updated - with refresh action
        const lastScanItem = new HealthItem(
            'Last Scan',
            health.lastUpdated || 'Never',
            'info',
            undefined,
            'Click to refresh'
        );
        lastScanItem.command = { command: 'empathy.refreshHealth', title: 'Refresh' };
        lastScanItem.contextValue = 'lastScan';
        items.push(lastScanItem);

        return items;
    }

    // Feature F: Update Problem Panel diagnostics
    async updateDiagnostics(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        this.diagnosticCollection.clear();

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(
            workspaceFolder,
            config.get<string>('empathyDir', '.empathy')
        );

        // Read issues from inspection results
        try {
            const issuesFile = path.join(empathyDir, 'issues.json');
            if (!fs.existsSync(issuesFile)) {
                return;
            }

            const data = JSON.parse(fs.readFileSync(issuesFile, 'utf8'));
            const diagnosticsMap = new Map<string, vscode.Diagnostic[]>();

            for (const issue of data.issues || []) {
                const filePath = issue.file || '';
                const line = (issue.line || 1) - 1;
                const message = issue.message || 'Unknown issue';
                const severity = this.getSeverity(issue.severity || 'warning');

                const range = new vscode.Range(line, 0, line, 1000);
                const diagnostic = new vscode.Diagnostic(range, message, severity);
                diagnostic.source = 'Empathy';
                diagnostic.code = issue.rule || issue.type || 'empathy';

                const fullPath = path.isAbsolute(filePath)
                    ? filePath
                    : path.join(workspaceFolder, filePath);

                if (!diagnosticsMap.has(fullPath)) {
                    diagnosticsMap.set(fullPath, []);
                }
                diagnosticsMap.get(fullPath)!.push(diagnostic);
            }

            // Apply diagnostics
            for (const [file, diagnostics] of diagnosticsMap) {
                const uri = vscode.Uri.file(file);
                this.diagnosticCollection.set(uri, diagnostics);
            }
        } catch {
            // Ignore errors reading issues file
        }
    }

    private getSeverity(level: string): vscode.DiagnosticSeverity {
        switch (level.toLowerCase()) {
            case 'error':
            case 'high':
            case 'critical':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
            case 'medium':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
            case 'low':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Hint;
        }
    }

    private async getHealthData(workspaceFolder: string): Promise<HealthData> {
        if (this.cachedHealth) {
            return this.cachedHealth;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(
            workspaceFolder,
            config.get<string>('empathyDir', '.empathy')
        );
        const patternsDir = path.join(
            workspaceFolder,
            config.get<string>('patternsDir', './patterns')
        );

        // Default health data
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

        // Read patterns count
        try {
            const debuggingFile = path.join(patternsDir, 'debugging.json');
            if (fs.existsSync(debuggingFile)) {
                const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
                health.patterns = data.patterns?.length || 0;
            }
        } catch { /* ignore */ }

        // Read health.json if exists (from empathy-inspect or ship)
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
                health.lastUpdated = data.timestamp ? new Date(data.timestamp).toLocaleString() : null;
            }
        } catch { /* ignore */ }

        // Read tech debt from patterns if available
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
        if (health.score === 0) {
            let score = 100;
            score -= health.lint.errors * 2;
            score -= health.lint.warnings * 0.5;
            score -= health.types.errors * 3;
            score -= health.security.high * 10;
            score -= health.security.medium * 5;
            score -= health.tests.failed * 5;
            score -= Math.max(0, 70 - health.tests.coverage);
            health.score = Math.max(0, Math.min(100, Math.round(score)));
        }

        this.cachedHealth = health;
        return health;
    }
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

class HealthItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly status: string,
        public readonly children?: HealthItem[],
        public readonly fullTooltip?: string
    ) {
        super(
            label,
            children ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None
        );
        this.description = value;
        this.tooltip = fullTooltip || `${label}: ${value}`;

        // Set icon based on status
        switch (status) {
            case 'ok':
                this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
                break;
            case 'warning':
                this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('editorWarning.foreground'));
                break;
            case 'error':
                this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
                break;
            case 'info':
                this.iconPath = new vscode.ThemeIcon('info');
                break;
            default:
                this.iconPath = new vscode.ThemeIcon('question');
        }
    }
}

// ============================================================================
// Welcome Message
// ============================================================================

function showWelcomeIfNeeded(context: vscode.ExtensionContext): void {
    const hasShownWelcome = context.globalState.get<boolean>('hasShownWelcome');
    if (!hasShownWelcome) {
        vscode.window
            .showInformationMessage(
                'Empathy Framework extension activated! Run "empathy morning" to get started.',
                'Open Command Palette',
                'Dismiss'
            )
            .then((selection) => {
                if (selection === 'Open Command Palette') {
                    vscode.commands.executeCommand(
                        'workbench.action.showCommands',
                        'Empathy'
                    );
                }
            });
        context.globalState.update('hasShownWelcome', true);
    }
}
