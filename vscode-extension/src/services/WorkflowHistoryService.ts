/**
 * Workflow History Service
 *
 * Tracks recent workflow executions for quick re-runs.
 * Part of the "Keyboard Conductor" UX enhancement.
 *
 * Usage:
 *   - Records each workflow run with timestamp and target
 *   - Persists to VSCode globalState
 *   - Provides quick picker for recent workflows (ctrl+shift+e z)
 */

import * as vscode from 'vscode';

/**
 * Represents a single workflow execution record
 */
export interface WorkflowExecution {
    /** Workflow identifier (e.g., 'code-review', 'bug-predict') */
    workflowId: string;
    /** Human-readable name */
    displayName: string;
    /** Target path or scope */
    target: string;
    /** Execution timestamp (ISO string) */
    timestamp: string;
    /** Optional icon for display */
    icon?: string;
}

/**
 * Service for managing workflow execution history
 */
export class WorkflowHistoryService {
    private static instance: WorkflowHistoryService | null = null;
    private context: vscode.ExtensionContext | null = null;
    private readonly STORAGE_KEY = 'empathy.workflowHistory';
    private readonly MAX_HISTORY = 10;

    private constructor() {}

    /**
     * Get the singleton instance
     */
    static getInstance(): WorkflowHistoryService {
        if (!WorkflowHistoryService.instance) {
            WorkflowHistoryService.instance = new WorkflowHistoryService();
        }
        return WorkflowHistoryService.instance;
    }

    /**
     * Initialize with extension context for persistence
     */
    initialize(context: vscode.ExtensionContext): void {
        this.context = context;
    }

    /**
     * Record a workflow execution
     */
    async recordExecution(execution: Omit<WorkflowExecution, 'timestamp'>): Promise<void> {
        if (!this.context) {
            console.warn('WorkflowHistoryService not initialized');
            return;
        }

        const history = this.getHistory();

        const record: WorkflowExecution = {
            ...execution,
            timestamp: new Date().toISOString(),
        };

        // Add to front of array
        history.unshift(record);

        // Trim to max size
        const trimmed = history.slice(0, this.MAX_HISTORY);

        // Persist
        try {
            await this.context.globalState.update(this.STORAGE_KEY, trimmed);
        } catch (error) {
            console.error('[WorkflowHistoryService] Failed to save history:', error);
        }
    }

    /**
     * Get workflow execution history
     */
    getHistory(): WorkflowExecution[] {
        if (!this.context) {
            return [];
        }
        return this.context.globalState.get<WorkflowExecution[]>(this.STORAGE_KEY) || [];
    }

    /**
     * Get most recent execution
     */
    getMostRecent(): WorkflowExecution | null {
        const history = this.getHistory();
        return history.length > 0 ? history[0] : null;
    }

    /**
     * Clear history
     */
    async clearHistory(): Promise<void> {
        if (!this.context) {
            return;
        }
        try {
            await this.context.globalState.update(this.STORAGE_KEY, []);
        } catch (error) {
            console.error('[WorkflowHistoryService] Failed to clear history:', error);
        }
    }

    /**
     * Format relative time (e.g., "2 min ago")
     */
    formatRelativeTime(timestamp: string): string {
        const now = Date.now();
        const then = new Date(timestamp).getTime();
        const diffMs = now - then;

        const minutes = Math.floor(diffMs / 60000);
        const hours = Math.floor(diffMs / 3600000);
        const days = Math.floor(diffMs / 86400000);

        if (minutes < 1) {
            return 'just now';
        } else if (minutes < 60) {
            return `${minutes} min ago`;
        } else if (hours < 24) {
            return `${hours}h ago`;
        } else if (days < 7) {
            return `${days}d ago`;
        } else {
            return new Date(timestamp).toLocaleDateString();
        }
    }

    /**
     * Show quick pick for recent workflows
     */
    async showRecentWorkflowsPicker(): Promise<WorkflowExecution | null> {
        const history = this.getHistory();

        if (history.length === 0) {
            vscode.window.showInformationMessage('No recent workflows. Run a workflow first!');
            return null;
        }

        const items = history.map((exec, index) => ({
            label: `${exec.icon || '$(play)'} ${exec.displayName}`,
            description: exec.target,
            detail: `${this.formatRelativeTime(exec.timestamp)}${index === 0 ? ' (most recent)' : ''}`,
            execution: exec,
        }));

        // Add "Clear History" option at the end
        const clearItem = {
            label: '$(trash) Clear History',
            description: '',
            detail: 'Remove all workflow history',
            execution: null as WorkflowExecution | null,
        };

        const selected = await vscode.window.showQuickPick([...items, clearItem], {
            placeHolder: 'Select a recent workflow to re-run (Ctrl+Shift+E Z)',
            matchOnDescription: true,
            matchOnDetail: true,
        });

        if (!selected) {
            return null;
        }

        if (selected.label.includes('Clear History')) {
            this.clearHistory();
            vscode.window.showInformationMessage('Workflow history cleared');
            return null;
        }

        return selected.execution;
    }
}

/**
 * Workflow metadata for the picker
 */
export const WORKFLOW_METADATA: Record<string, { displayName: string; icon: string }> = {
    'code-review': { displayName: 'Code Review', icon: '$(eye)' },
    'bug-predict': { displayName: 'Bug Prediction', icon: '$(bug)' },
    'security-audit': { displayName: 'Security Audit', icon: '$(shield)' },
    'perf-audit': { displayName: 'Performance Audit', icon: '$(dashboard)' },
    'refactor-plan': { displayName: 'Refactoring Plan', icon: '$(tools)' },
    'health-check': { displayName: 'Health Check', icon: '$(heart)' },
    'pr-review': { displayName: 'PR Review', icon: '$(git-pull-request)' },
    'pro-review': { displayName: 'Code Analysis', icon: '$(code)' },
    'test-gen': { displayName: 'Test Generation', icon: '$(beaker)' },
    'dependency-check': { displayName: 'Dependency Check', icon: '$(package)' },
    'document-gen': { displayName: 'Documentation', icon: '$(book)' },
    'research-synthesis': { displayName: 'Research Synthesis', icon: '$(search)' },
    'release-prep': { displayName: 'Release Prep', icon: '$(rocket)' },
};
