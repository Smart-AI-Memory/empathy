/**
 * Costs Panel - Dedicated webview for cost metrics and simulation
 *
 * Displays comprehensive cost analysis including:
 * - Current model configuration
 * - Cost summary (7 days)
 * - Daily cost trend chart
 * - Cost by tier (pie chart)
 * - Cost by provider (bar chart)
 * - Interactive cost simulator
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { getCostsDataService, CostsDataService } from '../services/CostsDataService';

export class CostsPanel {
    public static currentPanel: CostsPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private readonly _costsDataService: CostsDataService;

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._costsDataService = getCostsDataService();

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
        if (CostsPanel.currentPanel) {
            CostsPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyCostsPanel',
            'Cost Metrics',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        CostsPanel.currentPanel = new CostsPanel(panel, extensionUri);
    }

    public dispose() {
        CostsPanel.currentPanel = undefined;

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

        // Load cost data from service
        const costs = await this._costsDataService.getCostsData(workspaceFolder, force);

        // Load model configuration
        const modelConfig = this._costsDataService.getModelConfig(workspaceFolder);

        // Send to webview
        this._panel.webview.postMessage({
            type: 'costData',
            data: costs
        });

        this._panel.webview.postMessage({
            type: 'modelConfig',
            data: modelConfig
        });
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Cost Metrics';
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
    <title>Cost Metrics</title>
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
    </style>
</head>
<body>
    <div class="header">
        <h1>Cost Metrics</h1>
        <div class="header-actions">
            <button class="btn" onclick="openDashboard()">Dashboard</button>
            <button class="btn" onclick="refresh()">Refresh</button>
        </div>
    </div>

    <!-- Current Model Configuration -->
    <div class="card">
        <div class="card-title">Current Configuration</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
            <div>
                <div style="font-size: 10px; opacity: 0.7; margin-bottom: 4px;">Provider</div>
                <div style="font-size: 14px; font-weight: 600;" id="current-provider">Detecting...</div>
            </div>
            <div>
                <div style="font-size: 10px; opacity: 0.7; margin-bottom: 4px;">Mode</div>
                <div style="font-size: 14px; font-weight: 600;" id="current-mode">--</div>
            </div>
        </div>
        <div style="margin-top: 12px;">
            <div style="font-size: 10px; opacity: 0.7; margin-bottom: 4px;">Active Models by Tier</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-size: 11px;">
                <div style="padding: 6px; background: var(--vscode-input-background); border-radius: 4px;">
                    <div style="font-weight: 600; color: var(--vscode-charts-green);">Cheap</div>
                    <div style="opacity: 0.8;" id="model-cheap">--</div>
                </div>
                <div style="padding: 6px; background: var(--vscode-input-background); border-radius: 4px;">
                    <div style="font-weight: 600; color: var(--vscode-charts-blue);">Capable</div>
                    <div style="opacity: 0.8;" id="model-capable">--</div>
                </div>
                <div style="padding: 6px; background: var(--vscode-input-background); border-radius: 4px;">
                    <div style="font-weight: 600; color: var(--vscode-charts-purple);">Premium</div>
                    <div style="opacity: 0.8;" id="model-premium">--</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Cost Summary (7 days) -->
    <div class="card">
        <div class="card-title">Cost Summary (7 days)</div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 8px; text-align: center;">
            <div>
                <div style="font-size: 20px; font-weight: bold; color: var(--vscode-charts-green);" id="costs-saved">$0.00</div>
                <div style="font-size: 10px; opacity: 0.7;">Saved</div>
            </div>
            <div>
                <div style="font-size: 20px; font-weight: bold;" id="costs-percent">0%</div>
                <div style="font-size: 10px; opacity: 0.7;">Reduction</div>
            </div>
            <div>
                <div style="font-size: 20px; font-weight: bold;" id="costs-total">$0.00</div>
                <div style="font-size: 10px; opacity: 0.7;">Actual</div>
            </div>
        </div>
    </div>

    <!-- Cost Trend Chart (7 days) -->
    <div class="card">
        <div class="card-title">Daily Cost Trend</div>
        <div id="cost-trend-chart" style="height: 120px; display: flex; align-items: flex-end; gap: 4px; padding: 8px 0;">
            <div style="text-align: center; opacity: 0.5; width: 100%;">No data yet</div>
        </div>
        <div id="cost-trend-labels" style="display: flex; justify-content: space-between; font-size: 9px; opacity: 0.6; padding: 0 4px;"></div>
    </div>

    <!-- Tier Distribution Chart -->
    <div class="card">
        <div class="card-title">Cost by Tier</div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div id="tier-pie-chart" style="width: 80px; height: 80px; flex-shrink: 0;">
                <svg viewBox="0 0 32 32" style="transform: rotate(-90deg); width: 100%; height: 100%;">
                    <circle id="pie-cheap" r="16" cx="16" cy="16" fill="transparent" stroke="var(--vscode-charts-green)" stroke-width="32" stroke-dasharray="0 100" />
                    <circle id="pie-capable" r="16" cx="16" cy="16" fill="transparent" stroke="var(--vscode-charts-blue)" stroke-width="32" stroke-dasharray="0 100" stroke-dashoffset="0" />
                    <circle id="pie-premium" r="16" cx="16" cy="16" fill="transparent" stroke="var(--vscode-charts-purple)" stroke-width="32" stroke-dasharray="0 100" stroke-dashoffset="0" />
                </svg>
            </div>
            <div style="flex: 1; font-size: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span><span style="color: var(--vscode-charts-green);">●</span> Cheap</span>
                    <span id="tier-cheap-pct">--</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span><span style="color: var(--vscode-charts-blue);">●</span> Capable</span>
                    <span id="tier-capable-pct">--</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span><span style="color: var(--vscode-charts-purple);">●</span> Premium</span>
                    <span id="tier-premium-pct">--</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Provider Comparison -->
    <div class="card">
        <div class="card-title">Cost by Provider</div>
        <div id="provider-bars" style="display: flex; flex-direction: column; gap: 6px;">
            <div style="text-align: center; opacity: 0.5; padding: 8px;">No provider data</div>
        </div>
    </div>

    <!-- Cost Simulator -->
    <div class="card">
        <div class="card-title" style="display: flex; justify-content: space-between; align-items: center;">
            <span>Cost Simulator <span style="font-size: 9px; color: #a855f7; font-weight: normal; opacity: 0.9;">(Interactive)</span></span>
        </div>
        <div style="font-size: 10px; opacity: 0.7; margin-bottom: 8px;">Drag sliders to see real-time cost estimates</div>

        <div style="display: flex; flex-direction: column; gap: 12px;">
            <!-- Controls -->
            <div>
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 10px; margin-bottom: 4px; opacity: 0.8;">Provider preset</div>
                    <select id="sim-provider" style="width: 100%; padding: 6px 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--border); border-radius: 4px; font-size: 11px;">
                        <option value="cost-optimized">Cost-Optimized (Recommended)</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="openai">OpenAI</option>
                        <option value="google">Google Gemini</option>
                        <option value="ollama">Ollama (Free - Local)</option>
                    </select>
                </div>

                <div style="margin-bottom: 8px;">
                    <div style="font-size: 10px; margin-bottom: 4px; opacity: 0.8;">Scenario</div>
                    <select id="sim-scenario" style="width: 100%; padding: 6px 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--border); border-radius: 4px; font-size: 11px;">
                        <option value="default">Typical week</option>
                        <option value="heavy">Heavy experimentation</option>
                        <option value="light">Light usage</option>
                    </select>
                </div>

                <div style="margin-bottom: 8px;">
                    <div style="font-size: 10px; margin-bottom: 4px; opacity: 0.8;">Tier mix (drag to adjust)</div>
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 50px; font-size: 10px; color: var(--vscode-charts-green);">Cheap</span>
                            <input id="sim-cheap" type="range" min="0" max="100" step="5" value="50" style="flex: 1; height: 6px; accent-color: var(--vscode-charts-green);" />
                            <span id="sim-cheap-val" style="width: 30px; font-size: 10px; text-align: right;">50%</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 50px; font-size: 10px; color: var(--vscode-charts-blue);">Capable</span>
                            <input id="sim-capable" type="range" min="0" max="100" step="5" value="40" style="flex: 1; height: 6px; accent-color: var(--vscode-charts-blue);" />
                            <span id="sim-capable-val" style="width: 30px; font-size: 10px; text-align: right;">40%</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 50px; font-size: 10px; color: var(--vscode-charts-purple);">Premium</span>
                            <input id="sim-premium" type="range" min="0" max="100" step="5" value="10" style="flex: 1; height: 6px; accent-color: var(--vscode-charts-purple);" />
                            <span id="sim-premium-val" style="width: 30px; font-size: 10px; text-align: right;">10%</span>
                        </div>
                    </div>
                    <div id="sim-mix-warning" style="margin-top: 4px; font-size: 9px; color: var(--vscode-inputValidation-warningForeground); display: none;">Percentages normalized to 100%</div>
                </div>
            </div>

            <!-- Results -->
            <div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; text-align: center; margin-bottom: 8px;">
                    <div>
                        <div style="font-size: 13px; font-weight: 600;" id="sim-actual">$0.00</div>
                        <div style="font-size: 9px; opacity: 0.7;">Scenario</div>
                    </div>
                    <div>
                        <div style="font-size: 13px; font-weight: 600;" id="sim-baseline">$0.00</div>
                        <div style="font-size: 9px; opacity: 0.7;">Baseline</div>
                    </div>
                    <div>
                        <div style="font-size: 13px; font-weight: 600; color: var(--vscode-charts-green);" id="sim-savings">$0.00</div>
                        <div style="font-size: 9px; opacity: 0.7;">Saved</div>
                    </div>
                </div>

                <!-- Monthly Projection Chart -->
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 10px; opacity: 0.8; margin-bottom: 4px;">Monthly Projection</div>
                    <div id="sim-projection-chart" style="height: 50px; display: flex; gap: 2px; align-items: flex-end;">
                        <div style="flex: 1; background: var(--vscode-charts-blue); height: 50%; border-radius: 2px;" title="Scenario"></div>
                        <div style="flex: 1; background: var(--vscode-input-background); border: 1px dashed var(--vscode-charts-red); height: 100%; border-radius: 2px;" title="Baseline"></div>
                    </div>
                    <div style="display: flex; justify-content: space-around; font-size: 9px; opacity: 0.6; margin-top: 2px;">
                        <span>Scenario</span>
                        <span>Baseline</span>
                    </div>
                </div>

                <div style="font-size: 10px; opacity: 0.8; margin-bottom: 4px;">By tier</div>
                <div id="sim-tier-breakdown" style="font-size: 10px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px;"></div>

                <div style="font-size: 9px; opacity: 0.6; margin-top: 8px;">
                    Based on ~1K tokens/request
                </div>
            </div>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();

        // Pricing data for simulator
        const SIM_TIER_PRICING = {
            // Haiku: $0.80/$4.00, Sonnet: $3.00/$15.00, Opus: $15.00/$75.00
            anthropic: { cheap: 0.0028, capable: 0.0105, premium: 0.0525 },
            // GPT-4o-mini: $0.15/$0.60, GPT-4o: $2.50/$10.00, o1: $15.00/$60.00
            openai: { cheap: 0.00045, capable: 0.0075, premium: 0.045 },
            // Flash: $0.10/$0.40, 1.5 Pro: $1.25/$5.00, 2.5 Pro: $1.25/$10.00
            google: { cheap: 0.0003, capable: 0.00375, premium: 0.00625 },
            // Cost-Optimized: Google cheap/capable + Anthropic premium (best quality where it matters)
            'cost-optimized': { cheap: 0.0003, capable: 0.00375, premium: 0.0525 },
            // Local models - no API cost
            ollama: { cheap: 0, capable: 0, premium: 0 }
        };

        const SIM_SCENARIOS = {
            default: 200,
            heavy: 600,
            light: 60
        };

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'costData':
                    updateCostsPanel(message.data);
                    break;
                case 'modelConfig':
                    updateModelConfig(message.data);
                    break;
            }
        });

        function renderCostTrendChart(dailyCosts) {
            const container = document.getElementById('cost-trend-chart');
            const labelsContainer = document.getElementById('cost-trend-labels');

            if (!dailyCosts || dailyCosts.length === 0) {
                container.innerHTML = '<div style="text-align: center; opacity: 0.5; width: 100%;">No daily data yet</div>';
                labelsContainer.innerHTML = '';
                return;
            }

            // Get last 7 days
            const last7 = dailyCosts.slice(-7);
            const maxCost = Math.max(...last7.map(d => d.cost), 0.01);

            const barHtml = last7.map((d) => {
                const height = Math.max((d.cost / maxCost) * 100, 2);
                const savingsHeight = Math.max((d.savings / maxCost) * 100, 0);
                return '<div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; height: 100%;" title="' + d.date + ': $' + d.cost.toFixed(4) + '">' +
                    '<div style="flex: 1; display: flex; flex-direction: column; justify-content: flex-end; width: 100%;">' +
                        '<div style="background: var(--vscode-charts-green); opacity: 0.4; height: ' + savingsHeight + '%; border-radius: 2px 2px 0 0;"></div>' +
                        '<div style="background: var(--vscode-charts-blue); height: ' + height + '%; border-radius: 0 0 2px 2px; min-height: 2px;"></div>' +
                    '</div>' +
                '</div>';
            }).join('');

            container.innerHTML = barHtml;

            // Show first and last date labels
            if (last7.length > 0) {
                const firstDate = last7[0].date.split('-').slice(1).join('/');
                const lastDate = last7[last7.length - 1].date.split('-').slice(1).join('/');
                labelsContainer.innerHTML = '<span>' + firstDate + '</span><span>' + lastDate + '</span>';
            }
        }

        function renderTierPieChart(byTier) {
            if (!byTier || Object.keys(byTier).length === 0) {
                document.getElementById('tier-cheap-pct').textContent = '--';
                document.getElementById('tier-capable-pct').textContent = '--';
                document.getElementById('tier-premium-pct').textContent = '--';
                return;
            }

            const cheap = byTier.cheap?.cost || 0;
            const capable = byTier.capable?.cost || 0;
            const premium = byTier.premium?.cost || 0;
            const total = cheap + capable + premium;

            if (total === 0) {
                document.getElementById('tier-cheap-pct').textContent = '0%';
                document.getElementById('tier-capable-pct').textContent = '0%';
                document.getElementById('tier-premium-pct').textContent = '0%';
                return;
            }

            const cheapPct = (cheap / total) * 100;
            const capablePct = (capable / total) * 100;
            const premiumPct = (premium / total) * 100;

            // Update pie chart using stroke-dasharray
            const pct = 100;

            const pieChaps = document.getElementById('pie-cheap');
            const pieCapa = document.getElementById('pie-capable');
            const piePrem = document.getElementById('pie-premium');

            if (pieChaps) {
                pieChaps.setAttribute('stroke-dasharray', (cheapPct * pct / 100) + ' ' + pct);
            }
            if (pieCapa) {
                pieCapa.setAttribute('stroke-dasharray', (capablePct * pct / 100) + ' ' + pct);
                pieCapa.setAttribute('stroke-dashoffset', '-' + (cheapPct * pct / 100));
            }
            if (piePrem) {
                piePrem.setAttribute('stroke-dasharray', (premiumPct * pct / 100) + ' ' + pct);
                piePrem.setAttribute('stroke-dashoffset', '-' + ((cheapPct + capablePct) * pct / 100));
            }

            // Update legend
            document.getElementById('tier-cheap-pct').textContent = cheapPct.toFixed(0) + '% ($' + cheap.toFixed(2) + ')';
            document.getElementById('tier-capable-pct').textContent = capablePct.toFixed(0) + '% ($' + capable.toFixed(2) + ')';
            document.getElementById('tier-premium-pct').textContent = premiumPct.toFixed(0) + '% ($' + premium.toFixed(2) + ')';
        }

        function renderProviderBars(byProvider) {
            const container = document.getElementById('provider-bars');

            if (!byProvider || Object.keys(byProvider).length === 0) {
                container.innerHTML = '<div style="text-align: center; opacity: 0.5; padding: 8px;">No provider data</div>';
                return;
            }

            // If only "unknown" provider, show message instead
            const keys = Object.keys(byProvider);
            if (keys.length === 1 && keys[0] === 'unknown') {
                container.innerHTML = '<div style="text-align: center; opacity: 0.5; padding: 8px;">Provider data not recorded in telemetry</div>';
                return;
            }

            const providerColors = {
                anthropic: '#d97706',
                openai: '#22c55e',
                google: '#4285f4',
                ollama: '#6366f1'
            };

            // Filter out "unknown" if there are other providers
            const entries = Object.entries(byProvider).filter(([p, _]) => p !== 'unknown');
            if (entries.length === 0) {
                container.innerHTML = '<div style="text-align: center; opacity: 0.5; padding: 8px;">No provider data</div>';
                return;
            }

            const maxCost = Math.max(...entries.map(([_, v]) => v.cost), 0.01);

            container.innerHTML = entries.map(([provider, data]) => {
                const width = Math.max((data.cost / maxCost) * 100, 5);
                const color = providerColors[provider.toLowerCase()] || '#888';
                return '<div style="display: flex; align-items: center; gap: 8px; font-size: 10px;">' +
                    '<div style="width: 60px; text-transform: capitalize;">' + provider + '</div>' +
                    '<div style="flex: 1; height: 16px; background: var(--vscode-input-background); border-radius: 2px; overflow: hidden;">' +
                        '<div style="width: ' + width + '%; height: 100%; background: ' + color + '; border-radius: 2px;"></div>' +
                    '</div>' +
                    '<div style="width: 60px; text-align: right;">$' + data.cost.toFixed(2) + '</div>' +
                '</div>';
            }).join('');
        }

        function updateCostsPanel(data) {
            // Update summary
            document.getElementById('costs-saved').textContent = '$' + (data.totalSavings || 0).toFixed(2);
            document.getElementById('costs-percent').textContent = (data.savingsPercent || 0) + '%';
            document.getElementById('costs-total').textContent = '$' + (data.totalCost || 0).toFixed(2);

            // Render charts
            renderCostTrendChart(data.dailyCosts);
            renderTierPieChart(data.byTier);
            renderProviderBars(data.byProvider);
        }

        function updateModelConfig(data) {
            // Update provider and mode
            const providerEl = document.getElementById('current-provider');
            const modeEl = document.getElementById('current-mode');

            if (providerEl) {
                providerEl.textContent = data.provider || 'Unknown';
            }
            if (modeEl) {
                const modeLabels = {
                    'single': 'Single Provider',
                    'hybrid': 'Hybrid (Cost Optimized)',
                    'custom': 'Custom'
                };
                modeEl.textContent = modeLabels[data.mode] || data.mode || '--';
            }

            // Update tier models
            if (data.models) {
                const cheapEl = document.getElementById('model-cheap');
                const capableEl = document.getElementById('model-capable');
                const premiumEl = document.getElementById('model-premium');

                if (cheapEl) cheapEl.textContent = data.models.cheap || '--';
                if (capableEl) capableEl.textContent = data.models.capable || '--';
                if (premiumEl) premiumEl.textContent = data.models.premium || '--';
            }
        }

        // Simulator functions
        function normalizeMix(cheap, capable, premium) {
            const total = cheap + capable + premium;
            if (!total || total <= 0) {
                return { cheap: 0.5, capable: 0.4, premium: 0.1 };
            }
            return {
                cheap: cheap / total,
                capable: capable / total,
                premium: premium / total
            };
        }

        function updateSliderLabels() {
            const cheapVal = document.getElementById('sim-cheap-val');
            const capableVal = document.getElementById('sim-capable-val');
            const premiumVal = document.getElementById('sim-premium-val');
            const cheapInput = document.getElementById('sim-cheap');
            const capableInput = document.getElementById('sim-capable');
            const premiumInput = document.getElementById('sim-premium');

            if (cheapVal && cheapInput) cheapVal.textContent = cheapInput.value + '%';
            if (capableVal && capableInput) capableVal.textContent = capableInput.value + '%';
            if (premiumVal && premiumInput) premiumVal.textContent = premiumInput.value + '%';
        }

        function runSimulator() {
            const providerSelect = document.getElementById('sim-provider');
            const scenarioSelect = document.getElementById('sim-scenario');
            const cheapInput = document.getElementById('sim-cheap');
            const capableInput = document.getElementById('sim-capable');
            const premiumInput = document.getElementById('sim-premium');
            const mixWarning = document.getElementById('sim-mix-warning');

            if (!providerSelect || !scenarioSelect || !cheapInput || !capableInput || !premiumInput) {
                return;
            }

            // Update slider labels first
            updateSliderLabels();

            const provider = providerSelect.value || 'cost-optimized';
            const scenario = scenarioSelect.value || 'default';

            const cheapPct = parseFloat(cheapInput.value) || 0;
            const capablePct = parseFloat(capableInput.value) || 0;
            const premiumPct = parseFloat(premiumInput.value) || 0;

            const sum = cheapPct + capablePct + premiumPct;
            if (mixWarning) {
                mixWarning.style.display = sum > 100.5 || sum < 99.5 ? 'block' : 'none';
            }

            const mix = normalizeMix(cheapPct, capablePct, premiumPct);
            const totalRequests = SIM_SCENARIOS[scenario] || SIM_SCENARIOS.default;

            const pricing = SIM_TIER_PRICING[provider] || SIM_TIER_PRICING['cost-optimized'];

            const cheapReq = totalRequests * mix.cheap;
            const capableReq = totalRequests * mix.capable;
            const premiumReq = totalRequests * mix.premium;

            const cheapCost = cheapReq * pricing.cheap;
            const capableCost = capableReq * pricing.capable;
            const premiumCost = premiumReq * pricing.premium;

            const actualCost = cheapCost + capableCost + premiumCost;

            // Baseline: all-premium at same total requests with provider's premium pricing
            const baselineCost = totalRequests * pricing.premium;
            const savings = baselineCost - actualCost;

            // Update summary
            const actualEl = document.getElementById('sim-actual');
            const baselineEl = document.getElementById('sim-baseline');
            const savingsEl = document.getElementById('sim-savings');

            if (actualEl) actualEl.textContent = '$' + actualCost.toFixed(2);
            if (baselineEl) baselineEl.textContent = '$' + baselineCost.toFixed(2);
            if (savingsEl) savingsEl.textContent = '$' + Math.max(0, savings).toFixed(2);

            // Update projection chart (monthly = 4 weeks)
            const monthlyActual = actualCost * 4;
            const monthlyBaseline = baselineCost * 4;
            const projectionChart = document.getElementById('sim-projection-chart');
            if (projectionChart && monthlyBaseline > 0) {
                const actualHeight = Math.max((monthlyActual / monthlyBaseline) * 100, 5);
                projectionChart.innerHTML =
                    '<div style="flex: 1; display: flex; flex-direction: column; align-items: center;">' +
                        '<div style="flex: 1; width: 100%; display: flex; align-items: flex-end;">' +
                            '<div style="width: 100%; height: ' + actualHeight + '%; background: linear-gradient(to top, var(--vscode-charts-green), var(--vscode-charts-blue)); border-radius: 2px;"></div>' +
                        '</div>' +
                        '<div style="font-size: 9px; margin-top: 2px;">$' + monthlyActual.toFixed(0) + '/mo</div>' +
                    '</div>' +
                    '<div style="flex: 1; display: flex; flex-direction: column; align-items: center;">' +
                        '<div style="flex: 1; width: 100%; display: flex; align-items: flex-end;">' +
                            '<div style="width: 100%; height: 100%; background: var(--vscode-input-background); border: 1px dashed var(--vscode-charts-red); border-radius: 2px; opacity: 0.6;"></div>' +
                        '</div>' +
                        '<div style="font-size: 9px; margin-top: 2px;">$' + monthlyBaseline.toFixed(0) + '/mo</div>' +
                    '</div>';
            }

            // Tier breakdown
            const tierEl = document.getElementById('sim-tier-breakdown');
            if (tierEl) {
                tierEl.innerHTML = [
                    { key: 'cheap', label: 'Cheap', req: cheapReq, cost: cheapCost, color: '#22c55e' },
                    { key: 'capable', label: 'Capable', req: capableReq, cost: capableCost, color: '#3b82f6' },
                    { key: 'premium', label: 'Premium', req: premiumReq, cost: premiumCost, color: '#a855f7' }
                ].map(t => {
                    return '<div style="padding: 4px 6px; border: 1px solid var(--border); border-radius: 3px;">' +
                        '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                            '<span style="color: ' + t.color + '; font-weight: 600;">' + t.label + '</span>' +
                            '<span style="opacity: 0.7;">' + Math.round((t.req || 0)) + ' req</span>' +
                        '</div>' +
                        '<div style="font-size: 10px; opacity: 0.8; margin-top: 2px;">$' + (t.cost || 0).toFixed(2) + '</div>' +
                    '</div>';
                }).join('');
            }
        }

        // Real-time slider updates
        ['sim-cheap', 'sim-capable', 'sim-premium'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', function() {
                    runSimulator();
                });
            }
        });

        // Dropdown changes
        ['sim-provider', 'sim-scenario'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', function() {
                    runSimulator();
                });
            }
        });

        // Initialize simulator on load
        runSimulator();

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
