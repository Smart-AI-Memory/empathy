# Developer Guide: User Experience Enhancements

This document outlines the technical implementation plan for the proposed user experience enhancements to the Empathy Framework.

## 1. Command-Line Interface (CLI) Enhancements

**Objective:** Make the CLI more intuitive, discoverable, and user-friendly for new and existing users.

### 1.1. Create an Interactive `init` Command

**Goal:** Simplify the initial configuration process for new users.

**File to Modify:** `src/empathy_os/cli.py` (or `src/empathy_os/cli_unified.py` if that is the primary entry point).

**Implementation Steps:**

1. **Add a new command:** Define a new Typer command `init`.

    ```python
    @app.command()
    def init(
        ctx: typer.Context,
        force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing empathy.config.yml if it exists."),
    ):
        """
        Interactively create a new empathy.config.yml file.
        """
        # ... implementation ...
    ```

2. **Check for Existing Config:** Before proceeding, check if `empathy.config.yml` already exists. If it does and `--force` is not used, print a warning and exit.

3. **Gather Interactive Input:** Use `typer.prompt` to ask the user for key configuration details. Provide sensible defaults.

    ```python
    import typer
    import yaml

    # ... inside the init command ...
    typer.echo("Welcome to Empathy Framework! Let's set up your configuration.")

    provider = typer.prompt(
        "Which model provider will you use primarily?",
        type=click.Choice(["anthropic", "openai", "google", "ollama"]),
        default="anthropic",
    )

    api_key = typer.prompt(f"Enter your {provider.capitalize()} API key (optional, can be set as env var)", default="", show_default=False)

    # ... add prompts for other settings like default model tiers ...

    config_data = {
        "default_provider": provider,
        "providers": {
            provider: {
                "api_key": api_key if api_key else f"env(ANTHROPIC_API_KEY)" # Example
            }
        },
        # ... other settings ...
    }
    ```

4. **Write the Config File:** Use the `yaml` library to write the collected data to `empathy.config.yml`.

    ```python
    with open("empathy.config.yml", "w") as f:
        yaml.dump(config_data, f, sort_keys=False)

    typer.secho("✅ Configuration saved to empathy.config.yml!", fg=typer.colors.GREEN)
    ```

### 1.2. Improve Command Discovery

**Goal:** Make the full capabilities of the CLI easier for users to find.

**File to Modify:** `src/empathy_os/cli.py`

**Implementation Steps:**

1. **Use Rich Help Formatter:** Typer can use `rich` to create more structured help panels.

2. **Group Commands:** Organize commands into logical groups like "Workflows", "Project Management", and "Configuration". This requires creating separate `Typer` app instances and adding them to the main app.

    ```python
    # In src/empathy_os/cli.py
    import typer
    from rich.console import RichConsole

    # Main app
    app = typer.Typer(rich_markup_mode="markdown")

    # Create sub-apps for grouping
    workflow_app = typer.Typer(name="workflow", help="Run powerful AI-driven workflows.")
    project_app = typer.Typer(name="project", help="Manage and analyze your project.")

    # Add sub-apps to the main app
    app.add_typer(workflow_app)
    app.add_typer(project_app)

    # Add commands to the sub-apps
    @workflow_app.command("run")
    def workflow_run(...):
        # ... implementation ...

    @project_app.command("index")
    def project_index(...):
        # ... implementation ...
    ```

    This will produce a help output like:

    ```
    Usage: empathy [OPTIONS] COMMAND [ARGS]...

    ╭─ Options ────────────────────────────────────────────────────────────────╮
    │ --install-completion          Install completion for the current shell.  │
    │ --show-completion             Show completion for the current shell, to │
    │                               copy it or customize the installation.     │
    │ --help                        Show this message and exit.                │
    ╰──────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────╮
    │ project                       Manage and analyze your project.           │
    │ workflow                      Run powerful AI-driven workflows.          │
    ╰──────────────────────────────────────────────────────────────────────────╯
    ```

## 2. VS Code Extension Improvements

**Objective:** Create a richer, more integrated experience within the VS Code editor.

### 2.1. WebView-based Interactive Wizards

**Goal:** Move beyond simple text output and create graphical interfaces for complex workflows.

**Files to Modify:** `vscode-extension/src/extension.ts` and new files for the WebView content.

**Implementation Steps:**

1. **Create a WebView Panel:** Use the `vscode.window.createWebviewPanel` API to create a new panel when a wizard command is triggered.

2. **Develop the UI:** Create the UI for the WebView using HTML, CSS, and JavaScript. For complex UIs, a simple framework like Preact or Svelte can be bundled. The UI should be ableto post messages back to the extension.

    *   **Example HTML (`test-gen-wizard.html`):**

        ```html
        <h1>Test Generation Wizard</h1>
        <p>Select functions and classes to generate tests for:</p>
        <div id="items"></div>
        <button id="generate-btn">Generate Tests</button>
        <script>
            const vscode = acquireVsCodeApi();
            // ... logic to render items and handle button click ...
            // On click, post a message:
            vscode.postMessage({ command: 'generate', targets: [...] });
        </script>
        ```

3. **Establish Two-Way Communication:**

    *   **Extension to WebView:** The extension sends the initial data (e.g., list of functions from the `test-gen` `analyze` stage) to the WebView using `webview.postMessage()`.
    *   **WebView to Extension:** The WebView sends user actions (e.g., button clicks) back to the extension using the `acquireVsCodeApi()` and listening for messages in `webview.onDidReceiveMessage()`.

4. **Trigger Workflow:** When the extension receives the 'generate' message from the WebView, it executes the Empathy Framework workflow with the selected targets.

### 2.2. Deeper Editor Integration with Diagnostics

**Goal:** Show feedback from analysis workflows directly in the code editor.

**File to Modify:** `vscode-extension/src/extension.ts`

**Implementation Steps:**

1. **Create a Diagnostic Collection:** On extension activation, create a diagnostic collection.

    ```typescript
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('empathy');
    ```

2. **Run Workflow and Parse Results:** After running a workflow like `code-review` or `perf-audit`, parse the structured output (e.g., JSON or XML).

3. **Create and Apply Diagnostics:** For each finding in the report, create a `vscode.Diagnostic` object and add it to the collection.

    ```typescript
    // Inside the function that handles workflow results
    const diagnostics: vscode.Diagnostic[] = [];
    const range = new vscode.Range(finding.startLine, 0, finding.endLine, 100);
    const diagnostic = new vscode.Diagnostic(
        range,
        finding.message,
        vscode.DiagnosticSeverity.Warning // or Error, Information
    );
    diagnostic.source = 'empathy-framework';
    diagnostics.push(diagnostic);

    diagnosticCollection.set(vscode.Uri.file(filePath), diagnostics);
    ```

    This will cause warning squiggles to appear under the relevant lines of code in the editor.

## 3. Onboarding and Documentation

**Objective:** Make documentation more interactive and easier to navigate.

### 3.1. "Run in Empathy" Interactive Buttons

**Goal:** Allow users to run examples directly from the documentation website.

**Files to Modify:** MkDocs configuration (`mkdocs.yml`) and potentially custom JavaScript for the docs site.

**Implementation Steps:**

1. **Define a Custom Command URI:** The button will trigger a custom VS Code URI scheme. Example: `vscode://Smart-AI-Memory.empathy-framework/runCommand?command=empathy workflow run test-gen`.

2. **Register a URI Handler in the Extension:** In `vscode-extension/src/extension.ts`, register a `UriHandler` that listens for this custom URI.

    ```typescript
    vscode.window.registerUriHandler({
        handleUri(uri: vscode.Uri) {
            if (uri.path === '/runCommand') {
                const params = new URLSearchParams(uri.query);
                const commandToRun = params.get('command');
                if (commandToRun) {
                    // Find or create a terminal and run the command
                    const terminal = vscode.window.createTerminal('Empathy Docs');
                    terminal.sendText(commandToRun);
                    terminal.show();
                }
            }
        }
    });
    ```

3. **Create the Button in Markdown:** In your `.md` files, use raw HTML to create a button that links to the custom URI.

    ```markdown
    <a href="vscode://Smart-AI-Memory.empathy-framework/runCommand?command=empathy%20workflow%20run%20test-gen" class="md-button">Run in Empathy</a>
    ```

    This provides a low-tech but effective way to make documentation interactive, assuming the user has the extension installed.

---

This guide provides a starting point for each enhancement. I am ready to begin implementing the first set of changes, starting with the CLI improvements, when you are.
