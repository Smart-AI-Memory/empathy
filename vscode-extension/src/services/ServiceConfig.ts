/**
 * ServiceConfig - Centralized configuration for Empathy services
 *
 * Consolidates magic numbers and configurable values from all services.
 * Values can be overridden via VSCode settings (empathy.*).
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';

/**
 * Configuration values for all Empathy services
 */
export class ServiceConfig {
    // Pattern Learner Configuration
    static readonly PATTERN_MAX_PATTERNS = 100;
    static readonly PATTERN_TTL_DAYS = 90;
    static readonly PATTERN_PRUNE_PERCENTAGE = 0.1; // Remove bottom 10%

    // Workflow History Configuration
    static readonly HISTORY_MAX_ENTRIES = 50;

    // LLM Chat Service Configuration
    static readonly LLM_MAX_BUFFER_SIZE = 1024 * 1024; // 1MB
    static readonly LLM_TIMEOUT_MS = 60000; // 60 seconds
    static readonly LLM_DEFAULT_MAX_TOKENS = 1024;
    static readonly LLM_DEFAULT_TEMPERATURE = 0.7;

    // Cost Estimator Configuration
    static readonly COST_CHARS_TO_TOKENS_RATIO = 0.25; // 1 char ≈ 0.25 tokens
    static readonly COST_OUTPUT_TO_INPUT_RATIO = 0.3; // Output is 30% of input

    // Context Builder Configuration
    static readonly CONTEXT_MAX_FILES_TO_SCAN = 50;

    // Socratic Form Configuration
    static readonly SOCRATIC_MAX_CONVERSATIONS = 20;
    static readonly SOCRATIC_CONVERSATION_TTL_DAYS = 30;

    /**
     * Get configuration value from VSCode settings with fallback
     */
    private static getConfig<T>(key: string, defaultValue: T): T {
        const config = vscode.workspace.getConfiguration('empathy');
        return config.get<T>(key, defaultValue);
    }

    /**
     * Pattern Learner: Maximum number of patterns to store
     */
    static get patternMaxPatterns(): number {
        return this.getConfig('pattern.maxPatterns', this.PATTERN_MAX_PATTERNS);
    }

    /**
     * Pattern Learner: Pattern time-to-live in days
     */
    static get patternTTLDays(): number {
        return this.getConfig('pattern.ttlDays', this.PATTERN_TTL_DAYS);
    }

    /**
     * Workflow History: Maximum history entries
     */
    static get historyMaxEntries(): number {
        return this.getConfig('history.maxEntries', this.HISTORY_MAX_ENTRIES);
    }

    /**
     * LLM Chat: Request timeout in milliseconds
     */
    static get llmTimeoutMs(): number {
        return this.getConfig('llm.timeoutMs', this.LLM_TIMEOUT_MS);
    }

    /**
     * LLM Chat: Default max tokens per request
     */
    static get llmDefaultMaxTokens(): number {
        return this.getConfig('llm.defaultMaxTokens', this.LLM_DEFAULT_MAX_TOKENS);
    }

    /**
     * LLM Chat: Default temperature
     */
    static get llmDefaultTemperature(): number {
        return this.getConfig('llm.defaultTemperature', this.LLM_DEFAULT_TEMPERATURE);
    }

    /**
     * Context Builder: Maximum files to scan for type detection
     */
    static get contextMaxFilesToScan(): number {
        return this.getConfig('context.maxFilesToScan', this.CONTEXT_MAX_FILES_TO_SCAN);
    }

    /**
     * Socratic Form: Maximum conversations to store
     */
    static get socraticMaxConversations(): number {
        return this.getConfig('socratic.maxConversations', this.SOCRATIC_MAX_CONVERSATIONS);
    }

    /**
     * Socratic Form: Conversation time-to-live in days
     */
    static get socraticConversationTTLDays(): number {
        return this.getConfig('socratic.conversationTTLDays', this.SOCRATIC_CONVERSATION_TTL_DAYS);
    }
}
