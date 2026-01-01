/**
 * LLMChatService - Direct LLM integration for Socratic forms
 *
 * Replaces the broken CLI-based chat command with direct provider integration.
 * Supports Anthropic Claude API with fallback responses when no API key.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import { ServiceConfig } from './ServiceConfig';

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface ChatOptions {
    maxTokens?: number;
    temperature?: number;
    systemPrompt?: string;
}

export interface ChatResponse {
    content: string;
    inputTokens: number;
    outputTokens: number;
    model: string;
    fromFallback: boolean;
}

/**
 * LLMChatService - Handles LLM chat interactions
 */
export class LLMChatService {
    private static instance: LLMChatService;
    private context: vscode.ExtensionContext | null = null;
    private extensionPath: string = '';

    private constructor() {}

    static getInstance(): LLMChatService {
        if (!LLMChatService.instance) {
            LLMChatService.instance = new LLMChatService();
        }
        return LLMChatService.instance;
    }

    /**
     * Initialize with extension context
     */
    initialize(context: vscode.ExtensionContext): void {
        this.context = context;
        this.extensionPath = context.extensionPath;
    }

    /**
     * Send a chat message and get a response
     */
    async chat(
        messages: ChatMessage[],
        options: ChatOptions = {}
    ): Promise<ChatResponse> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return this.getFallbackResponse(messages, 'No workspace folder open');
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Try to use empathy_os providers directly via Python
        try {
            const response = await this.callPythonProvider(
                pythonPath,
                workspaceFolder,
                messages,
                options
            );
            return response;
        } catch (error) {
            console.error('[LLMChatService] Provider call failed:', error);
            return this.getFallbackResponse(messages, String(error));
        }
    }

    /**
     * Call Python provider for LLM response
     */
    private async callPythonProvider(
        pythonPath: string,
        workspaceFolder: string,
        messages: ChatMessage[],
        options: ChatOptions
    ): Promise<ChatResponse> {
        return new Promise((resolve, reject) => {
            // Path to external Python script
            const scriptPath = path.join(this.extensionPath, 'scripts', 'llm_provider_call.py');

            // Build arguments as JSON
            const args = JSON.stringify({
                messages,
                system_prompt: options.systemPrompt || '',
                max_tokens: options.maxTokens || ServiceConfig.llmDefaultMaxTokens,
                temperature: options.temperature || ServiceConfig.llmDefaultTemperature
            });

            cp.execFile(
                pythonPath,
                [scriptPath, args],
                {
                    cwd: workspaceFolder,
                    maxBuffer: ServiceConfig.LLM_MAX_BUFFER_SIZE,
                    timeout: ServiceConfig.llmTimeoutMs,
                    env: { ...process.env }
                },
                (error, stdout, stderr) => {
                    if (error) {
                        // Check if it's an API key issue
                        if (stderr.includes('API key') || stderr.includes('authentication')) {
                            resolve(this.getFallbackResponse(messages, 'No API key configured'));
                            return;
                        }
                        reject(new Error(`Python error: ${stderr || error.message}`));
                        return;
                    }

                    try {
                        const result = JSON.parse(stdout.trim());

                        // Check if fallback response
                        if (result.fallback) {
                            resolve(this.getFallbackResponse(messages, result.error || 'Unknown error'));
                            return;
                        }

                        resolve({
                            content: result.content || '',
                            inputTokens: result.input_tokens || 0,
                            outputTokens: result.output_tokens || 0,
                            model: result.model || 'unknown',
                            fromFallback: false
                        });
                    } catch (parseError) {
                        // If we got text but couldn't parse as JSON, use it directly
                        if (stdout.trim()) {
                            resolve({
                                content: stdout.trim(),
                                inputTokens: 0,
                                outputTokens: 0,
                                model: 'unknown',
                                fromFallback: false
                            });
                        } else {
                            resolve(this.getFallbackResponse(messages, 'Empty response'));
                        }
                    }
                }
            );
        });
    }

    /**
     * Get fallback response when LLM is unavailable
     */
    private getFallbackResponse(messages: ChatMessage[], reason: string): ChatResponse {
        const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
        const userContent = lastUserMessage?.content || '';

        // Detect context from conversation
        const isCodeReview = userContent.toLowerCase().includes('review') ||
                            userContent.toLowerCase().includes('code');
        const isTestGen = userContent.toLowerCase().includes('test') ||
                         userContent.toLowerCase().includes('coverage');
        const isRefactor = userContent.toLowerCase().includes('refactor') ||
                          userContent.toLowerCase().includes('improve');
        const isAgentDesign = userContent.toLowerCase().includes('agent') ||
                             userContent.toLowerCase().includes('crew');

        let content: string;

        if (isAgentDesign) {
            content = `To design an effective multi-agent workflow, I'd like to understand:

1. **Task Complexity**: Is this a single-step task or does it require multiple specialized skills?
2. **Expertise Areas**: What domains of knowledge are needed? (e.g., coding, research, analysis)
3. **Collaboration Pattern**: Should agents work sequentially, in parallel, or hierarchically?

What's the primary goal you're trying to accomplish with this agent crew?`;
        } else if (isCodeReview) {
            content = `To provide a focused code review, let me ask:

1. **Focus Area**: What aspect matters most? (Security, Performance, Maintainability, Best practices)
2. **Depth**: Quick scan, standard review, or deep analysis?
3. **Scope**: Specific file, folder, or entire project?

What would you like me to focus on?`;
        } else if (isTestGen) {
            content = `To generate appropriate tests, I need to understand:

1. **Test Type**: Unit tests, integration tests, or edge case coverage?
2. **Coverage Goal**: Critical paths only, 80% coverage, or comprehensive?
3. **Framework**: Any specific testing framework preference?

What type of tests would be most valuable?`;
        } else if (isRefactor) {
            content = `To plan the refactoring effectively:

1. **Goal**: Reduce complexity, improve performance, modernize patterns, or all of the above?
2. **Scope Constraint**: Minimal changes, moderate restructure, or major refactor is OK?
3. **Priority**: What's the most important outcome?

What's driving this refactoring effort?`;
        } else {
            content = `I understand you want to: "${userContent.substring(0, 100)}${userContent.length > 100 ? '...' : ''}"

To help you best, I have a few clarifying questions:

1. What's the primary goal you're trying to achieve?
2. Are there any constraints I should be aware of?
3. What would success look like for this task?

Please share more details so I can provide targeted assistance.`;
        }

        console.log(`[LLMChatService] Using fallback response. Reason: ${reason}`);

        return {
            content,
            inputTokens: 0,
            outputTokens: 0,
            model: 'fallback',
            fromFallback: true
        };
    }

    /**
     * Check if LLM is available (has API key)
     */
    async isAvailable(): Promise<boolean> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return false;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        return new Promise((resolve) => {
            const checkScript = `
import os
import json

api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY')

if not api_key:
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key in ('ANTHROPIC_API_KEY', 'OPENAI_API_KEY'):
                        api_key = value.strip('"').strip("'")
                        break

print(json.dumps({"available": bool(api_key)}))
`;

            cp.execFile(
                pythonPath,
                ['-c', checkScript],
                { cwd: workspaceFolder, timeout: 5000 },
                (error, stdout) => {
                    if (error) {
                        resolve(false);
                        return;
                    }
                    try {
                        const result = JSON.parse(stdout.trim());
                        resolve(result.available === true);
                    } catch {
                        resolve(false);
                    }
                }
            );
        });
    }
}
