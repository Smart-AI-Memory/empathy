/**
 * Empathy Memory Panel Extension
 *
 * VS Code extension for managing Empathy Framework memory system.
 * Provides real-time monitoring, Redis control, and pattern management.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import { MemoryPanelProvider } from './views/MemoryPanelProvider';

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Empathy Memory Panel extension is now active');

    // Create panel provider
    const provider = new MemoryPanelProvider(
        context.extensionUri,
        context
    );

    // Register webview provider
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            MemoryPanelProvider.viewType,
            provider,
            {
                webviewOptions: {
                    retainContextWhenHidden: true
                }
            }
        )
    );

    // Register commands
    registerCommands(context, provider);

    // Show welcome message on first install
    const hasShownWelcome = context.globalState.get<boolean>('empathyMemory.hasShownWelcome');
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
    }
}

/**
 * Register all extension commands
 */
function registerCommands(
    context: vscode.ExtensionContext,
    provider: MemoryPanelProvider
): void {
    // Show panel
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.showPanel', () => {
            vscode.commands.executeCommand('empathyMemory.controlPanel.focus');
        })
    );

    // Refresh status
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.refreshStatus', () => {
            provider.refresh();
            vscode.window.showInformationMessage('Empathy Memory: Status refreshed');
        })
    );

    // Start Redis
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.startRedis', async () => {
            // This will be handled by the webview, just show it
            await vscode.commands.executeCommand('empathyMemory.controlPanel.focus');
            vscode.window.showInformationMessage('Use the "Start Redis" button in the panel');
        })
    );

    // Stop Redis
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.stopRedis', async () => {
            // This will be handled by the webview, just show it
            await vscode.commands.executeCommand('empathyMemory.controlPanel.focus');
            vscode.window.showInformationMessage('Use the "Stop Redis" button in the panel');
        })
    );

    // View patterns
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.viewPatterns', async () => {
            await vscode.commands.executeCommand('empathyMemory.controlPanel.focus');
            vscode.window.showInformationMessage('View patterns in the panel');
        })
    );

    // Export patterns
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.exportPatterns', async () => {
            await vscode.commands.executeCommand('empathyMemory.controlPanel.focus');
            vscode.window.showInformationMessage('Use the "Export" button in the panel');
        })
    );

    // Health check
    context.subscriptions.push(
        vscode.commands.registerCommand('empathyMemory.healthCheck', async () => {
            await vscode.commands.executeCommand('empathyMemory.controlPanel.focus');
            vscode.window.showInformationMessage('Use the "Health Check" button in the panel');
        })
    );
}

/**
 * Show welcome message
 */
async function showWelcomeMessage(context: vscode.ExtensionContext): Promise<void> {
    const action = await vscode.window.showInformationMessage(
        'Welcome to Empathy Memory Panel! This extension helps you manage Redis and pattern storage for the Empathy Framework.',
        'Open Panel',
        'Documentation',
        'Don\'t Show Again'
    );

    if (action === 'Open Panel') {
        await vscode.commands.executeCommand('empathyMemory.showPanel');
    } else if (action === 'Documentation') {
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/your-org/empathy-framework'));
    }

    // Mark as shown
    context.globalState.update('empathyMemory.hasShownWelcome', true);
}

/**
 * Extension deactivation
 */
export function deactivate() {
    console.log('Empathy Memory Panel extension is now deactivated');
}
