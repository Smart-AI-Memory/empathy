# Installation

## Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version recommended

## Basic Installation

```bash
pip install empathy-framework
```

This installs the core Empathy Framework with basic functionality.

## Installation Options

### With LLM Support

```bash
pip install empathy-framework[llm]
```

Includes Anthropic Claude and OpenAI SDK.

### With Healthcare Support

```bash
pip install empathy-framework[healthcare]
```

Includes FHIR client, HL7 parsing, HIPAA audit logging.

### Full Installation (Recommended)

```bash
pip install empathy-framework[full]
```

Includes everything: LLM providers, healthcare, webhooks.

## Verification

```bash
python -c "import empathy_os; print(empathy_os.__version__)"
```

Or use the CLI:

```bash
empathy-framework version
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Build your first chatbot in 5 minutes
- [Configuration](configuration.md) - Learn about configuration options
