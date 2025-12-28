/**
 * Refactor Advisor Panel - Interactive Refactoring Assistant
 *
 * A Level 4 Empathy feature providing interactive code refactoring with:
 * - 2-agent analysis (RefactorAnalyzer + RefactorWriter)
 * - Session memory with checkpoint/rollback capability
 * - User preference learning over time
 * - Side panel for findings + editor tab for diff views
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';

// =============================================================================
// Types
// =============================================================================

interface RefactoringFinding {
    id: string;
    title: string;
    description: string;
    category: string;
    severity: string;
    file_path: string;
    start_line: number;
    end_line: number;
    before_code: string;
    after_code: string | null;
    confidence: number;
    estimated_impact: string;
    rationale: string;
}

interface CodeCheckpoint {
    id: string;
    file_path: string;
    original_content: string;
    timestamp: string;
    finding_id: string;
}

interface RefactorSession {
    sessionId: string;
    filePath: string;
    originalContent: string;
    findings: RefactoringFinding[];
    checkpoints: CodeCheckpoint[];
    userDecisions: Map<string, 'accepted' | 'rejected' | 'pending'>;
    currentFindingIndex: number;
}

interface BackendHealth {
    status: 'ok' | 'degraded' | 'unknown';
    lastSuccessTime: number | null;
    lastErrorTime: number | null;
    consecutiveFailures: number;
    lastError: string | null;
}

// =============================================================================
// Constants
// =============================================================================

const DEBUG = false; // Set to true to enable debug logging

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

function generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// =============================================================================
// RefactorAdvisorPanel Class
// =============================================================================

export class RefactorAdvisorPanel implements vscode.WebviewViewProvider {
    public static readonly viewType = 'refactor-advisor';

    private _view?: vscode.WebviewView;
    private _extensionUri: vscode.Uri;
    private _session: RefactorSession | null = null;
    private _disposables: vscode.Disposable[] = [];
    private _activeProcess: cp.ChildProcess | null = null;
    private _backendHealth: BackendHealth = {
        status: 'unknown',
        lastSuccessTime: null,
        lastErrorTime: null,
        consecutiveFailures: 0,
        lastError: null,
    };

    constructor(extensionUri: vscode.Uri, _context: vscode.ExtensionContext) {
        this._extensionUri = extensionUri;
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
            if (DEBUG) console.log('[RefactorAdvisor] Received message:', message.type, message);
            switch (message.type) {
                case 'startAnalysis':
                    if (DEBUG) console.log('[RefactorAdvisor] Starting analysis for:', message.filePath);
                    await this._startAnalysis(message.filePath);
                    break;
                case 'selectFinding':
                    await this._selectFinding(message.findingId);
                    break;
                case 'generateRefactor':
                    await this._generateRefactor(message.findingId);
                    break;
                case 'acceptChange':
                    await this._acceptChange(message.findingId);
                    break;
                case 'rejectChange':
                    await this._rejectChange(message.findingId);
                    break;
                case 'rollback':
                    await this._rollback(message.checkpointId);
                    break;
                case 'rollbackAll':
                    await this._rollbackAll();
                    break;
                case 'showFilePicker':
                    await this._showFilePicker();
                    break;
                case 'useActiveFile':
                    await this._useActiveFile();
                    break;
                case 'getSessionState':
                    this._sendSessionState();
                    this._sendHealthStatus();
                    break;
                case 'resetSession':
                    this._session = null;
                    break;
                case 'cancelAnalysis':
                    this._cancelAnalysis();
                    break;
            }
        });
        this._disposables.push(messageDisposable);
    }

    // =========================================================================
    // Analysis Methods
    // =========================================================================

    private _cancelAnalysis() {
        if (this._activeProcess) {
            this._activeProcess.kill();
            this._activeProcess = null;

            this._view?.webview.postMessage({
                type: 'analysisCancelled',
            });

            vscode.window.showInformationMessage('Analysis cancelled');
        }
    }

    private _recordBackendSuccess() {
        this._backendHealth.status = 'ok';
        this._backendHealth.lastSuccessTime = Date.now();
        this._backendHealth.consecutiveFailures = 0;
        this._backendHealth.lastError = null;
        this._sendHealthStatus();
    }

    private _recordBackendFailure(error: string) {
        this._backendHealth.lastErrorTime = Date.now();
        this._backendHealth.consecutiveFailures++;
        this._backendHealth.lastError = error;

        // Degraded after 2+ consecutive failures
        if (this._backendHealth.consecutiveFailures >= 2) {
            this._backendHealth.status = 'degraded';
        }
        this._sendHealthStatus();
    }

    private _sendHealthStatus() {
        this._view?.webview.postMessage({
            type: 'healthStatus',
            health: {
                status: this._backendHealth.status,
                lastSuccessTime: this._backendHealth.lastSuccessTime,
                consecutiveFailures: this._backendHealth.consecutiveFailures,
                lastError: this._backendHealth.lastError,
            },
        });
    }

    private async _preflightCheck(): Promise<{ ok: boolean; error?: string }> {
        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Check Python is available
        return new Promise((resolve) => {
            cp.execFile(pythonPath, ['--version'], { timeout: 5000 }, (error) => {
                if (error) {
                    resolve({ ok: false, error: `Python not found. Please install Python or configure 'empathy.pythonPath'. (${error.message})` });
                    return;
                }

                // Check for API key
                cp.execFile(pythonPath, ['-c', 'import os; k = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"); exit(0 if k else 1)'],
                    { timeout: 5000 }, (apiError) => {
                        if (apiError) {
                            resolve({ ok: false, error: 'No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.' });
                            return;
                        }
                        resolve({ ok: true });
                    }
                );
            });
        });
    }

    private async _startAnalysis(filePath: string) {
        if (DEBUG) console.log('[RefactorAdvisor] Starting analysis for:', filePath);

        // Pre-flight validation
        const preflight = await this._preflightCheck();
        if (!preflight.ok) {
            this._sendError(preflight.error || 'Pre-flight check failed');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            this._sendError('No workspace folder open');
            return;
        }

        // Resolve file path
        const fullPath = path.isAbsolute(filePath)
            ? filePath
            : path.join(workspaceFolder, filePath);

        if (DEBUG) console.log('[RefactorAdvisor] Full path:', fullPath);

        // Read file content
        let fileContent: string;

        try {
            const stats = fs.statSync(fullPath);

            if (stats.isDirectory()) {
                this._sendError('Please select a file, not a folder. Use the Browse button to navigate.');
                return;
            }

            fileContent = fs.readFileSync(fullPath, 'utf-8');
        } catch (err) {
            console.error('[RefactorAdvisor] Error reading file:', err);
            this._sendError(`Cannot read: ${filePath} - ${err}`);
            return;
        }

        // Initialize session
        this._session = {
            sessionId: generateUUID(),
            filePath: filePath,
            originalContent: fileContent,
            findings: [],
            checkpoints: [],
            userDecisions: new Map(),
            currentFindingIndex: 0,
        };

        // Send analyzing state
        this._view?.webview.postMessage({
            type: 'analyzing',
            filePath: filePath,
        });

        // Run analysis via Python
        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Use base64 encoding to avoid escaping issues
        const codeB64 = Buffer.from(fileContent).toString('base64');
        const filePathB64 = Buffer.from(filePath).toString('base64');

        const script = `
import json
import asyncio
import base64
import os
from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew, RefactoringConfig

async def analyze():
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
    provider = 'anthropic' if os.getenv('ANTHROPIC_API_KEY') else 'openai'

    if not api_key:
        print(json.dumps({
            "findings": [],
            "summary": "No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.",
            "duration": 0
        }))
        return

    config = RefactoringConfig(
        api_key=api_key,
        provider=provider,
        memory_graph_enabled=False,
        user_profile_enabled=True,
        user_profile_path=".empathy/refactor_profile.json"
    )
    crew = RefactoringCrew(config=config)

    code = base64.b64decode('${codeB64}').decode('utf-8')
    file_path = base64.b64decode('${filePathB64}').decode('utf-8')

    report = await crew.analyze(code, file_path)

    result = {
        "findings": [f.to_dict() for f in report.findings],
        "summary": report.summary,
        "duration": report.duration_seconds
    }
    print(json.dumps(result))

asyncio.run(analyze())
`;

        const args = ['-c', script];

        this._activeProcess = cp.execFile(pythonPath, args, {
            cwd: workspaceFolder,
            maxBuffer: 5 * 1024 * 1024,
            timeout: 120000
        }, (error, stdout, stderr) => {
            this._activeProcess = null;

            if (error) {
                // Check if killed (cancelled)
                if (error.killed) {
                    return; // Already handled by _cancelAnalysis
                }
                console.error('Analysis error:', stderr || error.message);
                this._recordBackendFailure(error.message);
                this._sendError(`Analysis failed: ${error.message}`);
                return;
            }

            try {
                const result = JSON.parse(stdout.trim());
                this._session!.findings = result.findings;

                // Initialize decisions
                for (const finding of result.findings) {
                    this._session!.userDecisions.set(finding.id, 'pending');
                }

                this._recordBackendSuccess();

                this._view?.webview.postMessage({
                    type: 'findings',
                    findings: result.findings,
                    summary: result.summary,
                    duration: result.duration,
                });
            } catch (parseErr) {
                console.error('Parse error:', stdout, parseErr);
                this._recordBackendFailure('Failed to parse analysis results');
                this._sendError('Failed to parse analysis results');
            }
        });
    }

    private async _selectFinding(findingId: string) {
        if (!this._session) return;

        const finding = this._session.findings.find(f => f.id === findingId);
        if (!finding) return;

        // Update current index
        this._session.currentFindingIndex = this._session.findings.indexOf(finding);

        // Send finding details to webview
        this._view?.webview.postMessage({
            type: 'findingSelected',
            finding: finding,
            decision: this._session.userDecisions.get(findingId) || 'pending',
        });

        // If no after_code yet, auto-generate
        if (!finding.after_code) {
            await this._generateRefactor(findingId);
        }
    }

    private async _generateRefactor(findingId: string) {
        if (!this._session) return;

        const finding = this._session.findings.find(f => f.id === findingId);
        if (!finding) return;

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) return;

        // Send generating state
        this._view?.webview.postMessage({
            type: 'generating',
            findingId: findingId,
        });

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Use base64 encoding to avoid escaping issues
        const findingJsonB64 = Buffer.from(JSON.stringify(finding)).toString('base64');
        const codeB64 = Buffer.from(this._session.originalContent).toString('base64');

        const script = `
import json
import asyncio
import base64
import os
from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew, RefactoringConfig, RefactoringFinding

async def generate():
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
    provider = 'anthropic' if os.getenv('ANTHROPIC_API_KEY') else 'openai'

    if not api_key:
        print(json.dumps({"after_code": "Error: No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY."}))
        return

    config = RefactoringConfig(
        api_key=api_key,
        provider=provider,
        memory_graph_enabled=False
    )
    crew = RefactoringCrew(config=config)

    finding_data = json.loads(base64.b64decode('${findingJsonB64}').decode('utf-8'))
    finding = RefactoringFinding.from_dict(finding_data)

    full_code = base64.b64decode('${codeB64}').decode('utf-8')

    updated = await crew.generate_refactor(finding, full_code)

    print(json.dumps({"after_code": updated.after_code}))

asyncio.run(generate())
`;

        const args = ['-c', script];

        cp.execFile(pythonPath, args, {
            cwd: workspaceFolder,
            maxBuffer: 5 * 1024 * 1024,
            timeout: 60000
        }, (error, stdout, stderr) => {
            if (error) {
                console.error('Generation error:', stderr || error.message);
                this._recordBackendFailure(error.message);
                this._view?.webview.postMessage({
                    type: 'generationError',
                    findingId: findingId,
                    error: error.message,
                });
                return;
            }

            try {
                const result = JSON.parse(stdout.trim());
                finding.after_code = result.after_code;

                this._recordBackendSuccess();

                this._view?.webview.postMessage({
                    type: 'refactorGenerated',
                    findingId: findingId,
                    after_code: result.after_code,
                });
            } catch (parseErr) {
                this._recordBackendFailure('Failed to parse generated code');
                this._view?.webview.postMessage({
                    type: 'generationError',
                    findingId: findingId,
                    error: 'Failed to parse generated code',
                });
            }
        });
    }

    // =========================================================================
    // Apply/Reject/Rollback Methods
    // =========================================================================

    private async _acceptChange(findingId: string) {
        if (!this._session) return;

        const finding = this._session.findings.find(f => f.id === findingId);
        if (!finding || !finding.after_code) {
            this._sendError('No refactored code available');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) return;

        const fullPath = path.join(workspaceFolder, this._session.filePath);

        // Create checkpoint before applying
        let currentContent: string;
        try {
            currentContent = fs.readFileSync(fullPath, 'utf-8');
        } catch (err) {
            this._sendError('Cannot read file for checkpoint');
            return;
        }

        const checkpoint: CodeCheckpoint = {
            id: generateUUID(),
            file_path: this._session.filePath,
            original_content: currentContent,
            timestamp: new Date().toISOString(),
            finding_id: findingId,
        };
        this._session.checkpoints.push(checkpoint);

        // Apply the change by replacing the before_code with after_code
        const newContent = currentContent.replace(finding.before_code, finding.after_code);

        try {
            fs.writeFileSync(fullPath, newContent, 'utf-8');
            this._session.userDecisions.set(findingId, 'accepted');

            // Update stored content
            this._session.originalContent = newContent;

            this._view?.webview.postMessage({
                type: 'changeApplied',
                findingId: findingId,
                checkpointId: checkpoint.id,
            });

            // Record decision to user profile
            this._recordDecision(findingId, true);

        } catch (err) {
            this._sendError(`Failed to apply change: ${err}`);
            // Remove checkpoint since we didn't apply
            this._session.checkpoints.pop();
        }
    }

    private async _rejectChange(findingId: string) {
        if (!this._session) return;

        this._session.userDecisions.set(findingId, 'rejected');

        this._view?.webview.postMessage({
            type: 'changeRejected',
            findingId: findingId,
        });

        // Record decision to user profile
        this._recordDecision(findingId, false);
    }

    private async _rollback(checkpointId: string) {
        if (!this._session) return;

        const checkpointIndex = this._session.checkpoints.findIndex(c => c.id === checkpointId);
        if (checkpointIndex === -1) {
            this._sendError('Checkpoint not found');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) return;

        // Rollback this and all subsequent checkpoints (in reverse order)
        for (let i = this._session.checkpoints.length - 1; i >= checkpointIndex; i--) {
            const cp = this._session.checkpoints[i];
            const fullPath = path.join(workspaceFolder, cp.file_path);

            try {
                fs.writeFileSync(fullPath, cp.original_content, 'utf-8');
                this._session.userDecisions.set(cp.finding_id, 'pending');
            } catch (err) {
                this._sendError(`Failed to rollback: ${err}`);
                return;
            }
        }

        // Update stored content
        const targetCheckpoint = this._session.checkpoints[checkpointIndex];
        this._session.originalContent = targetCheckpoint.original_content;

        // Remove rolled-back checkpoints
        this._session.checkpoints = this._session.checkpoints.slice(0, checkpointIndex);

        this._view?.webview.postMessage({
            type: 'rolledBack',
            checkpointId: checkpointId,
            remainingCheckpoints: this._session.checkpoints.length,
        });
    }

    private async _rollbackAll() {
        if (!this._session || this._session.checkpoints.length === 0) return;

        // Rollback to first checkpoint
        await this._rollback(this._session.checkpoints[0].id);
    }

    private _recordDecision(findingId: string, accepted: boolean) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder || !this._session) return;

        const finding = this._session.findings.find(f => f.id === findingId);
        if (!finding) return;

        // Run Python to update user profile
        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Use base64 encoding to avoid escaping issues (consistent with other methods)
        const findingB64 = Buffer.from(JSON.stringify(finding)).toString('base64');

        const script = `
import json
import base64
from empathy_llm_toolkit.agent_factory.crews import RefactoringCrew, RefactoringFinding

finding_data = json.loads(base64.b64decode('${findingB64}').decode('utf-8'))
finding = RefactoringFinding.from_dict(finding_data)

crew = RefactoringCrew(
    memory_graph_enabled=False,
    user_profile_enabled=True,
    user_profile_path=".empathy/refactor_profile.json"
)
crew._user_profile = crew._load_user_profile()
crew.record_decision(finding, ${accepted ? 'True' : 'False'})
`;

        cp.execFile(pythonPath, ['-c', script], {
            cwd: workspaceFolder,
            timeout: 5000
        }, (error) => {
            if (error) {
                console.error('Failed to record decision:', error);
            }
        });
    }

    // =========================================================================
    // File Selection Methods
    // =========================================================================

    private async _showFilePicker() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri;

        const result = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            defaultUri: workspaceFolder,
            title: 'Select file to analyze',
            openLabel: 'Analyze',
            filters: {
                'Python': ['py'],
                'TypeScript': ['ts', 'tsx'],
                'JavaScript': ['js', 'jsx'],
                'All Files': ['*']
            }
        });

        if (result && result[0]) {
            const relativePath = vscode.workspace.asRelativePath(result[0]);
            this._view?.webview.postMessage({
                type: 'fileSelected',
                path: relativePath,
            });
        }
    }


    private async _useActiveFile() {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            this._sendError('No active file');
            return;
        }

        const relativePath = vscode.workspace.asRelativePath(activeEditor.document.uri);
        this._view?.webview.postMessage({
            type: 'fileSelected',
            path: relativePath,
        });
    }

    // =========================================================================
    // Helper Methods
    // =========================================================================

    private _sendError(message: string) {
        vscode.window.showErrorMessage(message);
        this._view?.webview.postMessage({
            type: 'error',
            message: message,
        });
    }

    private _sendSessionState() {
        if (!this._session) {
            this._view?.webview.postMessage({
                type: 'sessionState',
                session: null,
            });
            return;
        }

        const decisions: Record<string, string> = {};
        this._session.userDecisions.forEach((v, k) => {
            decisions[k] = v;
        });

        this._view?.webview.postMessage({
            type: 'sessionState',
            session: {
                sessionId: this._session.sessionId,
                filePath: this._session.filePath,
                findingsCount: this._session.findings.length,
                checkpointsCount: this._session.checkpoints.length,
                decisions: decisions,
            },
        });
    }

    public refresh() {
        this._sendSessionState();
    }

    // =========================================================================
    // Webview HTML
    // =========================================================================

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Refactor Advisor</title>
    <style>
        :root {
            --bg: var(--vscode-sideBar-background);
            --fg: var(--vscode-sideBar-foreground);
            --border: var(--vscode-panel-border);
            --button-bg: var(--vscode-button-background);
            --button-fg: var(--vscode-button-foreground);
            --input-bg: var(--vscode-input-background);
            --input-fg: var(--vscode-input-foreground);
            --success: var(--vscode-testing-iconPassed);
            --error: var(--vscode-testing-iconFailed);
            --warning: var(--vscode-editorWarning-foreground);
            --info: var(--vscode-editorInfo-foreground);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: var(--vscode-font-family);
            font-size: 12px;
            color: var(--fg);
            background: var(--bg);
            padding: 12px;
            height: 100vh;
            overflow-y: auto;
        }

        h2 {
            font-size: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .section {
            margin-bottom: 16px;
        }

        .card {
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 8px;
        }

        .button {
            background: var(--button-bg);
            color: var(--button-fg);
            border: none;
            padding: 6px 12px;
            border-radius: 2px;
            cursor: pointer;
            font-size: 11px;
        }

        .button:hover { opacity: 0.9; }
        .button:disabled { opacity: 0.5; cursor: not-allowed; }

        .button-secondary {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--fg);
        }

        .button-success { background: var(--success); }
        .button-danger { background: var(--error); }

        .button-row {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }

        .input-group {
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
        }

        .input {
            flex: 1;
            padding: 6px 8px;
            background: var(--input-bg);
            border: 1px solid var(--border);
            color: var(--input-fg);
            border-radius: 2px;
            font-size: 11px;
        }

        /* Finding List */
        .findings-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .finding-item {
            padding: 8px;
            border: 1px solid var(--border);
            border-radius: 4px;
            margin-bottom: 6px;
            cursor: pointer;
        }

        .finding-item:hover { background: var(--input-bg); }
        .finding-item.selected { border-color: var(--button-bg); }
        .finding-item.accepted { border-left: 3px solid var(--success); }
        .finding-item.rejected { border-left: 3px solid var(--error); opacity: 0.6; }

        .finding-title {
            font-weight: bold;
            margin-bottom: 4px;
        }

        .finding-meta {
            font-size: 10px;
            opacity: 0.8;
        }

        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 9px;
            font-weight: bold;
            text-transform: uppercase;
        }

        .badge-high { background: var(--error); color: white; }
        .badge-medium { background: var(--warning); color: black; }
        .badge-low { background: var(--info); color: white; }

        /* Diff View */
        .diff-container {
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            overflow: hidden;
        }

        .diff-header {
            padding: 8px;
            border-bottom: 1px solid var(--border);
            font-weight: bold;
        }

        .diff-content {
            display: flex;
        }

        .diff-pane {
            flex: 1;
            padding: 8px;
            overflow-x: auto;
        }

        .diff-pane pre {
            margin: 0;
            font-family: var(--vscode-editor-font-family);
            font-size: 11px;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .diff-before { border-right: 1px solid var(--border); }

        /* Syntax Highlighting */
        .diff-pane pre { color: var(--fg); }
        .diff-pane .keyword { color: #c586c0; }
        .diff-pane .builtin { color: #4ec9b0; }
        .diff-pane .string { color: #ce9178; }
        .diff-pane .comment { color: #6a9955; font-style: italic; }
        .diff-pane .number { color: #b5cea8; }
        .diff-pane .function { color: #dcdcaa; }
        .diff-pane .decorator { color: #d7ba7d; }
        .diff-pane .operator { color: #d4d4d4; }

        .diff-before .line-marker { color: var(--error); }
        .diff-after .line-marker { color: var(--success); }

        /* Status Messages */
        .status {
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 8px;
            text-align: center;
        }

        .status-info { background: rgba(0, 120, 212, 0.2); }
        .status-success { background: rgba(0, 128, 0, 0.2); }
        .status-error { background: rgba(255, 0, 0, 0.2); }

        .spinner {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid var(--fg);
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Summary Stats */
        .stats {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }

        .stat {
            text-align: center;
        }

        .stat-value {
            font-size: 18px;
            font-weight: bold;
        }

        .stat-label {
            font-size: 10px;
            opacity: 0.8;
        }

        .hidden { display: none !important; }

        /* Health Indicator */
        .health-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 10px;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        .health-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }
        .health-ok { background: rgba(0, 128, 0, 0.15); }
        .health-ok .health-dot { background: var(--success); }
        .health-degraded { background: rgba(255, 165, 0, 0.15); }
        .health-degraded .health-dot { background: var(--warning); }
        .health-unknown { background: rgba(128, 128, 128, 0.15); }
        .health-unknown .health-dot { background: #888; }
    </style>
</head>
<body>
    <!-- Health Indicator -->
    <div id="health-indicator" class="health-indicator health-unknown">
        <span class="health-dot"></span>
        <span id="health-text">Backend: Checking...</span>
    </div>

    <!-- File Selection -->
    <div id="file-selection" class="section">
        <h2>Refactor Advisor</h2>
        <div class="card">
            <p style="margin-bottom: 8px;">Select a file to analyze for refactoring opportunities.</p>
            <div class="input-group">
                <input type="text" id="file-path" class="input" placeholder="Path to file..." readonly>
            </div>
            <div class="button-row">
                <button class="button button-secondary" id="btn-browse">Browse...</button>
                <button class="button button-secondary" id="btn-active">Active File</button>
                <button class="button" id="btn-analyze" disabled>Analyze</button>
            </div>
        </div>
    </div>

    <!-- Analyzing Status -->
    <div id="analyzing-status" class="section hidden">
        <div class="status status-info">
            <span class="spinner"></span>
            Analyzing <span id="analyzing-file">file</span>...
        </div>
        <div class="button-row" style="justify-content: center; margin-top: 8px;">
            <button class="button button-danger" id="btn-cancel">Cancel</button>
        </div>
    </div>

    <!-- Findings Section -->
    <div id="findings-section" class="section hidden">
        <!-- Summary Stats -->
        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-label">Findings</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-accepted">0</div>
                <div class="stat-label">Accepted</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-rejected">0</div>
                <div class="stat-label">Rejected</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-pending">0</div>
                <div class="stat-label">Pending</div>
            </div>
        </div>

        <!-- Findings List -->
        <h2>Findings</h2>
        <div id="findings-list" class="findings-list"></div>

        <!-- Rollback -->
        <div class="button-row" id="rollback-row" style="display: none;">
            <button class="button button-danger" id="btn-rollback-all">Rollback All Changes</button>
        </div>

        <!-- New Analysis -->
        <div class="button-row" style="margin-top: 12px;">
            <button class="button button-secondary" id="btn-new-analysis">New Analysis</button>
        </div>
    </div>

    <!-- Finding Detail -->
    <div id="finding-detail" class="section hidden">
        <h2>
            <span id="detail-title">Finding</span>
            <span id="detail-badge" class="badge"></span>
        </h2>
        <div class="card">
            <p id="detail-description"></p>
            <p style="margin-top: 8px; font-size: 10px; opacity: 0.8;">
                <strong>Category:</strong> <span id="detail-category"></span> |
                <strong>Lines:</strong> <span id="detail-lines"></span> |
                <strong>Confidence:</strong> <span id="detail-confidence"></span>
            </p>
        </div>

        <!-- Generating Status -->
        <div id="generating-status" class="status status-info hidden">
            <span class="spinner"></span> Generating refactored code...
        </div>

        <!-- Diff View -->
        <div id="diff-view" class="diff-container hidden">
            <div class="diff-header">Code Changes</div>
            <div class="diff-content">
                <div class="diff-pane diff-before">
                    <strong>Before:</strong>
                    <pre id="diff-before-code"></pre>
                </div>
                <div class="diff-pane diff-after">
                    <strong>After:</strong>
                    <pre id="diff-after-code"></pre>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="button-row" id="action-buttons">
            <button class="button button-success" id="btn-accept">Accept</button>
            <button class="button button-danger" id="btn-reject">Reject</button>
            <button class="button button-secondary" id="btn-back">Back to List</button>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        const DEBUG = false; // Set to true to enable debug logging

        // State
        let currentFilePath = '';
        let findings = [];
        let selectedFindingId = null;
        let decisions = {};

        // DOM Elements
        const filePathInput = document.getElementById('file-path');
        const btnBrowse = document.getElementById('btn-browse');
        const btnActive = document.getElementById('btn-active');
        const btnAnalyze = document.getElementById('btn-analyze');
        const fileSelectionSection = document.getElementById('file-selection');
        const analyzingStatus = document.getElementById('analyzing-status');
        const analyzingFile = document.getElementById('analyzing-file');
        const findingsSection = document.getElementById('findings-section');
        const findingsList = document.getElementById('findings-list');
        const findingDetail = document.getElementById('finding-detail');
        const rollbackRow = document.getElementById('rollback-row');

        // Event Listeners
        btnBrowse.addEventListener('click', () => {
            vscode.postMessage({ type: 'showFilePicker' });
        });

        btnActive.addEventListener('click', () => {
            vscode.postMessage({ type: 'useActiveFile' });
        });

        btnAnalyze.addEventListener('click', () => {
            if (DEBUG) console.log('[RefactorAdvisor WebView] Analyze clicked, currentFilePath:', currentFilePath);
            if (currentFilePath) {
                if (DEBUG) console.log('[RefactorAdvisor WebView] Sending startAnalysis message');
                vscode.postMessage({ type: 'startAnalysis', filePath: currentFilePath });
            } else {
                if (DEBUG) console.log('[RefactorAdvisor WebView] No file path set');
            }
        });

        document.getElementById('btn-cancel').addEventListener('click', () => {
            vscode.postMessage({ type: 'cancelAnalysis' });
        });

        document.getElementById('btn-accept').addEventListener('click', () => {
            if (selectedFindingId) {
                vscode.postMessage({ type: 'acceptChange', findingId: selectedFindingId });
            }
        });

        document.getElementById('btn-reject').addEventListener('click', () => {
            if (selectedFindingId) {
                vscode.postMessage({ type: 'rejectChange', findingId: selectedFindingId });
            }
        });

        document.getElementById('btn-new-analysis').addEventListener('click', () => {
            // Reset state
            currentFilePath = '';
            findings = [];
            selectedFindingId = null;
            decisions = {};

            // Reset UI
            filePathInput.value = '';
            btnAnalyze.disabled = true;
            findingsList.innerHTML = '';
            rollbackRow.style.display = 'none';

            // Show file selection, hide other sections
            fileSelectionSection.classList.remove('hidden');
            findingsSection.classList.add('hidden');
            findingDetail.classList.add('hidden');
            analyzingStatus.classList.add('hidden');

            // Tell backend to reset session
            vscode.postMessage({ type: 'resetSession' });
        });

        document.getElementById('btn-back').addEventListener('click', () => {
            showFindingsList();
        });

        document.getElementById('btn-rollback-all').addEventListener('click', () => {
            vscode.postMessage({ type: 'rollbackAll' });
        });

        // Message Handler
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'fileSelected':
                    if (DEBUG) console.log('[RefactorAdvisor WebView] File selected:', message.path);
                    currentFilePath = message.path;
                    filePathInput.value = message.path;
                    btnAnalyze.disabled = false;
                    if (DEBUG) console.log('[RefactorAdvisor WebView] Analyze button enabled');
                    break;

                case 'analyzing':
                    analyzingFile.textContent = message.filePath;
                    fileSelectionSection.classList.add('hidden');
                    analyzingStatus.classList.remove('hidden');
                    findingsSection.classList.add('hidden');
                    findingDetail.classList.add('hidden');
                    break;

                case 'analysisCancelled':
                    analyzingStatus.classList.add('hidden');
                    fileSelectionSection.classList.remove('hidden');
                    break;

                case 'findings':
                    findings = message.findings;
                    decisions = {};
                    findings.forEach(f => decisions[f.id] = 'pending');
                    analyzingStatus.classList.add('hidden');
                    renderFindings();
                    findingsSection.classList.remove('hidden');
                    break;

                case 'findingSelected':
                    showFindingDetail(message.finding, message.decision);
                    break;

                case 'generating':
                    document.getElementById('generating-status').classList.remove('hidden');
                    document.getElementById('diff-view').classList.add('hidden');
                    break;

                case 'refactorGenerated':
                    document.getElementById('generating-status').classList.add('hidden');
                    const finding = findings.find(f => f.id === message.findingId);
                    if (finding) {
                        finding.after_code = message.after_code;
                        showDiff(finding);
                    }
                    break;

                case 'generationError':
                    document.getElementById('generating-status').classList.add('hidden');
                    // Show error in diff view
                    document.getElementById('diff-view').classList.remove('hidden');
                    document.getElementById('diff-after-code').textContent = 'Error: ' + message.error;
                    break;

                case 'changeApplied':
                    decisions[message.findingId] = 'accepted';
                    updateStats();
                    renderFindings();
                    rollbackRow.style.display = 'flex';
                    showFindingsList();
                    break;

                case 'changeRejected':
                    decisions[message.findingId] = 'rejected';
                    updateStats();
                    renderFindings();
                    showFindingsList();
                    break;

                case 'rolledBack':
                    // Reset decisions for rolled-back findings
                    Object.keys(decisions).forEach(id => {
                        if (decisions[id] === 'accepted') {
                            decisions[id] = 'pending';
                        }
                    });
                    if (message.remainingCheckpoints === 0) {
                        rollbackRow.style.display = 'none';
                    }
                    updateStats();
                    renderFindings();
                    break;

                case 'error':
                    // Show error notification
                    console.error(message.message);
                    break;

                case 'healthStatus':
                    updateHealthIndicator(message.health);
                    break;
            }
        });

        // Health indicator update
        function updateHealthIndicator(health) {
            const indicator = document.getElementById('health-indicator');
            const text = document.getElementById('health-text');

            // Remove old classes
            indicator.classList.remove('health-ok', 'health-degraded', 'health-unknown');

            if (health.status === 'ok') {
                indicator.classList.add('health-ok');
                const ago = health.lastSuccessTime ? formatTimeAgo(health.lastSuccessTime) : '';
                text.textContent = 'Backend: OK' + (ago ? ' (' + ago + ')' : '');
            } else if (health.status === 'degraded') {
                indicator.classList.add('health-degraded');
                text.textContent = 'Backend: Degraded (' + health.consecutiveFailures + ' failures)';
            } else {
                indicator.classList.add('health-unknown');
                text.textContent = 'Backend: Unknown';
            }
        }

        function formatTimeAgo(timestamp) {
            const seconds = Math.floor((Date.now() - timestamp) / 1000);
            if (seconds < 60) return 'just now';
            if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
            return Math.floor(seconds / 3600) + 'h ago';
        }

        // Render Functions
        function renderFindings() {
            findingsList.innerHTML = '';

            findings.forEach(finding => {
                const item = document.createElement('div');
                item.className = 'finding-item';
                if (decisions[finding.id] === 'accepted') item.classList.add('accepted');
                if (decisions[finding.id] === 'rejected') item.classList.add('rejected');

                const impactBadge = finding.estimated_impact === 'high' ? 'badge-high' :
                                   finding.estimated_impact === 'medium' ? 'badge-medium' : 'badge-low';

                item.innerHTML = \`
                    <div class="finding-title">\${finding.title}</div>
                    <div class="finding-meta">
                        <span class="badge \${impactBadge}">\${finding.estimated_impact}</span>
                        \${finding.category} | Lines \${finding.start_line}-\${finding.end_line}
                    </div>
                \`;

                item.addEventListener('click', () => {
                    selectedFindingId = finding.id;
                    vscode.postMessage({ type: 'selectFinding', findingId: finding.id });
                });

                findingsList.appendChild(item);
            });

            updateStats();
        }

        function showFindingDetail(finding, decision) {
            findingsSection.classList.add('hidden');
            findingDetail.classList.remove('hidden');

            document.getElementById('detail-title').textContent = finding.title;
            document.getElementById('detail-description').textContent = finding.description;
            document.getElementById('detail-category').textContent = finding.category;
            document.getElementById('detail-lines').textContent = finding.start_line + '-' + finding.end_line;
            document.getElementById('detail-confidence').textContent = Math.round(finding.confidence * 100) + '%';

            const badge = document.getElementById('detail-badge');
            badge.textContent = finding.estimated_impact;
            badge.className = 'badge ' + (finding.estimated_impact === 'high' ? 'badge-high' :
                                         finding.estimated_impact === 'medium' ? 'badge-medium' : 'badge-low');

            // Show or hide action buttons based on decision
            const actionBtns = document.getElementById('action-buttons');
            if (decision === 'accepted' || decision === 'rejected') {
                document.getElementById('btn-accept').disabled = true;
                document.getElementById('btn-reject').disabled = true;
            } else {
                document.getElementById('btn-accept').disabled = false;
                document.getElementById('btn-reject').disabled = false;
            }

            if (finding.after_code) {
                showDiff(finding);
            } else {
                document.getElementById('diff-view').classList.add('hidden');
            }
        }

        // Syntax highlighter for Python/JS/TS code
        function highlightCode(code, marker) {
            if (!code) return marker === '-' ? '(no code)' : '(generating...)';

            // Escape HTML first
            let escaped = code
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');

            // Python/JS keywords
            const kwPattern = /\\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|async|await|yield|lambda|pass|break|continue|raise|in|is|not|and|or|True|False|None|function|const|let|var|export|default|interface|type|enum|extends|implements|new|this|super|static|public|private|throw|catch)\\b/g;

            // Built-in types/functions
            const biPattern = /\\b(str|int|float|bool|list|dict|set|tuple|len|range|print|open|self|typeof|console|Promise|Array|Object|String|Number|Boolean)\\b/g;

            // Apply highlighting (order matters)
            escaped = escaped
                // Comments (# or //)
                .replace(/(#[^\\n]*)/g, '<span class="comment">$1</span>')
                // Decorators (@something)
                .replace(/(@\\w+)/g, '<span class="decorator">$1</span>')
                // Strings (single and double quotes only)
                .replace(/('[^'\\n]*'|"[^"\\n]*")/g, '<span class="string">$1</span>')
                // Numbers
                .replace(/\\b(\\d+\\.?\\d*)\\b/g, '<span class="number">$1</span>')
                // Keywords
                .replace(kwPattern, '<span class="keyword">$1</span>')
                // Built-ins
                .replace(biPattern, '<span class="builtin">$1</span>')
                // Function calls (word followed by paren)
                .replace(/\\b([a-zA-Z_]\\w*)(\\s*\\()/g, '<span class="function">$1</span>$2');

            // Add line markers
            const lines = escaped.split('\\n');
            return lines.map(function(line) {
                return '<span class="line-marker">' + marker + '</span> ' + line;
            }).join('\\n');
        }

        function showDiff(finding) {
            document.getElementById('diff-view').classList.remove('hidden');
            document.getElementById('diff-before-code').innerHTML = highlightCode(finding.before_code, '-');
            document.getElementById('diff-after-code').innerHTML = highlightCode(finding.after_code, '+');
        }

        function showFindingsList() {
            findingDetail.classList.add('hidden');
            findingsSection.classList.remove('hidden');
            selectedFindingId = null;
        }

        function updateStats() {
            const total = findings.length;
            const accepted = Object.values(decisions).filter(d => d === 'accepted').length;
            const rejected = Object.values(decisions).filter(d => d === 'rejected').length;
            const pending = total - accepted - rejected;

            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-accepted').textContent = accepted;
            document.getElementById('stat-rejected').textContent = rejected;
            document.getElementById('stat-pending').textContent = pending;
        }

        // Request initial state
        vscode.postMessage({ type: 'getSessionState' });
    </script>
</body>
</html>`;
    }
}
