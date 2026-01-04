/**
 * Workflow History Panel - Dedicated webview for workflow execution tracking
 *
 * Displays comprehensive workflow execution history including:
 * - Execution statistics (total runs, success rate, costs, savings)
 * - 24-hour execution timeline
 * - Cost breakdown by workflow type
 * - Recent runs with XML-enhanced details
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { getWorkflowDataService, WorkflowDataService } from '../services/WorkflowDataService';

export class WorkflowHistoryPanel {
    public static currentPanel: WorkflowHistoryPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private readonly _workflowDataService: WorkflowDataService;

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._workflowDataService = getWorkflowDataService();

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'refresh':
                        await this._updateData(true);
                        break;
                    case 'openDashboard':
                        vscode.commands.executeCommand('empathy.dashboard');
                        break;
                }
            },
            null,
            this._disposables
        );

        // Auto-refresh data every 30 seconds
        const refreshInterval = setInterval(() => this._updateData(false), 30000);
        this._disposables.push({ dispose: () => clearInterval(refreshInterval) });
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (WorkflowHistoryPanel.currentPanel) {
            WorkflowHistoryPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyWorkflowHistoryPanel',
            'Workflow History',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        WorkflowHistoryPanel.currentPanel = new WorkflowHistoryPanel(panel, extensionUri);
    }

    public dispose() {
        WorkflowHistoryPanel.currentPanel = undefined;

        // Clean up resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private async _updateData(force: boolean) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

        // Load workflow data from service
        const workflows = await this._workflowDataService.getWorkflowData(empathyDir, force);

        // Send to webview
        this._panel.webview.postMessage({
            type: 'workflowData',
            data: workflows
        });
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Workflow History';
        this._panel.webview.html = this._getHtmlForWebview(webview);
        this._updateData(false);
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Workflow History</title>
    <style>
        :root {
            --bg: var(--vscode-editor-background);
            --fg: var(--vscode-editor-foreground);
            --border: var(--vscode-panel-border);
            --button-bg: var(--vscode-button-background);
            --button-fg: var(--vscode-button-foreground);
            --button-hover: var(--vscode-button-hoverBackground);
            --success: var(--vscode-testing-iconPassed);
            --error: var(--vscode-testing-iconFailed);
            --warning: var(--vscode-editorWarning-foreground);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--fg);
            background: var(--bg);
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }

        .header-actions {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            background: var(--button-bg);
            color: var(--button-fg);
        }

        .btn:hover {
            background: var(--button-hover);
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 15px;
        }

        .metric {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }

        .metric-value {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 4px;
        }

        .metric-value.success {
            color: var(--success);
        }

        .metric-label {
            font-size: 10px;
            opacity: 0.7;
        }

        .card {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 15px;
        }

        .card-title {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 10px;
            opacity: 0.9;
        }

        .list-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            border-bottom: 1px solid var(--border);
            transition: background 0.2s;
        }

        .list-item:last-child {
            border-bottom: none;
        }

        .list-item:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .list-item-icon {
            font-size: 14px;
            width: 20px;
            text-align: center;
        }

        .list-item-content {
            flex: 1;
        }

        .list-item-title {
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 2px;
        }

        .list-item-desc {
            font-size: 10px;
            opacity: 0.7;
        }

        .badge {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
        }

        .badge.success {
            background: var(--success);
            color: var(--bg);
        }

        .badge.error {
            background: var(--error);
            color: var(--bg);
        }

        .xml-badge {
            background: #a855f7;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 9px;
            font-weight: 600;
            margin-left: 6px;
        }

        .xml-summary {
            margin-top: 6px;
            padding: 6px;
            background: var(--vscode-input-background);
            border-radius: 3px;
            font-size: 11px;
            opacity: 0.9;
        }

        .findings-list {
            margin-top: 6px;
        }

        .finding-item {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px;
            margin-bottom: 2px;
            font-size: 10px;
        }

        .severity-badge {
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 8px;
            font-weight: 600;
        }

        .severity-badge.high {
            background: var(--error);
            color: white;
        }

        .severity-badge.medium {
            background: var(--warning);
            color: var(--bg);
        }

        .severity-badge.low {
            background: var(--vscode-charts-blue);
            color: white;
        }

        .finding-title {
            flex: 1;
        }

        .checklist-list {
            margin-top: 6px;
        }

        .checklist-item {
            padding: 2px 0;
            font-size: 10px;
            opacity: 0.8;
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            opacity: 0.6;
        }

        .empty-state .icon {
            font-size: 48px;
            display: block;
            margin-bottom: 12px;
        }

        .empty-state p {
            margin-bottom: 4px;
        }

        .empty-state .hint {
            font-size: 11px;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Workflow History</h1>
        <div class="header-actions">
            <button class="btn" onclick="openDashboard()">Dashboard</button>
            <button class="btn" onclick="refresh()">Refresh</button>
        </div>
    </div>

    <!-- Workflow Stats -->
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

    <!-- Execution Timeline (last 24h) -->
    <div class="card">
        <div class="card-title">Execution Timeline (24h)</div>
        <div id="workflow-timeline" style="display: flex; align-items: flex-end; gap: 2px; height: 60px; padding: 8px 0;">
            <div style="text-align: center; opacity: 0.5; width: 100%;">No recent activity</div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 9px; opacity: 0.6; margin-top: 4px;">
            <span>24h ago</span>
            <span>Now</span>
        </div>
    </div>

    <!-- Workflow Cost Comparison -->
    <div class="card">
        <div class="card-title">Cost by Workflow Type</div>
        <div id="workflow-cost-bars" style="display: flex; flex-direction: column; gap: 6px;">
            <div style="text-align: center; opacity: 0.5; padding: 8px;">No workflow data</div>
        </div>
    </div>

    <!-- Recent Runs -->
    <div class="card">
        <div class="card-title">Recent Runs</div>
        <div id="workflows-list">
            <div class="empty-state">No workflow runs yet</div>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'workflowData':
                    updateWorkflows(message.data);
                    break;
            }
        });

        function renderWorkflowTimeline(recentRuns) {
            const container = document.getElementById('workflow-timeline');

            if (!recentRuns || recentRuns.length === 0) {
                container.innerHTML = '<div style="text-align: center; opacity: 0.5; width: 100%;">No recent activity</div>';
                return;
            }

            // Group runs by hour buckets (last 24 hours = 24 slots)
            const now = new Date();
            const buckets = new Array(24).fill(null).map(() => ({ success: 0, failed: 0 }));

            for (const run of recentRuns) {
                if (!run.timestamp) continue;
                const runTime = new Date(run.timestamp);
                const hoursAgo = Math.floor((now - runTime) / 3600000);
                if (hoursAgo >= 0 && hoursAgo < 24) {
                    const bucketIdx = 23 - hoursAgo; // 0 = oldest, 23 = most recent
                    if (run.success) {
                        buckets[bucketIdx].success++;
                    } else {
                        buckets[bucketIdx].failed++;
                    }
                }
            }

            const maxCount = Math.max(...buckets.map(b => b.success + b.failed), 1);

            const barsHtml = buckets.map((bucket) => {
                const total = bucket.success + bucket.failed;
                if (total === 0) {
                    return '<div style="flex: 1; height: 100%; display: flex; align-items: flex-end;">' +
                        '<div style="width: 100%; height: 2px; background: var(--vscode-input-background); border-radius: 1px;"></div>' +
                    '</div>';
                }
                const height = Math.max((total / maxCount) * 100, 8);
                const successPct = (bucket.success / total) * 100;
                const color = bucket.failed > 0 ? 'linear-gradient(to top, var(--vscode-testing-iconFailed) ' + (100 - successPct) + '%, var(--vscode-testing-iconPassed) ' + (100 - successPct) + '%)' : 'var(--vscode-testing-iconPassed)';
                return '<div style="flex: 1; height: 100%; display: flex; align-items: flex-end;" title="' + total + ' run(s)">' +
                    '<div style="width: 100%; height: ' + height + '%; background: ' + color + '; border-radius: 2px; min-height: 4px;"></div>' +
                '</div>';
            }).join('');

            container.innerHTML = barsHtml;
        }

        function renderWorkflowCostBars(byWorkflow) {
            const container = document.getElementById('workflow-cost-bars');

            if (!byWorkflow || Object.keys(byWorkflow).length === 0) {
                container.innerHTML = '<div style="text-align: center; opacity: 0.5; padding: 8px;">No workflow data</div>';
                return;
            }

            const entries = Object.entries(byWorkflow).sort((a, b) => b[1].cost - a[1].cost);
            const maxCost = Math.max(...entries.map(([_, v]) => v.cost), 0.01);

            const workflowColors = {
                'security-audit': '#ef4444',
                'code-review': '#3b82f6',
                'bug-predict': '#f59e0b',
                'perf-audit': '#8b5cf6',
                'test-gen': '#22c55e',
                'doc-orchestrator': '#06b6d4',
                'refactor-plan': '#ec4899',
                'release-prep': '#6366f1'
            };

            container.innerHTML = entries.slice(0, 6).map(([workflow, data]) => {
                const width = Math.max((data.cost / maxCost) * 100, 5);
                const color = workflowColors[workflow] || '#888';
                const shortName = workflow.replace('-audit', '').replace('-gen', '').replace('-', ' ');
                return '<div style="display: flex; align-items: center; gap: 8px; font-size: 10px;">' +
                    '<div style="width: 70px; text-transform: capitalize; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="' + workflow + '">' + shortName + '</div>' +
                    '<div style="flex: 1; height: 14px; background: var(--vscode-input-background); border-radius: 2px; overflow: hidden;">' +
                        '<div style="width: ' + width + '%; height: 100%; background: ' + color + '; border-radius: 2px;"></div>' +
                    '</div>' +
                    '<div style="width: 50px; text-align: right;">$' + data.cost.toFixed(3) + '</div>' +
                '</div>';
            }).join('');
        }

        function updateWorkflows(workflows) {
            // Guard against null workflows data
            if (!workflows) {
                document.getElementById('wf-runs').textContent = '0';
                document.getElementById('wf-success').textContent = '0%';
                document.getElementById('wf-cost').textContent = '$0.00';
                document.getElementById('wf-savings').textContent = '$0.00';
                renderWorkflowTimeline([]);
                renderWorkflowCostBars({});
                return;
            }

            document.getElementById('wf-runs').textContent = workflows.totalRuns || 0;
            document.getElementById('wf-success').textContent = workflows.totalRuns > 0 ? Math.round((workflows.successfulRuns / workflows.totalRuns) * 100) + '%' : '0%';
            document.getElementById('wf-cost').textContent = '$' + workflows.totalCost.toFixed(4);
            document.getElementById('wf-savings').textContent = '$' + workflows.totalSavings.toFixed(4);

            // Render charts
            renderWorkflowTimeline(workflows.recentRuns);
            renderWorkflowCostBars(workflows.byWorkflow);

            const list = document.getElementById('workflows-list');

            // Check for empty state
            if (!workflows.recentRuns || workflows.recentRuns.length === 0) {
                list.innerHTML = \`
                    <div class="empty-state">
                        <span class="icon">&#x1F4E6;</span>
                        <p>No workflow runs yet</p>
                        <p class="hint">Run workflows to see execution history</p>
                    </div>
                \`;
                return;
            }

            list.innerHTML = workflows.recentRuns.slice(0, 10).map(run => {
                // Build XML summary section if available
                let xmlSection = '';
                if (run.xml_parsed && run.summary) {
                    xmlSection = \`<div class="xml-summary">\${run.summary}</div>\`;
                }
                // Build findings section if available
                let findingsSection = '';
                if (run.xml_parsed && run.findings && run.findings.length > 0) {
                    const findingsHtml = run.findings.slice(0, 3).map(f => \`
                        <div class="finding-item \${f.severity}">
                            <span class="severity-badge \${f.severity}">\${f.severity.toUpperCase()}</span>
                            <span class="finding-title">\${f.title}</span>
                        </div>
                    \`).join('');
                    findingsSection = \`<div class="findings-list">\${findingsHtml}</div>\`;
                }
                // Build checklist section if available
                let checklistSection = '';
                if (run.xml_parsed && run.checklist && run.checklist.length > 0) {
                    const checklistHtml = run.checklist.slice(0, 3).map(item => \`
                        <div class="checklist-item">&#x25A1; \${item}</div>
                    \`).join('');
                    checklistSection = \`<div class="checklist-list">\${checklistHtml}</div>\`;
                }

                return \`
                <div class="list-item \${run.xml_parsed ? 'xml-enhanced' : ''}">
                    <span class="list-item-icon">\${run.success ? '&#x2714;' : '&#x2718;'}</span>
                    <div class="list-item-content">
                        <div class="list-item-title">\${run.workflow}\${run.xml_parsed ? ' <span class="xml-badge">XML</span>' : ''}</div>
                        <div class="list-item-desc">Saved $\${run.savings.toFixed(4)}</div>
                        \${xmlSection}
                        \${findingsSection}
                        \${checklistSection}
                    </div>
                    <span class="badge \${run.success ? 'success' : 'error'}">\${run.success ? 'OK' : 'Failed'}</span>
                </div>
            \`;
            }).join('');
        }

        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }

        function openDashboard() {
            vscode.postMessage({ type: 'openDashboard' });
        }
    </script>
</body>
</html>`;
    }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
