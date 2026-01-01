/**
 * WorkflowRefinementService - Central orchestrator for Socratic workflow refinement
 *
 * Coordinates the refinement flow:
 * 1. Checks if refinement is needed via TriggerAnalyzer
 * 2. Shows QuickPick questions based on workflow type
 * 3. Enhances the workflow input with refined answers
 * 4. Returns enhanced input for execution
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { TriggerAnalyzer, TriggerSource, WorkflowContext, TriggerAnalysisResult } from './TriggerAnalyzer';
import { LLMChatService } from './LLMChatService';
import { WorkflowHistoryService } from './WorkflowHistoryService';
import { PatternLearner, PatternContext, PatternSuggestion } from './PatternLearner';
import { PromptEnhancer } from './PromptEnhancer';

/**
 * Question definition for refinement flow
 */
export interface RefinementQuestion {
    id: string;
    label: string;
    description?: string;
    options: RefinementOption[];
    allowMultiple?: boolean;
}

/**
 * Option for a refinement question
 */
export interface RefinementOption {
    label: string;
    value: string;
    description?: string;
    detail?: string;
}

/**
 * Result of a refinement session
 */
export interface RefinementResult {
    cancelled: boolean;
    answers: Record<string, string | string[]>;
    enhancedInput: string;
    originalInput?: string;
    workflowName: string;
    refinementReason?: string;
}

/**
 * Workflow-specific question sets
 */
const WORKFLOW_QUESTIONS: Record<string, RefinementQuestion[]> = {
    'code-review': [
        {
            id: 'focus',
            label: 'What should I focus on?',
            description: 'Select the primary focus areas for this review',
            options: [
                { label: '🔒 Security', value: 'security', description: 'Check for vulnerabilities and security issues' },
                { label: '⚡ Performance', value: 'performance', description: 'Identify performance bottlenecks' },
                { label: '🔧 Maintainability', value: 'maintainability', description: 'Code quality and maintainability' },
                { label: '📋 Best Practices', value: 'best-practices', description: 'Adherence to coding standards' },
                { label: '🎯 All Areas', value: 'all', description: 'Comprehensive review of all aspects' }
            ]
        },
        {
            id: 'depth',
            label: 'How thorough should the review be?',
            options: [
                { label: '👀 Quick Scan', value: 'quick', description: 'Fast overview, major issues only' },
                { label: '📝 Standard Review', value: 'standard', description: 'Balanced thoroughness' },
                { label: '🔬 Deep Analysis', value: 'deep', description: 'Comprehensive, line-by-line review' }
            ]
        }
    ],
    'test-gen': [
        {
            id: 'testType',
            label: 'What type of tests should I generate?',
            options: [
                { label: '🧪 Unit Tests', value: 'unit', description: 'Test individual functions and methods' },
                { label: '🔗 Integration Tests', value: 'integration', description: 'Test component interactions' },
                { label: '🎯 Edge Cases', value: 'edge-cases', description: 'Focus on boundary conditions' },
                { label: '📦 All Types', value: 'all', description: 'Comprehensive test coverage' }
            ]
        },
        {
            id: 'coverage',
            label: 'What coverage target?',
            options: [
                { label: '🎯 Critical Paths', value: 'critical', description: 'Cover essential code paths only' },
                { label: '📊 80% Coverage', value: '80', description: 'Standard coverage target' },
                { label: '💯 Comprehensive', value: 'comprehensive', description: 'Maximum coverage possible' }
            ]
        }
    ],
    'refactor-plan': [
        {
            id: 'goal',
            label: "What's the refactoring goal?",
            options: [
                { label: '🧹 Reduce Complexity', value: 'complexity', description: 'Simplify convoluted code' },
                { label: '⚡ Improve Performance', value: 'performance', description: 'Optimize for speed/memory' },
                { label: '🏗️ Better Patterns', value: 'patterns', description: 'Apply design patterns' },
                { label: '🔄 Modernize', value: 'modernize', description: 'Update to latest practices' }
            ]
        },
        {
            id: 'scope',
            label: 'What scope constraint?',
            options: [
                { label: '🎯 Minimal Changes', value: 'minimal', description: 'Conservative, low-risk changes' },
                { label: '📐 Moderate Restructure', value: 'moderate', description: 'Balanced refactoring' },
                { label: '🔨 Major Refactor OK', value: 'major', description: 'Significant restructuring allowed' }
            ]
        }
    ],
    'security-audit': [
        {
            id: 'depth',
            label: 'How thorough should the security audit be?',
            options: [
                { label: '👀 Quick Scan', value: 'quick', description: 'Fast OWASP Top 10 check' },
                { label: '📝 Standard Audit', value: 'standard', description: 'Common vulnerabilities' },
                { label: '🔬 Deep Analysis', value: 'deep', description: 'Comprehensive security review' }
            ]
        }
    ],
    'bug-predict': [
        {
            id: 'focus',
            label: 'What types of bugs should I look for?',
            options: [
                { label: '🐛 All Types', value: 'all', description: 'Check for all bug patterns' },
                { label: '💥 Runtime Errors', value: 'runtime', description: 'Focus on crash risks' },
                { label: '🔄 Logic Errors', value: 'logic', description: 'Focus on incorrect behavior' },
                { label: '🧵 Concurrency', value: 'concurrency', description: 'Race conditions and deadlocks' }
            ]
        }
    ],
    'perf-audit': [
        {
            id: 'focus',
            label: 'What performance aspect to analyze?',
            options: [
                { label: '⏱️ Speed', value: 'speed', description: 'Execution time optimization' },
                { label: '💾 Memory', value: 'memory', description: 'Memory usage and leaks' },
                { label: '🔌 I/O', value: 'io', description: 'File and network operations' },
                { label: '📊 All Aspects', value: 'all', description: 'Comprehensive performance review' }
            ]
        }
    ],
    'doc-gen': [
        {
            id: 'style',
            label: 'What documentation style?',
            options: [
                { label: '📚 API Reference', value: 'api', description: 'Technical API documentation' },
                { label: '📖 Tutorial', value: 'tutorial', description: 'How-to guides and tutorials' },
                { label: '📋 README', value: 'readme', description: 'Project overview and setup' },
                { label: '🎯 All Styles', value: 'all', description: 'Comprehensive documentation' }
            ]
        }
    ],
    'pro-review': [
        {
            id: 'focus',
            label: 'What should the professional review focus on?',
            options: [
                { label: '🔒 Security', value: 'security', description: 'Security vulnerabilities' },
                { label: '⚡ Performance', value: 'performance', description: 'Performance optimization' },
                { label: '🏗️ Architecture', value: 'architecture', description: 'Structural patterns' },
                { label: '🎯 All Areas', value: 'all', description: 'Comprehensive review' }
            ]
        },
        {
            id: 'depth',
            label: 'Review depth?',
            options: [
                { label: '👀 Quick', value: 'quick', description: 'Fast high-level review' },
                { label: '📝 Standard', value: 'standard', description: 'Balanced review' },
                { label: '🔬 Deep', value: 'deep', description: 'Line-by-line analysis' }
            ]
        },
        {
            id: 'priority',
            label: 'What to prioritize in findings?',
            options: [
                { label: '🚨 Critical Only', value: 'critical', description: 'Only blocking issues' },
                { label: '⚠️ Important+', value: 'important', description: 'Important and critical' },
                { label: '📋 All Findings', value: 'all', description: 'Include suggestions' }
            ]
        }
    ],
    'secure-release': [
        {
            id: 'scope',
            label: 'What scope for the secure release check?',
            options: [
                { label: '🔒 Security Only', value: 'security', description: 'Focus on security aspects' },
                { label: '📋 Full Pipeline', value: 'full', description: 'Complete release validation' },
                { label: '🎯 Critical Paths', value: 'critical', description: 'Critical components only' }
            ]
        }
    ],
    'doc-orchestrator': [
        {
            id: 'scope',
            label: 'What documentation scope?',
            options: [
                { label: '📄 Single File', value: 'file', description: 'Document one file' },
                { label: '📁 Directory', value: 'directory', description: 'Document a folder' },
                { label: '📚 Full Project', value: 'project', description: 'Complete project docs' }
            ]
        },
        {
            id: 'style',
            label: 'Documentation style?',
            options: [
                { label: '📋 Technical', value: 'technical', description: 'Developer-focused' },
                { label: '📖 User Guide', value: 'user', description: 'End-user focused' },
                { label: '🎓 Tutorial', value: 'tutorial', description: 'Learning-focused' }
            ]
        }
    ]
};

/**
 * WorkflowRefinementService - Singleton orchestrator for Socratic refinement
 */
export class WorkflowRefinementService {
    private static instance: WorkflowRefinementService;
    private triggerAnalyzer: TriggerAnalyzer;
    private llmService: LLMChatService;
    private patternLearner: PatternLearner;
    private promptEnhancer: PromptEnhancer;
    private historyService: WorkflowHistoryService | null = null;
    private context: vscode.ExtensionContext | null = null;

    private constructor() {
        this.triggerAnalyzer = TriggerAnalyzer.getInstance();
        this.llmService = LLMChatService.getInstance();
        this.patternLearner = PatternLearner.getInstance();
        this.promptEnhancer = PromptEnhancer.getInstance();
    }

    static getInstance(): WorkflowRefinementService {
        if (!WorkflowRefinementService.instance) {
            WorkflowRefinementService.instance = new WorkflowRefinementService();
        }
        return WorkflowRefinementService.instance;
    }

    /**
     * Initialize with extension context
     */
    initialize(context: vscode.ExtensionContext, historyService?: WorkflowHistoryService): void {
        this.context = context;
        this.llmService.initialize(context);
        this.patternLearner.initialize(context);
        if (historyService) {
            this.historyService = historyService;
            this.triggerAnalyzer.initialize(historyService);
        }
    }

    /**
     * Check if refinement should be shown for a workflow
     */
    async shouldRefine(
        workflowName: string,
        input?: string,
        triggerSource: TriggerSource = 'dashboard'
    ): Promise<TriggerAnalysisResult> {
        const workflowContext = await this.triggerAnalyzer.gatherContext(
            workflowName,
            input,
            triggerSource
        );
        return this.triggerAnalyzer.analyze(workflowContext);
    }

    /**
     * Run the refinement flow for a workflow
     */
    async refine(
        workflowName: string,
        input?: string,
        triggerSource: TriggerSource = 'dashboard'
    ): Promise<RefinementResult> {
        const analysisResult = await this.shouldRefine(workflowName, input, triggerSource);

        if (!analysisResult.shouldRefine) {
            return {
                cancelled: false,
                answers: {},
                enhancedInput: input || '',
                originalInput: input,
                workflowName
            };
        }

        // Get questions for this workflow
        const questions = this.getQuestionsForWorkflow(workflowName);

        if (questions.length === 0) {
            return {
                cancelled: false,
                answers: {},
                enhancedInput: input || '',
                originalInput: input,
                workflowName,
                refinementReason: 'No questions defined for workflow'
            };
        }

        // Build pattern context
        const patternContext = this.buildPatternContext(workflowName, input);

        // Check for existing patterns
        const existingPattern = this.patternLearner.getBestMatch(patternContext);
        if (existingPattern && existingPattern.confidence >= 0.8) {
            // Offer to use existing pattern
            const usePattern = await this.offerExistingPattern(workflowName, existingPattern);
            if (usePattern === 'use') {
                // Use the existing pattern's refinements
                await this.patternLearner.recordUsage(existingPattern.pattern.id);
                const enhancedInput = this.enhanceInput(workflowName, input, existingPattern.pattern.refinements);
                return {
                    cancelled: false,
                    answers: existingPattern.pattern.refinements,
                    enhancedInput,
                    originalInput: input,
                    workflowName,
                    refinementReason: 'Used learned pattern'
                };
            } else if (usePattern === 'cancel') {
                return {
                    cancelled: true,
                    answers: {},
                    enhancedInput: input || '',
                    originalInput: input,
                    workflowName
                };
            }
            // If 'new', continue with questions
        }

        // Show QuickPick questions
        const answers = await this.showQuickPickQuestions(workflowName, questions);

        if (answers === null) {
            return {
                cancelled: true,
                answers: {},
                enhancedInput: input || '',
                originalInput: input,
                workflowName
            };
        }

        // Enhance the input with answers
        const enhancedInput = this.enhanceInput(workflowName, input, answers);

        // Show review before run (if enabled)
        const config = vscode.workspace.getConfiguration('empathy');
        const showReview = config.get<boolean>('socraticRefinement.showReviewBeforeRun', true);

        if (showReview) {
            const proceed = await this.showReviewConfirmation(workflowName, answers, enhancedInput);
            if (!proceed) {
                return {
                    cancelled: true,
                    answers,
                    enhancedInput,
                    originalInput: input,
                    workflowName
                };
            }
        }

        // Learn the pattern for future use
        await this.patternLearner.learn(patternContext, answers);

        return {
            cancelled: false,
            answers,
            enhancedInput,
            originalInput: input,
            workflowName,
            refinementReason: analysisResult.reason
        };
    }

    /**
     * Build pattern context from workflow and input
     */
    private buildPatternContext(workflowName: string, input?: string): PatternContext {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        let targetPath: string | undefined;
        if (input) {
            try {
                const parsed = JSON.parse(input);
                targetPath = parsed.target || parsed.path || parsed.diff;
            } catch {
                targetPath = input;
            }
        }

        return {
            workflowName,
            targetPath,
            folderName: targetPath ? path.basename(path.dirname(targetPath)) : undefined,
            projectType: workspaceFolder ? PatternLearner.detectProjectType(workspaceFolder) : undefined,
            fileTypes: targetPath ? PatternLearner.detectFileTypes(targetPath) : undefined
        };
    }

    /**
     * Offer to use an existing learned pattern
     */
    private async offerExistingPattern(
        workflowName: string,
        suggestion: PatternSuggestion
    ): Promise<'use' | 'new' | 'cancel'> {
        const displayName = this.getWorkflowDisplayName(workflowName);
        const refinementSummary = Object.entries(suggestion.pattern.refinements)
            .map(([key, value]) => `${this.formatAnswerKey(key)}: ${value}`)
            .join(', ');

        const result = await vscode.window.showQuickPick(
            [
                {
                    label: '$(history) Use Previous Settings',
                    description: refinementSummary,
                    detail: `Used ${suggestion.pattern.usageCount} times (${Math.round(suggestion.confidence * 100)}% match)`,
                    value: 'use' as const
                },
                {
                    label: '$(add) Choose New Settings',
                    description: 'Answer questions to customize this run',
                    value: 'new' as const
                },
                {
                    label: '$(close) Cancel',
                    description: 'Cancel workflow execution',
                    value: 'cancel' as const
                }
            ],
            {
                title: `${displayName} - Previous Settings Found`,
                placeHolder: 'Use previous settings or choose new ones?'
            }
        );

        return result?.value || 'cancel';
    }

    /**
     * Get questions for a specific workflow
     */
    private getQuestionsForWorkflow(workflowName: string): RefinementQuestion[] {
        return WORKFLOW_QUESTIONS[workflowName] || [];
    }

    /**
     * Show QuickPick questions and collect answers
     */
    private async showQuickPickQuestions(
        workflowName: string,
        questions: RefinementQuestion[]
    ): Promise<Record<string, string | string[]> | null> {
        const answers: Record<string, string | string[]> = {};

        for (const question of questions) {
            const items: vscode.QuickPickItem[] = question.options.map(opt => ({
                label: opt.label,
                description: opt.description,
                detail: opt.detail
            }));

            // Add skip option
            items.push({
                label: '$(arrow-right) Skip',
                description: 'Use default for this question'
            });

            const selected = await vscode.window.showQuickPick(items, {
                title: `${this.getWorkflowDisplayName(workflowName)} Refinement`,
                placeHolder: question.label,
                ignoreFocusOut: true,
                matchOnDescription: true,
                matchOnDetail: true
            });

            if (selected === undefined) {
                // User cancelled
                return null;
            }

            if (selected.label !== '$(arrow-right) Skip') {
                // Find the option value
                const option = question.options.find(opt => opt.label === selected.label);
                if (option) {
                    answers[question.id] = option.value;
                }
            }
        }

        return answers;
    }

    /**
     * Enhance workflow input with refined answers and XML-enhanced prompt
     */
    private enhanceInput(
        workflowName: string,
        originalInput: string | undefined,
        answers: Record<string, string | string[]>
    ): string {
        // Parse original input
        let inputObj: Record<string, unknown> = {};
        if (originalInput) {
            try {
                inputObj = JSON.parse(originalInput);
            } catch {
                // If not JSON, treat as target path
                inputObj = { target: originalInput };
            }
        }

        // Convert answers to RefinementContext for PromptEnhancer
        const refinementContext: Record<string, string | string[] | undefined> = {};
        for (const [key, value] of Object.entries(answers)) {
            refinementContext[key] = value;
        }

        // Generate XML-enhanced prompt using PromptEnhancer
        const enhancedPrompt = this.promptEnhancer.enhance(workflowName, refinementContext);

        // Add refinement context with XML prompt
        inputObj.refinement = {
            ...answers,
            timestamp: new Date().toISOString(),
            xmlPrompt: enhancedPrompt.xmlString,
            enhancements: enhancedPrompt.enhancements
        };

        // Add the XML prompt as a top-level field for workflows to use directly
        inputObj.enhanced_prompt = enhancedPrompt.xmlString;

        // Also add specific fields for backwards compatibility
        if (answers.focus) {
            inputObj.focus = answers.focus;
        }
        if (answers.depth) {
            inputObj.depth = answers.depth;
        }
        if (answers.scope) {
            inputObj.scope = answers.scope;
        }
        if (answers.testType) {
            inputObj.testType = answers.testType;
        }
        if (answers.coverage) {
            inputObj.coverage = answers.coverage;
        }
        if (answers.goal) {
            inputObj.goal = answers.goal;
        }
        if (answers.style) {
            inputObj.style = answers.style;
        }
        if (answers.priority) {
            inputObj.priority = answers.priority;
        }

        console.log(`[WorkflowRefinement] Generated XML-enhanced prompt with ${enhancedPrompt.enhancements.length} enhancements`);
        return JSON.stringify(inputObj);
    }

    /**
     * Show review confirmation before running
     */
    private async showReviewConfirmation(
        workflowName: string,
        answers: Record<string, string | string[]>,
        enhancedInput: string
    ): Promise<boolean> {
        const displayName = this.getWorkflowDisplayName(workflowName);

        // Build summary
        const answerSummary = Object.entries(answers)
            .map(([key, value]) => `• ${this.formatAnswerKey(key)}: ${value}`)
            .join('\n');

        const message = `Run ${displayName} with these settings?\n\n${answerSummary}`;

        const result = await vscode.window.showInformationMessage(
            message,
            { modal: true },
            'Run Workflow',
            'Edit Settings',
            'Cancel'
        );

        if (result === 'Run Workflow') {
            return true;
        } else if (result === 'Edit Settings') {
            // Re-run refinement
            const questions = this.getQuestionsForWorkflow(workflowName);
            const newAnswers = await this.showQuickPickQuestions(workflowName, questions);
            if (newAnswers !== null) {
                // Recursively confirm with new answers
                const newEnhancedInput = this.enhanceInput(workflowName, enhancedInput, newAnswers);
                return this.showReviewConfirmation(workflowName, newAnswers, newEnhancedInput);
            }
            return false;
        }

        return false;
    }

    /**
     * Get display name for workflow
     */
    private getWorkflowDisplayName(workflowName: string): string {
        const displayNames: Record<string, string> = {
            'code-review': 'Code Review',
            'test-gen': 'Test Generation',
            'refactor-plan': 'Refactor Plan',
            'security-audit': 'Security Audit',
            'bug-predict': 'Bug Prediction',
            'perf-audit': 'Performance Audit',
            'doc-gen': 'Documentation',
            'pro-review': 'Professional Review',
            'secure-release': 'Secure Release',
            'doc-orchestrator': 'Documentation Orchestrator'
        };
        return displayNames[workflowName] || workflowName;
    }

    /**
     * Format answer key for display
     */
    private formatAnswerKey(key: string): string {
        const keyLabels: Record<string, string> = {
            focus: 'Focus',
            depth: 'Depth',
            scope: 'Scope',
            testType: 'Test Type',
            coverage: 'Coverage',
            goal: 'Goal',
            style: 'Style',
            priority: 'Priority'
        };
        return keyLabels[key] || key;
    }

    /**
     * Get available questions for a workflow (for external use)
     */
    getAvailableQuestions(workflowName: string): RefinementQuestion[] {
        return WORKFLOW_QUESTIONS[workflowName] || [];
    }

    /**
     * Check if a workflow supports refinement
     */
    supportsRefinement(workflowName: string): boolean {
        return workflowName in WORKFLOW_QUESTIONS && WORKFLOW_QUESTIONS[workflowName].length > 0;
    }

    /**
     * Get all workflows that support refinement
     */
    getRefinableWorkflows(): string[] {
        return Object.keys(WORKFLOW_QUESTIONS);
    }
}
