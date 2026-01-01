/**
 * TriggerAnalyzer - Determines when Socratic refinement should be shown
 *
 * Analyzes workflow context to decide if clarifying questions are needed.
 * Considers: input ambiguity, workflow cost tier, stage complexity, and history.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import { WorkflowHistoryService } from './WorkflowHistoryService';

/**
 * Workflow tier classification based on model cost
 */
export type WorkflowTier = 'cheap' | 'capable' | 'premium';

/**
 * Source of the workflow trigger
 */
export type TriggerSource = 'dashboard' | 'context-menu' | 'command-palette' | 'keyboard' | 'history';

/**
 * Context gathered about the workflow execution
 */
export interface WorkflowContext {
    workflowName: string;
    targetPath?: string;
    activeEditorFile?: string;
    scope: 'file' | 'folder' | 'project' | 'unknown';
    triggerSource: TriggerSource;
    isFromHistory: boolean;
    hasExplicitTarget: boolean;
}

/**
 * Result of trigger analysis
 */
export interface TriggerAnalysisResult {
    shouldRefine: boolean;
    reason: string;
    suggestedQuestions: string[];
    confidence: 'high' | 'medium' | 'low';
}

/**
 * Workflow metadata for trigger decisions
 */
interface WorkflowMetadata {
    tier: WorkflowTier;
    stageCount: number;
    description: string;
    defaultQuestions: string[];
}

/**
 * Workflow registry with tier and stage information
 */
const WORKFLOW_METADATA: Record<string, WorkflowMetadata> = {
    'code-review': {
        tier: 'premium',
        stageCount: 4,
        description: 'Multi-stage code review with architectural analysis',
        defaultQuestions: ['focus', 'depth']
    },
    'test-gen': {
        tier: 'capable',
        stageCount: 3,
        description: 'Test generation with coverage analysis',
        defaultQuestions: ['testType', 'coverage']
    },
    'refactor-plan': {
        tier: 'premium',
        stageCount: 3,
        description: 'Refactoring strategy with impact analysis',
        defaultQuestions: ['goal', 'scope']
    },
    'security-audit': {
        tier: 'capable',
        stageCount: 2,
        description: 'Security vulnerability scanning',
        defaultQuestions: ['depth']
    },
    'bug-predict': {
        tier: 'capable',
        stageCount: 2,
        description: 'Bug prediction analysis',
        defaultQuestions: ['focus']
    },
    'perf-audit': {
        tier: 'capable',
        stageCount: 2,
        description: 'Performance analysis',
        defaultQuestions: ['focus']
    },
    'doc-gen': {
        tier: 'capable',
        stageCount: 2,
        description: 'Documentation generation',
        defaultQuestions: ['style']
    },
    'pro-review': {
        tier: 'premium',
        stageCount: 4,
        description: 'Professional code review pipeline',
        defaultQuestions: ['focus', 'depth', 'priority']
    },
    'secure-release': {
        tier: 'premium',
        stageCount: 5,
        description: 'Secure release pipeline',
        defaultQuestions: ['scope']
    },
    'doc-orchestrator': {
        tier: 'capable',
        stageCount: 3,
        description: 'Documentation orchestration',
        defaultQuestions: ['scope', 'style']
    },
    'health-check': {
        tier: 'cheap',
        stageCount: 1,
        description: 'Quick health check',
        defaultQuestions: []
    },
    'morning': {
        tier: 'cheap',
        stageCount: 1,
        description: 'Morning briefing',
        defaultQuestions: []
    },
    'ship': {
        tier: 'cheap',
        stageCount: 1,
        description: 'Pre-ship checklist',
        defaultQuestions: []
    },
    'fix-all': {
        tier: 'cheap',
        stageCount: 1,
        description: 'Fix all issues',
        defaultQuestions: []
    }
};

/**
 * TriggerAnalyzer - Singleton service for analyzing workflow triggers
 */
export class TriggerAnalyzer {
    private static instance: TriggerAnalyzer;
    private historyService: WorkflowHistoryService | null = null;

    private constructor() {}

    static getInstance(): TriggerAnalyzer {
        if (!TriggerAnalyzer.instance) {
            TriggerAnalyzer.instance = new TriggerAnalyzer();
        }
        return TriggerAnalyzer.instance;
    }

    /**
     * Initialize with history service
     */
    initialize(historyService: WorkflowHistoryService): void {
        this.historyService = historyService;
    }

    /**
     * Gather context about the current workflow execution
     */
    async gatherContext(
        workflowName: string,
        input?: string,
        triggerSource: TriggerSource = 'dashboard'
    ): Promise<WorkflowContext> {
        const activeEditor = vscode.window.activeTextEditor;
        const activeFile = activeEditor?.document.uri.fsPath;

        // Parse input to determine target
        let targetPath: string | undefined;
        let hasExplicitTarget = false;

        if (input) {
            try {
                const parsed = JSON.parse(input);
                targetPath = parsed.target || parsed.path || parsed.diff;
                hasExplicitTarget = !!targetPath && targetPath !== '.' && targetPath !== './';
            } catch {
                // Input is not JSON, might be a direct path
                if (input !== '.' && input !== './') {
                    targetPath = input;
                    hasExplicitTarget = true;
                }
            }
        }

        // Determine scope
        let scope: 'file' | 'folder' | 'project' | 'unknown' = 'unknown';
        if (hasExplicitTarget && targetPath) {
            // Check if it's a file or folder
            try {
                const uri = vscode.Uri.file(targetPath);
                const stat = await vscode.workspace.fs.stat(uri);
                scope = stat.type === vscode.FileType.Directory ? 'folder' : 'file';
            } catch {
                // Can't stat, assume based on path
                scope = targetPath.includes('.') ? 'file' : 'folder';
            }
        } else if (!targetPath || targetPath === '.' || targetPath === './') {
            scope = 'project';
        }

        // Check history
        const isFromHistory = triggerSource === 'history';

        return {
            workflowName,
            targetPath,
            activeEditorFile: activeFile,
            scope,
            triggerSource,
            isFromHistory,
            hasExplicitTarget
        };
    }

    /**
     * Analyze whether refinement should be shown
     */
    analyze(context: WorkflowContext): TriggerAnalysisResult {
        const metadata = WORKFLOW_METADATA[context.workflowName];

        // Check if refinement is enabled in settings
        const config = vscode.workspace.getConfiguration('empathy');
        const refinementEnabled = config.get<boolean>('socraticRefinement.enabled', true);

        if (!refinementEnabled) {
            return {
                shouldRefine: false,
                reason: 'Refinement disabled in settings',
                suggestedQuestions: [],
                confidence: 'high'
            };
        }

        // Unknown workflow - skip refinement
        if (!metadata) {
            return {
                shouldRefine: false,
                reason: 'Unknown workflow',
                suggestedQuestions: [],
                confidence: 'high'
            };
        }

        // No default questions defined - skip refinement
        if (metadata.defaultQuestions.length === 0) {
            return {
                shouldRefine: false,
                reason: 'Workflow does not require refinement',
                suggestedQuestions: [],
                confidence: 'high'
            };
        }

        // Check skip conditions
        const skipConditions = this.checkSkipConditions(context, metadata);
        if (skipConditions.shouldSkip) {
            return {
                shouldRefine: false,
                reason: skipConditions.reason,
                suggestedQuestions: [],
                confidence: skipConditions.confidence
            };
        }

        // Check trigger conditions
        const triggerConditions = this.checkTriggerConditions(context, metadata);

        return {
            shouldRefine: triggerConditions.shouldTrigger,
            reason: triggerConditions.reason,
            suggestedQuestions: metadata.defaultQuestions,
            confidence: triggerConditions.confidence
        };
    }

    /**
     * Check conditions that should skip refinement
     */
    private checkSkipConditions(
        context: WorkflowContext,
        metadata: WorkflowMetadata
    ): { shouldSkip: boolean; reason: string; confidence: 'high' | 'medium' | 'low' } {
        // Skip if from context menu with explicit file target
        const skipForContextMenu = vscode.workspace.getConfiguration('empathy')
            .get<boolean>('socraticRefinement.skipForContextMenu', true);

        if (
            skipForContextMenu &&
            context.triggerSource === 'context-menu' &&
            context.scope === 'file' &&
            context.hasExplicitTarget
        ) {
            return {
                shouldSkip: true,
                reason: 'Context menu with explicit file target',
                confidence: 'high'
            };
        }

        // Skip if re-running from history
        if (context.isFromHistory) {
            return {
                shouldSkip: true,
                reason: 'Re-running from history',
                confidence: 'high'
            };
        }

        // Skip cheap tier workflows - refinement overhead not worth it for quick tasks
        if (metadata.tier === 'cheap') {
            return {
                shouldSkip: true,
                reason: 'Low-cost workflow - refinement not efficient',
                confidence: 'high'
            };
        }

        return { shouldSkip: false, reason: '', confidence: 'high' };
    }

    /**
     * Check conditions that should trigger refinement
     */
    private checkTriggerConditions(
        context: WorkflowContext,
        metadata: WorkflowMetadata
    ): { shouldTrigger: boolean; reason: string; confidence: 'high' | 'medium' | 'low' } {
        const triggers: { condition: boolean; reason: string; weight: number }[] = [];

        // Condition 1: Workflow has refinement questions (always triggers for all tiers)
        // This ensures ALL workflows with questions offer refinement, not just premium
        if (metadata.defaultQuestions.length > 0) {
            triggers.push({
                condition: true,
                reason: 'Workflow supports refinement for better results',
                weight: 2
            });
        }

        // Condition 2: Ambiguous input (project-wide or no target) - adds extra weight
        if (context.scope === 'project' || !context.hasExplicitTarget) {
            triggers.push({
                condition: true,
                reason: 'Ambiguous scope - clarification recommended',
                weight: 1
            });
        }

        // Condition 3: Premium tier workflow - adds extra weight for cost efficiency
        if (metadata.tier === 'premium') {
            triggers.push({
                condition: true,
                reason: 'Premium tier - refinement improves cost efficiency',
                weight: 1
            });
        }

        // Condition 4: Complex multi-stage workflow (3+ stages)
        if (metadata.stageCount >= 3) {
            triggers.push({
                condition: true,
                reason: 'Multi-stage workflow - upfront clarity reduces wasted stages',
                weight: 1
            });
        }

        // Condition 5: No active editor and no explicit target - critical context missing
        if (!context.activeEditorFile && !context.hasExplicitTarget) {
            triggers.push({
                condition: true,
                reason: 'No context available - need to specify target',
                weight: 2
            });
        }

        // Calculate total weight
        const totalWeight = triggers.reduce((sum, t) => sum + (t.condition ? t.weight : 0), 0);
        const activeReasons = triggers.filter(t => t.condition).map(t => t.reason);

        // Threshold: trigger if weight >= 2
        if (totalWeight >= 2) {
            return {
                shouldTrigger: true,
                reason: activeReasons.join('; '),
                confidence: totalWeight >= 4 ? 'high' : 'medium'
            };
        }

        return {
            shouldTrigger: false,
            reason: 'Context is clear - no refinement needed',
            confidence: 'medium'
        };
    }

    /**
     * Get workflow metadata
     */
    getWorkflowMetadata(workflowName: string): WorkflowMetadata | undefined {
        return WORKFLOW_METADATA[workflowName];
    }

    /**
     * Get all refinable workflows
     */
    getRefinableWorkflows(): string[] {
        return Object.entries(WORKFLOW_METADATA)
            .filter(([_, meta]) => meta.defaultQuestions.length > 0)
            .map(([name]) => name);
    }
}
