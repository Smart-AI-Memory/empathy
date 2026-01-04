/**
 * Costs Data Service
 *
 * Centralized service for loading and caching cost metrics and model configuration.
 * Provides singleton pattern with 30-second cache to prevent redundant CLI calls.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';

// =============================================================================
// Types
// =============================================================================

export interface CostData {
    totalCost: number;
    totalSavings: number;
    savingsPercent: number;
    requests: number;
    baselineCost: number;
    dailyCosts: Array<{ date: string; cost: number; savings: number }>;
    byProvider: Record<string, { requests: number; cost: number }>;
    byTier?: Record<string, { requests: number; savings: number; cost: number }>;
}

export interface CostSummary {
    totalCost: number;
    totalSavings: number;
    savingsPercent: number;
    requests: number;
}

export interface ModelConfig {
    provider: string;
    mode: string;
    models: {
        cheap: string;
        capable: string;
        premium: string;
    };
}

// Response shape from `python -m empathy_os.models.cli telemetry --costs -f json`
interface TelemetryCostData {
    workflow_count: number;
    total_actual_cost: number;
    total_baseline_cost: number;
    total_savings: number;
    savings_percent: number;
    avg_cost_per_workflow: number;
}

// =============================================================================
// Service
// =============================================================================

export class CostsDataService {
    private static _instance: CostsDataService | null = null;
    private _cache: CostData | null = null;
    private _cacheTime: number = 0;
    private readonly CACHE_TTL = 30000; // 30 seconds

    public static getInstance(): CostsDataService {
        if (!CostsDataService._instance) {
            CostsDataService._instance = new CostsDataService();
        }
        return CostsDataService._instance;
    }

    private constructor() {
        // Private constructor for singleton
    }

    /**
     * Get cost data with caching
     * Tries CLI first, falls back to file if CLI fails
     * @param workspaceFolder Path to workspace folder
     * @param force Force refresh, bypass cache
     */
    public async getCostsData(workspaceFolder?: string, force = false): Promise<CostData> {
        // Check cache
        if (!force && this._cache && Date.now() - this._cacheTime < this.CACHE_TTL) {
            return this._cache;
        }

        // Load fresh data
        const costs = await this._fetchCostsFromCLI(workspaceFolder);

        // Update cache
        this._cache = costs;
        this._cacheTime = Date.now();

        return costs;
    }

    /**
     * Get lightweight summary for dashboard display
     */
    public getCostsSummary(): CostSummary {
        if (!this._cache) {
            return {
                totalCost: 0,
                totalSavings: 0,
                savingsPercent: 0,
                requests: 0
            };
        }

        return {
            totalCost: this._cache.totalCost,
            totalSavings: this._cache.totalSavings,
            savingsPercent: this._cache.savingsPercent,
            requests: this._cache.requests
        };
    }

    /**
     * Get model configuration from .env and config files
     */
    public getModelConfig(workspaceFolder?: string): ModelConfig {
        // Default model configuration
        const modelConfig: ModelConfig = {
            provider: 'anthropic',
            mode: 'single',
            models: {
                cheap: 'claude-3-5-haiku',
                capable: 'claude-sonnet-4-5',
                premium: 'claude-opus-4-5'
            }
        };

        if (!workspaceFolder) {
            workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        }

        if (!workspaceFolder) {
            return modelConfig;
        }

        // Try to read from .env file
        const envFile = path.join(workspaceFolder, '.env');
        if (fs.existsSync(envFile)) {
            try {
                const envContent = fs.readFileSync(envFile, 'utf8');

                // Check for provider keys
                const hasAnthropic = envContent.includes('ANTHROPIC_API_KEY');
                const hasOpenAI = envContent.includes('OPENAI_API_KEY');

                if (hasAnthropic && hasOpenAI) {
                    modelConfig.provider = 'Hybrid';
                    modelConfig.mode = 'hybrid';
                    modelConfig.models = {
                        cheap: 'gpt-4o-mini',
                        capable: 'claude-sonnet-4-5',
                        premium: 'claude-opus-4-5'
                    };
                } else if (hasOpenAI && !hasAnthropic) {
                    modelConfig.provider = 'OpenAI';
                    modelConfig.mode = 'single';
                    modelConfig.models = {
                        cheap: 'gpt-4o-mini',
                        capable: 'gpt-4o',
                        premium: 'o1'
                    };
                } else {
                    modelConfig.provider = 'Anthropic';
                }
            } catch {
                // Use defaults
            }
        }

        // Try to read from empathy config
        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));
        const configFile = path.join(empathyDir, 'config.json');

        if (fs.existsSync(configFile)) {
            try {
                const savedConfig = JSON.parse(fs.readFileSync(configFile, 'utf8'));
                if (savedConfig.provider) {
                    modelConfig.provider = savedConfig.provider;
                }
                if (savedConfig.mode) {
                    modelConfig.mode = savedConfig.mode;
                }
                if (savedConfig.models) {
                    modelConfig.models = { ...modelConfig.models, ...savedConfig.models };
                }
            } catch {
                // Use defaults
            }
        }

        return modelConfig;
    }

    /**
     * Clear cache (useful for testing or manual refresh)
     */
    public clearCache(): void {
        this._cache = null;
        this._cacheTime = 0;
    }

    /**
     * Fetch costs from telemetry CLI (preferred method).
     * Falls back to file-based loading if CLI fails.
     * Extracted from EmpathyDashboardPanel._fetchCostsFromCLI()
     */
    private async _fetchCostsFromCLI(workspaceFolder?: string): Promise<CostData> {
        if (!workspaceFolder) {
            workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        }

        if (!workspaceFolder) {
            return this._getEmptyCostData();
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));

        return new Promise((resolve) => {
            const proc = cp.spawn(pythonPath, [
                '-m', 'empathy_os.models.cli', 'telemetry', '--costs', '-f', 'json', '-d', '30'
            ], { cwd: workspaceFolder });

            let stdout = '';
            let stderr = '';
            proc.stdout.on('data', (data: Buffer) => { stdout += data.toString(); });
            proc.stderr.on('data', (data: Buffer) => { stderr += data.toString(); });

            proc.on('close', (code) => {
                if (code === 0 && stdout) {
                    try {
                        const data: TelemetryCostData = JSON.parse(stdout.trim());
                        resolve({
                            totalCost: data.total_actual_cost || 0,
                            totalSavings: data.total_savings || 0,
                            savingsPercent: data.savings_percent || 0,
                            requests: data.workflow_count || 0,
                            baselineCost: data.total_baseline_cost || 0,
                            dailyCosts: [],
                            byProvider: {},
                        });
                    } catch {
                        // JSON parse failed, fall back to file
                        resolve(this._loadCostsFromFile(empathyDir));
                    }
                } else {
                    // CLI failed, fall back to file-based loading
                    resolve(this._loadCostsFromFile(empathyDir));
                }
            });

            // Timeout after 5 seconds
            setTimeout(() => {
                proc.kill();
                resolve(this._loadCostsFromFile(empathyDir));
            }, 5000);
        });
    }

    /**
     * Load costs from .empathy/costs.json file (fallback method).
     * Extracted from EmpathyDashboardPanel._loadCostsFromFile()
     */
    private _loadCostsFromFile(empathyDir: string): CostData {
        const costs: CostData = this._getEmptyCostData();

        try {
            const costsFile = path.join(empathyDir, 'costs.json');
            if (fs.existsSync(costsFile)) {
                const data = JSON.parse(fs.readFileSync(costsFile, 'utf8'));
                let baselineCost = 0;

                for (const [dateStr, daily] of Object.entries(data.daily_totals || {})) {
                    const d = daily as any;
                    costs.totalCost += d.actual_cost || 0;
                    costs.totalSavings += d.savings || 0;
                    costs.requests += d.requests || 0;
                    baselineCost += d.baseline_cost || 0;

                    costs.dailyCosts.push({
                        date: dateStr,
                        cost: d.actual_cost || 0,
                        savings: d.savings || 0,
                    });
                }

                costs.baselineCost = baselineCost;
                costs.savingsPercent = baselineCost > 0 ? Math.round((costs.totalSavings / baselineCost) * 100) : 0;

                // By provider
                for (const [provider, providerData] of Object.entries(data.by_provider || {})) {
                    costs.byProvider[provider] = {
                        requests: (providerData as any).requests || 0,
                        cost: (providerData as any).actual_cost || 0,
                    };
                }

                // Sort daily costs by date
                costs.dailyCosts.sort((a, b) => a.date.localeCompare(b.date));
            }
        } catch { /* ignore */ }

        return costs;
    }

    /**
     * Get empty cost data structure
     * Extracted from EmpathyDashboardPanel._getEmptyCostData()
     */
    private _getEmptyCostData(): CostData {
        return {
            totalCost: 0,
            totalSavings: 0,
            savingsPercent: 0,
            requests: 0,
            baselineCost: 0,
            dailyCosts: [],
            byProvider: {},
            byTier: undefined,
        };
    }
}

// =============================================================================
// Exports
// =============================================================================

/**
 * Convenience function to get service instance
 */
export function getCostsDataService(): CostsDataService {
    return CostsDataService.getInstance();
}
