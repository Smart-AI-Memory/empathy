/**
 * Health Data Service
 *
 * Centralized service for loading and caching project health metrics.
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

export interface HealthData {
    score: number;
    patterns: number;
    lint: { errors: number; warnings: number };
    types: { errors: number };
    security: { high: number; medium: number; low: number };
    tests: { passed: number; failed: number; total: number; coverage: number };
    techDebt: { total: number; todos: number; fixmes: number; hacks: number };
    lastUpdated: string | null;
}

export interface HealthSummary {
    score: number;
    scoreLabel: string; // "Good", "Warning", "Poor"
    lastUpdated: string | null;
}

// =============================================================================
// Service
// =============================================================================

export class HealthDataService {
    private static _instance: HealthDataService | null = null;
    private _cache: HealthData | null = null;
    private _cacheTime: number = 0;
    private readonly CACHE_TTL = 30000; // 30 seconds

    public static getInstance(): HealthDataService {
        if (!HealthDataService._instance) {
            HealthDataService._instance = new HealthDataService();
        }
        return HealthDataService._instance;
    }

    private constructor() {
        // Private constructor for singleton
    }

    /**
     * Get health data with caching
     * @param empathyDir Path to .empathy directory
     * @param patternsDir Path to patterns directory
     * @param force Force refresh, bypass cache
     */
    public async getHealthData(empathyDir: string, patternsDir: string, force = false): Promise<HealthData> {
        // Check cache
        if (!force && this._cache && Date.now() - this._cacheTime < this.CACHE_TTL) {
            return this._cache;
        }

        // Load fresh data
        const health = this._loadHealthFromFiles(empathyDir, patternsDir);

        // Update cache
        this._cache = health;
        this._cacheTime = Date.now();

        return health;
    }

    /**
     * Get lightweight summary for dashboard display
     */
    public getHealthSummary(): HealthSummary {
        if (!this._cache) {
            return {
                score: 0,
                scoreLabel: 'Unknown',
                lastUpdated: null
            };
        }

        const scoreLabel = this._cache.score >= 80 ? 'Good'
            : this._cache.score >= 50 ? 'Warning'
            : 'Poor';

        return {
            score: this._cache.score,
            scoreLabel,
            lastUpdated: this._cache.lastUpdated
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
     * Load health data from files
     * Extracted from EmpathyDashboardPanel._loadHealth()
     */
    private _loadHealthFromFiles(empathyDir: string, patternsDir: string): HealthData {
        const health: HealthData = {
            score: 0,
            patterns: 0,
            lint: { errors: 0, warnings: 0 },
            types: { errors: 0 },
            security: { high: 0, medium: 0, low: 0 },
            tests: { passed: 0, failed: 0, total: 0, coverage: 0 },
            techDebt: { total: 0, todos: 0, fixmes: 0, hacks: 0 },
            lastUpdated: null,
        };

        // Load patterns count from debugging.json
        try {
            const debuggingFile = path.join(patternsDir, 'debugging.json');
            if (fs.existsSync(debuggingFile)) {
                const data = JSON.parse(fs.readFileSync(debuggingFile, 'utf8'));
                health.patterns = data.patterns?.length || 0;
            }
        } catch { /* ignore */ }

        // Load health metrics from health.json
        try {
            const healthFile = path.join(empathyDir, 'health.json');
            if (fs.existsSync(healthFile)) {
                const data = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
                health.score = data.score || 0;
                health.lint = data.lint || health.lint;
                health.types = data.types || health.types;
                health.security = data.security || health.security;
                health.tests = data.tests || health.tests;
                health.techDebt = data.tech_debt || health.techDebt;
                health.lastUpdated = data.timestamp || null;
            }
        } catch { /* ignore */ }

        // Load tech debt details from tech_debt.json
        try {
            const debtFile = path.join(patternsDir, 'tech_debt.json');
            if (fs.existsSync(debtFile)) {
                const data = JSON.parse(fs.readFileSync(debtFile, 'utf8'));
                if (data.snapshots && data.snapshots.length > 0) {
                    const latest = data.snapshots[data.snapshots.length - 1];
                    health.techDebt.total = latest.total_items || 0;
                    if (latest.by_type) {
                        health.techDebt.todos = latest.by_type.todo || 0;
                        health.techDebt.fixmes = latest.by_type.fixme || 0;
                        health.techDebt.hacks = latest.by_type.hack || 0;
                    }
                }
            }
        } catch { /* ignore */ }

        // Calculate score if not set
        if (health.score === 0 && health.patterns > 0) {
            let score = 100;
            score -= health.lint.errors * 2;
            score -= health.types.errors * 3;
            score -= health.security.high * 10;
            score -= health.tests.failed * 5;
            health.score = Math.max(0, Math.min(100, Math.round(score)));
        }

        return health;
    }
}

// =============================================================================
// Exports
// =============================================================================

/**
 * Convenience function to get service instance
 */
export function getHealthDataService(): HealthDataService {
    return HealthDataService.getInstance();
}
