/**
 * Artifacts Tree View Provider
 * Displays generated artifacts (specs, reports, plans)
 */

import * as vscode from 'vscode';

export class ArtifactsTreeProvider implements vscode.TreeDataProvider<ArtifactItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ArtifactItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private artifacts: any[] = [];

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    addArtifacts(wizardResult: any): void {
        // Add artifacts from wizard result
        const primary = wizardResult.primary_output;
        if (primary && primary.artifacts) {
            for (const artifact of primary.artifacts) {
                this.artifacts.push({
                    name: artifact.name,
                    content: artifact.content,
                    format: artifact.format,
                    wizard: primary.wizard_name,
                    timestamp: new Date()
                });
            }
        }

        // Limit to last 50 artifacts
        if (this.artifacts.length > 50) {
            this.artifacts = this.artifacts.slice(-50);
        }

        this.refresh();
    }

    getTreeItem(element: ArtifactItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ArtifactItem): ArtifactItem[] {
        if (!element) {
            // Root: show all artifacts
            return this.artifacts.map(a => new ArtifactItem(
                a.name,
                a.wizard,
                a.content,
                a.format,
                a.timestamp
            )).reverse(); // Most recent first
        }
        return [];
    }

    clear(): void {
        this.artifacts = [];
        this.refresh();
    }
}

class ArtifactItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        private wizard: string,
        private content: string,
        private format: string,
        private timestamp: Date
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);

        const timeAgo = this.getTimeAgo(timestamp);
        this.description = `${wizard} · ${timeAgo}`;
        this.tooltip = `${wizard}\n${timeAgo}\nFormat: ${format}`;

        // Icon based on format
        if (format === 'yaml' || format === 'json') {
            this.iconPath = new vscode.ThemeIcon('file-code');
        } else if (format === 'markdown') {
            this.iconPath = new vscode.ThemeIcon('markdown');
        } else {
            this.iconPath = new vscode.ThemeIcon('file-text');
        }

        this.command = {
            command: 'coach.showArtifact',
            title: 'Show Artifact',
            arguments: [this]
        };
    }

    private getTimeAgo(date: Date): string {
        const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

        if (seconds < 60) return `${seconds}s ago`;
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    }

    getContent(): string {
        return this.content;
    }

    getFormat(): string {
        return this.format;
    }
}
