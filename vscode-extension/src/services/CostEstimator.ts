/**
 * Cost Estimator Service
 *
 * Provides cost estimates for workflows based on file size and model tier.
 * Used for displaying cost information in workflow suggestions.
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

export interface CostEstimate {
    estimatedCost: number;
    tokenEstimate: number;
    tier: 'cheap' | 'capable' | 'premium';
}

export class CostEstimator {
    // Token costs per 1K tokens (input and output)
    // Based on current pricing as of 2025
    private static readonly TOKEN_COST_PER_1K = {
        cheap: {
            input: 0.00025,  // GPT-4o-mini / Haiku input
            output: 0.00125, // GPT-4o-mini / Haiku output
        },
        capable: {
            input: 0.003,  // GPT-4o / Sonnet input
            output: 0.015, // GPT-4o / Sonnet output
        },
        premium: {
            input: 0.015,  // o1 / Opus input
            output: 0.075, // o1 / Opus output
        },
    };

    // Default tier assignments for workflows
    private static readonly WORKFLOW_TIER_MAP: Record<string, 'cheap' | 'capable' | 'premium'> = {
        'code-review': 'premium',
        'refactor-plan': 'capable',
        'test-gen': 'capable',
        'debug': 'capable',
        'security-scan': 'capable',
        'bug-predict': 'cheap',
        'health-check': 'cheap',
        'doc-orchestrator': 'capable',
        'pr-review': 'premium',
        'pro-review': 'premium',
    };

    /**
     * Estimate cost for a workflow based on file size
     *
     * @param workflowName - Name of the workflow
     * @param fileSize - Size of input in characters
     * @param tier - Optional tier override (defaults to workflow's default tier)
     * @returns Cost estimate with breakdown
     */
    static estimateWorkflowCost(
        workflowName: string,
        fileSize: number,
        tier?: 'cheap' | 'capable' | 'premium'
    ): CostEstimate {
        // Determine tier to use
        const workflowTier = tier || this.getDefaultTier(workflowName);

        // Convert characters to tokens (rough heuristic: 1 char ≈ 0.25 tokens)
        const inputTokens = Math.ceil(fileSize * 0.25);

        // Estimate output tokens (assume 30% of input for most workflows)
        // Some workflows like refactor-plan may generate more, but this is a reasonable average
        const outputTokens = Math.ceil(inputTokens * 0.3);

        // Get cost rates for this tier
        const costs = this.TOKEN_COST_PER_1K[workflowTier];

        // Calculate total cost
        const inputCost = (inputTokens / 1000) * costs.input;
        const outputCost = (outputTokens / 1000) * costs.output;
        const totalCost = inputCost + outputCost;

        // Round to nearest cent
        const estimatedCost = Math.ceil(totalCost * 100) / 100;

        return {
            estimatedCost,
            tokenEstimate: inputTokens + outputTokens,
            tier: workflowTier,
        };
    }

    /**
     * Estimate cost for multiple files
     *
     * @param workflowName - Name of the workflow
     * @param fileSizes - Array of file sizes in characters
     * @param tier - Optional tier override
     * @returns Combined cost estimate
     */
    static estimateBatchCost(
        workflowName: string,
        fileSizes: number[],
        tier?: 'cheap' | 'capable' | 'premium'
    ): CostEstimate {
        const totalSize = fileSizes.reduce((sum, size) => sum + size, 0);
        return this.estimateWorkflowCost(workflowName, totalSize, tier);
    }

    /**
     * Get the default tier for a workflow
     *
     * @param workflowName - Name of the workflow
     * @returns Default tier ('cheap', 'capable', or 'premium')
     */
    static getDefaultTier(workflowName: string): 'cheap' | 'capable' | 'premium' {
        return this.WORKFLOW_TIER_MAP[workflowName] || 'capable';
    }

    /**
     * Format cost as a user-friendly string
     *
     * @param cost - Cost in dollars
     * @returns Formatted cost string (e.g., "$0.05", "<$0.01")
     */
    static formatCost(cost: number): string {
        if (cost < 0.01) {
            return '<$0.01';
        }
        return `$${cost.toFixed(2)}`;
    }

    /**
     * Get cost breakdown by tier for a given file size
     *
     * @param fileSize - Size of input in characters
     * @returns Cost estimates for all three tiers
     */
    static getCostBreakdown(fileSize: number): {
        cheap: number;
        capable: number;
        premium: number;
    } {
        return {
            cheap: this.estimateWorkflowCost('generic', fileSize, 'cheap').estimatedCost,
            capable: this.estimateWorkflowCost('generic', fileSize, 'capable').estimatedCost,
            premium: this.estimateWorkflowCost('generic', fileSize, 'premium').estimatedCost,
        };
    }

    /**
     * Calculate potential savings from using cheaper tier
     *
     * @param workflowName - Name of the workflow
     * @param fileSize - Size of input in characters
     * @param fromTier - Current tier
     * @param toTier - Target tier
     * @returns Savings amount and percentage
     */
    static calculateSavings(
        workflowName: string,
        fileSize: number,
        fromTier: 'cheap' | 'capable' | 'premium',
        toTier: 'cheap' | 'capable' | 'premium'
    ): { amount: number; percentage: number } {
        const fromCost = this.estimateWorkflowCost(workflowName, fileSize, fromTier).estimatedCost;
        const toCost = this.estimateWorkflowCost(workflowName, fileSize, toTier).estimatedCost;

        const amount = fromCost - toCost;
        const percentage = fromCost > 0 ? Math.round((amount / fromCost) * 100) : 0;

        return { amount, percentage };
    }

    /**
     * Estimate monthly cost based on usage patterns
     *
     * @param workflowUsage - Map of workflow name to monthly run count
     * @param averageFileSize - Average file size in characters
     * @returns Estimated monthly cost
     */
    static estimateMonthlyCost(
        workflowUsage: Record<string, number>,
        averageFileSize: number = 5000
    ): number {
        let totalCost = 0;

        for (const [workflowName, runCount] of Object.entries(workflowUsage)) {
            const estimate = this.estimateWorkflowCost(workflowName, averageFileSize);
            totalCost += estimate.estimatedCost * runCount;
        }

        return Math.ceil(totalCost * 100) / 100;
    }
}
