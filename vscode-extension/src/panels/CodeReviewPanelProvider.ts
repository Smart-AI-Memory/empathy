/**
 * Code Review Panel for VSCode Extension
 *
 * Displays interactive code review findings with filtering, grouping,
 * and navigation capabilities.
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import { WorkflowFinding, CodeReviewResult } from '../types/WorkflowContracts';
import { CostEstimator } from '../services/CostEstimator';

// =============================================================================
// Types
// =============================================================================

interface ReviewSession {
    findings: WorkflowFinding[];
    summary: {
        total_findings: number;
        by_severity: Record<string, number>;
        by_category: Record<string, number>;
        files_affected: string[];
    };
    verdict?: 'approve' | 'approve_with_suggestions' | 'request_changes' | 'reject';
    security_score?: number;
    model_tier_used?: string;
    filters: {
        severities: string[];
        categories: string[];
        searchText: string;
    };
    groupBy: 'file' | 'severity' | 'category';
}

// =============================================================================
// Panel Implementation
// =============================================================================

export class CodeReviewPanelProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'empathy-code-review';

    private static _instance: CodeReviewPanelProvider;

    private _view?: vscode.WebviewView;
    private _extensionUri: vscode.Uri;
    private _session: ReviewSession = {
        findings: [],
        summary: {
            total_findings: 0,
            by_severity: {},
            by_category: {},
            files_affected: [],
        },
        filters: {
            severities: [],
            categories: [],
            searchText: '',
        },
        groupBy: 'file',
    };
    private _disposables: vscode.Disposable[] = [];

    private constructor(extensionUri: vscode.Uri) {
        this._extensionUri = extensionUri;
    }

    public static getInstance(extensionUri?: vscode.Uri): CodeReviewPanelProvider {
        if (!CodeReviewPanelProvider._instance && extensionUri) {
            CodeReviewPanelProvider._instance = new CodeReviewPanelProvider(extensionUri);
        }
        return CodeReviewPanelProvider._instance;
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

        webviewView.webview.html = this._getHtmlContent();

        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'review:goToLocation':
                    await vscode.commands.executeCommand('empathy.goToLocation', {
                        file: message.file,
                        line: message.line,
                        column: message.column ?? 1,
                    });
                    break;

                case 'review:filter':
                    this._session.filters = message.filters;
                    this._sendSessionState();
                    break;

                case 'review:groupBy':
                    this._session.groupBy = message.groupBy;
                    this._sendSessionState();
                    break;

                case 'review:clearFilters':
                    this._session.filters = {
                        severities: [],
                        categories: [],
                        searchText: '',
                    };
                    this._sendSessionState();
                    break;

                case 'getSessionState':
                    this._sendSessionState();
                    break;

                case 'workflow:suggest':
                    await this._handleWorkflowSuggestion(message);
                    break;

                case 'review:runCodeReview':
                    await this._handleRunCodeReview();
                    break;
            }
        });
    }

    /**
     * Update findings from workflow result
     */
    public updateFindings(result: CodeReviewResult) {
        this._session.findings = result.findings || [];
        this._session.summary = result.summary || {
            total_findings: 0,
            by_severity: {},
            by_category: {},
            files_affected: [],
        };
        this._session.verdict = result.verdict;
        this._session.security_score = result.security_score;
        this._session.model_tier_used = result.model_tier_used;

        // Reset filters when new results arrive
        this._session.filters = {
            severities: [],
            categories: [],
            searchText: '',
        };

        this._sendSessionState();
    }

    private _sendSessionState() {
        this._view?.webview.postMessage({
            type: 'sessionState',
            session: this._session,
        });
    }

    /**
     * Handle workflow suggestion from webview
     */
    private async _handleWorkflowSuggestion(message: any) {
        const { workflowName, targetFile, estimatedCost } = message;

        // Show confirmation dialog with cost estimate
        const selection = await vscode.window.showInformationMessage(
            `Run ${workflowName} on ${targetFile}?\n\nEstimated cost: ${CostEstimator.formatCost(estimatedCost)}`,
            { modal: true },
            'Run Workflow',
            'Cancel'
        );

        if (selection === 'Run Workflow') {
            // Execute the suggested workflow
            await vscode.commands.executeCommand('empathy.runWorkflow', workflowName, targetFile);

            // TODO: Record suggestion acceptance for pattern learning (Phase 2C)
        }
    }

    /**
     * Handle run code review request from webview
     */
    private async _handleRunCodeReview() {
        // Launch the code review workflow via the quick workflow command
        await vscode.commands.executeCommand('empathy.runWorkflowQuick', 'code-review');
    }

    // =========================================================================
    // HTML Content
    // =========================================================================

    private _getHtmlContent(): string {
        const nonce = this._getNonce();

        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <style>
        :root {
            --bg: var(--vscode-editor-background);
            --fg: var(--vscode-editor-foreground);
            --border: var(--vscode-panel-border);
            --button-bg: var(--vscode-button-background);
            --button-fg: var(--vscode-button-foreground);
            --input-bg: var(--vscode-input-background);
            --input-fg: var(--vscode-input-foreground);
            --input-border: var(--vscode-input-border);
            --critical: #d32f2f;
            --high: #f57c00;
            --medium: #fbc02d;
            --low: #689f38;
            --info: #1976d2;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--fg);
            background: var(--bg);
            padding: 12px;
            margin: 0;
        }

        h2 {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 12px 0;
        }

        h3 {
            font-size: 13px;
            font-weight: 600;
            margin: 12px 0 8px 0;
        }

        .header {
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
        }

        .header-left {
            flex: 1;
        }

        .header-right {
            display: flex;
            align-items: center;
        }

        .btn-primary {
            background: var(--button-bg);
            color: var(--button-fg);
        }

        .summary-stats {
            display: flex;
            gap: 12px;
            margin: 8px 0;
            flex-wrap: wrap;
        }

        .stat {
            font-size: 11px;
            padding: 4px 8px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 4px;
        }

        .stat-label {
            opacity: 0.7;
            margin-right: 4px;
        }

        .stat-value {
            font-weight: 600;
        }

        .filters {
            margin-bottom: 12px;
            padding: 8px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 6px;
        }

        .filter-row {
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
            align-items: center;
        }

        .filter-group {
            flex: 1;
        }

        .filter-label {
            font-size: 11px;
            opacity: 0.7;
            margin-bottom: 4px;
        }

        .checkbox-group {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .checkbox-label {
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        input[type="checkbox"] {
            cursor: pointer;
        }

        input[type="text"] {
            width: 100%;
            padding: 6px 8px;
            border: 1px solid var(--input-border);
            border-radius: 4px;
            background: var(--input-bg);
            color: var(--input-fg);
            font-size: 12px;
        }

        .btn {
            background: var(--button-bg);
            color: var(--button-fg);
            border: none;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }

        .btn:hover {
            opacity: 0.9;
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--fg);
        }

        .group-by {
            display: flex;
            gap: 4px;
            margin-bottom: 12px;
        }

        .group-by .btn {
            flex: 1;
        }

        .group-by .btn.active {
            background: var(--vscode-button-hoverBackground);
        }

        .findings-container {
            max-height: calc(100vh - 300px);
            overflow-y: auto;
        }

        .file-group, .severity-group, .category-group {
            margin-bottom: 16px;
        }

        .group-header {
            font-size: 12px;
            font-weight: 600;
            padding: 6px 8px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 4px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .group-count {
            font-size: 11px;
            opacity: 0.7;
        }

        .finding-item {
            padding: 8px;
            background: var(--input-bg);
            border-left: 3px solid var(--border);
            border-radius: 4px;
            margin-bottom: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .finding-item:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .finding-item.critical {
            border-left-color: var(--critical);
        }

        .finding-item.high {
            border-left-color: var(--high);
        }

        .finding-item.medium {
            border-left-color: var(--medium);
        }

        .finding-item.low {
            border-left-color: var(--low);
        }

        .finding-item.info {
            border-left-color: var(--info);
        }

        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }

        .finding-badges {
            display: flex;
            gap: 6px;
        }

        .severity-badge, .category-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .severity-badge.critical {
            background: var(--critical);
            color: white;
        }

        .severity-badge.high {
            background: var(--high);
            color: white;
        }

        .severity-badge.medium {
            background: var(--medium);
            color: black;
        }

        .severity-badge.low {
            background: var(--low);
            color: white;
        }

        .severity-badge.info {
            background: var(--info);
            color: white;
        }

        .category-badge {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
        }

        .finding-location {
            font-size: 10px;
            opacity: 0.7;
            font-family: monospace;
        }

        .finding-message {
            font-size: 12px;
            margin: 6px 0;
        }

        .finding-details {
            font-size: 11px;
            opacity: 0.8;
            margin-top: 4px;
            padding-top: 4px;
            border-top: 1px solid var(--border);
        }

        .empty-state {
            text-align: center;
            padding: 32px 16px;
            opacity: 0.6;
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 12px;
        }

        .empty-state-text {
            font-size: 13px;
            margin-bottom: 16px;
        }

        .empty-state-actions {
            margin-top: 16px;
        }

        .empty-state-actions .btn {
            opacity: 1;
        }

        .verdict {
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 12px;
            font-size: 12px;
            font-weight: 600;
        }

        .verdict.approve {
            background: #4caf5020;
            color: #4caf50;
        }

        .verdict.approve_with_suggestions {
            background: #2196f320;
            color: #2196f3;
        }

        .verdict.request_changes {
            background: #ff980020;
            color: #ff9800;
        }

        .verdict.reject {
            background: #f4433620;
            color: #f44336;
        }

        .suggested-actions {
            margin-top: 8px;
            padding: 8px;
            background: var(--vscode-editor-background);
            border-top: 1px solid var(--border);
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .action-btn {
            background: var(--button-bg);
            color: var(--button-fg);
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: opacity 0.2s;
        }

        .action-btn:hover {
            opacity: 0.9;
        }

        .cost-badge {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div class="header-left">
                <h2>Code Review Results</h2>
                <div class="summary-stats" id="summaryStats">
                    <div class="stat">
                        <span class="stat-label">Total:</span>
                        <span class="stat-value">0</span>
                    </div>
                </div>
            </div>
            <div class="header-right">
                <button class="btn btn-primary" onclick="runCodeReview()">▶️ Run Code Review</button>
            </div>
        </div>

        <div class="filters" id="filters" style="display: none;">
            <div class="filter-row">
                <div class="filter-group">
                    <div class="filter-label">Search</div>
                    <input type="text" id="searchInput" placeholder="Filter by message..." />
                </div>
            </div>
            <div class="filter-row">
                <div class="filter-group">
                    <div class="filter-label">Severity</div>
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" name="severity" value="critical" />
                            Critical
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="severity" value="high" />
                            High
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="severity" value="medium" />
                            Medium
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="severity" value="low" />
                            Low
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="severity" value="info" />
                            Info
                        </label>
                    </div>
                </div>
            </div>
            <div class="filter-row">
                <div class="filter-group">
                    <div class="filter-label">Category</div>
                    <div class="checkbox-group" id="categoryFilters">
                        <!-- Populated dynamically -->
                    </div>
                </div>
            </div>
            <div class="filter-row">
                <button class="btn btn-secondary" onclick="clearFilters()">Clear Filters</button>
            </div>
        </div>

        <div class="group-by" id="groupByButtons">
            <button class="btn active" data-group="file" onclick="setGroupBy('file')">By File</button>
            <button class="btn" data-group="severity" onclick="setGroupBy('severity')">By Severity</button>
            <button class="btn" data-group="category" onclick="setGroupBy('category')">By Category</button>
        </div>

        <div id="verdict"></div>

        <div class="findings-container" id="findingsContainer">
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">No code review results yet.<br/>Run a code review to see findings here.</div>
                <div class="empty-state-actions">
                    <button class="btn" onclick="runCodeReview()">▶️ Run Code Review</button>
                </div>
            </div>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        let currentSession = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            console.log('[CodeReviewPanel] Initializing...');
            setupEventListeners();
            vscode.postMessage({ type: 'getSessionState' });
        });

        function setupEventListeners() {
            // Search input
            document.getElementById('searchInput').addEventListener('input', (e) => {
                updateFilters();
            });

            // Severity checkboxes
            document.querySelectorAll('input[name="severity"]').forEach(cb => {
                cb.addEventListener('change', updateFilters);
            });
        }

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'sessionState':
                    currentSession = message.session;
                    renderSession();
                    break;
            }
        });

        function renderSession() {
            if (!currentSession) return;

            // Render verdict
            renderVerdict();

            // Render summary stats
            renderSummaryStats();

            // Show/hide filters
            const filtersEl = document.getElementById('filters');
            filtersEl.style.display = currentSession.findings.length > 0 ? 'block' : 'none';

            // Update category filters dynamically
            updateCategoryFilters();

            // Render findings
            renderFindings();

            // Update group-by buttons
            document.querySelectorAll('.group-by .btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.group === currentSession.groupBy);
            });
        }

        function renderVerdict() {
            const verdictEl = document.getElementById('verdict');
            if (!currentSession.verdict) {
                verdictEl.innerHTML = '';
                return;
            }

            const verdictText = {
                'approve': '✅ Approved',
                'approve_with_suggestions': '✅ Approved with Suggestions',
                'request_changes': '⚠️ Changes Requested',
                'reject': '❌ Rejected'
            }[currentSession.verdict] || '';

            verdictEl.innerHTML = \`<div class="verdict \${currentSession.verdict}">\${verdictText}</div>\`;
        }

        function renderSummaryStats() {
            const stats = currentSession.summary;
            const statsEl = document.getElementById('summaryStats');

            const severityOrder = ['critical', 'high', 'medium', 'low', 'info'];
            const severityStats = severityOrder
                .filter(sev => stats.by_severity[sev] > 0)
                .map(sev => \`
                    <div class="stat">
                        <span class="stat-label">\${capitalize(sev)}:</span>
                        <span class="stat-value">\${stats.by_severity[sev]}</span>
                    </div>
                \`)
                .join('');

            statsEl.innerHTML = \`
                <div class="stat">
                    <span class="stat-label">Total:</span>
                    <span class="stat-value">\${stats.total_findings}</span>
                </div>
                \${severityStats}
                <div class="stat">
                    <span class="stat-label">Files:</span>
                    <span class="stat-value">\${stats.files_affected.length}</span>
                </div>
            \`;

            if (currentSession.security_score !== undefined) {
                statsEl.innerHTML += \`
                    <div class="stat">
                        <span class="stat-label">Security Score:</span>
                        <span class="stat-value">\${currentSession.security_score}</span>
                    </div>
                \`;
            }
        }

        function updateCategoryFilters() {
            const categories = Object.keys(currentSession.summary.by_category);
            const container = document.getElementById('categoryFilters');

            container.innerHTML = categories.map(cat => \`
                <label class="checkbox-label">
                    <input type="checkbox" name="category" value="\${cat}" />
                    \${capitalize(cat)}
                </label>
            \`).join('');

            // Add event listeners to new checkboxes
            container.querySelectorAll('input[name="category"]').forEach(cb => {
                cb.addEventListener('change', updateFilters);
            });
        }

        function renderFindings() {
            const container = document.getElementById('findingsContainer');

            if (currentSession.findings.length === 0) {
                container.innerHTML = \`
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <div class="empty-state-text">No code review results yet.<br/>Run a code review workflow to see findings here.</div>
                    </div>
                \`;
                return;
            }

            // Apply filters
            let filteredFindings = applyFilters(currentSession.findings);

            if (filteredFindings.length === 0) {
                container.innerHTML = \`
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <div class="empty-state-text">No findings match current filters.</div>
                    </div>
                \`;
                return;
            }

            // Group findings
            const groups = groupFindings(filteredFindings, currentSession.groupBy);

            // Render groups
            container.innerHTML = Object.entries(groups).map(([groupKey, findings]) => {
                // Generate suggested actions for file groups
                const suggestedActions = currentSession.groupBy === 'file'
                    ? renderSuggestedActions(groupKey, findings)
                    : '';

                return \`
                    <div class="\${currentSession.groupBy}-group">
                        <div class="group-header">
                            <span>\${groupKey}</span>
                            <span class="group-count">\${findings.length} finding\${findings.length !== 1 ? 's' : ''}</span>
                        </div>
                        \${suggestedActions}
                        \${findings.map(renderFinding).join('')}
                    </div>
                \`;
            }).join('');
        }

        function renderFinding(finding) {
            return \`
                <div class="finding-item \${finding.severity}"
                     onclick="goToLocation('\${finding.file}', \${finding.line}, \${finding.column || 1})">
                    <div class="finding-header">
                        <div class="finding-location">\${finding.file}:\${finding.line}\${finding.column ? ':' + finding.column : ''}</div>
                        <div class="finding-badges">
                            <span class="severity-badge \${finding.severity}">\${finding.severity}</span>
                            <span class="category-badge">\${finding.category}</span>
                        </div>
                    </div>
                    <div class="finding-message">\${escapeHtml(finding.message)}</div>
                    \${finding.details || finding.recommendation ? \`
                        <div class="finding-details">
                            \${finding.details ? \`<div><strong>Details:</strong> \${escapeHtml(finding.details)}</div>\` : ''}
                            \${finding.recommendation ? \`<div><strong>Fix:</strong> \${escapeHtml(finding.recommendation)}</div>\` : ''}
                        </div>
                    \` : ''}
                </div>
            \`;
        }

        function applyFilters(findings) {
            const filters = currentSession.filters;

            return findings.filter(finding => {
                // Severity filter
                if (filters.severities.length > 0 && !filters.severities.includes(finding.severity)) {
                    return false;
                }

                // Category filter
                if (filters.categories.length > 0 && !filters.categories.includes(finding.category)) {
                    return false;
                }

                // Search text filter
                if (filters.searchText) {
                    const searchLower = filters.searchText.toLowerCase();
                    const matchesSearch =
                        finding.message.toLowerCase().includes(searchLower) ||
                        (finding.details && finding.details.toLowerCase().includes(searchLower)) ||
                        (finding.recommendation && finding.recommendation.toLowerCase().includes(searchLower)) ||
                        finding.file.toLowerCase().includes(searchLower);

                    if (!matchesSearch) {
                        return false;
                    }
                }

                return true;
            });
        }

        function groupFindings(findings, groupBy) {
            const groups = {};

            findings.forEach(finding => {
                let key;
                switch (groupBy) {
                    case 'file':
                        key = finding.file;
                        break;
                    case 'severity':
                        key = capitalize(finding.severity);
                        break;
                    case 'category':
                        key = capitalize(finding.category);
                        break;
                    default:
                        key = 'Other';
                }

                if (!groups[key]) {
                    groups[key] = [];
                }
                groups[key].push(finding);
            });

            // Sort groups
            if (groupBy === 'severity') {
                const severityOrder = ['Critical', 'High', 'Medium', 'Low', 'Info'];
                return Object.fromEntries(
                    severityOrder
                        .filter(key => groups[key])
                        .map(key => [key, groups[key]])
                );
            }

            return groups;
        }

        function updateFilters() {
            const severities = Array.from(document.querySelectorAll('input[name="severity"]:checked'))
                .map(cb => cb.value);

            const categories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
                .map(cb => cb.value);

            const searchText = document.getElementById('searchInput').value;

            vscode.postMessage({
                type: 'review:filter',
                filters: {
                    severities,
                    categories,
                    searchText
                }
            });
        }

        function clearFilters() {
            document.querySelectorAll('input[name="severity"]').forEach(cb => cb.checked = false);
            document.querySelectorAll('input[name="category"]').forEach(cb => cb.checked = false);
            document.getElementById('searchInput').value = '';

            vscode.postMessage({ type: 'review:clearFilters' });
        }

        function setGroupBy(groupBy) {
            vscode.postMessage({
                type: 'review:groupBy',
                groupBy
            });
        }

        function goToLocation(file, line, column) {
            vscode.postMessage({
                type: 'review:goToLocation',
                file,
                line,
                column
            });
        }

        function runCodeReview() {
            vscode.postMessage({
                type: 'review:runCodeReview'
            });
        }

        function renderSuggestedActions(file, findings) {
            // Check if we should show actions for this file
            const highSeverityCount = findings.filter(f =>
                f.severity === 'critical' || f.severity === 'high'
            ).length;

            // Only show actions if there are 3+ high/critical findings
            if (highSeverityCount < 3) {
                return '';
            }

            // Estimate file size (rough estimate: 100 chars per finding as proxy)
            const estimatedFileSize = findings.length * 100;

            // Calculate costs for suggested workflows
            const refactorCost = estimateWorkflowCost('refactor-plan', estimatedFileSize);
            const testCost = estimateWorkflowCost('test-gen', estimatedFileSize);

            return \`
                <div class="suggested-actions">
                    <button class="action-btn" onclick="suggestWorkflow('refactor-plan', '\${file}', \${refactorCost})">
                        🔧 Plan Refactor
                        <span class="cost-badge">\${formatCost(refactorCost)}</span>
                    </button>
                    <button class="action-btn" onclick="suggestWorkflow('test-gen', '\${file}', \${testCost})">
                        🧪 Generate Tests
                        <span class="cost-badge">\${formatCost(testCost)}</span>
                    </button>
                </div>
            \`;
        }

        function estimateWorkflowCost(workflowName, fileSize) {
            // Cost estimation tiers (per 1K tokens)
            const tierCosts = {
                'refactor-plan': { input: 0.003, output: 0.015 },  // capable tier
                'test-gen': { input: 0.003, output: 0.015 }         // capable tier
            };

            const costs = tierCosts[workflowName] || { input: 0.003, output: 0.015 };

            // Convert chars to tokens (1 char ≈ 0.25 tokens)
            const inputTokens = Math.ceil(fileSize * 0.25);
            const outputTokens = Math.ceil(inputTokens * 0.3);

            // Calculate cost
            const inputCost = (inputTokens / 1000) * costs.input;
            const outputCost = (outputTokens / 1000) * costs.output;
            const totalCost = inputCost + outputCost;

            // Round to nearest cent
            return Math.ceil(totalCost * 100) / 100;
        }

        function formatCost(cost) {
            if (cost < 0.01) {
                return '<$0.01';
            }
            return '$' + cost.toFixed(2);
        }

        function suggestWorkflow(workflowName, targetFile, estimatedCost) {
            vscode.postMessage({
                type: 'workflow:suggest',
                workflowName,
                targetFile,
                estimatedCost
            });
        }

        function capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>`;
    }

    private _getNonce(): string {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }
}
