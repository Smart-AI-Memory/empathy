/**
 * Telemetry Panel - Real-time LLM usage monitoring
 *
 * Displays comprehensive telemetry analytics including:
 * - Overview stats (total cost, calls, success rate)
 * - Activity feed (recent LLM calls with filtering)
 * - Cost charts (line, pie, bar)
 * - Top expensive workflows list
 * - Export to CSV functionality
 *
 * **Implementation:** Sprint 1 (Week 1)
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export class TelemetryPanel {
    public static currentPanel: TelemetryPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'refresh':
                        await this._update();
                        break;
                    case 'exportCSV':
                        await this._exportToCSV();
                        break;
                    case 'openFile':
                        if (message.filePath) {
                            await this._openFile(message.filePath, message.line);
                        }
                        break;
                }
            },
            null,
            this._disposables
        );

        // Auto-refresh data every 60 seconds
        const refreshInterval = setInterval(() => this._update(), 60000);
        this._disposables.push({ dispose: () => clearInterval(refreshInterval) });
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (TelemetryPanel.currentPanel) {
            TelemetryPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyTelemetryPanel',
            '📊 LLM Telemetry',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        TelemetryPanel.currentPanel = new TelemetryPanel(panel, extensionUri);
    }

    public dispose() {
        TelemetryPanel.currentPanel = undefined;

        // Clean up resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private async _update() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            this._panel.webview.html = this._getNoWorkspaceHtml();
            return;
        }

        const data = await this._loadTelemetryData(workspaceFolder);
        this._panel.webview.html = this._getHtmlForWebview(data);
    }

    private async _loadTelemetryData(workspaceFolder: string): Promise<TelemetryStats> {
        const empathyDir = path.join(workspaceFolder, '.empathy');
        const callsFile = path.join(empathyDir, 'llm_calls.jsonl');
        const workflowsFile = path.join(empathyDir, 'workflow_runs.jsonl');

        const stats: TelemetryStats = {
            totalCost: 0,
            totalCalls: 0,
            totalWorkflows: 0,
            successRate: 0,
            avgLatencyMs: 0,
            totalTokens: 0,
            recentCalls: [],
            topWorkflows: [],
            providerBreakdown: [],
            tierBreakdown: [],
        };

        // Load LLM calls
        if (fs.existsSync(callsFile)) {
            const calls = this._parseLLMCalls(callsFile);
            stats.totalCalls = calls.length;

            if (calls.length > 0) {
                stats.totalCost = calls.reduce((sum, c) => sum + c.estimatedCost, 0);
                const successfulCalls = calls.filter((c) => c.success).length;
                stats.successRate = successfulCalls / calls.length;
                const totalLatency = calls.reduce((sum, c) => sum + c.latencyMs, 0);
                stats.avgLatencyMs = totalLatency / calls.length;
                stats.totalTokens = calls.reduce(
                    (sum, c) => sum + c.inputTokens + c.outputTokens,
                    0
                );
                stats.recentCalls = calls.slice(-50).reverse();

                // Provider breakdown
                const providerMap = new Map<string, ProviderStats>();
                for (const call of calls) {
                    const existing = providerMap.get(call.provider) || {
                        provider: call.provider,
                        callCount: 0,
                        totalCost: 0,
                        avgCost: 0,
                        errorCount: 0,
                        successRate: 0,
                    };
                    existing.callCount += 1;
                    existing.totalCost += call.estimatedCost;
                    if (!call.success) {
                        existing.errorCount += 1;
                    }
                    providerMap.set(call.provider, existing);
                }
                stats.providerBreakdown = Array.from(providerMap.values()).map((p) => ({
                    ...p,
                    avgCost: p.callCount > 0 ? p.totalCost / p.callCount : 0,
                    successRate:
                        p.callCount > 0 ? (p.callCount - p.errorCount) / p.callCount : 0,
                }));

                // Tier breakdown
                const tierMap = new Map<string, { count: number; cost: number }>();
                for (const call of calls) {
                    const existing = tierMap.get(call.tier) || { count: 0, cost: 0 };
                    existing.count += 1;
                    existing.cost += call.estimatedCost;
                    tierMap.set(call.tier, existing);
                }
                stats.tierBreakdown = Array.from(tierMap.entries()).map(([tier, s]) => ({
                    tier,
                    count: s.count,
                    cost: s.cost,
                    percent: (s.count / calls.length) * 100,
                }));
            }
        }

        // Load workflow runs
        if (fs.existsSync(workflowsFile)) {
            const workflows = this._parseWorkflowRuns(workflowsFile);
            stats.totalWorkflows = workflows.length;

            // Top workflows by cost
            const workflowMap = new Map<string, WorkflowSummary>();
            for (const wf of workflows) {
                const existing = workflowMap.get(wf.workflowName) || {
                    workflowName: wf.workflowName,
                    totalCost: 0,
                    runCount: 0,
                    avgCost: 0,
                    totalSavings: 0,
                };
                existing.totalCost += wf.totalCost;
                existing.runCount += 1;
                existing.totalSavings += wf.savings;
                workflowMap.set(wf.workflowName, existing);
            }
            stats.topWorkflows = Array.from(workflowMap.values())
                .map((w) => ({
                    ...w,
                    avgCost: w.runCount > 0 ? w.totalCost / w.runCount : 0,
                }))
                .sort((a, b) => b.totalCost - a.totalCost)
                .slice(0, 10);
        }

        return stats;
    }

    private _parseLLMCalls(filePath: string): LLMCallRecord[] {
        const records: LLMCallRecord[] = [];
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content.split('\n');

        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const record = JSON.parse(line) as LLMCallRecord;
                records.push(record);
            } catch {
                // Skip malformed lines
            }
        }

        return records;
    }

    private _parseWorkflowRuns(filePath: string): WorkflowRunRecord[] {
        const records: WorkflowRunRecord[] = [];
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content.split('\n');

        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const record = JSON.parse(line) as WorkflowRunRecord;
                records.push(record);
            } catch {
                // Skip malformed lines
            }
        }

        return records;
    }

    private async _exportToCSV() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        const callsFile = path.join(workspaceFolder, '.empathy', 'llm_calls.jsonl');
        if (!fs.existsSync(callsFile)) {
            vscode.window.showWarningMessage('No telemetry data to export');
            return;
        }

        const calls = this._parseLLMCalls(callsFile);
        const csv = this._convertToCSV(calls);

        const saveUri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(path.join(workspaceFolder, 'telemetry_export.csv')),
            filters: { 'CSV Files': ['csv'] },
        });

        if (saveUri) {
            fs.writeFileSync(saveUri.fsPath, csv);
            vscode.window.showInformationMessage(`Exported ${calls.length} records to CSV`);
        }
    }

    private _convertToCSV(calls: LLMCallRecord[]): string {
        const headers = [
            'timestamp',
            'workflow_name',
            'provider',
            'tier',
            'model_id',
            'input_tokens',
            'output_tokens',
            'cost',
            'latency_ms',
            'success',
            'fallback_used',
        ];

        const rows = calls.map((c) => [
            c.timestamp,
            c.workflowName || '',
            c.provider,
            c.tier,
            c.modelId,
            c.inputTokens,
            c.outputTokens,
            c.estimatedCost.toFixed(6),
            c.latencyMs,
            c.success,
            c.fallbackUsed,
        ]);

        return [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    }

    private async _openFile(filePath: string, line?: number) {
        try {
            const doc = await vscode.workspace.openTextDocument(filePath);
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

    private _getNoWorkspaceHtml(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Telemetry</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            padding: 40px;
            text-align: center;
        }
        h1 { color: var(--vscode-foreground); }
        p { color: var(--vscode-descriptionForeground); }
    </style>
</head>
<body>
    <h1>📊 LLM Telemetry</h1>
    <p>Open a workspace folder to view telemetry data</p>
</body>
</html>`;
    }

    private _getHtmlForWebview(data: TelemetryStats): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Telemetry</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            margin: 0;
            padding: 24px;
            line-height: 1.6;
        }
        .header {
            border-bottom: 2px solid var(--vscode-input-border);
            padding-bottom: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 { margin: 0; font-size: 28px; }
        .actions {
            display: flex;
            gap: 8px;
        }
        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .stat-card {
            background: var(--vscode-textCodeBlock-background);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--vscode-input-border);
        }
        .stat-title {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
            text-transform: uppercase;
            font-weight: 500;
        }
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .stat-subtitle {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        .section {
            margin-bottom: 32px;
        }
        .section h2 {
            font-size: 18px;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--vscode-input-border);
            padding-bottom: 8px;
        }
        .call-item {
            background: var(--vscode-textCodeBlock-background);
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            border-left: 3px solid var(--vscode-input-border);
        }
        .call-item.tier-cheap { border-left-color: #73c991; }
        .call-item.tier-capable { border-left-color: #4a9eff; }
        .call-item.tier-premium { border-left-color: #b57edc; }
        .call-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }
        .call-meta {
            display: flex;
            gap: 16px;
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
            margin-right: 8px;
        }
        .badge.tier-cheap { background: rgba(115, 201, 145, 0.2); color: #73c991; }
        .badge.tier-capable { background: rgba(74, 158, 255, 0.2); color: #4a9eff; }
        .badge.tier-premium { background: rgba(181, 126, 220, 0.2); color: #b57edc; }
        .badge.fallback { background: rgba(255, 165, 0, 0.2); color: #ffa500; }
        .badge.failed { background: rgba(241, 76, 76, 0.2); color: #f14c4c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 LLM Telemetry Dashboard</h1>
        <div class="actions">
            <button onclick="exportCSV()">📥 Export CSV</button>
            <button onclick="refresh()">🔄 Refresh</button>
        </div>
    </div>

    <div class="overview-grid">
        <div class="stat-card">
            <div class="stat-title">Total Cost</div>
            <div class="stat-value">$${data.totalCost.toFixed(2)}</div>
            <div class="stat-subtitle">All-time LLM spend</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Total Calls</div>
            <div class="stat-value">${data.totalCalls.toLocaleString()}</div>
            <div class="stat-subtitle">API calls</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Success Rate</div>
            <div class="stat-value">${(data.successRate * 100).toFixed(1)}%</div>
            <div class="stat-subtitle">Call success rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Avg Latency</div>
            <div class="stat-value">${data.avgLatencyMs.toFixed(0)}ms</div>
            <div class="stat-subtitle">Response time</div>
        </div>
    </div>

    <div class="section">
        <h2>Recent Activity</h2>
        ${
            data.recentCalls.length === 0
                ? '<p style="color: var(--vscode-descriptionForeground);">No activity yet. Run a workflow to see LLM calls appear here.</p>'
                : data.recentCalls
                      .slice(0, 20)
                      .map(
                          (call) => `
            <div class="call-item tier-${call.tier}">
                <div class="call-header">
                    <div>
                        <span class="badge tier-${call.tier}">${call.tier.toUpperCase()}</span>
                        ${call.fallbackUsed ? '<span class="badge fallback">FALLBACK</span>' : ''}
                        ${!call.success ? '<span class="badge failed">FAILED</span>' : ''}
                        <strong>${call.provider}/${call.modelId}</strong>
                        ${call.workflowName ? `<span style="color: var(--vscode-descriptionForeground);"> → ${call.workflowName}</span>` : ''}
                    </div>
                    <div>
                        <strong>$${call.estimatedCost.toFixed(4)}</strong>
                        <span style="margin-left: 12px; color: var(--vscode-descriptionForeground);">${call.latencyMs}ms</span>
                    </div>
                </div>
                <div class="call-meta">
                    <span>Input: ${call.inputTokens.toLocaleString()} tokens</span>
                    <span>Output: ${call.outputTokens.toLocaleString()} tokens</span>
                    <span>${this._formatTimestamp(call.timestamp)}</span>
                </div>
            </div>
        `
                      )
                      .join('')
        }
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }
        function exportCSV() {
            vscode.postMessage({ type: 'exportCSV' });
        }
    </script>
</body>
</html>`;
    }

    private _formatTimestamp(timestamp: string): string {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffSec < 60) return `${diffSec}s ago`;
        if (diffMin < 60) return `${diffMin}m ago`;
        if (diffHour < 24) return `${diffHour}h ago`;
        if (diffDay < 7) return `${diffDay}d ago`;

        return date.toLocaleDateString();
    }
}

// Types
interface TelemetryStats {
    totalCost: number;
    totalCalls: number;
    totalWorkflows: number;
    successRate: number;
    avgLatencyMs: number;
    totalTokens: number;
    recentCalls: LLMCallRecord[];
    topWorkflows: WorkflowSummary[];
    providerBreakdown: ProviderStats[];
    tierBreakdown: TierStats[];
}

interface LLMCallRecord {
    callId: string;
    timestamp: string;
    workflowName: string | null;
    provider: string;
    tier: string;
    modelId: string;
    inputTokens: number;
    outputTokens: number;
    estimatedCost: number;
    latencyMs: number;
    success: boolean;
    fallbackUsed: boolean;
}

interface WorkflowRunRecord {
    workflowName: string;
    totalCost: number;
    savings: number;
}

interface WorkflowSummary {
    workflowName: string;
    totalCost: number;
    runCount: number;
    avgCost: number;
    totalSavings: number;
}

interface ProviderStats {
    provider: string;
    callCount: number;
    totalCost: number;
    avgCost: number;
    errorCount: number;
    successRate: number;
}

interface TierStats {
    tier: string;
    count: number;
    cost: number;
    percent: number;
}
