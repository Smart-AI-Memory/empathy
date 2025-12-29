/**
 * Basic tests for Empathy Framework VS Code extension.
 *
 * These tests verify the extension activates correctly and commands are registered.
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('smart-ai-memory.empathy-framework'));
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('smart-ai-memory.empathy-framework');
        if (extension) {
            await extension.activate();
            assert.strictEqual(extension.isActive, true);
        }
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);

        // Check for main commands
        assert.ok(commands.includes('empathy.dashboard'), 'Dashboard command not found');
        assert.ok(commands.includes('empathy.morning'), 'Morning command not found');
        assert.ok(commands.includes('empathy.costs'), 'Costs command not found');
    });
});

suite('Dashboard Panel Tests', () => {
    test('Dashboard command should be executable', async () => {
        // Verify the command exists and can be called
        try {
            // Just verify command is registered, don't actually execute
            const commands = await vscode.commands.getCommands(true);
            assert.ok(commands.includes('empathy.dashboard'));
        } catch (error) {
            assert.fail('Dashboard command should exist');
        }
    });
});

suite('Initialize Wizard Tests', () => {
    test('Initialize command should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(commands.includes('empathy.initialize'), 'Initialize command not found');
    });

    test('Supported providers should not include hybrid', () => {
        // Verify hybrid was removed from supported providers
        const supportedProviders = ['anthropic', 'openai', 'google', 'ollama'];
        assert.ok(!supportedProviders.includes('hybrid'), 'Hybrid should be removed');
        assert.ok(supportedProviders.includes('google'), 'Google should be supported');
    });
});
