/**
 * File Picker Service
 *
 * Standardized file/folder selection across all VS Code extension panels.
 * Provides:
 * - OS-native file/folder dialogs via vscode.window.showOpenDialog()
 * - Four standardized shortcuts: File, Folder, Active, Project
 * - Consistent message protocol between webview and extension
 * - Reusable UI component (HTML/CSS/JS)
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as path from 'path';

// =============================================================================
// Types
// =============================================================================

/**
 * File picker filter configuration
 */
export interface FilePickerFilters {
    [name: string]: string[];
}

/**
 * Options for file picker dialog
 */
export interface FilePickerOptions {
    filters?: FilePickerFilters;
    title?: string;
    allowMultiple?: boolean;
    defaultPath?: vscode.Uri;
    openLabel?: string;
}

/**
 * Options for folder picker dialog
 */
export interface FolderPickerOptions {
    title?: string;
    defaultPath?: vscode.Uri;
    openLabel?: string;
}

/**
 * Result from file/folder selection
 */
export interface FilePickerResult {
    path: string;           // Relative path from workspace
    absolutePath: string;   // Full absolute path
    isDirectory: boolean;
    fileName: string;       // Just the filename
}

/**
 * Message from webview to extension for file picker actions
 */
export interface FilePickerMessage {
    type: FilePickerMessageType;
    options?: {
        filters?: FilePickerFilters;
        title?: string;
        languageFilter?: string | string[];
    };
    context?: string;
}

/**
 * Response from extension to webview
 */
export interface FilePickerResponse {
    type: 'filePicker:result';
    success: boolean;
    result?: FilePickerResult | FilePickerResult[];
    error?: string;
    context?: string;
}

/**
 * Standard message types for file picker
 */
export type FilePickerMessageType =
    | 'filePicker:selectFile'
    | 'filePicker:selectFiles'
    | 'filePicker:selectFolder'
    | 'filePicker:useActiveFile'
    | 'filePicker:useProjectRoot';

// =============================================================================
// Predefined Filters
// =============================================================================

/**
 * Predefined file filters for consistency across panels.
 *
 * @example
 * ```typescript
 * // Use in showFilePicker options
 * const files = await service.showFilePicker({
 *     filters: FILE_FILTERS.PYTHON,
 *     title: 'Select Python file'
 * });
 *
 * // Or in webview message
 * vscode.postMessage({
 *     type: 'filePicker:selectFile',
 *     options: { filters: { 'Python Files': ['py'] } }
 * });
 * ```
 *
 * @property PYTHON - Filter for `.py` files only
 * @property TYPESCRIPT - Filter for `.ts` and `.tsx` files
 * @property JAVASCRIPT - Filter for `.js` and `.jsx` files
 * @property CODE_ALL - Common code files (py, ts, tsx, js, jsx) plus all files
 * @property DOCUMENTS - Documents (md, txt, json, yaml) plus code files
 * @property ALL - All files (no filtering)
 */
export const FILE_FILTERS: { [key: string]: FilePickerFilters } = {
    PYTHON: { 'Python Files': ['py'] },
    TYPESCRIPT: { 'TypeScript': ['ts', 'tsx'] },
    JAVASCRIPT: { 'JavaScript': ['js', 'jsx'] },
    CODE_ALL: {
        'Code Files': ['py', 'ts', 'tsx', 'js', 'jsx'],
        'All Files': ['*']
    },
    DOCUMENTS: {
        'Documents': ['md', 'txt', 'json', 'yaml', 'yml'],
        'Code': ['py', 'ts', 'js', 'tsx', 'jsx'],
        'All Files': ['*']
    },
    ALL: { 'All Files': ['*'] }
};

// =============================================================================
// FilePickerService Class
// =============================================================================

/**
 * Singleton service for standardized file/folder selection across all panels.
 *
 * Provides a consistent API for:
 * - File selection (single or multiple)
 * - Folder selection
 * - Getting the currently active file in the editor
 * - Getting the project/workspace root
 *
 * @example
 * ```typescript
 * // Get the singleton instance
 * const service = getFilePickerService();
 *
 * // Show file picker
 * const files = await service.showFilePicker({
 *     filters: FILE_FILTERS.PYTHON,
 *     title: 'Select Python file'
 * });
 *
 * // Get active file with language filter
 * const activeFile = service.getActiveFile('python');
 *
 * // Get project root
 * const root = service.getProjectRoot();
 * ```
 */
export class FilePickerService {
    private static _instance: FilePickerService | null = null;

    public static getInstance(): FilePickerService {
        if (!FilePickerService._instance) {
            FilePickerService._instance = new FilePickerService();
        }
        return FilePickerService._instance;
    }

    /**
     * Show file picker dialog
     * @returns Array of selected files, or undefined if cancelled
     */
    public async showFilePicker(
        options?: FilePickerOptions
    ): Promise<FilePickerResult[] | undefined> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri;

        const result = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: options?.allowMultiple ?? false,
            defaultUri: options?.defaultPath ?? workspaceFolder,
            filters: options?.filters ?? FILE_FILTERS.ALL,
            title: options?.title ?? 'Select File',
            openLabel: options?.openLabel ?? 'Select'
        });

        if (!result || result.length === 0) {
            return undefined;
        }

        return result.map(uri => this._uriToResult(uri, false));
    }

    /**
     * Show folder picker dialog
     * @returns Selected folder, or undefined if cancelled
     */
    public async showFolderPicker(
        options?: FolderPickerOptions
    ): Promise<FilePickerResult | undefined> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri;

        const result = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            defaultUri: options?.defaultPath ?? workspaceFolder,
            title: options?.title ?? 'Select Folder',
            openLabel: options?.openLabel ?? 'Select'
        });

        if (!result || result.length === 0) {
            return undefined;
        }

        return this._uriToResult(result[0], true);
    }

    /**
     * Get currently active file in editor
     * @param languageFilter Optional language ID filter (e.g., 'python', 'typescript')
     * @returns Active file result, or undefined if no matching file
     */
    public getActiveFile(
        languageFilter?: string | string[]
    ): FilePickerResult | undefined {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return undefined;
        }

        const doc = editor.document;

        // Check language filter if provided
        if (languageFilter) {
            const filters = Array.isArray(languageFilter)
                ? languageFilter
                : [languageFilter];
            if (!filters.includes(doc.languageId)) {
                return undefined;
            }
        }

        // Skip untitled/unsaved files
        if (doc.isUntitled) {
            return undefined;
        }

        return this._uriToResult(doc.uri, false);
    }

    /**
     * Get workspace root folder
     * @returns Project root result, or undefined if no workspace
     */
    public getProjectRoot(): FilePickerResult | undefined {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return undefined;
        }

        return {
            path: '.',
            absolutePath: workspaceFolder.uri.fsPath,
            isDirectory: true,
            fileName: workspaceFolder.name
        };
    }

    /**
     * Convert URI to FilePickerResult
     */
    private _uriToResult(uri: vscode.Uri, isDirectory: boolean): FilePickerResult {
        const relativePath = vscode.workspace.asRelativePath(uri);
        const fileName = path.basename(uri.fsPath);

        return {
            path: relativePath || '.',
            absolutePath: uri.fsPath,
            isDirectory,
            fileName
        };
    }
}

// =============================================================================
// Singleton Getter
// =============================================================================

/**
 * Get the FilePickerService singleton instance
 */
export function getFilePickerService(): FilePickerService {
    return FilePickerService.getInstance();
}

// =============================================================================
// Message Handler Factory
// =============================================================================

/**
 * Create a message handler for file picker operations.
 *
 * Use this factory to create a handler that routes `filePicker:*` messages
 * from the webview to the appropriate FilePickerService methods.
 *
 * @param service - FilePickerService instance (use getFilePickerService())
 * @param postMessage - Function to send FilePickerResponse back to webview
 * @returns Handler function that returns true if message was handled
 *
 * @example
 * ```typescript
 * // In your panel's resolveWebviewView method:
 * this._handleFilePicker = createFilePickerMessageHandler(
 *     this._filePickerService,
 *     (msg: FilePickerResponse) => {
 *         if (msg.type === 'filePicker:result' && msg.success && msg.result) {
 *             const result = Array.isArray(msg.result) ? msg.result[0] : msg.result;
 *             webviewView.webview.postMessage({
 *                 type: 'pathSelected',
 *                 path: result.path
 *             });
 *         }
 *     }
 * );
 *
 * // In your message handler:
 * if (message.type?.startsWith('filePicker:')) {
 *     await this._handleFilePicker?.(message);
 *     return;
 * }
 * ```
 */
export function createFilePickerMessageHandler(
    service: FilePickerService,
    postMessage: (message: FilePickerResponse) => void
): (message: FilePickerMessage) => Promise<boolean> {
    return async (message: FilePickerMessage): Promise<boolean> => {
        // Only handle filePicker messages
        if (!message.type?.startsWith('filePicker:')) {
            return false;
        }

        let result: FilePickerResult | FilePickerResult[] | undefined;
        let error: string | undefined;

        try {
            switch (message.type) {
                case 'filePicker:selectFile': {
                    const fileResult = await service.showFilePicker({
                        ...message.options,
                        allowMultiple: false
                    });
                    result = fileResult?.[0];
                    break;
                }

                case 'filePicker:selectFiles': {
                    result = await service.showFilePicker({
                        ...message.options,
                        allowMultiple: true
                    });
                    break;
                }

                case 'filePicker:selectFolder': {
                    result = await service.showFolderPicker(message.options);
                    break;
                }

                case 'filePicker:useActiveFile': {
                    result = service.getActiveFile(message.options?.languageFilter);
                    if (!result) {
                        error = 'No active file matches the criteria';
                    }
                    break;
                }

                case 'filePicker:useProjectRoot': {
                    result = service.getProjectRoot();
                    if (!result) {
                        error = 'No workspace folder open';
                    }
                    break;
                }

                default:
                    return false;
            }
        } catch (e) {
            error = e instanceof Error ? e.message : 'Unknown error';
        }

        postMessage({
            type: 'filePicker:result',
            success: !error && result !== undefined,
            result,
            error,
            context: message.context
        });

        return true;
    };
}

// =============================================================================
// UI Component Snippets
// =============================================================================

/**
 * Options for generating file picker UI snippet
 */
export interface FilePickerUIOptions {
    inputId: string;
    showFile?: boolean;
    showFolder?: boolean;
    showActive?: boolean;
    showProject?: boolean;
    fileLabel?: string;
    folderLabel?: string;
    activeLabel?: string;
    projectLabel?: string;
    placeholder?: string;
    filters?: string;           // JSON stringified filters
    languageFilter?: string;    // For active file validation
}

/**
 * Generate HTML snippet for file picker UI
 */
export function getFilePickerUISnippet(options: FilePickerUIOptions): string {
    const {
        inputId,
        showFile = true,
        showFolder = true,
        showActive = true,
        showProject = true,
        fileLabel = 'File',
        folderLabel = 'Folder',
        activeLabel = 'Active',
        projectLabel = 'Project',
        placeholder = 'Select a path...',
        filters = '',
        languageFilter = ''
    } = options;

    return `
        <div class="file-picker-group">
            <input type="text"
                   id="${inputId}"
                   class="file-picker-input"
                   placeholder="${placeholder}"
                   readonly>
            <div class="file-picker-buttons">
                ${showFile ? `<button class="file-picker-btn" data-action="selectFile" data-target="${inputId}" ${filters ? `data-filters='${filters}'` : ''}>${fileLabel}</button>` : ''}
                ${showFolder ? `<button class="file-picker-btn" data-action="selectFolder" data-target="${inputId}">${folderLabel}</button>` : ''}
                ${showActive ? `<button class="file-picker-btn" data-action="useActiveFile" data-target="${inputId}" ${languageFilter ? `data-language="${languageFilter}"` : ''}>${activeLabel}</button>` : ''}
                ${showProject ? `<button class="file-picker-btn" data-action="useProjectRoot" data-target="${inputId}">${projectLabel}</button>` : ''}
            </div>
        </div>
    `;
}

/**
 * CSS styles for file picker component
 */
export const FILE_PICKER_STYLES = `
    .file-picker-group {
        margin-bottom: 12px;
    }
    .file-picker-input {
        width: 100%;
        padding: 6px 10px;
        border: 1px solid var(--vscode-input-border);
        background: var(--vscode-input-background);
        color: var(--vscode-input-foreground);
        border-radius: 4px;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .file-picker-input:read-only {
        opacity: 0.9;
    }
    .file-picker-input::placeholder {
        color: var(--vscode-input-placeholderForeground);
    }
    .file-picker-buttons {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .file-picker-btn {
        padding: 5px 12px;
        border: none;
        border-radius: 4px;
        font-size: 11px;
        cursor: pointer;
        background: var(--vscode-button-secondaryBackground);
        color: var(--vscode-button-secondaryForeground);
    }
    .file-picker-btn:hover {
        background: var(--vscode-button-secondaryHoverBackground);
    }
    .file-picker-btn:focus {
        outline: 1px solid var(--vscode-focusBorder);
    }
`;

/**
 * JavaScript for file picker component (to be included in webview)
 */
export const FILE_PICKER_SCRIPT = `
    // File picker button handler
    document.querySelectorAll('.file-picker-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            const targetId = btn.dataset.target;
            const filters = btn.dataset.filters ? JSON.parse(btn.dataset.filters) : undefined;
            const languageFilter = btn.dataset.language;

            vscode.postMessage({
                type: 'filePicker:' + action,
                options: { filters, languageFilter },
                context: targetId
            });
        });
    });

    // Handle file picker results
    function handleFilePickerResult(message) {
        if (message.type !== 'filePicker:result') return false;

        const input = document.getElementById(message.context);
        if (input && message.success && message.result) {
            const result = Array.isArray(message.result) ? message.result : [message.result];
            input.value = result.map(r => r.path).join(', ');
            input.dataset.absolutePath = result.map(r => r.absolutePath).join(',');
            input.dataset.isDirectory = result[0]?.isDirectory?.toString() || 'false';

            // Dispatch custom event for panel-specific handling
            input.dispatchEvent(new CustomEvent('pathSelected', {
                detail: { result: message.result, context: message.context }
            }));
        } else if (!message.success && message.error) {
            // Show error (panel can override this)
            console.warn('File picker error:', message.error);
        }
        return true;
    }
`;
