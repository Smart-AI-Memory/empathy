/**
 * ContextBuilder - Shared utility for building workflow context
 *
 * Provides common context-building logic used across TriggerAnalyzer
 * and PatternLearner to reduce code duplication.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as crypto from 'crypto';

/**
 * Detected project type based on config files
 */
export type ProjectType = 'node' | 'python' | 'rust' | 'go' | 'java-maven' | 'java-gradle' | 'ruby' | 'php' | 'unknown';

/**
 * Scope of the workflow execution
 */
export type WorkflowScope = 'file' | 'folder' | 'project' | 'unknown';

/**
 * Common context information
 */
export interface CommonContext {
    workspacePath?: string;
    projectType?: ProjectType;
    targetPath?: string;
    scope: WorkflowScope;
    fileTypes: string[];
    folderName?: string;
}

/**
 * ContextBuilder - Static utility class for context operations
 */
export class ContextBuilder {
    /**
     * Detect project type from workspace
     */
    static detectProjectType(workspacePath: string): ProjectType {
        const fs = require('fs');
        const indicators: Record<string, ProjectType> = {
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
            try {
                if (fs.existsSync(path.join(workspacePath, file))) {
                    return projectType;
                }
            } catch {
                // Ignore errors
            }
        }

        return 'unknown';
    }

    /**
     * Detect file types in a path
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

    /**
     * Determine scope from target path
     */
    static determineScope(targetPath?: string, workspacePath?: string): WorkflowScope {
        if (!targetPath) {
            return 'unknown';
        }

        const fs = require('fs');

        try {
            const stat = fs.statSync(targetPath);
            if (stat.isFile()) {
                return 'file';
            }

            if (stat.isDirectory()) {
                // Check if it's the workspace root
                if (workspacePath && path.resolve(targetPath) === path.resolve(workspacePath)) {
                    return 'project';
                }
                return 'folder';
            }
        } catch {
            // If path doesn't exist or can't be accessed
        }

        return 'unknown';
    }

    /**
     * Build common context from target path
     */
    static buildCommonContext(targetPath?: string): CommonContext {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const workspacePath = workspaceFolder?.uri.fsPath;

        const scope = this.determineScope(targetPath, workspacePath);
        const fileTypes = targetPath ? this.detectFileTypes(targetPath) : [];
        const projectType = workspacePath ? this.detectProjectType(workspacePath) : undefined;
        const folderName = targetPath ? path.basename(targetPath) : undefined;

        return {
            workspacePath,
            projectType,
            targetPath,
            scope,
            fileTypes,
            folderName
        };
    }

    /**
     * Generate a signature hash for context
     */
    static generateSignature(...parts: (string | undefined)[]): string {
        const filtered = parts.filter(p => p !== undefined && p !== '');
        const hash = crypto.createHash('sha256');
        hash.update(filtered.join('|'));
        return hash.digest('hex').substring(0, 16);
    }

    /**
     * Get folder name from path
     */
    static getFolderName(targetPath?: string): string | undefined {
        if (!targetPath) {
            return undefined;
        }

        const fs = require('fs');

        try {
            const stat = fs.statSync(targetPath);
            if (stat.isDirectory()) {
                return path.basename(targetPath);
            } else if (stat.isFile()) {
                return path.basename(path.dirname(targetPath));
            }
        } catch {
            // If error, try to get folder name from path
            return path.basename(path.dirname(targetPath));
        }

        return undefined;
    }

    /**
     * Parse target from input string or JSON
     */
    static parseTarget(input?: string): string | undefined {
        if (!input) {
            return undefined;
        }

        try {
            // Try parsing as JSON
            const parsed = JSON.parse(input);
            return parsed.target || parsed.path || parsed.diff;
        } catch {
            // Not JSON, treat as direct path
            if (input !== '.' && input !== './') {
                return input;
            }
        }

        return undefined;
    }

    /**
     * Check if target is explicitly specified (not default)
     */
    static isExplicitTarget(input?: string): boolean {
        if (!input) {
            return false;
        }

        const target = this.parseTarget(input);
        return !!target && target !== '.' && target !== './';
    }
}
