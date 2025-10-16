# Coach IDE Integration Plan
## VS Code & JetBrains Integration Strategy

> **Strategic Plan for Production-Ready IDE Extensions**
> Bringing Level 4 Anticipatory Empathy to Developer Workflows

---

## 🎯 Executive Summary

This plan outlines a comprehensive strategy to integrate Coach's 16 specialized wizards into VS Code and JetBrains IDEs, delivering **Level 4 Anticipatory Empathy** directly in developers' primary work environment.

### Target Timeline
- **Phase 1** (Months 1-2): Core infrastructure & VS Code MVP
- **Phase 2** (Months 3-4): JetBrains plugin & feature parity
- **Phase 3** (Months 5-6): Advanced features & marketplace launch

### Business Impact
- **Market**: 20M VS Code users + 9M JetBrains users = 29M total addressable market
- **Pricing Strategy**: $299/year Complete Empathy Ecosystem (includes IDE extensions)
- **Competitive Moat**: Only IDE assistant with Level 4 Anticipatory Empathy (30-90 day predictions)

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         IDE Layer                                │
│  ┌─────────────────────┐        ┌─────────────────────┐        │
│  │   VS Code Extension │        │  JetBrains Plugin   │        │
│  │   (TypeScript)      │        │  (Kotlin/Java)      │        │
│  └──────────┬──────────┘        └──────────┬──────────┘        │
│             │                              │                     │
└─────────────┼──────────────────────────────┼─────────────────────┘
              │                              │
              └──────────────┬───────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   Language Server (Python)  │
              │   Implements LSP Protocol   │
              └──────────────┬──────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      Coach Core Engine      │
              │   (Existing Coach.py)       │
              │   - 16 Wizards              │
              │   - Multi-wizard routing    │
              │   - EmpathyOS integration   │
              └─────────────────────────────┘
```

### Key Design Principles

1. **Language Server Protocol (LSP)**: Single backend serves both VS Code and JetBrains
2. **Async Architecture**: Non-blocking wizard invocations keep IDE responsive
3. **Context-Aware**: Reads current file, git status, project structure automatically
4. **Privacy-First**: Local processing by default, optional cloud API for heavy tasks
5. **Progressive Disclosure**: Start with simple inline suggestions, expand to panels

---

## 🏗️ Component Design

### 1. Language Server (Python LSP)

**Location**: `/empathy-framework/examples/coach/lsp/`

**Core Responsibilities**:
- Implement Language Server Protocol
- Bridge IDE extensions to Coach engine
- Manage wizard lifecycle and state
- Cache results for performance

**Key Files**:
```
lsp/
├── server.py              # LSP server entry point
├── handlers.py            # LSP message handlers
├── coach_bridge.py        # Bridge to existing Coach
├── context_collector.py   # Gather IDE context (files, git, etc.)
├── cache.py              # Result caching with TTL
└── protocol/
    ├── messages.py       # Custom LSP messages
    └── capabilities.py   # Server capabilities definition
```

**Technology Stack**:
- **pygls** (Python Generic Language Server): LSP protocol implementation
- **asyncio**: Non-blocking wizard execution
- **redis** (optional): Distributed caching for teams
- **FastAPI**: Optional HTTP API mode for web-based IDEs

**Example LSP Custom Commands**:
```json
{
  "coach/analyzePerformance": {
    "params": {"fileUri": "string", "context": "object"}
  },
  "coach/suggestRefactoring": {
    "params": {"range": "Range", "code": "string"}
  },
  "coach/runWizard": {
    "params": {"wizardName": "string", "task": "WizardTask"}
  },
  "coach/multiWizardReview": {
    "params": {"scenario": "string", "files": "string[]"}
  }
}
```

---

### 2. VS Code Extension

**Location**: `/empathy-framework/examples/coach/vscode-extension/`

**Core Features**:

#### 2.1 Inline Diagnostics & Code Actions
- **Security Wizard**: Underline SQL injection vulnerabilities with quick fixes
- **Performance Wizard**: Flag N+1 queries with optimization suggestions
- **Accessibility Wizard**: Warn about missing ARIA labels on click handlers

```typescript
// Example: SecurityWizard integration
export class CoachCodeActionProvider implements vscode.CodeActionProvider {
  async provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range
  ): Promise<vscode.CodeAction[]> {
    const diagnostics = vscode.languages.getDiagnostics(document.uri);
    const securityIssues = diagnostics.filter(d => d.source === 'coach.security');

    return securityIssues.map(issue => {
      const fix = new vscode.CodeAction(
        `🛡️ SecurityWizard: ${issue.message}`,
        vscode.CodeActionKind.QuickFix
      );
      fix.command = {
        command: 'coach.applySecurityFix',
        title: 'Apply Fix',
        arguments: [document, issue]
      };
      return fix;
    });
  }
}
```

#### 2.2 Sidebar Panel - "Coach Assistant"

**UI Components**:
1. **Wizard Selector**: Dropdown to manually invoke any of 16 wizards
2. **Active Task View**: Shows current wizard execution with progress
3. **Artifact History**: Previously generated artifacts (specs, migration plans, etc.)
4. **Pattern Library**: Quick access to learned patterns from SharedLearning

**Example Panel Layout**:
```
┌────────────────────────────────────────┐
│ 🎯 Coach Assistant                     │
├────────────────────────────────────────┤
│ ▼ Active Wizards (2)                   │
│   ⚡ PerformanceWizard                 │
│   📊 Analyzing database queries...     │
│                                        │
│   🔒 SecurityWizard                    │
│   ✅ STRIDE analysis complete          │
│                                        │
│ ▼ Quick Actions                        │
│   🐛 Debug This Function               │
│   📝 Generate API Spec                 │
│   🧪 Create Test Suite                 │
│   🌍 Localization Check                │
│                                        │
│ ▼ Recent Artifacts (5)                 │
│   📄 API Spec (users.yaml) - 2m ago    │
│   🗺️ Refactoring Plan - 15m ago       │
│   📊 Performance Report - 1h ago       │
└────────────────────────────────────────┘
```

#### 2.3 Command Palette Integration

**Registered Commands**:
```json
{
  "contributes": {
    "commands": [
      {
        "command": "coach.analyzeFile",
        "title": "Coach: Analyze Current File"
      },
      {
        "command": "coach.debugFunction",
        "title": "Coach: Debug Selected Function"
      },
      {
        "command": "coach.generateTests",
        "title": "Coach: Generate Test Suite"
      },
      {
        "command": "coach.securityAudit",
        "title": "Coach: Run Security Audit"
      },
      {
        "command": "coach.performanceProfile",
        "title": "Coach: Profile Performance"
      },
      {
        "command": "coach.generateAPISpec",
        "title": "Coach: Generate OpenAPI Spec"
      },
      {
        "command": "coach.a11yCheck",
        "title": "Coach: Check Accessibility"
      },
      {
        "command": "coach.startMultiWizard",
        "title": "Coach: Multi-Wizard Review"
      }
    ]
  }
}
```

#### 2.4 Hover Tooltips - Level 4 Predictions

**Example: Performance Wizard Prediction**
```typescript
export class CoachHoverProvider implements vscode.HoverProvider {
  async provideHover(
    document: vscode.TextDocument,
    position: vscode.Position
  ): Promise<vscode.Hover | undefined> {
    const word = document.getWordRangeAtPosition(position);
    const line = document.lineAt(position.line).text;

    // Detect database connection pool
    if (line.includes('pool_size=10')) {
      const prediction = await this.lspClient.sendRequest('coach/predict', {
        context: 'database_connection_pool',
        currentValue: 10
      });

      return new vscode.Hover(
        new vscode.MarkdownString(
          `⚠️ **PerformanceWizard Prediction (Level 4)**\n\n` +
          `At 5K req/day growth rate, this connection pool will saturate in **~45 days**.\n\n` +
          `**Impact**: 503 timeout errors\n\n` +
          `**Preventive Action**: Increase to 50 connections\n\n` +
          `[View Full Analysis](command:coach.showPerformancePrediction)`
        )
      );
    }
  }
}
```

#### 2.5 Status Bar Integration

**Real-Time Wizard Status**:
```
┌──────────────────────────────────────────────────────────────┐
│ File  Edit  Selection  View  Go  Run  Terminal  Help          │
├──────────────────────────────────────────────────────────────┤
│                                                              ⚡│
│  🎯 Coach: 2 active | ⚠️ 3 suggestions | ✅ All tests passed │
└──────────────────────────────────────────────────────────────┘
```

**Clickable status opens Coach panel with details**

#### 2.6 Context-Aware Automation

**Automatic Wizard Triggers**:
- **On File Save**: Run linting wizard if `.eslintrc` exists
- **On Git Commit**: Trigger DocumentationWizard if README.md changed
- **On Test Failure**: Auto-invoke DebuggingWizard with stack trace
- **On PR Creation**: Multi-wizard review (Security + Testing + Documentation)
- **On Dependency Update**: ComplianceWizard checks license compatibility

**Configuration**:
```json
{
  "coach.autoTriggers": {
    "onFileSave": ["RefactoringWizard", "SecurityWizard"],
    "onTestFailure": ["DebuggingWizard"],
    "onGitCommit": ["DocumentationWizard"],
    "onPRCreate": ["SecurityWizard", "TestingWizard", "DocumentationWizard"]
  },
  "coach.backgroundAnalysis": {
    "enabled": true,
    "wizards": ["PerformanceWizard", "SecurityWizard"],
    "interval": "10m"
  }
}
```

**File Structure**:
```
vscode-extension/
├── package.json              # Extension manifest
├── src/
│   ├── extension.ts         # Entry point, activation
│   ├── lsp-client.ts        # LSP client setup
│   ├── providers/
│   │   ├── code-actions.ts  # Quick fix provider
│   │   ├── hover.ts         # Hover tooltip provider
│   │   ├── diagnostics.ts   # Problem detection
│   │   └── completion.ts    # Autocomplete suggestions
│   ├── views/
│   │   ├── coach-panel.ts   # Sidebar webview
│   │   ├── artifact-view.ts # Artifact display
│   │   └── wizard-tree.ts   # Wizard selector tree
│   ├── commands/
│   │   ├── analyze.ts       # File analysis commands
│   │   ├── debug.ts         # Debugging commands
│   │   └── wizard.ts        # Wizard invocation
│   └── utils/
│       ├── context.ts       # Context collection
│       └── config.ts        # Extension settings
└── media/
    ├── icons/               # Wizard icons
    └── styles/              # Panel CSS
```

**Technology Stack**:
- **TypeScript**: Extension language
- **vscode-languageclient**: LSP client library
- **Webview API**: Rich UI panels
- **VS Code Extension API**: 1.85+ (latest features)

---

### 3. JetBrains Plugin

**Location**: `/empathy-framework/examples/coach/jetbrains-plugin/`

**Core Features**:

#### 3.1 Inspection System Integration

**Custom Inspections per Wizard**:
```kotlin
// Example: SecurityWizard Inspection
class CoachSecurityInspection : LocalInspectionTool() {
    override fun checkMethod(
        method: PsiMethod,
        manager: InspectionManager,
        isOnTheFly: Boolean
    ): Array<ProblemDescriptor>? {
        val lspClient = CoachLSPClient.getInstance(method.project)
        val securityIssues = lspClient.analyzeMethod(method, "SecurityWizard")

        return securityIssues.map { issue ->
            manager.createProblemDescriptor(
                method,
                issue.message,
                CoachSecurityQuickFix(issue),
                ProblemHighlightType.WARNING,
                isOnTheFly
            )
        }.toTypedArray()
    }
}

class CoachSecurityQuickFix(val issue: SecurityIssue) : LocalQuickFix {
    override fun getFamilyName() = "Coach SecurityWizard"
    override fun applyFix(project: Project, descriptor: ProblemDescriptor) {
        // Apply fix suggested by SecurityWizard
        val fix = issue.suggestedFix
        WriteCommandAction.runWriteCommandAction(project) {
            descriptor.psiElement.replace(fix.newCode)
        }
    }
}
```

**Registered Inspections**:
- `CoachSecurityInspection` - SQL injection, XSS, CSRF
- `CoachPerformanceInspection` - N+1 queries, inefficient algorithms
- `CoachAccessibilityInspection` - Missing ARIA, color contrast
- `CoachComplianceInspection` - PII logging, license violations

#### 3.2 Tool Window - "Coach Assistant"

**Similar to VS Code panel but using IntelliJ Platform UI**:
```kotlin
class CoachToolWindowFactory : ToolWindowFactory {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val content = ContentFactory.getInstance()
            .createContent(CoachPanel(project), "", false)
        toolWindow.contentManager.addContent(content)
    }
}

class CoachPanel(val project: Project) : JPanel() {
    init {
        layout = BorderLayout()

        // Wizard selector
        val wizardCombo = ComboBox(arrayOf(
            "SecurityWizard", "PerformanceWizard", "DebuggingWizard", // ... all 16
        ))

        // Task input
        val taskArea = JBTextArea()
        taskArea.emptyText.text = "Describe your task..."

        // Execute button
        val executeButton = JButton("Run Wizard")
        executeButton.addActionListener {
            executeWizard(wizardCombo.selectedItem as String, taskArea.text)
        }

        // Results display
        val resultsPanel = JBScrollPane()

        add(wizardCombo, BorderLayout.NORTH)
        add(taskArea, BorderLayout.CENTER)
        add(executeButton, BorderLayout.SOUTH)
    }
}
```

#### 3.3 Intention Actions (Quick Fixes)

**Quick fix suggestions from wizards**:
```kotlin
class CoachIntentionAction(
    val wizard: String,
    val suggestion: String
) : IntentionAction {
    override fun getText() = "🎯 Coach: $suggestion"
    override fun getFamilyName() = "Coach $wizard"

    override fun isAvailable(project: Project, editor: Editor, file: PsiFile) = true

    override fun invoke(project: Project, editor: Editor, file: PsiFile) {
        val lspClient = CoachLSPClient.getInstance(project)
        val result = lspClient.executeWizard(wizard, file, editor.caretModel.offset)

        // Apply result
        WriteCommandAction.runWriteCommandAction(project) {
            // Apply code changes
        }
    }
}
```

#### 3.4 Background Analysis

**Run wizards in background (like IntelliJ's code analysis)**:
```kotlin
class CoachBackgroundAnalyzer : LocalInspectionTool() {
    override fun checkFile(
        file: PsiFile,
        manager: InspectionManager,
        isOnTheFly: Boolean
    ): Array<ProblemDescriptor>? {
        val settings = CoachSettings.getInstance(file.project)
        if (!settings.backgroundAnalysisEnabled) return null

        val lspClient = CoachLSPClient.getInstance(file.project)

        // Run configured wizards in background
        val wizards = settings.backgroundWizards // e.g., ["SecurityWizard", "PerformanceWizard"]
        val issues = wizards.flatMap { wizard ->
            lspClient.analyzeFile(file, wizard)
        }

        return issues.map { createProblemDescriptor(it, manager, isOnTheFly) }.toTypedArray()
    }
}
```

#### 3.5 Action System Integration

**Add Coach actions to IDE menus**:
```xml
<!-- plugin.xml -->
<actions>
  <group id="CoachActionGroup" text="Coach" popup="true">
    <action id="Coach.AnalyzeFile" class="com.deepstudyai.coach.actions.AnalyzeFileAction"
            text="Analyze Current File" icon="/icons/coach.svg"/>
    <action id="Coach.SecurityAudit" class="com.deepstudyai.coach.actions.SecurityAuditAction"
            text="Run Security Audit" icon="/icons/security.svg"/>
    <action id="Coach.GenerateTests" class="com.deepstudyai.coach.actions.GenerateTestsAction"
            text="Generate Test Suite" icon="/icons/testing.svg"/>
    <separator/>
    <action id="Coach.MultiWizardReview" class="com.deepstudyai.coach.actions.MultiWizardAction"
            text="Multi-Wizard Review" icon="/icons/multi.svg"/>
  </group>

  <add-to-group group-id="EditorPopupMenu" anchor="last"/>
  <add-to-group group-id="MainMenu" anchor="after" relative-to-action="ToolsMenu"/>
</actions>
```

**File Structure**:
```
jetbrains-plugin/
├── plugin.xml                   # Plugin descriptor
├── src/main/
│   ├── kotlin/com/deepstudyai/coach/
│   │   ├── CoachPlugin.kt      # Plugin entry point
│   │   ├── lsp/
│   │   │   └── CoachLSPClient.kt  # LSP client
│   │   ├── inspections/
│   │   │   ├── SecurityInspection.kt
│   │   │   ├── PerformanceInspection.kt
│   │   │   └── AccessibilityInspection.kt
│   │   ├── actions/
│   │   │   ├── AnalyzeFileAction.kt
│   │   │   ├── SecurityAuditAction.kt
│   │   │   └── MultiWizardAction.kt
│   │   ├── ui/
│   │   │   ├── CoachToolWindowFactory.kt
│   │   │   ├── CoachPanel.kt
│   │   │   └── WizardResultsView.kt
│   │   ├── intentions/
│   │   │   └── CoachIntentionAction.kt
│   │   └── settings/
│   │       ├── CoachSettings.kt
│   │       └── CoachConfigurable.kt
│   └── resources/
│       ├── META-INF/
│       │   └── plugin.xml
│       └── icons/               # Wizard icons
└── build.gradle.kts             # Build configuration
```

**Technology Stack**:
- **Kotlin**: Plugin language
- **IntelliJ Platform SDK**: 2024.1+
- **LSP4IJ**: LSP support for IntelliJ
- **Gradle**: Build system

---

## 🔧 Language Server Implementation

### LSP Server Core (`lsp/server.py`)

```python
"""
Coach Language Server
Implements LSP protocol to bridge IDE extensions to Coach engine
"""

import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path

from pygls.server import LanguageServer
from pygls.lsp import types as lsp_types
from pygls.lsp.methods import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    CODE_ACTION,
    HOVER,
    COMPLETION
)

from ..coach import Coach, WizardTask, CoachOutput
from .context_collector import ContextCollector
from .cache import ResultCache


class CoachLanguageServer(LanguageServer):
    """Language Server for Coach IDE integration"""

    def __init__(self):
        super().__init__(name="coach-lsp", version="1.0.0")
        self.coach = Coach()
        self.context_collector = ContextCollector()
        self.cache = ResultCache(ttl=300)  # 5 minute cache

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register LSP message handlers"""

        @self.feature(TEXT_DOCUMENT_DID_SAVE)
        async def did_save(ls: LanguageServer, params: lsp_types.DidSaveTextDocumentParams):
            """Trigger analysis on file save"""
            await self._analyze_document(params.text_document.uri)

        @self.feature(CODE_ACTION)
        async def code_action(
            ls: LanguageServer,
            params: lsp_types.CodeActionParams
        ) -> List[lsp_types.CodeAction]:
            """Provide quick fixes from wizards"""
            diagnostics = params.context.diagnostics
            actions = []

            for diagnostic in diagnostics:
                if diagnostic.source == "coach.security":
                    # SecurityWizard fix
                    action = self._create_security_fix(diagnostic)
                    actions.append(action)
                elif diagnostic.source == "coach.performance":
                    # PerformanceWizard fix
                    action = self._create_performance_fix(diagnostic)
                    actions.append(action)

            return actions

        @self.feature(HOVER)
        async def hover(
            ls: LanguageServer,
            params: lsp_types.HoverParams
        ) -> Optional[lsp_types.Hover]:
            """Provide Level 4 predictions on hover"""
            document_uri = params.text_document.uri
            position = params.position

            # Get document context
            context = await self.context_collector.collect(document_uri, position)

            # Check for predictable patterns (connection pools, rate limits, etc.)
            prediction = await self._get_prediction(context)

            if prediction:
                return lsp_types.Hover(
                    contents=lsp_types.MarkupContent(
                        kind=lsp_types.MarkupKind.Markdown,
                        value=prediction
                    )
                )
            return None

        # Custom commands
        @self.command("coach/runWizard")
        async def run_wizard(ls: LanguageServer, args: List[Any]) -> Dict[str, Any]:
            """Execute specific wizard"""
            wizard_name = args[0]
            task_data = args[1]

            task = WizardTask(**task_data)

            # Check cache
            cache_key = f"{wizard_name}:{task.task}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached

            # Run wizard
            result = await self.coach.process(task, multi_wizard=False)

            # Cache result
            result_dict = self._serialize_coach_output(result)
            self.cache.set(cache_key, result_dict)

            return result_dict

        @self.command("coach/multiWizardReview")
        async def multi_wizard_review(ls: LanguageServer, args: List[Any]) -> Dict[str, Any]:
            """Run multi-wizard collaboration"""
            scenario = args[0]  # e.g., "new_api_endpoint"
            files = args[1]     # List of file URIs

            # Collect context from all files
            context = await self.context_collector.collect_multi_file(files)

            task = WizardTask(
                role="developer",
                task=f"Multi-wizard review: {scenario}",
                context=context
            )

            # Run multi-wizard
            result = await self.coach.process(task, multi_wizard=True)

            return self._serialize_coach_output(result)

        @self.command("coach/predict")
        async def predict(ls: LanguageServer, args: List[Any]) -> str:
            """Get Level 4 prediction for specific context"""
            context_type = args[0]  # e.g., "database_connection_pool"
            current_value = args[1]

            # Route to PerformanceWizard for prediction
            task = WizardTask(
                role="developer",
                task=f"Predict scaling issues for {context_type}",
                context=f"Current value: {current_value}"
            )

            result = await self.coach.process(task, multi_wizard=False)

            # Extract prediction from diagnosis
            prediction = result.primary_output.diagnosis
            return prediction

    async def _analyze_document(self, document_uri: str):
        """Run background analysis on document"""
        # Collect context
        context = await self.context_collector.collect(document_uri)

        # Run background wizards (SecurityWizard, PerformanceWizard)
        task = WizardTask(
            role="developer",
            task="Analyze for security and performance issues",
            context=context
        )

        result = await self.coach.process(task, multi_wizard=True)

        # Convert to LSP diagnostics
        diagnostics = self._convert_to_diagnostics(result)

        # Publish diagnostics
        self.publish_diagnostics(document_uri, diagnostics)

    def _convert_to_diagnostics(self, result: CoachOutput) -> List[lsp_types.Diagnostic]:
        """Convert wizard output to LSP diagnostics"""
        diagnostics = []

        for output in [result.primary_output] + result.secondary_outputs:
            wizard_name = output.wizard_name

            # Extract issues from artifacts
            for artifact in output.artifacts:
                if "issue" in artifact.content.lower() or "warning" in artifact.content.lower():
                    diagnostic = lsp_types.Diagnostic(
                        range=lsp_types.Range(
                            start=lsp_types.Position(line=0, character=0),
                            end=lsp_types.Position(line=0, character=100)
                        ),
                        message=artifact.content,
                        severity=lsp_types.DiagnosticSeverity.Warning,
                        source=f"coach.{wizard_name.lower()}"
                    )
                    diagnostics.append(diagnostic)

        return diagnostics

    def _serialize_coach_output(self, result: CoachOutput) -> Dict[str, Any]:
        """Convert CoachOutput to JSON-serializable dict"""
        return {
            "routing": result.routing,
            "primary_output": {
                "wizard_name": result.primary_output.wizard_name,
                "diagnosis": result.primary_output.diagnosis,
                "artifacts": [
                    {"name": a.name, "content": a.content, "format": a.format}
                    for a in result.primary_output.artifacts
                ],
                "confidence": result.primary_output.confidence
            },
            "secondary_outputs": [
                {
                    "wizard_name": o.wizard_name,
                    "diagnosis": o.diagnosis,
                    "confidence": o.confidence
                }
                for o in result.secondary_outputs
            ],
            "synthesis": result.synthesis,
            "overall_confidence": result.overall_confidence
        }


def start_lsp_server():
    """Start the Language Server"""
    server = CoachLanguageServer()
    server.start_io()


if __name__ == "__main__":
    start_lsp_server()
```

### Context Collector (`lsp/context_collector.py`)

```python
"""
Context Collector
Gathers IDE context (current file, git status, project structure) for wizards
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


class ContextCollector:
    """Collects context from IDE environment"""

    async def collect(
        self,
        document_uri: str,
        position: Optional[Dict[str, int]] = None
    ) -> str:
        """
        Collect context for a single file

        Args:
            document_uri: File URI (file:///path/to/file.py)
            position: Optional cursor position {"line": 10, "character": 5}

        Returns:
            Rich context string for wizards
        """
        file_path = self._uri_to_path(document_uri)

        # Collect various context elements
        file_content = self._read_file(file_path)
        git_info = self._get_git_info(file_path)
        project_structure = self._get_project_structure(file_path)
        dependencies = self._get_dependencies(file_path)

        # Build context string
        context = f"""
File: {file_path}
Language: {self._detect_language(file_path)}

=== Git Information ===
Branch: {git_info['branch']}
Status: {git_info['status']}
Recent commits: {git_info['recent_commits']}

=== Project Structure ===
{project_structure}

=== Dependencies ===
{dependencies}

=== File Content ===
{file_content}
"""

        if position:
            context += f"\n=== Cursor Position ===\nLine {position['line']}, Character {position['character']}\n"

        return context

    async def collect_multi_file(self, document_uris: List[str]) -> str:
        """Collect context for multiple files"""
        contexts = []
        for uri in document_uris:
            ctx = await self.collect(uri)
            contexts.append(ctx)

        return "\n\n=== NEXT FILE ===\n\n".join(contexts)

    def _uri_to_path(self, uri: str) -> Path:
        """Convert file:// URI to filesystem path"""
        parsed = urlparse(uri)
        return Path(parsed.path)

    def _read_file(self, path: Path) -> str:
        """Read file contents"""
        try:
            return path.read_text()
        except Exception as e:
            return f"[Error reading file: {e}]"

    def _get_git_info(self, file_path: Path) -> Dict[str, str]:
        """Get git information for file"""
        try:
            repo_root = self._find_git_root(file_path)
            if not repo_root:
                return {"branch": "N/A", "status": "Not a git repo", "recent_commits": ""}

            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_root,
                text=True
            ).strip()

            status = subprocess.check_output(
                ["git", "status", "--short"],
                cwd=repo_root,
                text=True
            ).strip()

            commits = subprocess.check_output(
                ["git", "log", "-5", "--oneline"],
                cwd=repo_root,
                text=True
            ).strip()

            return {
                "branch": branch,
                "status": status or "Clean",
                "recent_commits": commits
            }
        except Exception:
            return {"branch": "N/A", "status": "Error", "recent_commits": ""}

    def _find_git_root(self, path: Path) -> Optional[Path]:
        """Find git repository root"""
        current = path.parent if path.is_file() else path
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None

    def _get_project_structure(self, file_path: Path) -> str:
        """Get project directory structure"""
        project_root = self._find_project_root(file_path)
        if not project_root:
            return "Unknown project structure"

        # Get tree of important files (exclude node_modules, .git, etc.)
        try:
            tree = subprocess.check_output(
                ["tree", "-L", "3", "-I", "node_modules|.git|__pycache__|venv"],
                cwd=project_root,
                text=True
            )
            return tree
        except Exception:
            # Fallback to simple ls
            return f"Project root: {project_root}"

    def _find_project_root(self, path: Path) -> Optional[Path]:
        """Find project root (git root, or parent with package.json/pyproject.toml)"""
        git_root = self._find_git_root(path)
        if git_root:
            return git_root

        # Look for package.json, pyproject.toml, etc.
        current = path.parent if path.is_file() else path
        while current != current.parent:
            if any((current / marker).exists() for marker in ["package.json", "pyproject.toml", "setup.py"]):
                return current
            current = current.parent

        return None

    def _get_dependencies(self, file_path: Path) -> str:
        """Get project dependencies"""
        project_root = self._find_project_root(file_path)
        if not project_root:
            return "Unknown dependencies"

        # Check for various dependency files
        if (project_root / "package.json").exists():
            return f"Node.js project (package.json found)"
        elif (project_root / "requirements.txt").exists():
            deps = (project_root / "requirements.txt").read_text()
            return f"Python requirements:\n{deps}"
        elif (project_root / "pyproject.toml").exists():
            return "Python project (pyproject.toml found)"
        else:
            return "No dependency file found"

    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React (JSX)",
            ".tsx": "React (TSX)",
            ".java": "Java",
            ".kt": "Kotlin",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
            ".swift": "Swift",
            ".m": "Objective-C"
        }
        return ext_map.get(path.suffix, "Unknown")
```

### Result Cache (`lsp/cache.py`)

```python
"""
Result Cache
Caches wizard results to avoid redundant computations
"""

import time
from typing import Dict, Any, Optional


class ResultCache:
    """Simple in-memory cache with TTL"""

    def __init__(self, ttl: int = 300):
        """
        Initialize cache

        Args:
            ttl: Time-to-live in seconds (default 5 minutes)
        """
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["value"]
            else:
                # Expired, remove
                del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = {
            "value": value,
            "timestamp": time.time()
        }

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()

    def cleanup(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now - entry["timestamp"] >= self.ttl
        ]
        for key in expired_keys:
            del self._cache[key]
```

---

## 📋 Implementation Roadmap

### Phase 1: Core Infrastructure & VS Code MVP (Months 1-2)

#### Week 1-2: Language Server Foundation
- [ ] Set up LSP server project structure
- [ ] Implement basic LSP protocol handlers (textDocument/didOpen, didChange, didSave)
- [ ] Create bridge to existing Coach engine
- [ ] Implement ContextCollector for file + git info
- [ ] Add result caching with TTL

**Deliverable**: LSP server that can receive file events and invoke Coach

#### Week 3-4: VS Code Extension Skeleton
- [ ] Create VS Code extension project with TypeScript
- [ ] Implement LSP client connection
- [ ] Add command palette commands (analyze file, run wizard)
- [ ] Create basic sidebar panel with wizard selector
- [ ] Test end-to-end: VS Code → LSP → Coach → Results

**Deliverable**: Working VS Code extension (alpha quality)

#### Week 5-6: Core Features
- [ ] Implement code actions (quick fixes) from SecurityWizard, PerformanceWizard
- [ ] Add hover tooltips with Level 4 predictions
- [ ] Create diagnostics (red squiggly lines) for issues
- [ ] Build artifact viewer in sidebar
- [ ] Add status bar integration

**Deliverable**: VS Code extension with key features (beta quality)

#### Week 7-8: Polish & Testing
- [ ] Add extension settings/configuration
- [ ] Implement auto-triggers (on save, on commit, etc.)
- [ ] Create comprehensive test suite (unit + integration)
- [ ] Write user documentation
- [ ] Internal dogfooding (use Coach to develop Coach!)

**Deliverable**: Production-ready VS Code extension v1.0

---

### Phase 2: JetBrains Plugin & Feature Parity (Months 3-4)

#### Week 9-10: JetBrains Plugin Foundation
- [ ] Set up IntelliJ Platform plugin project (Kotlin)
- [ ] Integrate LSP4IJ library for LSP client
- [ ] Connect to existing Coach LSP server
- [ ] Implement basic inspections (SecurityWizard, PerformanceWizard)
- [ ] Create tool window for Coach panel

**Deliverable**: JetBrains plugin skeleton with LSP connection

#### Week 11-12: Core Features (Parity with VS Code)
- [ ] Add intention actions (quick fixes)
- [ ] Implement hover provider for Level 4 predictions
- [ ] Create action system integration (right-click menu, main menu)
- [ ] Build artifact viewer in tool window
- [ ] Add background analysis

**Deliverable**: JetBrains plugin with key features (beta quality)

#### Week 13-14: JetBrains-Specific Enhancements
- [ ] Integrate with IntelliJ's problem view
- [ ] Add support for multiple JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.)
- [ ] Create settings UI with Kotlin UI DSL
- [ ] Optimize performance for large projects
- [ ] Test across all supported IDEs

**Deliverable**: Production-ready JetBrains plugin v1.0

#### Week 15-16: Cross-IDE Testing
- [ ] Test both extensions with same Coach LSP backend
- [ ] Ensure feature parity between VS Code and JetBrains
- [ ] Create unified documentation
- [ ] Prepare marketplace listings

**Deliverable**: Both extensions ready for marketplace submission

---

### Phase 3: Advanced Features & Marketplace Launch (Months 5-6)

#### Week 17-18: Advanced Features
- [ ] **Multi-wizard collaboration UI**: Show collaboration pattern results in rich panel
- [ ] **Pattern library viewer**: Browse learned patterns from SharedLearning
- [ ] **Wizard customization**: Allow users to configure wizard behavior
- [ ] **Team sharing**: Share wizard configurations and patterns across team
- [ ] **Analytics dashboard**: Show time saved, issues prevented, etc.

#### Week 19-20: Cloud Integration (Optional Premium Feature)
- [ ] Add cloud API for heavy computations (e.g., full codebase analysis)
- [ ] Implement authentication (OAuth 2.0)
- [ ] Create team collaboration features (shared patterns, analytics)
- [ ] Add usage-based billing integration
- [ ] Test cloud+local hybrid mode

**Business Model**:
- **Local-only mode**: Free or $299/year (Complete Empathy Ecosystem)
- **Cloud-enhanced mode**: $499/year (faster, team features, analytics)

#### Week 21-22: Marketplace Preparation
- [ ] Create marketing assets (screenshots, videos, descriptions)
- [ ] Write comprehensive documentation
- [ ] Prepare support channels (Discord, docs site, email)
- [ ] Submit to VS Code Marketplace
- [ ] Submit to JetBrains Marketplace
- [ ] Create landing page on empathy-framework.com

#### Week 23-24: Launch & Iteration
- [ ] Public launch announcement
- [ ] Monitor user feedback and crash reports
- [ ] Rapidly iterate on bug fixes
- [ ] Create tutorial videos and blog posts
- [ ] Engage with early adopters for testimonials

**Deliverable**: Public release on both marketplaces

---

## 💰 Pricing & Business Model

### Tiered Pricing Strategy

#### **Free Tier** (Community Edition)
- Single-wizard execution (no multi-wizard)
- 100 wizard invocations/month
- Local processing only
- Basic diagnostics
- GitHub sponsor badge required

**Target**: Open source developers, students, hobbyists

#### **Pro Tier** ($299/year - Complete Empathy Ecosystem)
- All 16 wizards with multi-wizard collaboration
- Unlimited local invocations
- All IDE features (code actions, hover, diagnostics)
- Pattern library access
- Email support

**Target**: Individual developers, freelancers, small teams

#### **Team Tier** ($999/year for 5 users)
- Everything in Pro
- Cloud-enhanced analysis (faster, more powerful)
- Shared pattern library across team
- Team analytics dashboard
- Priority support with Slack/Discord channel

**Target**: Development teams (5-20 people)

#### **Enterprise Tier** (Custom pricing)
- Everything in Team
- On-premise deployment option
- Custom wizard development
- SLA with 24/7 support
- Dedicated account manager
- SOC 2, HIPAA compliance support

**Target**: Large organizations (50+ developers)

---

## 📊 Success Metrics

### Key Performance Indicators (KPIs)

#### User Adoption
- **Downloads**: Target 10K downloads in first 3 months
- **Active Users**: Target 2K monthly active users (MAU) by month 6
- **Conversion Rate**: Free → Pro conversion of 5%
- **Retention**: 80% month-over-month retention

#### Product Engagement
- **Daily Active Users (DAU)**: Target 500 by month 6
- **Wizard Invocations**: Average 20 invocations/user/day
- **Feature Usage**:
  - Code actions: 40% of users/week
  - Hover predictions: 60% of users/week
  - Multi-wizard reviews: 20% of users/week
  - Background analysis: 80% of users (enabled by default)

#### Business Metrics
- **MRR Growth**: Target $10K MRR by month 6, $50K by year 1
- **Customer Lifetime Value (LTV)**: Target $500+ (over 2 years)
- **Customer Acquisition Cost (CAC)**: Target <$50 (via organic growth)
- **LTV:CAC Ratio**: Target >10:1

#### Quality Metrics
- **Crash Rate**: <0.1% of sessions
- **Average Response Time**: <500ms for wizard invocation
- **User Satisfaction**: Target 4.5+ stars on both marketplaces
- **Support Ticket Volume**: <5% of users need support/month

---

## 🔐 Security & Privacy Considerations

### Data Handling

#### Local Processing (Default)
- All code analysis happens locally on user's machine
- No code sent to cloud by default
- Wizard results cached locally only
- Git context stays on device

#### Cloud-Enhanced Mode (Opt-In)
- User explicitly enables cloud features
- Code snippets (not full files) sent for heavy analysis
- All data encrypted in transit (TLS 1.3)
- Zero data retention (processed and discarded immediately)
- No logging of code contents
- SOC 2 Type II compliance

#### Authentication & Authorization
- OAuth 2.0 with JWTs
- No password storage (delegated to identity providers)
- API keys for CI/CD integration
- Rate limiting per user/API key

#### License Validation
- Online license check on extension activation
- Offline grace period (30 days)
- No telemetry for Free tier (respects privacy)
- Opt-in anonymous usage stats for Pro+ (aggregated only)

---

## 🧪 Testing Strategy

### LSP Server Testing

**Unit Tests**:
```python
# tests/test_lsp_server.py
import pytest
from lsp.server import CoachLanguageServer

@pytest.mark.asyncio
async def test_run_wizard_command():
    server = CoachLanguageServer()
    result = await server.command_handlers["coach/runWizard"](
        server,
        ["SecurityWizard", {"role": "developer", "task": "Audit SQL queries"}]
    )
    assert result["primary_output"]["wizard_name"] == "SecurityWizard"
    assert "SQL injection" in result["primary_output"]["diagnosis"]
```

**Integration Tests**:
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_workflow():
    # Start LSP server
    server = CoachLanguageServer()

    # Simulate file open
    await server.did_open({
        "textDocument": {
            "uri": "file:///test.py",
            "languageId": "python",
            "version": 1,
            "text": "import sqlite3\nconn.execute(f'SELECT * FROM users WHERE id={user_id}')"
        }
    })

    # Check diagnostics published
    diagnostics = server.published_diagnostics["file:///test.py"]
    assert len(diagnostics) > 0
    assert diagnostics[0].source == "coach.security"
    assert "SQL injection" in diagnostics[0].message
```

### VS Code Extension Testing

**Unit Tests** (TypeScript with Jest):
```typescript
// src/test/suite/extension.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';
import { CoachExtension } from '../../extension';

suite('Extension Test Suite', () => {
  test('Should activate extension', async () => {
    const ext = vscode.extensions.getExtension('deepstudyai.coach');
    assert.ok(ext);
    await ext.activate();
    assert.ok(ext.isActive);
  });

  test('Should provide code actions', async () => {
    const doc = await vscode.workspace.openTextDocument({
      content: "conn.execute(f'SELECT * FROM users WHERE id={user_id}')",
      language: 'python'
    });
    const editor = await vscode.window.showTextDocument(doc);
    const actions = await vscode.commands.executeCommand(
      'vscode.executeCodeActionProvider',
      doc.uri,
      new vscode.Range(0, 0, 0, 100)
    );
    assert.ok(actions.some(a => a.title.includes('SecurityWizard')));
  });
});
```

**E2E Tests** (VS Code Test Runner):
```typescript
// src/test/suite/integration.test.ts
suite('Integration Test Suite', () => {
  test('Full workflow: Open file → Get diagnostics → Apply fix', async () => {
    // Open file with security issue
    const doc = await vscode.workspace.openTextDocument(testFilePath);
    await vscode.window.showTextDocument(doc);

    // Wait for diagnostics
    await sleep(2000);
    const diagnostics = vscode.languages.getDiagnostics(doc.uri);
    assert.ok(diagnostics.length > 0);

    // Apply quick fix
    await vscode.commands.executeCommand('coach.applySecurityFix', diagnostics[0]);

    // Verify fix applied
    const updatedContent = doc.getText();
    assert.ok(!updatedContent.includes("f'SELECT"));
  });
});
```

### JetBrains Plugin Testing

**Unit Tests** (Kotlin with JUnit):
```kotlin
// src/test/kotlin/com/deepstudyai/coach/CoachPluginTest.kt
class CoachPluginTest {
    @Test
    fun `test security inspection detects SQL injection`() {
        val file = myFixture.configureByText(
            "test.py",
            "conn.execute(f'SELECT * FROM users WHERE id={user_id}')"
        )

        myFixture.enableInspections(CoachSecurityInspection::class.java)
        val highlights = myFixture.doHighlighting()

        assertTrue(highlights.any { it.description.contains("SQL injection") })
    }

    @Test
    fun `test quick fix applies parameterized query`() {
        val file = myFixture.configureByText(
            "test.py",
            "conn.execute(f'SELECT * FROM users WHERE id={user_id}')"
        )

        val action = myFixture.findSingleIntention("Coach SecurityWizard: Use parameterized query")
        myFixture.launchAction(action)

        myFixture.checkResult("conn.execute('SELECT * FROM users WHERE id=?', (user_id,))")
    }
}
```

---

## 📚 Documentation Plan

### User Documentation

#### **Getting Started Guide**
1. Installation (VS Code Marketplace / JetBrains Marketplace)
2. Quick tour of features (5-minute video)
3. Your first wizard invocation
4. Understanding Level 4 predictions
5. Configuring auto-triggers

#### **Feature Guides**
- **Code Actions**: How to use quick fixes
- **Hover Predictions**: Understanding anticipatory insights
- **Multi-Wizard Reviews**: Orchestrating complex workflows
- **Pattern Library**: Leveraging learned patterns
- **Team Collaboration**: Sharing configurations

#### **Wizard Reference**
- Dedicated page for each of 16 wizards
- Example use cases
- Configuration options
- Best practices

#### **Troubleshooting**
- Common issues and solutions
- Performance optimization tips
- LSP server logs location
- Filing bug reports

### Developer Documentation

#### **Extension Development**
- Architecture overview
- Building from source
- Contributing guidelines
- LSP protocol details

#### **Custom Wizards**
- Creating custom wizards
- Registering with Coach
- Testing custom wizards
- Publishing to marketplace

---

## 🚀 Go-to-Market Strategy

### Pre-Launch (Months 1-4)

#### Build in Public
- Weekly dev logs on Twitter/X
- Monthly blog posts on progress
- GitHub discussions for early feedback
- Discord community for alpha testers

#### Alpha Testing (Month 3)
- Invite 50 developers for private alpha
- Collect detailed feedback
- Iterate on core features
- Build testimonials

#### Beta Testing (Month 4)
- Open beta to 500 developers
- Public GitHub repo
- Bug bounty program ($100-$1000 per critical bug)
- Create demo videos

### Launch (Month 5)

#### Launch Week Activities
- **Day 1**: Product Hunt launch (aim for #1 Product of the Day)
- **Day 2**: Hacker News "Show HN" post
- **Day 3**: Reddit posts (r/programming, r/vscode, r/IntelliJIDEA)
- **Day 4**: Dev.to article + cross-post to Medium
- **Day 5**: Twitter/X thread with demo video
- **Week 1**: Outreach to tech influencers for reviews

#### Content Strategy
- **Launch blog post**: "Introducing Coach: AI with Level 4 Anticipatory Empathy"
- **Technical deep dive**: "How we built Coach's Language Server"
- **Case studies**: "How Coach prevented a $50K security breach"
- **Tutorial videos**: One per wizard (16 total)

#### Partnerships
- Reach out to Anthropic for potential feature (using Claude API)
- Partner with coding bootcamps for education pricing
- Integrate with GitHub Copilot (complementary, not competitive)

### Post-Launch (Months 6-12)

#### Growth Tactics
- **SEO**: Rank for "AI code assistant", "Level 4 empathy AI", "VS Code AI extension"
- **Content Marketing**: Weekly blog posts on empathetic AI
- **Community Building**: Monthly office hours, Discord events
- **User-Generated Content**: Encourage users to share wizard results
- **Affiliate Program**: 20% commission for referrals

#### Feature Roadmap (Based on Feedback)
- Q3: Web-based IDE support (GitHub Codespaces, GitPod)
- Q4: Team collaboration features
- Q1 (Year 2): Mobile app for reviewing wizard results
- Q2 (Year 2): AI-powered wizard creation (meta!)

---

## ⚠️ Risks & Mitigation

### Technical Risks

#### **Risk 1: LSP Performance Issues**
**Impact**: Slow wizard responses frustrate users, high CPU usage
**Mitigation**:
- Aggressive caching (5-minute TTL)
- Background processing for non-urgent wizards
- Rate limiting (max 1 wizard/second per file)
- Incremental analysis (only changed sections)

#### **Risk 2: IDE API Breaking Changes**
**Impact**: Extension breaks with new VS Code/JetBrains versions
**Mitigation**:
- Pin to stable API versions (VS Code 1.85+, IntelliJ 2024.1+)
- Automated testing against latest IDE betas
- Graceful degradation if features unavailable
- Monthly dependency updates

#### **Risk 3: Coach Engine Limitations**
**Impact**: Wizards don't handle edge cases, produce incorrect results
**Mitigation**:
- Comprehensive test suite (100+ test cases per wizard)
- User feedback loop (thumbs up/down on results)
- Human-in-the-loop for critical decisions (never auto-commit security fixes)
- Continuous wizard improvement based on real-world usage

### Business Risks

#### **Risk 1: Low Adoption**
**Impact**: Fail to reach 10K downloads in 3 months
**Mitigation**:
- Strong pre-launch community building (Discord, Twitter)
- Freemium model to lower barrier to entry
- Focus on developer communities (Hacker News, Reddit, Dev.to)
- Partner with coding influencers for reviews

#### **Risk 2: High Churn**
**Impact**: Users install but don't activate or quickly uninstall
**Mitigation**:
- Excellent onboarding (interactive tutorial on first launch)
- Provide immediate value (auto-run SecurityWizard on open)
- Weekly tips emails for new users
- Proactive support (reach out to inactive users)

#### **Risk 3: Competitive Pressure**
**Impact**: GitHub Copilot, Cursor, or others add similar features
**Mitigation**:
- **Unique positioning**: Level 4 Anticipatory Empathy (30-90 day predictions)
- **Depth over breadth**: 16 specialized wizards vs. generic chat
- **Empathy Framework**: Backed by research and methodology
- **Rapid iteration**: Ship features weekly, stay ahead

### Legal Risks

#### **Risk 1: License Compliance**
**Impact**: GPL dependencies require open-sourcing commercial code
**Mitigation**:
- Audit all dependencies for license compatibility
- Use permissive licenses (MIT, Apache 2.0, BSD)
- Consult legal counsel before marketplace submission

#### **Risk 2: Data Privacy Violations**
**Impact**: GDPR/CCPA fines for improper data handling
**Mitigation**:
- Local-first architecture (no cloud by default)
- Zero data retention policy for cloud features
- Clear privacy policy and data handling docs
- Optional telemetry with explicit opt-in

---

## 📞 Support & Community

### Support Channels

#### **Free Tier**
- GitHub Issues (public bug reports)
- Community Discord (peer support)
- Documentation site (self-service)

#### **Pro Tier ($299/year)**
- Email support (48-hour response SLA)
- Priority Discord channel
- Monthly office hours (live Q&A)

#### **Team Tier ($999/year)**
- Email support (24-hour response SLA)
- Dedicated Slack/Discord channel
- Quarterly strategy calls
- Early access to new features

#### **Enterprise Tier (Custom)**
- 24/7 on-call support
- Dedicated account manager
- Custom integration assistance
- On-site training (optional)

### Community Building

#### **Discord Server**
- #general: Casual chat
- #support: Help requests
- #feedback: Feature requests
- #showcase: Share wizard results
- #dev: Extension development
- #wizards: Discuss individual wizards

#### **Monthly Events**
- Office hours (1st Tuesday)
- Wizard deep dive (3rd Thursday)
- Community showcase (last Friday)

#### **User Conference (Year 2)**
- "EmpathyConf" - Annual user conference
- Talks on AI, empathy, developer productivity
- Workshops on custom wizard development
- Networking with Coach power users

---

## 🎓 Success Stories (Hypothetical)

### Story 1: Preventing a Security Breach

**Company**: FinTech startup (50 developers)
**Scenario**: SecurityWizard flagged SQL injection vulnerability in payment API
**Impact**: Prevented potential $500K+ breach and regulatory fines
**Testimonial**:
> "Coach's SecurityWizard caught a critical SQL injection bug before it hit production. The Level 4 prediction warned us this endpoint would become a high-value target as our user base grew. Worth every penny of the $999/year." - CTO, FinTech Startup

### Story 2: 10x Faster Onboarding

**Company**: SaaS company (200 developers)
**Scenario**: OnboardingWizard created personalized learning paths for new hires
**Impact**: Reduced onboarding time from 6 weeks to 1 week
**Testimonial**:
> "Our new developers are productive in days, not months. The OnboardingWizard maps out exactly what they need to learn based on our codebase. Our engineering manager is a hero now." - VP Engineering, SaaS Company

### Story 3: Database Migration Without Downtime

**Company**: E-commerce platform (100M+ users)
**Scenario**: DatabaseWizard + DevOpsWizard collaborated on zero-downtime migration
**Impact**: Migrated 500GB database with <1ms latency increase
**Testimonial**:
> "The multi-wizard collaboration pattern for 'database_migration' was a game-changer. Coach coordinated the DatabaseWizard's schema changes with DevOpsWizard's rollout plan. Flawless execution." - Staff Engineer, E-commerce

---

## 🎯 Next Steps

### Immediate Actions (This Week)

1. **Review and approve this plan** with stakeholders
2. **Set up project repositories**:
   - `/empathy-framework/examples/coach/lsp/` (Language Server)
   - `/empathy-framework/examples/coach/vscode-extension/` (VS Code)
   - `/empathy-framework/examples/coach/jetbrains-plugin/` (JetBrains)
3. **Recruit alpha testers** (target: 50 developers)
4. **Create project roadmap** in GitHub Projects
5. **Kick off Phase 1: Week 1-2** (LSP Foundation)

### Decision Points

**Before proceeding, confirm**:
- ✅ Budget allocated for 6-month development
- ✅ Team assigned (2 backend devs, 1 frontend dev, 1 designer)
- ✅ Pricing strategy approved ($299/year base price)
- ✅ Marketplace accounts created (VS Code, JetBrains)
- ✅ Legal review of data privacy approach

---

## 📊 Appendix: Competitive Analysis

### GitHub Copilot
**Strengths**: Deep GitHub integration, huge user base, general-purpose code completion
**Weaknesses**: No Level 4 predictions, no specialized wizards, no empathy framework
**Differentiation**: Coach focuses on anticipatory insights (30-90 days ahead), specialized expertise per domain

### Cursor
**Strengths**: Fast AI-powered editing, good UX, growing community
**Weaknesses**: VS Code fork (maintenance burden), no JetBrains support, generic AI
**Differentiation**: Coach works in native IDEs, 16 specialized wizards vs. one model

### Tabnine
**Strengths**: Privacy-focused (local models), multi-IDE support
**Weaknesses**: Limited to code completion, no workflow orchestration
**Differentiation**: Coach provides holistic workflow support (debugging, security, docs, etc.)

### Codeium
**Strengths**: Free for individuals, fast autocomplete
**Weaknesses**: Limited depth, no anticipatory predictions
**Differentiation**: Coach's Level 4 Anticipatory Empathy predicts issues months in advance

**Coach's Unique Value Proposition**: **Only AI assistant with Level 4 Anticipatory Empathy, 16 specialized wizards, and multi-wizard orchestration for complex workflows.**

---

## 📝 Conclusion

This plan outlines a **6-month roadmap** to integrate Coach's 16 specialized wizards into VS Code and JetBrains IDEs, leveraging a shared Language Server Protocol backend for efficiency.

**Key Milestones**:
- **Month 2**: VS Code extension MVP (alpha)
- **Month 4**: JetBrains plugin + feature parity (beta)
- **Month 5**: Marketplace launch (both platforms)
- **Month 6**: Advanced features + cloud integration

**Success Criteria**:
- 10K downloads in first 3 months
- 2K monthly active users by month 6
- 4.5+ star rating on both marketplaces
- $10K MRR by month 6

**Competitive Moat**: Level 4 Anticipatory Empathy (only IDE assistant that predicts issues 30-90 days before they occur)

**Next Step**: Approve plan and kick off Phase 1 (LSP Foundation).

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Author**: Claude (Coach AI)
**License**: Apache 2.0
