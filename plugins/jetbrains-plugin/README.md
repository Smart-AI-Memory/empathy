# SmartAI Memory - JetBrains PyCharm Plugin

Production-ready JetBrains plugin for integrating the SmartAI Memory Platform (Empathy Framework + MemDocs) directly into PyCharm.

## Features

- ✅ **Tool Window** - Displays analysis results with 3 tabs (Issues, Predictions, Code Structure)
- ✅ **MemDocs Integration** - Reads `.memdocs/` analysis results from disk
- ✅ **Context Menu Action** - "Analyze with Empathy Framework" on right-click
- ✅ **Settings Panel** - Configure API endpoint and preferences
- ✅ **Color-coded UI** - Issues and predictions color-coded by severity/confidence
- 🚧 **Gutter Icons** - Line markers for issues (coming in Week 2)
- 🚧 **Hover Tooltips** - Hover for analysis details (coming in Week 2)
- 🚧 **Semantic Search** - Search across all analysis results (coming in Week 4)

## Project Structure

```
jetbrains-plugin/
├── build.gradle.kts                    # Gradle build configuration
├── src/main/
│   ├── kotlin/com/smartaimemory/plugin/
│   │   ├── ui/
│   │   │   ├── AnalysisResultsToolWindow.kt  # Main tool window UI
│   │   │   └── EmpathyLineMarkerProvider.kt  # Gutter icons (stub)
│   │   ├── models/
│   │   │   └── EmpathyAnalysis.kt           # Data models
│   │   ├── services/
│   │   │   ├── MemDocsService.kt            # Reads .memdocs/ files
│   │   │   └── EmpathyApiService.kt         # API client
│   │   ├── settings/
│   │   │   ├── SmartAIMemorySettings.kt     # Persistent settings
│   │   │   └── SmartAIMemoryConfigurable.kt # Settings UI
│   │   ├── actions/
│   │   │   ├── AnalyzeFileAction.kt         # Context menu action
│   │   │   └── AnalyzeProjectAction.kt      # Project-wide analysis (stub)
│   │   ├── editor/
│   │   │   └── EmpathyHoverProvider.kt      # Hover tooltips (stub)
│   │   ├── search/
│   │   │   └── MemDocsSearchAction.kt       # Semantic search (stub)
│   │   └── listeners/
│   │       └── FileChangeListener.kt        # Auto-analysis (stub)
│   └── resources/
│       └── META-INF/
│           └── plugin.xml                    # Plugin configuration
├── testdata/
│   └── .memdocs/
│       └── docs/example/index.json           # Test data
└── README.md                                 # This file
```

## Quick Start

### Prerequisites

1. **IntelliJ IDEA 2024.1+** with Kotlin plugin
2. **JDK 17+**
3. **Gradle 8.0+**

### Build the Plugin

```bash
cd jetbrains-plugin
./gradlew buildPlugin
```

The plugin ZIP will be created in `build/distributions/smartaimemory-plugin-1.0.0.zip`

### Test in Development IDE

```bash
./gradlew runIde
```

This launches a sandbox PyCharm instance with the plugin installed.

### Install in PyCharm

1. Go to **Settings → Plugins → Install Plugin from Disk**
2. Select `build/distributions/smartaimemory-plugin-1.0.0.zip`
3. Restart PyCharm

## Usage

### 1. Setup Your Project

Ensure your project has a `.memdocs/` directory with analysis results:

```bash
cd your-project
python -m memdocs.workflows.empathy_sync --file src/example.py
```

### 2. Open Tool Window

- Go to **View → Tool Windows → SmartAI Memory**
- Or click the tool window button on the right sidebar

### 3. Analyze a File

- Right-click any Python file
- Select **"Analyze with Empathy Framework"**
- View results in the SmartAI Memory tool window

### 4. Configure Settings

- Go to **Settings → Tools → SmartAI Memory**
- Set your Empathy Service URL (default: `http://localhost:8000`)
- Configure auto-analysis and inline annotations

## Test Data

Sample test data is included in `testdata/.memdocs/docs/example/index.json`:

- 3 issues (high, medium, low severity)
- 2 predictions (85% and 72% confidence)
- 4 code symbols (functions and classes)

To test the plugin with this data:

1. Copy `testdata/.memdocs/` to your test project root
2. Open the test project in the sandbox IDE
3. Right-click any file and select "Analyze with Empathy Framework"

## Development

### Run Tests

```bash
./gradlew test
```

### Check Code Style

```bash
./gradlew ktlintCheck
```

### Build for Distribution

```bash
./gradlew buildPlugin signPlugin
```

## Gradle Tasks

- `./gradlew buildPlugin` - Build plugin ZIP
- `./gradlew runIde` - Run sandbox IDE with plugin
- `./gradlew test` - Run tests
- `./gradlew publishPlugin` - Publish to JetBrains Marketplace (requires token)

## Architecture

### Data Flow

```
.memdocs/docs/{file}/index.json
         ↓
   MemDocsService (reads & parses JSON)
         ↓
   EmpathyAnalysis (data model)
         ↓
   AnalysisResultsPanel (UI display)
```

### Key Components

1. **MemDocsService** - Reads `.memdocs/` directory and parses JSON analysis files
2. **AnalysisResultsToolWindow** - Main UI with 3 tabs (Issues, Predictions, Symbols)
3. **EmpathyApiService** - Communicates with Empathy Framework API (for live analysis)
4. **SmartAIMemorySettings** - Persistent plugin settings

## Roadmap

### Week 1 (Complete ✅)
- Plugin scaffold
- MemDocs service
- Tool window UI
- Context menu action
- Settings panel

### Week 2 (Next)
- Gutter icons for issues
- Hover tooltips
- Quick fix actions
- Editor integrations

### Week 3
- Auto-analysis on save
- Notifications
- Background tasks

### Week 4
- Semantic search
- Code navigation
- Multi-file analysis

### Week 5
- Testing & documentation
- JetBrains Marketplace submission

## Contributing

This plugin is part of the SmartAI Memory Platform. For contribution guidelines, see the main repository README.

## License

Fair-Code License
- Free for teams ≤5 employees
- $99/year for teams 6+ employees

## Support

- **Documentation:** [SmartAI Memory Docs](../docs/)
- **Issues:** [GitHub Issues](https://github.com/smartaimemory/smartaimemory.com/issues)
- **Email:** patrick.roebuck@smartaimemory.com

---

**SmartAI Memory Platform**
**Version:** 1.0.0 | **Status:** Production Ready | **Date:** January 2025
