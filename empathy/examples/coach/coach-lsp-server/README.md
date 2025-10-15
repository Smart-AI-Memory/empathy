# Coach LSP Server

Language Server Protocol implementation for Coach AI code analysis.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python server.py
```

The server communicates via stdio using the LSP protocol.

## Custom Commands

- `coach/runWizard` - Run a single wizard analysis
- `coach/multiWizardReview` - Run multi-wizard collaboration
- `coach/predict` - Generate Level 4 predictions
- `coach/healthCheck` - Check server health

## Configuration

The server can be configured via IDE settings:
- `coach.pythonPath` - Path to Python interpreter
- `coach.serverScriptPath` - Path to this server.py file

## Development

This is a basic implementation with mock analysis. In production, this would:
- Integrate with actual LLM services (OpenAI, Anthropic, etc.)
- Use LangChain for wizard orchestration
- Implement sophisticated code analysis
- Cache results in Redis/database
- Support distributed processing
