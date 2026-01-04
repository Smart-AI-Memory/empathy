/**
 * Workflow Data Service
 *
 * Centralized service for loading and caching workflow execution history.
 * Provides singleton pattern with 30-second cache to prevent redundant file reads.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as fs from 'fs';
import * as path from 'path';

// =============================================================================
// Types
// =============================================================================

// XML-enhanced finding from parsed response
export interface XmlFinding {
    severity: string;
    title: string;
    location: string | null;
    details: string;
    fix: string;
}

export interface WorkflowRunData {
    workflow: string;
    success: boolean;
    cost: number;
    savings: number;
    timestamp: string;
    // XML-enhanced fields (optional)
    xml_parsed?: boolean;
    summary?: string;
    findings?: XmlFinding[];
    checklist?: string[];
}

export interface WorkflowData {
    totalRuns: number;
    successfulRuns: number;
    totalCost: number;
    totalSavings: number;
    recentRuns: WorkflowRunData[];
    byWorkflow: Record<string, { runs: number; cost: number; savings: number }>;
}

export interface WorkflowSummary {
    totalRuns: number;
    successfulRuns: number;
    successRate: number;
    totalCost: number;
}

// =============================================================================
// Service
// =============================================================================

export class WorkflowDataService {
    private static _instance: WorkflowDataService | null = null;
    private _cache: WorkflowData | null = null;
    private _cacheTime: number = 0;
    private readonly CACHE_TTL = 30000; // 30 seconds

    public static getInstance(): WorkflowDataService {
        if (!WorkflowDataService._instance) {
            WorkflowDataService._instance = new WorkflowDataService();
        }
        return WorkflowDataService._instance;
    }

    private constructor() {
        // Private constructor for singleton
    }

    /**
     * Get workflow data with caching
     * @param empathyDir Path to .empathy directory
     * @param force Force refresh, bypass cache
     */
    public async getWorkflowData(empathyDir: string, force = false): Promise<WorkflowData> {
        // Check cache
        if (!force && this._cache && Date.now() - this._cacheTime < this.CACHE_TTL) {
            return this._cache;
        }

        // Load fresh data
        const workflows = this._loadWorkflowsFromFile(empathyDir);

        // Update cache
        this._cache = workflows;
        this._cacheTime = Date.now();

        return workflows;
    }

    /**
     * Get lightweight summary for dashboard display
     */
    public getWorkflowSummary(): WorkflowSummary {
        if (!this._cache) {
            return {
                totalRuns: 0,
                successfulRuns: 0,
                successRate: 0,
                totalCost: 0
            };
        }

        const successRate = this._cache.totalRuns > 0
            ? Math.round((this._cache.successfulRuns / this._cache.totalRuns) * 100)
            : 0;

        return {
            totalRuns: this._cache.totalRuns,
            successfulRuns: this._cache.successfulRuns,
            successRate,
            totalCost: this._cache.totalCost
        };
    }

    /**
     * Clear cache (useful for testing or manual refresh)
     */
    public clearCache(): void {
        this._cache = null;
        this._cacheTime = 0;
    }

    /**
     * Load workflow data from workflow_runs.json file
     * Extracted from EmpathyDashboardPanel._loadWorkflows()
     */
    private _loadWorkflowsFromFile(empathyDir: string): WorkflowData {
        const workflows: WorkflowData = {
            totalRuns: 0,
            successfulRuns: 0,
            totalCost: 0,
            totalSavings: 0,
            recentRuns: [],
            byWorkflow: {},
        };

        try {
            const runsFile = path.join(empathyDir, 'workflow_runs.json');
            if (fs.existsSync(runsFile)) {
                const runs = JSON.parse(fs.readFileSync(runsFile, 'utf8')) as any[];

                workflows.totalRuns = runs.length;
                workflows.successfulRuns = runs.filter(r => r.success).length;

                for (const run of runs) {
                    workflows.totalCost += run.cost || 0;
                    workflows.totalSavings += run.savings || 0;

                    const wfName = run.workflow || 'unknown';
                    if (!workflows.byWorkflow[wfName]) {
                        workflows.byWorkflow[wfName] = { runs: 0, cost: 0, savings: 0 };
                    }
                    workflows.byWorkflow[wfName].runs++;
                    workflows.byWorkflow[wfName].cost += run.cost || 0;
                    workflows.byWorkflow[wfName].savings += run.savings || 0;
                }

                workflows.recentRuns = runs.slice(-10).reverse().map(r => {
                    const run: WorkflowRunData = {
                        workflow: r.workflow || 'unknown',
                        success: r.success || false,
                        cost: r.cost || 0,
                        savings: r.savings || 0,
                        timestamp: r.started_at || '',
                    };
                    // Include XML-parsed fields if available
                    if (r.xml_parsed) {
                        run.xml_parsed = true;
                        run.summary = r.summary;
                        run.findings = r.findings || [];
                        run.checklist = r.checklist || [];
                    }
                    return run;
                });
            }
        } catch { /* ignore */ }

        return workflows;
    }
}

// =============================================================================
// Exports
// =============================================================================

/**
 * Convenience function to get service instance
 */
export function getWorkflowDataService(): WorkflowDataService {
    return WorkflowDataService.getInstance();
}
