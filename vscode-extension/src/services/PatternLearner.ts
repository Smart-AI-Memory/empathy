/**
 * PatternLearner - Learns and recalls refinement patterns
 *
 * Stores refinement patterns to reduce future friction by suggesting
 * previous answers for similar contexts.
 *
 * Pattern matching is based on:
 * - Workflow name
 * - File types involved
 * - Folder structure
 * - Project type indicators
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as crypto from 'crypto';
import * as path from 'path';

/**
 * Learned refinement pattern
 */
export interface LearnedPattern {
    id: string;
    workflowId: string;
    contextSignature: string;
    refinements: Record<string, string | string[]>;
    usageCount: number;
    lastUsed: number;
    created: number;
    description?: string;
}

/**
 * Context for pattern matching
 */
export interface PatternContext {
    workflowName: string;
    targetPath?: string;
    fileTypes?: string[];
    folderName?: string;
    projectType?: string;
}

/**
 * Pattern suggestion result
 */
export interface PatternSuggestion {
    pattern: LearnedPattern;
    confidence: number;
    reason: string;
}

/**
 * PatternLearner - Singleton service for learning refinement patterns
 */
export class PatternLearner {
    private static instance: PatternLearner;
    private context: vscode.ExtensionContext | null = null;
    private patterns: Map<string, LearnedPattern> = new Map();

    private readonly STORAGE_KEY = 'empathy.refinementPatterns';
    private readonly MAX_PATTERNS = 100;
    private readonly PATTERN_TTL_DAYS = 90;

    private constructor() {}

    static getInstance(): PatternLearner {
        if (!PatternLearner.instance) {
            PatternLearner.instance = new PatternLearner();
        }
        return PatternLearner.instance;
    }

    /**
     * Initialize with extension context
     */
    initialize(context: vscode.ExtensionContext): void {
        this.context = context;
        this.loadPatterns();
    }

    /**
     * Load patterns from storage
     */
    private loadPatterns(): void {
        if (!this.context) {
            return;
        }

        const stored = this.context.globalState.get<Record<string, LearnedPattern>>(
            this.STORAGE_KEY,
            {}
        );

        this.patterns = new Map(Object.entries(stored));

        // Clean up old patterns
        this.pruneOldPatterns();
    }

    /**
     * Save patterns to storage
     */
    private async savePatterns(): Promise<void> {
        if (!this.context) {
            return;
        }

        const toStore: Record<string, LearnedPattern> = {};
        for (const [id, pattern] of this.patterns) {
            toStore[id] = pattern;
        }

        await this.context.globalState.update(this.STORAGE_KEY, toStore);
    }

    /**
     * Generate context signature for pattern matching
     */
    generateContextSignature(context: PatternContext): string {
        const parts = [
            context.workflowName,
            context.folderName || '',
            context.projectType || '',
            (context.fileTypes || []).sort().join(',')
        ];

        const hash = crypto.createHash('sha256');
        hash.update(parts.join('|'));
        return hash.digest('hex').substring(0, 16);
    }

    /**
     * Learn a new pattern from user refinement
     */
    async learn(
        context: PatternContext,
        refinements: Record<string, string | string[]>
    ): Promise<LearnedPattern> {
        const signature = this.generateContextSignature(context);
        const id = `${context.workflowName}-${signature}`;

        // Check if pattern already exists
        const existing = this.patterns.get(id);
        if (existing) {
            // Update existing pattern
            existing.refinements = refinements;
            existing.usageCount++;
            existing.lastUsed = Date.now();
            await this.savePatterns();
            console.log(`[PatternLearner] Updated existing pattern: ${id}`);
            return existing;
        }

        // Create new pattern
        const pattern: LearnedPattern = {
            id,
            workflowId: context.workflowName,
            contextSignature: signature,
            refinements,
            usageCount: 1,
            lastUsed: Date.now(),
            created: Date.now(),
            description: this.generateDescription(context, refinements)
        };

        this.patterns.set(id, pattern);

        // Prune if over limit
        if (this.patterns.size > this.MAX_PATTERNS) {
            this.pruneLeastUsed();
        }

        await this.savePatterns();
        console.log(`[PatternLearner] Learned new pattern: ${id}`);

        return pattern;
    }

    /**
     * Find matching patterns for a context
     */
    findMatches(context: PatternContext): PatternSuggestion[] {
        const signature = this.generateContextSignature(context);
        const suggestions: PatternSuggestion[] = [];

        for (const pattern of this.patterns.values()) {
            if (pattern.workflowId !== context.workflowName) {
                continue;
            }

            // Exact match
            if (pattern.contextSignature === signature) {
                suggestions.push({
                    pattern,
                    confidence: 1.0,
                    reason: 'Exact context match'
                });
                continue;
            }

            // Partial match - same workflow, similar context
            const similarity = this.calculateSimilarity(pattern, context);
            if (similarity > 0.5) {
                suggestions.push({
                    pattern,
                    confidence: similarity,
                    reason: `Similar context (${Math.round(similarity * 100)}% match)`
                });
            }
        }

        // Sort by confidence, then by usage count
        return suggestions.sort((a, b) => {
            if (b.confidence !== a.confidence) {
                return b.confidence - a.confidence;
            }
            return b.pattern.usageCount - a.pattern.usageCount;
        });
    }

    /**
     * Get the best matching pattern for a context
     */
    getBestMatch(context: PatternContext): PatternSuggestion | null {
        const matches = this.findMatches(context);
        return matches.length > 0 ? matches[0] : null;
    }

    /**
     * Calculate similarity between a pattern and context
     */
    private calculateSimilarity(pattern: LearnedPattern, context: PatternContext): number {
        let score = 0;
        let factors = 0;

        // Same workflow is required
        if (pattern.workflowId === context.workflowName) {
            score += 1;
            factors += 1;
        }

        // Check if context contains hints from the pattern description
        if (pattern.description && context.folderName) {
            if (pattern.description.toLowerCase().includes(context.folderName.toLowerCase())) {
                score += 0.5;
            }
            factors += 0.5;
        }

        // Recent patterns get slight boost
        const daysSinceUse = (Date.now() - pattern.lastUsed) / (1000 * 60 * 60 * 24);
        if (daysSinceUse < 7) {
            score += 0.2;
        }
        factors += 0.2;

        // High usage patterns get boost
        if (pattern.usageCount > 5) {
            score += 0.3;
        }
        factors += 0.3;

        return factors > 0 ? score / factors : 0;
    }

    /**
     * Generate a human-readable description for a pattern
     */
    private generateDescription(
        context: PatternContext,
        refinements: Record<string, string | string[]>
    ): string {
        const parts: string[] = [];

        if (context.folderName) {
            parts.push(context.folderName);
        }

        if (context.projectType) {
            parts.push(context.projectType);
        }

        const refinementSummary = Object.entries(refinements)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');

        if (refinementSummary) {
            parts.push(`[${refinementSummary}]`);
        }

        return parts.join(' ');
    }

    /**
     * Remove patterns older than TTL
     */
    private pruneOldPatterns(): void {
        const cutoff = Date.now() - (this.PATTERN_TTL_DAYS * 24 * 60 * 60 * 1000);
        let pruned = 0;

        for (const [id, pattern] of this.patterns) {
            if (pattern.lastUsed < cutoff) {
                this.patterns.delete(id);
                pruned++;
            }
        }

        if (pruned > 0) {
            console.log(`[PatternLearner] Pruned ${pruned} old patterns`);
            this.savePatterns();
        }
    }

    /**
     * Remove least used patterns when over limit
     */
    private pruneLeastUsed(): void {
        const patterns = Array.from(this.patterns.values());
        patterns.sort((a, b) => a.usageCount - b.usageCount);

        // Remove bottom 10%
        const toRemove = Math.ceil(patterns.length * 0.1);
        for (let i = 0; i < toRemove; i++) {
            this.patterns.delete(patterns[i].id);
        }

        console.log(`[PatternLearner] Pruned ${toRemove} least-used patterns`);
    }

    /**
     * Record usage of a pattern
     */
    async recordUsage(patternId: string): Promise<void> {
        const pattern = this.patterns.get(patternId);
        if (pattern) {
            pattern.usageCount++;
            pattern.lastUsed = Date.now();
            await this.savePatterns();
        }
    }

    /**
     * Get all patterns for a workflow
     */
    getPatternsForWorkflow(workflowName: string): LearnedPattern[] {
        const patterns: LearnedPattern[] = [];
        for (const pattern of this.patterns.values()) {
            if (pattern.workflowId === workflowName) {
                patterns.push(pattern);
            }
        }
        return patterns.sort((a, b) => b.usageCount - a.usageCount);
    }

    /**
     * Delete a specific pattern
     */
    async deletePattern(patternId: string): Promise<boolean> {
        const deleted = this.patterns.delete(patternId);
        if (deleted) {
            await this.savePatterns();
        }
        return deleted;
    }

    /**
     * Clear all patterns
     */
    async clearAllPatterns(): Promise<void> {
        this.patterns.clear();
        await this.savePatterns();
    }

    /**
     * Get pattern statistics
     */
    getStatistics(): {
        totalPatterns: number;
        patternsByWorkflow: Record<string, number>;
        averageUsage: number;
        oldestPattern: number | null;
    } {
        const patternsByWorkflow: Record<string, number> = {};
        let totalUsage = 0;
        let oldest: number | null = null;

        for (const pattern of this.patterns.values()) {
            patternsByWorkflow[pattern.workflowId] = (patternsByWorkflow[pattern.workflowId] || 0) + 1;
            totalUsage += pattern.usageCount;
            if (oldest === null || pattern.created < oldest) {
                oldest = pattern.created;
            }
        }

        return {
            totalPatterns: this.patterns.size,
            patternsByWorkflow,
            averageUsage: this.patterns.size > 0 ? totalUsage / this.patterns.size : 0,
            oldestPattern: oldest
        };
    }

    /**
     * Detect project type from context
     */
    static detectProjectType(workspacePath: string): string | undefined {
        const fs = require('fs');
        const indicators: Record<string, string> = {
            'package.json': 'node',
            'pyproject.toml': 'python',
            'Cargo.toml': 'rust',
            'go.mod': 'go',
            'pom.xml': 'java-maven',
            'build.gradle': 'java-gradle',
            'Gemfile': 'ruby',
            'composer.json': 'php'
        };

        for (const [file, projectType] of Object.entries(indicators)) {
            if (fs.existsSync(path.join(workspacePath, file))) {
                return projectType;
            }
        }

        return undefined;
    }

    /**
     * Detect file types in a directory
     */
    static detectFileTypes(targetPath: string): string[] {
        const fs = require('fs');
        const fileTypes = new Set<string>();

        try {
            const stat = fs.statSync(targetPath);
            if (stat.isFile()) {
                const ext = path.extname(targetPath).toLowerCase();
                if (ext) {
                    fileTypes.add(ext);
                }
            } else if (stat.isDirectory()) {
                const files = fs.readdirSync(targetPath);
                for (const file of files.slice(0, 50)) { // Limit to first 50 files
                    const ext = path.extname(file).toLowerCase();
                    if (ext && !ext.startsWith('.git')) {
                        fileTypes.add(ext);
                    }
                }
            }
        } catch {
            // Ignore errors
        }

        return Array.from(fileTypes);
    }
}
