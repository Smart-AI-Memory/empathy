'use client';

/**
 * Debug Wizard Component
 *
 * Memory-Enhanced Debugging Wizard with:
 * - Error input and file upload
 * - Historical pattern correlation
 * - Fix recommendations
 * - Resolution recording
 */

import { useState } from 'react';
import type {
  AnalysisInput,
  AnalysisResult,
  AnalysisResponse,
  ErrorType,
  HistoricalMatch,
  Prediction,
  FileInput,
} from '@/lib/debug-wizard/types';
import {
  AccessTier,
  getTierLimits,
  getTierDisplay,
  validateFilesForTier,
  getUpgradePath,
} from '@/lib/debug-wizard/tiers';

// ============================================================================
// Types
// ============================================================================

interface DetectedError {
  id: string;
  file: string;
  line: number;
  column?: number;
  type: 'syntax' | 'null_reference' | 'missing_await' | 'unused_variable' | 'missing_import' | 'type_error' | 'potential_bug';
  severity: 'error' | 'warning' | 'info';
  message: string;
  codeSnippet: string;
  suggestedFix?: string;
  fixedCode?: string;
  autoFixable: boolean;
}

interface ScanResult {
  totalFiles: number;
  filesScanned: number;
  errors: DetectedError[];
  warnings: DetectedError[];
  infos: DetectedError[];
}

interface WizardState {
  step: 'input' | 'scanning' | 'scan_results' | 'analyzing' | 'results';
  error_message: string;
  file_path: string;
  stack_trace: string;
  line_number: string;
  code_snippet: string;
  correlate_with_history: boolean;
  files: FileInput[];
  inputMode: 'files' | 'folder' | 'paste';
}

// Files/folders to exclude from uploads
const EXCLUDED_PATTERNS = [
  'node_modules',
  '.git',
  '.next',
  '__pycache__',
  '.pytest_cache',
  'dist',
  'build',
  '.venv',
  'venv',
  '.env',
  '.DS_Store',
  'package-lock.json',
  'yarn.lock',
  'pnpm-lock.yaml',
  '.ico',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.svg',
  '.woff',
  '.woff2',
  '.ttf',
  '.eot',
];

// Check if a file path should be excluded
function shouldExcludeFile(path: string): boolean {
  const normalizedPath = path.toLowerCase();
  return EXCLUDED_PATTERNS.some(pattern =>
    normalizedPath.includes(pattern.toLowerCase())
  );
}

// Group files by directory for tree view
function groupFilesByDirectory(files: FileInput[]): Map<string, FileInput[]> {
  const groups = new Map<string, FileInput[]>();

  for (const file of files) {
    const parts = file.path.split('/');
    const dir = parts.length > 1 ? parts.slice(0, -1).join('/') : '(root)';

    if (!groups.has(dir)) {
      groups.set(dir, []);
    }
    groups.get(dir)!.push(file);
  }

  return groups;
}

// ============================================================================
// Error Detection Patterns
// ============================================================================

interface ErrorPattern {
  type: DetectedError['type'];
  severity: DetectedError['severity'];
  pattern: RegExp;
  message: (match: RegExpMatchArray) => string;
  suggestedFix?: (match: RegExpMatchArray, line: string) => string;
  fixedCode?: (match: RegExpMatchArray, line: string) => string;
  autoFixable: boolean;
  fileTypes?: string[];
}

const ERROR_PATTERNS: ErrorPattern[] = [
  // Missing await on async calls
  {
    type: 'missing_await',
    severity: 'error',
    pattern: /(?<!await\s+)(?:fetch|axios\.(?:get|post|put|delete|patch)|\.then\(|Promise\.(?:all|race|allSettled))\s*\(/g,
    message: () => 'Possible missing await on async operation',
    suggestedFix: () => 'Add "await" before the async call',
    autoFixable: false,
    fileTypes: ['.js', '.jsx', '.ts', '.tsx'],
  },
  // Null/undefined access risk in JavaScript/TypeScript
  {
    type: 'null_reference',
    severity: 'warning',
    pattern: /(\w+)\s*\.\s*(\w+)\s*\.\s*(\w+)/g,
    message: (match) => `Potential null reference: chained access "${match[0]}" - consider optional chaining`,
    suggestedFix: () => 'Use optional chaining (?.) to prevent null reference errors',
    autoFixable: true,
    fixedCode: (match) => match[0].replace(/\./g, '?.'),
    fileTypes: ['.js', '.jsx', '.ts', '.tsx'],
  },
  // Missing Python type hints for function parameters
  {
    type: 'type_error',
    severity: 'info',
    pattern: /def\s+\w+\s*\(([^)]*[a-zA-Z_]\w*)\s*(?:,|$)/g,
    message: () => 'Function parameter without type hint',
    suggestedFix: () => 'Add type hints for better code clarity',
    autoFixable: false,
    fileTypes: ['.py'],
  },
  // console.log left in code (TypeScript/JavaScript)
  {
    type: 'potential_bug',
    severity: 'warning',
    pattern: /console\.(log|warn|error|info|debug)\s*\(/g,
    message: (match) => `console.${match[1]} statement found - consider removing for production`,
    suggestedFix: () => 'Remove console statements or use a proper logging library',
    autoFixable: true,
    fixedCode: () => '// console statement removed',
    fileTypes: ['.js', '.jsx', '.ts', '.tsx'],
  },
  // TODO/FIXME comments
  {
    type: 'potential_bug',
    severity: 'info',
    pattern: /\/\/\s*(TODO|FIXME|XXX|HACK|BUG):\s*(.+)$/gim,
    message: (match) => `${match[1]} comment: ${match[2]}`,
    autoFixable: false,
  },
  // Empty catch block
  {
    type: 'potential_bug',
    severity: 'warning',
    pattern: /catch\s*\([^)]*\)\s*\{\s*\}/g,
    message: () => 'Empty catch block - errors will be silently swallowed',
    suggestedFix: () => 'Add error handling or at minimum log the error',
    autoFixable: false,
    fileTypes: ['.js', '.jsx', '.ts', '.tsx'],
  },
  // Unused variable declarations (simple detection)
  {
    type: 'unused_variable',
    severity: 'warning',
    pattern: /(?:const|let|var)\s+_(\w+)\s*=/g,
    message: (match) => `Variable "_${match[1]}" prefixed with underscore suggests it may be unused`,
    suggestedFix: () => 'Remove the variable if unused or rename if it is used',
    autoFixable: false,
    fileTypes: ['.js', '.jsx', '.ts', '.tsx'],
  },
  // Python bare except
  {
    type: 'potential_bug',
    severity: 'warning',
    pattern: /except:\s*$/gm,
    message: () => 'Bare except clause catches all exceptions including KeyboardInterrupt',
    suggestedFix: () => 'Use "except Exception:" to catch only exceptions',
    autoFixable: true,
    fixedCode: () => 'except Exception:',
    fileTypes: ['.py'],
  },
  // == instead of === in JavaScript
  {
    type: 'potential_bug',
    severity: 'warning',
    pattern: /(?<![=!<>])([=!])=(?!=)\s*(?:null|undefined|true|false)/g,
    message: () => 'Using == instead of === for comparison - may cause type coercion issues',
    suggestedFix: () => 'Use === for strict equality comparison',
    autoFixable: true,
    fixedCode: (match) => match[0].replace(/([=!])=/, '$1=='),
    fileTypes: ['.js', '.jsx', '.ts', '.tsx'],
  },
  // Hardcoded URLs/IPs
  {
    type: 'potential_bug',
    severity: 'info',
    pattern: /['"]https?:\/\/(?:localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)[^'"]*['"]/g,
    message: () => 'Hardcoded localhost/local IP address found',
    suggestedFix: () => 'Use environment variables for URLs',
    autoFixable: false,
  },
];

// Scan a single file for errors
function scanFileForErrors(file: FileInput): DetectedError[] {
  const errors: DetectedError[] = [];
  const lines = file.content.split('\n');
  const extension = '.' + (file.path.split('.').pop() || '').toLowerCase();

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
    const line = lines[lineIndex];
    const lineNumber = lineIndex + 1;

    for (const pattern of ERROR_PATTERNS) {
      // Skip patterns that don't apply to this file type
      if (pattern.fileTypes && !pattern.fileTypes.includes(extension)) {
        continue;
      }

      // Reset regex lastIndex for global patterns
      pattern.pattern.lastIndex = 0;

      let match;
      while ((match = pattern.pattern.exec(line)) !== null) {
        const id = `${file.path}:${lineNumber}:${match.index}`;

        // Avoid duplicates
        if (errors.some(e => e.id === id)) continue;

        errors.push({
          id,
          file: file.path,
          line: lineNumber,
          column: match.index + 1,
          type: pattern.type,
          severity: pattern.severity,
          message: pattern.message(match),
          codeSnippet: line.trim(),
          suggestedFix: pattern.suggestedFix?.(match, line),
          fixedCode: pattern.fixedCode?.(match, line),
          autoFixable: pattern.autoFixable,
        });
      }
    }
  }

  return errors;
}

// Scan all files
function scanAllFiles(files: FileInput[]): ScanResult {
  const allErrors: DetectedError[] = [];

  for (const file of files) {
    const fileErrors = scanFileForErrors(file);
    allErrors.push(...fileErrors);
  }

  return {
    totalFiles: files.length,
    filesScanned: files.length,
    errors: allErrors.filter(e => e.severity === 'error'),
    warnings: allErrors.filter(e => e.severity === 'warning'),
    infos: allErrors.filter(e => e.severity === 'info'),
  };
}

// ============================================================================
// Helper Components
// ============================================================================

function ErrorTypeIcon({ type }: { type: ErrorType }) {
  const icons: Record<ErrorType, string> = {
    null_reference: '0',
    type_mismatch: 'T',
    async_timing: 'A',
    import_error: 'I',
    api_error: 'N',
    unknown: '?',
  };
  const colors: Record<ErrorType, string> = {
    null_reference: 'bg-red-500',
    type_mismatch: 'bg-orange-500',
    async_timing: 'bg-purple-500',
    import_error: 'bg-yellow-500',
    api_error: 'bg-blue-500',
    unknown: 'bg-gray-500',
  };
  return (
    <span
      className={`inline-flex items-center justify-center w-6 h-6 rounded text-white text-xs font-bold ${colors[type]}`}
      title={type.replace('_', ' ')}
    >
      {icons[type]}
    </span>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    info: 'bg-blue-100 text-blue-800',
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[severity] || colors.info}`}>
      {severity}
    </span>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const percent = Math.round(value * 100);
  const color =
    percent >= 80 ? 'bg-green-500' : percent >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${percent}%` }} />
      </div>
      <span className="text-sm text-gray-600">{percent}%</span>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export default function DebugWizard() {
  const [tier] = useState<AccessTier>(AccessTier.FREE);
  const [state, setState] = useState<WizardState>({
    step: 'input',
    error_message: '',
    file_path: '',
    stack_trace: '',
    line_number: '',
    code_snippet: '',
    correlate_with_history: true,
    files: [],
    inputMode: 'files',
  });
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [collapsedDirs, setCollapsedDirs] = useState<Set<string>>(new Set());
  const [uploadStats, setUploadStats] = useState<{ total: number; excluded: number } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [selectedErrors, setSelectedErrors] = useState<Set<string>>(new Set());
  const [fixedFiles, setFixedFiles] = useState<Map<string, string>>(new Map());
  const [reviewIndex, setReviewIndex] = useState(0);
  const [reviewMode, setReviewMode] = useState<'list' | 'one-by-one'>('list');

  const limits = getTierLimits(tier);
  const tierDisplay = getTierDisplay(tier);
  const upgradeTier = getUpgradePath(tier);

  // ============================================================================
  // Handlers
  // ============================================================================

  const handleInputChange = (field: keyof WizardState, value: string | boolean) => {
    setState((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = async (files: File[], preservePaths = false) => {
    setIsUploading(true);
    setError(null);

    const maxFiles = limits.maxFiles ?? 100;
    const maxSizeMB = limits.maxFileSizeMB ?? 1;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;

    const newFiles: FileInput[] = [];
    let excludedCount = 0;

    for (const file of files) {
      // Get the file path - use webkitRelativePath for folder uploads, otherwise just the name
      const filePath = preservePaths && file.webkitRelativePath
        ? file.webkitRelativePath
        : file.name;

      // Skip excluded files/folders
      if (shouldExcludeFile(filePath)) {
        excludedCount++;
        continue;
      }

      // Check file size
      if (file.size > maxSizeBytes) {
        // Skip silently for folder uploads, show error for single files
        if (!preservePaths) {
          setError(`File "${file.name}" exceeds the ${maxSizeMB}MB limit.`);
        }
        excludedCount++;
        continue;
      }

      // Skip empty files
      if (file.size === 0) {
        excludedCount++;
        continue;
      }

      // Read file content
      try {
        const content = await file.text();
        newFiles.push({
          path: filePath,
          content: content,
          size_bytes: file.size,
        });
      } catch (err) {
        console.error('Error reading file:', err);
        excludedCount++;
      }
    }

    // Check file count limit after filtering
    const totalFiles = state.files.length + newFiles.length;
    if (totalFiles > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed. You have ${state.files.length} and tried to add ${newFiles.length} (after filtering).`);
      setIsUploading(false);
      return;
    }

    if (newFiles.length > 0) {
      setState((prev) => ({
        ...prev,
        files: [...prev.files, ...newFiles],
        // Auto-fill file path from first file if not set
        file_path: prev.file_path || newFiles[0].path,
      }));
      setError(null);
      setUploadStats({ total: files.length, excluded: excludedCount });
    } else if (files.length > 0) {
      setError('No valid files found after filtering. All files were excluded or too large.');
    }

    setIsUploading(false);
  };

  const toggleDirCollapse = (dir: string) => {
    setCollapsedDirs(prev => {
      const next = new Set(prev);
      if (next.has(dir)) {
        next.delete(dir);
      } else {
        next.add(dir);
      }
      return next;
    });
  };

  const removeFile = (index: number) => {
    setState((prev) => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index),
    }));
  };

  const handleAnalyze = async () => {
    setError(null);

    // Validate input
    if (!state.error_message.trim()) {
      setError('Please enter an error message to analyze');
      return;
    }

    // Validate files if any
    if (state.files.length > 0) {
      const validation = validateFilesForTier(tier, state.files);
      if (!validation.valid) {
        setError(validation.errors.join('; '));
        return;
      }
    }

    setState((prev) => ({ ...prev, step: 'analyzing' }));

    try {
      const input: AnalysisInput = {
        error_message: state.error_message,
        file_path: state.file_path || 'unknown',
        stack_trace: state.stack_trace || undefined,
        line_number: state.line_number ? parseInt(state.line_number, 10) : undefined,
        code_snippet: state.code_snippet || undefined,
        correlate_with_history: state.correlate_with_history,
        file_contents: state.files.length > 0 ? state.files : undefined,
      };

      const response = await fetch('/api/debug-wizard/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });

      const data: AnalysisResponse = await response.json();

      if (!data.success || !data.data) {
        throw new Error(data.error || 'Analysis failed');
      }

      setResult(data.data);
      setState((prev) => ({ ...prev, step: 'results' }));
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setState((prev) => ({ ...prev, step: 'input' }));
    }
  };

  const handleReset = () => {
    setState({
      step: 'input',
      error_message: '',
      file_path: '',
      stack_trace: '',
      line_number: '',
      code_snippet: '',
      correlate_with_history: true,
      files: [],
      inputMode: 'files',
    });
    setResult(null);
    setError(null);
    setCollapsedDirs(new Set());
    setUploadStats(null);
    setScanResult(null);
    setSelectedErrors(new Set());
    setFixedFiles(new Map());
    setReviewIndex(0);
    setReviewMode('list');
  };

  const handleCopyFix = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Scan files for errors
  const handleScanFiles = () => {
    if (state.files.length === 0) {
      setError('Please upload files to scan');
      return;
    }

    setState((prev) => ({ ...prev, step: 'scanning' }));

    // Simulate scanning delay for UX
    setTimeout(() => {
      const result = scanAllFiles(state.files);
      setScanResult(result);
      setSelectedErrors(new Set());
      setFixedFiles(new Map());
      setReviewIndex(0);
      setState((prev) => ({ ...prev, step: 'scan_results' }));
    }, 500);
  };

  // Toggle error selection
  const toggleErrorSelection = (errorId: string) => {
    setSelectedErrors((prev) => {
      const next = new Set(prev);
      if (next.has(errorId)) {
        next.delete(errorId);
      } else {
        next.add(errorId);
      }
      return next;
    });
  };

  // Select all auto-fixable errors
  const selectAllAutoFixable = () => {
    if (!scanResult) return;
    const allErrors = [...scanResult.errors, ...scanResult.warnings, ...scanResult.infos];
    const autoFixable = allErrors.filter((e) => e.autoFixable).map((e) => e.id);
    setSelectedErrors(new Set(autoFixable));
  };

  // Apply fixes to selected errors
  const applySelectedFixes = () => {
    if (!scanResult) return;

    const allErrors = [...scanResult.errors, ...scanResult.warnings, ...scanResult.infos];
    const errorsToFix = allErrors.filter((e) => selectedErrors.has(e.id) && e.autoFixable && e.fixedCode);

    // Group errors by file
    const errorsByFile = new Map<string, DetectedError[]>();
    for (const err of errorsToFix) {
      if (!errorsByFile.has(err.file)) {
        errorsByFile.set(err.file, []);
      }
      errorsByFile.get(err.file)!.push(err);
    }

    // Apply fixes to each file
    const newFixedFiles = new Map(fixedFiles);
    for (const [filePath, errors] of errorsByFile) {
      const file = state.files.find((f) => f.path === filePath);
      if (!file) continue;

      const content = newFixedFiles.get(filePath) || file.content;
      const lines = content.split('\n');

      // Sort errors by line number (descending) to avoid line number shifts
      const sortedErrors = [...errors].sort((a, b) => b.line - a.line);

      for (const err of sortedErrors) {
        if (err.fixedCode) {
          const lineIndex = err.line - 1;
          if (lineIndex >= 0 && lineIndex < lines.length) {
            // Simple replacement of the problematic code snippet
            lines[lineIndex] = lines[lineIndex].replace(err.codeSnippet, err.fixedCode);
          }
        }
      }

      newFixedFiles.set(filePath, lines.join('\n'));
    }

    setFixedFiles(newFixedFiles);

    // Remove fixed errors from selection
    const remainingSelected = new Set(selectedErrors);
    for (const err of errorsToFix) {
      remainingSelected.delete(err.id);
    }
    setSelectedErrors(remainingSelected);
  };

  // Download fixed files as zip or individual file
  const downloadFixedFiles = () => {
    if (fixedFiles.size === 0) {
      alert('No fixes have been applied yet.');
      return;
    }

    if (fixedFiles.size === 1) {
      // Single file download
      const [[fileName, content]] = Array.from(fixedFiles.entries());
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName.split('/').pop() || 'fixed_file.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else {
      // Multiple files - create a simple text summary
      let summary = '=== FIXED FILES ===\n\n';
      for (const [fileName, content] of fixedFiles) {
        summary += `\n${'='.repeat(60)}\n`;
        summary += `FILE: ${fileName}\n`;
        summary += `${'='.repeat(60)}\n\n`;
        summary += content;
        summary += '\n\n';
      }

      const blob = new Blob([summary], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'fixed_files.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  // Send error to AI analysis
  const sendToAIAnalysis = (detectedError: DetectedError) => {
    const file = state.files.find((f) => f.path === detectedError.file);
    setState((prev) => ({
      ...prev,
      error_message: detectedError.message,
      file_path: detectedError.file,
      line_number: detectedError.line.toString(),
      code_snippet: detectedError.codeSnippet,
      step: 'input',
    }));

    // Auto-fill more context if available
    if (file) {
      const lines = file.content.split('\n');
      const startLine = Math.max(0, detectedError.line - 3);
      const endLine = Math.min(lines.length, detectedError.line + 3);
      const context = lines.slice(startLine, endLine).join('\n');
      setState((prev) => ({
        ...prev,
        code_snippet: context,
      }));
    }
  };

  // Demo fill handlers
  const fillNullRefDemo = () => {
    setState((prev) => ({
      ...prev,
      error_message: "TypeError: Cannot read property 'map' of undefined",
      file_path: 'src/components/UserList.tsx',
      stack_trace: `TypeError: Cannot read property 'map' of undefined
    at UserList (src/components/UserList.tsx:15:23)
    at renderWithHooks (node_modules/react-dom/cjs/react-dom.development.js:14985:18)`,
      line_number: '15',
      code_snippet: `const users = data.users;
return users.map(user => <UserCard key={user.id} user={user} />);`,
    }));
  };

  const fillAsyncDemo = () => {
    setState((prev) => ({
      ...prev,
      error_message: 'UnhandledPromiseRejection: Promise rejected before await',
      file_path: 'src/api/fetchData.ts',
      stack_trace: `UnhandledPromiseRejection: Promise rejected
    at fetchUserData (src/api/fetchData.ts:23:5)`,
      line_number: '23',
      code_snippet: `async function fetchUserData() {
  const result = fetchData(); // Missing await!
  return result.data;
}`,
    }));
  };

  const fillImportDemo = () => {
    setState((prev) => ({
      ...prev,
      error_message: "ModuleNotFoundError: No module named 'structlog'",
      file_path: 'src/utils/logger.py',
      stack_trace: `ModuleNotFoundError: No module named 'structlog'
  File "src/utils/logger.py", line 1, in <module>
    import structlog`,
      line_number: '1',
      code_snippet: `import structlog

logger = structlog.get_logger()`,
    }));
  };

  // ============================================================================
  // Render: Input Step
  // ============================================================================

  if (state.step === 'input') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 rounded-t-lg">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">D</span>
              <div>
                <h2 className="text-2xl font-bold">Memory-Enhanced Debugging Wizard</h2>
                <p className="text-purple-200 text-sm">
                  AI that remembers past bugs and their fixes
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-3">
              <span className="px-2 py-1 bg-purple-500 rounded text-xs">
                {tierDisplay.name}
              </span>
              <span className="text-purple-200 text-xs">
                {limits.maxFiles === null ? 'Unlimited files' : `Up to ${limits.maxFiles} files`}
              </span>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="m-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Input Form */}
          <div className="p-6 space-y-6">
            {/* Error Message */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Error Message <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={3}
                value={state.error_message}
                onChange={(e) => handleInputChange('error_message', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                placeholder="Paste your error message here..."
              />
            </div>

            {/* File Upload Section */}
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Add Source Code</h3>
                  <p className="text-sm text-gray-500">
                    Optional - helps the AI understand your code context
                  </p>
                </div>
                <span className="text-xs text-gray-400 bg-white px-3 py-1 rounded-full border">
                  {limits.maxFiles === null ? 'Unlimited' : `Up to ${limits.maxFiles}`} files
                </span>
              </div>

              {/* Loading State */}
              {isUploading && (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin w-8 h-8 border-3 border-purple-200 border-t-purple-600 rounded-full mr-3" />
                  <span className="text-gray-600">Processing files...</span>
                </div>
              )}

              {/* Upload Options - Show when not uploading and no files selected */}
              {!isUploading && state.files.length === 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Individual Files Card */}
                  <div
                    className="relative bg-white rounded-xl border-2 border-dashed border-gray-200 p-6 text-center hover:border-purple-400 hover:bg-purple-50 transition-all cursor-pointer group"
                    onDragOver={(e) => {
                      e.preventDefault();
                      e.currentTarget.classList.add('border-purple-500', 'bg-purple-50');
                    }}
                    onDragLeave={(e) => {
                      e.currentTarget.classList.remove('border-purple-500', 'bg-purple-50');
                    }}
                    onDrop={(e) => {
                      e.preventDefault();
                      e.currentTarget.classList.remove('border-purple-500', 'bg-purple-50');
                      const droppedFiles = Array.from(e.dataTransfer.files);
                      handleFileUpload(droppedFiles, false);
                    }}
                  >
                    <label className="cursor-pointer block">
                      <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                        <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <h4 className="font-semibold text-gray-900 mb-1">Select Files</h4>
                      <p className="text-sm text-gray-500 mb-3">
                        Choose one or more files
                      </p>
                      <span className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                        Browse Files
                      </span>
                      <input
                        type="file"
                        multiple
                        accept=".ts,.tsx,.js,.jsx,.py,.java,.go,.rs,.rb,.php,.c,.cpp,.h,.hpp,.cs,.swift,.kt,.scala,.vue,.svelte,.json,.yaml,.yml,.md,.txt"
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files) {
                            handleFileUpload(Array.from(e.target.files), false);
                          }
                        }}
                      />
                    </label>
                    <p className="text-xs text-gray-400 mt-3">
                      or drag & drop here
                    </p>
                  </div>

                  {/* Folder Card */}
                  <div className="relative bg-white rounded-xl border-2 border-dashed border-gray-200 p-6 text-center hover:border-purple-400 hover:bg-purple-50 transition-all cursor-pointer group">
                    <label className="cursor-pointer block">
                      <div className="w-16 h-16 mx-auto mb-4 bg-yellow-100 rounded-full flex items-center justify-center group-hover:bg-yellow-200 transition-colors">
                        <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                        </svg>
                      </div>
                      <h4 className="font-semibold text-gray-900 mb-1">Select Folder</h4>
                      <p className="text-sm text-gray-500 mb-3">
                        Upload entire project
                      </p>
                      <span className="inline-block px-4 py-2 bg-yellow-600 text-white rounded-lg text-sm font-medium hover:bg-yellow-700 transition-colors">
                        Choose Folder
                      </span>
                      <input
                        type="file"
                        // @ts-expect-error webkitdirectory is non-standard but widely supported
                        webkitdirectory=""
                        directory=""
                        multiple
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files) {
                            handleFileUpload(Array.from(e.target.files), true);
                          }
                        }}
                      />
                    </label>
                    <p className="text-xs text-gray-400 mt-3">
                      Auto-filters node_modules
                    </p>
                  </div>

                  {/* Paste Code Card */}
                  <div
                    className="relative bg-white rounded-xl border-2 border-dashed border-gray-200 p-6 text-center hover:border-purple-400 hover:bg-purple-50 transition-all cursor-pointer group"
                    onClick={() => setState(prev => ({ ...prev, inputMode: 'paste' }))}
                  >
                    <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center group-hover:bg-green-200 transition-colors">
                      <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-1">Paste Code</h4>
                    <p className="text-sm text-gray-500 mb-3">
                      Paste code snippet
                    </p>
                    <span className="inline-block px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors">
                      Paste Code
                    </span>
                    <p className="text-xs text-gray-400 mt-3">
                      Quick & simple
                    </p>
                  </div>
                </div>
              )}

              {/* Paste Mode - Show text area when paste is selected */}
              {!isUploading && state.inputMode === 'paste' && state.files.length === 0 && (
                <div className="mt-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Paste your code:</span>
                    <button
                      type="button"
                      onClick={() => setState(prev => ({ ...prev, inputMode: 'files' }))}
                      className="text-sm text-gray-500 hover:text-gray-700"
                    >
                      ← Back to file options
                    </button>
                  </div>
                  <textarea
                    rows={10}
                    value={state.code_snippet}
                    onChange={(e) => handleInputChange('code_snippet', e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono text-sm bg-white"
                    placeholder="// Paste your code here...&#10;&#10;function example() {&#10;  // Your code&#10;}"
                    autoFocus
                  />
                  <p className="text-xs text-gray-500">
                    Tip: Fill in the &quot;File Path&quot; field below for better context.
                  </p>
                </div>
              )}

              {/* Selected Files Display - Tree View */}
              {!isUploading && state.files.length > 0 && (
                <div className="bg-white rounded-xl border-2 border-green-200 p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <span className="font-semibold text-green-700">
                          {state.files.length} file{state.files.length !== 1 ? 's' : ''} ready
                        </span>
                        {uploadStats && uploadStats.excluded > 0 && (
                          <p className="text-xs text-gray-500">
                            {uploadStats.excluded} files auto-filtered (node_modules, etc.)
                          </p>
                        )}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setState(prev => ({ ...prev, files: [], inputMode: 'files' }));
                        setUploadStats(null);
                        setCollapsedDirs(new Set());
                      }}
                      className="text-sm text-red-600 hover:text-red-800 px-3 py-1 rounded hover:bg-red-50 transition-colors"
                    >
                      Clear all
                    </button>
                  </div>

                  {/* Tree View */}
                  <div className="space-y-1 max-h-48 overflow-y-auto bg-gray-50 rounded-lg border border-gray-200 p-3">
                    {Array.from(groupFilesByDirectory(state.files)).map(([dir, dirFiles]) => (
                      <div key={dir}>
                        {/* Directory Header */}
                        <button
                          type="button"
                          onClick={() => toggleDirCollapse(dir)}
                          className="flex items-center gap-2 w-full text-left py-1.5 px-2 hover:bg-white rounded-lg text-sm transition-colors"
                        >
                          <span className="text-gray-400 text-xs">
                            {collapsedDirs.has(dir) ? '▶' : '▼'}
                          </span>
                          <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                          </svg>
                          <span className="font-medium text-gray-700">{dir}</span>
                          <span className="text-xs text-gray-400 bg-gray-200 px-1.5 py-0.5 rounded">
                            {dirFiles.length}
                          </span>
                        </button>

                        {/* Files in Directory */}
                        {!collapsedDirs.has(dir) && (
                          <div className="ml-7 space-y-0.5 border-l-2 border-gray-200 pl-3 mt-1">
                            {dirFiles.map((file) => {
                              const fileName = file.path.split('/').pop() || file.path;
                              const fileIndex = state.files.findIndex(f => f.path === file.path);
                              return (
                                <div
                                  key={file.path}
                                  className="flex items-center justify-between py-1 px-2 hover:bg-white rounded group transition-colors"
                                >
                                  <div className="flex items-center gap-2 min-w-0">
                                    <svg className="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                                    </svg>
                                    <span className="text-sm font-mono truncate text-gray-700">{fileName}</span>
                                    <span className="text-xs text-gray-400">
                                      {Math.round(file.content.length / 1024 * 10) / 10}KB
                                    </span>
                                  </div>
                                  <button
                                    type="button"
                                    onClick={() => removeFile(fileIndex)}
                                    className="text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity p-1"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                  </button>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Add More Files */}
                  <div className="mt-4 flex gap-3 pt-3 border-t border-gray-200">
                    <label className="flex items-center gap-2 text-sm text-purple-600 hover:text-purple-800 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-purple-50 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Add files
                      <input
                        type="file"
                        multiple
                        accept=".ts,.tsx,.js,.jsx,.py,.java,.go,.rs,.rb,.php,.c,.cpp,.h,.hpp,.cs,.swift,.kt,.scala,.vue,.svelte,.json,.yaml,.yml,.md,.txt"
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files) {
                            handleFileUpload(Array.from(e.target.files), false);
                          }
                        }}
                      />
                    </label>
                    <label className="flex items-center gap-2 text-sm text-purple-600 hover:text-purple-800 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-purple-50 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      </svg>
                      Add folder
                      <input
                        type="file"
                        // @ts-expect-error webkitdirectory is non-standard but widely supported
                        webkitdirectory=""
                        directory=""
                        multiple
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files) {
                            handleFileUpload(Array.from(e.target.files), true);
                          }
                        }}
                      />
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* File Path and Line Number (manual entry fallback) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File Path
                  <span className="text-gray-500 font-normal ml-2">(or enter manually if not uploading)</span>
                </label>
                <input
                  type="text"
                  value={state.file_path}
                  onChange={(e) => handleInputChange('file_path', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="src/components/MyComponent.tsx"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Line Number</label>
                <input
                  type="text"
                  value={state.line_number}
                  onChange={(e) => handleInputChange('line_number', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="42"
                />
              </div>
            </div>

            {/* Stack Trace */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stack Trace (optional)
              </label>
              <textarea
                rows={4}
                value={state.stack_trace}
                onChange={(e) => handleInputChange('stack_trace', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono text-sm"
                placeholder="Paste full stack trace..."
              />
            </div>

            {/* Code Snippet */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code Snippet (optional)
              </label>
              <textarea
                rows={4}
                value={state.code_snippet}
                onChange={(e) => handleInputChange('code_snippet', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono text-sm"
                placeholder="Paste relevant code..."
              />
            </div>

            {/* Options */}
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={state.correlate_with_history}
                  onChange={(e) => handleInputChange('correlate_with_history', e.target.checked)}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">Search historical bug patterns</span>
              </label>
            </div>

            {/* Quick Fill Demos */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-3">Try a demo:</p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={fillNullRefDemo}
                  className="px-3 py-1.5 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
                >
                  Null Reference
                </button>
                <button
                  type="button"
                  onClick={fillAsyncDemo}
                  className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded text-sm hover:bg-purple-200"
                >
                  Async/Await
                </button>
                <button
                  type="button"
                  onClick={fillImportDemo}
                  className="px-3 py-1.5 bg-yellow-100 text-yellow-700 rounded text-sm hover:bg-yellow-200"
                >
                  Import Error
                </button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="border-t border-gray-200 p-6">
            {/* Scan Files Action */}
            {state.files.length > 0 && (
              <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-semibold text-blue-900">Auto-Scan for Errors</h4>
                      <p className="text-sm text-blue-700">
                        Scan {state.files.length} file{state.files.length !== 1 ? 's' : ''} for common bugs and issues
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleScanFiles}
                    className="px-5 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    Scan Files
                  </button>
                </div>
              </div>
            )}

            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                {limits.dailyRequestLimit !== null && (
                  <span>
                    Daily limit: {limits.dailyRequestLimit} analyses
                  </span>
                )}
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={!state.error_message.trim()}
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Analyze Bug
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Upgrade CTA */}
        {limits.showUpgradeCTA && upgradeTier && (
          <div className="mt-6 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-purple-900">
                  Want more power?
                </h4>
                <p className="text-sm text-purple-700">
                  Upgrade to {getTierDisplay(upgradeTier).name} for expanded limits and features.
                </p>
              </div>
              <a
                href={getTierDisplay(upgradeTier).ctaLink}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
              >
                {getTierDisplay(upgradeTier).ctaText}
              </a>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ============================================================================
  // Render: Scanning Step
  // ============================================================================

  if (state.step === 'scanning') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg p-12 text-center">
          <div className="animate-spin w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Scanning your files...</h3>
          <p className="text-gray-600">Detecting common bugs, issues, and potential improvements</p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Scan Results Step
  // ============================================================================

  if (state.step === 'scan_results' && scanResult) {
    const allErrors = [...scanResult.errors, ...scanResult.warnings, ...scanResult.infos];
    const autoFixableCount = allErrors.filter((e) => e.autoFixable).length;
    const selectedCount = selectedErrors.size;
    const currentError = reviewMode === 'one-by-one' ? allErrors[reviewIndex] : null;

    return (
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg">
          <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-3xl">S</span>
                <div>
                  <h2 className="text-2xl font-bold">Scan Complete</h2>
                  <p className="text-blue-200 text-sm">
                    Found {allErrors.length} issue{allErrors.length !== 1 ? 's' : ''} in {scanResult.filesScanned} file{scanResult.filesScanned !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setState((prev) => ({ ...prev, step: 'input' }))}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm"
              >
                Back to Input
              </button>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="p-6 border-b border-gray-200">
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
                <p className="text-3xl font-bold text-red-600">{scanResult.errors.length}</p>
                <p className="text-sm text-red-700">Errors</p>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-3xl font-bold text-yellow-600">{scanResult.warnings.length}</p>
                <p className="text-sm text-yellow-700">Warnings</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-3xl font-bold text-blue-600">{scanResult.infos.length}</p>
                <p className="text-sm text-blue-700">Info</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-3xl font-bold text-green-600">{autoFixableCount}</p>
                <p className="text-sm text-green-700">Auto-fixable</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          {allErrors.length > 0 && (
            <div className="p-6 border-b border-gray-200 bg-gray-50">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-sm font-medium text-gray-700">Fix Mode:</span>
                <button
                  type="button"
                  onClick={() => setReviewMode('list')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    reviewMode === 'list'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
                  }`}
                >
                  List View
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setReviewMode('one-by-one');
                    setReviewIndex(0);
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    reviewMode === 'one-by-one'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
                  }`}
                >
                  One-by-One Review
                </button>

                <div className="flex-1" />

                {autoFixableCount > 0 && reviewMode === 'list' && (
                  <>
                    <button
                      type="button"
                      onClick={selectAllAutoFixable}
                      className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200"
                    >
                      Select All Auto-fixable ({autoFixableCount})
                    </button>
                    {selectedCount > 0 && (
                      <button
                        type="button"
                        onClick={applySelectedFixes}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 flex items-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Fix Selected ({selectedCount})
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* One-by-One Review Mode */}
          {reviewMode === 'one-by-one' && currentError && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-500">
                  Issue {reviewIndex + 1} of {allErrors.length}
                </span>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setReviewIndex(Math.max(0, reviewIndex - 1))}
                    disabled={reviewIndex === 0}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    onClick={() => setReviewIndex(Math.min(allErrors.length - 1, reviewIndex + 1))}
                    disabled={reviewIndex === allErrors.length - 1}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>

              <div className={`p-6 rounded-lg border-2 ${
                currentError.severity === 'error' ? 'bg-red-50 border-red-200' :
                currentError.severity === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                      currentError.severity === 'error' ? 'bg-red-500 text-white' :
                      currentError.severity === 'warning' ? 'bg-yellow-500 text-white' :
                      'bg-blue-500 text-white'
                    }`}>
                      {currentError.severity}
                    </span>
                    <span className="px-2 py-1 bg-gray-200 rounded text-xs font-medium text-gray-700 capitalize">
                      {currentError.type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500 font-mono">
                    {currentError.file}:{currentError.line}
                  </span>
                </div>

                <h4 className="font-semibold text-gray-900 mb-3">{currentError.message}</h4>

                <div className="mb-4">
                  <p className="text-xs font-medium text-gray-500 mb-1">Code:</p>
                  <pre className="bg-gray-900 text-gray-100 p-3 rounded text-sm overflow-x-auto font-mono">
                    <span className="text-gray-500">{currentError.line}: </span>
                    {currentError.codeSnippet}
                  </pre>
                </div>

                {currentError.suggestedFix && (
                  <div className="mb-4 p-3 bg-white rounded border border-gray-200">
                    <p className="text-xs font-medium text-gray-500 mb-1">Suggested Fix:</p>
                    <p className="text-sm text-gray-700">{currentError.suggestedFix}</p>
                  </div>
                )}

                {currentError.fixedCode && (
                  <div className="mb-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Fixed Code:</p>
                    <pre className="bg-green-900 text-green-100 p-3 rounded text-sm overflow-x-auto font-mono">
                      {currentError.fixedCode}
                    </pre>
                  </div>
                )}

                <div className="flex gap-3 mt-4">
                  {currentError.autoFixable && currentError.fixedCode && (
                    <button
                      type="button"
                      onClick={() => {
                        toggleErrorSelection(currentError.id);
                        applySelectedFixes();
                        if (reviewIndex < allErrors.length - 1) {
                          setReviewIndex(reviewIndex + 1);
                        }
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
                    >
                      Apply Fix & Next
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => sendToAIAnalysis(currentError)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
                  >
                    Send to AI Analysis
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      if (reviewIndex < allErrors.length - 1) {
                        setReviewIndex(reviewIndex + 1);
                      }
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300"
                  >
                    Skip
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* List View Mode */}
          {reviewMode === 'list' && allErrors.length > 0 && (
            <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
              {allErrors.map((err) => (
                <div
                  key={err.id}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedErrors.has(err.id)
                      ? 'border-purple-500 bg-purple-50'
                      : err.severity === 'error' ? 'border-red-200 bg-red-50' :
                        err.severity === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                        'border-blue-200 bg-blue-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {err.autoFixable && (
                      <input
                        type="checkbox"
                        checked={selectedErrors.has(err.id)}
                        onChange={() => toggleErrorSelection(err.id)}
                        className="mt-1 w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                          err.severity === 'error' ? 'bg-red-500 text-white' :
                          err.severity === 'warning' ? 'bg-yellow-500 text-white' :
                          'bg-blue-500 text-white'
                        }`}>
                          {err.severity}
                        </span>
                        <span className="px-2 py-0.5 bg-gray-200 rounded text-xs font-medium text-gray-700 capitalize">
                          {err.type.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-500 font-mono truncate">
                          {err.file}:{err.line}
                        </span>
                        {err.autoFixable && (
                          <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">
                            Auto-fixable
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{err.message}</p>
                      <pre className="bg-gray-900 text-gray-100 p-2 rounded text-xs overflow-x-auto font-mono">
                        {err.codeSnippet}
                      </pre>
                      {err.suggestedFix && (
                        <p className="text-xs text-gray-500 mt-2">
                          <strong>Fix:</strong> {err.suggestedFix}
                        </p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => sendToAIAnalysis(err)}
                      className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded text-xs font-medium hover:bg-purple-200"
                    >
                      AI Analyze
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* No Issues Found */}
          {allErrors.length === 0 && (
            <div className="p-12 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Issues Found!</h3>
              <p className="text-gray-600">Your code looks clean. No common bugs or issues detected.</p>
            </div>
          )}

          {/* Fixed Files Download */}
          {fixedFiles.size > 0 && (
            <div className="p-6 border-t border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-900">Fixes Applied</h4>
                    <p className="text-sm text-green-700">
                      {fixedFiles.size} file{fixedFiles.size !== 1 ? 's' : ''} modified
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={downloadFixedFiles}
                  className="px-5 py-2.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download Fixed Files
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Back to Input */}
        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => setState((prev) => ({ ...prev, step: 'input' }))}
            className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
          >
            Back to Input
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700"
          >
            Start Fresh
          </button>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Analyzing Step
  // ============================================================================

  if (state.step === 'analyzing') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg p-12 text-center">
          <div className="animate-spin w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Analyzing your bug...</h3>
          <p className="text-gray-600">Searching historical patterns and generating recommendations</p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Results Step
  // ============================================================================

  if (state.step === 'results' && result) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg">
          <div className="bg-gradient-to-r from-green-600 to-teal-600 text-white p-6 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-3xl">V</span>
                <div>
                  <h2 className="text-2xl font-bold">Analysis Complete</h2>
                  <p className="text-green-200 text-sm">
                    Found {result.matches_found} historical pattern
                    {result.matches_found !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm"
              >
                New Analysis
              </button>
            </div>
          </div>

          {/* Error Classification */}
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ErrorTypeIcon type={result.error_classification.error_type} />
              Error Classification
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Error Type</p>
                <p className="font-medium capitalize">
                  {result.error_classification.error_type.replace('_', ' ')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">File</p>
                <p className="font-medium font-mono text-sm">
                  {result.error_classification.file_path}
                  {result.error_classification.line_number &&
                    `:${result.error_classification.line_number}`}
                </p>
              </div>
            </div>

            {/* Likely Causes */}
            <div className="mt-4">
              <p className="text-sm text-gray-500 mb-2">Likely Causes</p>
              <div className="space-y-2">
                {result.error_classification.likely_causes.map((cause, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 bg-gray-50 p-3 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-sm">{cause.cause}</p>
                      <p className="text-sm text-gray-600">{cause.check}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-gray-500">
                        {Math.round(cause.likelihood * 100)}% likely
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Fix */}
          {result.recommended_fix && (
            <div className="p-6 border-b border-gray-200 bg-purple-50">
              <h3 className="text-lg font-semibold text-purple-900 mb-4">
                Recommended Fix (from Historical Match)
              </h3>
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-medium text-purple-900">
                      {result.recommended_fix.original_fix}
                    </p>
                    <p className="text-sm text-gray-500">
                      Based on: {result.recommended_fix.based_on}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Expected time</p>
                    <p className="font-medium">{result.recommended_fix.expected_resolution_time}</p>
                  </div>
                </div>

                {result.recommended_fix.fix_code && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-gray-700">Example Fix Code:</p>
                      <button
                        type="button"
                        onClick={() => handleCopyFix(result.recommended_fix!.fix_code!)}
                        className="text-sm text-purple-600 hover:text-purple-800"
                      >
                        {copied ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <pre className="bg-gray-900 text-green-400 p-3 rounded text-sm overflow-x-auto">
                      {result.recommended_fix.fix_code}
                    </pre>
                  </div>
                )}

                {result.recommended_fix.adaptation_notes.length > 0 && (
                  <div className="mt-3 bg-yellow-50 border border-yellow-200 rounded p-3">
                    <p className="text-sm font-medium text-yellow-800 mb-1">Adaptation Notes:</p>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      {result.recommended_fix.adaptation_notes.map((note, idx) => (
                        <li key={idx}>- {note}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-3">
                  <p className="text-sm text-gray-500 mb-1">Confidence</p>
                  <ConfidenceBar value={result.recommended_fix.confidence} />
                </div>
              </div>
            </div>
          )}

          {/* Historical Matches */}
          {result.historical_matches.length > 0 && (
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Historical Matches ({result.historical_matches.length})
              </h3>
              <div className="space-y-3">
                {result.historical_matches.map((match: HistoricalMatch, idx: number) => (
                  <div
                    key={idx}
                    className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <ErrorTypeIcon type={match.error_type} />
                        <span className="font-medium">{match.file}</span>
                      </div>
                      <span className="text-sm text-gray-500">{match.date}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Root cause:</strong> {match.root_cause}
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Fix:</strong> {match.fix_applied}
                    </p>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-500">
                        Resolved in {match.resolution_time_minutes} min
                      </span>
                      <span className="text-purple-600">
                        {Math.round(match.similarity_score * 100)}% match
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {match.matching_factors.map((factor, fidx) => (
                        <span
                          key={fidx}
                          className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs"
                        >
                          {factor}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Predictions */}
          {result.predictions.length > 0 && (
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Predictions & Insights
              </h3>
              <div className="space-y-3">
                {result.predictions.map((prediction: Prediction, idx: number) => (
                  <div
                    key={idx}
                    className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <SeverityBadge severity={prediction.severity} />
                      <span className="font-medium capitalize">
                        {prediction.type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{prediction.description}</p>
                    {prediction.prevention_steps.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-1">Prevention steps:</p>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {prediction.prevention_steps.map((step, sidx) => (
                            <li key={sidx} className="flex items-start gap-2">
                              <span className="text-green-500">-</span>
                              {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
            <ul className="space-y-2">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-3 text-gray-700">
                  <span className="text-purple-500 mt-0.5">-</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>

          {/* Memory Benefit */}
          <div className="p-6 bg-gradient-to-r from-purple-50 to-indigo-50">
            <h3 className="text-lg font-semibold text-purple-900 mb-3">
              Memory Benefit
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <p className="text-2xl font-bold text-purple-600">
                  {result.memory_benefit.matches_found}
                </p>
                <p className="text-sm text-gray-600">Patterns Found</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <p className="text-2xl font-bold text-green-600">
                  {result.memory_benefit.time_saved_estimate}
                </p>
                <p className="text-sm text-gray-600">Time Saved</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-200 md:col-span-1">
                <p className="text-sm text-gray-700">{result.memory_benefit.value_statement}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="button"
            onClick={handleReset}
            className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
          >
            Analyze Another Bug
          </button>
          {limits.resolutionRecordingEnabled && result.bug_id && (
            <button
              type="button"
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
              onClick={() => {
                // TODO: Implement resolution recording modal
                alert(
                  `Resolution recording for bug ${result.bug_id} coming soon!\n\nAfter you fix this bug, you can record the resolution to help future debugging.`
                );
              }}
            >
              Record Resolution
            </button>
          )}
        </div>
      </div>
    );
  }

  return null;
}
