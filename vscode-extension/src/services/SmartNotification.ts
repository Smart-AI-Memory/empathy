/**
 * Smart Notification System
 *
 * Triggers notification after first workflow with cost >= $0.50
 * Offers one-click "Enable Monitoring" setup
 *
 * **Implementation:** Sprint 2 (Week 2)
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as net from 'net';

export class SmartNotificationService {
    private context: vscode.ExtensionContext;
    private hasShownNotification: boolean = false;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.hasShownNotification =
            context.globalState.get<boolean>('telemetry.hasShownNotification') || false;
    }

    /**
     * Check if we should show the notification
     */
    async checkAndNotify(): Promise<void> {
        if (this.hasShownNotification) {
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        const empathyDir = path.join(workspaceFolder, '.empathy');
        const workflowsFile = path.join(empathyDir, 'workflow_runs.jsonl');

        if (!fs.existsSync(workflowsFile)) {
            return;
        }

        // Check if any workflow has cost >= $0.50
        const hasExpensiveWorkflow = this.checkExpensiveWorkflows(workflowsFile);

        if (hasExpensiveWorkflow) {
            await this.showMonitoringNotification();
        }
    }

    /**
     * Check if any workflow has cost >= $0.50
     */
    private checkExpensiveWorkflows(filePath: string): boolean {
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const lines = content.split('\n');

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const workflow = JSON.parse(line);
                    if (workflow.totalCost >= 0.50) {
                        return true;
                    }
                } catch {
                    continue;
                }
            }
        } catch {
            // Ignore errors
        }

        return false;
    }

    /**
     * Show the monitoring notification with one-click setup
     */
    private async showMonitoringNotification(): Promise<void> {
        const choice = await vscode.window.showInformationMessage(
            '💰 Monitoring Available - High-cost workflow detected. Would you like to enable LLM telemetry monitoring?',
            'Enable Monitoring',
            'Later',
            'Never'
        );

        if (choice === 'Enable Monitoring') {
            await this.enableMonitoring();
            this.hasShownNotification = true;
            await this.context.globalState.update(
                'telemetry.hasShownNotification',
                true
            );
        } else if (choice === 'Never') {
            this.hasShownNotification = true;
            await this.context.globalState.update(
                'telemetry.hasShownNotification',
                true
            );
        }
    }

    /**
     * One-click monitoring setup
     */
    private async enableMonitoring(): Promise<void> {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: 'Setting up monitoring...',
                cancellable: false,
            },
            async (progress) => {
                // Step 1: Open telemetry dashboard
                progress.report({ message: 'Opening telemetry dashboard...' });
                await vscode.commands.executeCommand('empathy.openTelemetry');
                await new Promise((resolve) => setTimeout(resolve, 500));

                // Step 2: Set up cost alert (daily spend > $10)
                progress.report({ message: 'Configuring cost alert...' });
                await this.setupCostAlert();

                // Step 3: Check for OTEL collector
                progress.report({ message: 'Checking for OTEL collector...' });
                const hasOTEL = await this.checkOTELCollector();

                if (hasOTEL) {
                    await this.offerOTELSetup();
                }

                // Complete
                vscode.window.showInformationMessage(
                    '✅ Monitoring enabled! View telemetry in the dashboard.'
                );
            }
        );
    }

    /**
     * Set up cost alert (daily spend > $10, logs to VSCode output)
     */
    private async setupCostAlert(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        const empathyDir = path.join(workspaceFolder, '.empathy');
        const alertsFile = path.join(empathyDir, 'alerts.json');

        // Create default alert configuration
        const alertConfig = {
            alerts: [
                {
                    id: 'daily-cost-alert',
                    name: 'Daily Cost Alert',
                    metric: 'daily_cost',
                    threshold: 10.0,
                    channel: 'vscode_output',
                    enabled: true,
                    cooldown: 3600,
                },
            ],
        };

        try {
            fs.writeFileSync(alertsFile, JSON.stringify(alertConfig, null, 2));
        } catch (error) {
            console.error('Failed to create alert configuration:', error);
        }
    }

    /**
     * Check if OTEL collector is running on localhost:4317
     */
    private async checkOTELCollector(): Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            const socket = new net.Socket();
            const timeout = setTimeout(() => {
                socket.destroy();
                resolve(false);
            }, 1000);

            socket.connect(4317, 'localhost', () => {
                clearTimeout(timeout);
                socket.destroy();
                resolve(true);
            });

            socket.on('error', () => {
                clearTimeout(timeout);
                socket.destroy();
                resolve(false);
            });
        });
    }

    /**
     * Offer OTEL setup if collector is detected
     */
    private async offerOTELSetup(): Promise<void> {
        const choice = await vscode.window.showInformationMessage(
            '🔍 OTEL Collector detected on localhost:4317. Enable telemetry export?',
            'Enable OTEL',
            'Not Now'
        );

        if (choice === 'Enable OTEL') {
            vscode.window.showInformationMessage(
                'To enable OTEL export:\n1. Set EMPATHY_OTEL_ENDPOINT=http://localhost:4317\n2. Run: pip install empathy-framework[otel]'
            );
        }
    }

    /**
     * Reset notification state (for testing)
     */
    async reset(): Promise<void> {
        this.hasShownNotification = false;
        await this.context.globalState.update('telemetry.hasShownNotification', false);
    }
}
