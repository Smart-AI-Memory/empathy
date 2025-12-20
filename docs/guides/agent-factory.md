# Agent Factory

The Universal Agent Factory allows you to create AI agents and workflows using your preferred framework while retaining Empathy's core features: cost optimization, pattern learning, and memory.

## Supported Frameworks

| Framework | Best For | Install Command |
|-----------|----------|-----------------|
| **Native** | Simple agents, cost optimization | Included |
| **LangChain** | Chains, tools, RAG | `pip install langchain langchain-anthropic` |
| **LangGraph** | Stateful workflows, multi-step | `pip install langgraph` |
| **AutoGen** | Multi-agent conversations | `pip install pyautogen` |
| **Haystack** | Document QA, RAG pipelines | `pip install haystack-ai` |

## Quick Start

```python
from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

# Create factory with your preferred framework
factory = AgentFactory(framework=Framework.LANGGRAPH)

# Create agents
researcher = factory.create_agent(
    name="researcher",
    role="researcher",
    model_tier="capable"  # Uses Sonnet
)

writer = factory.create_agent(
    name="writer",
    role="writer",
    model_tier="premium"  # Uses Opus
)

# Create workflow
pipeline = factory.create_workflow(
    name="research_pipeline",
    agents=[researcher, writer],
    mode="sequential"
)

# Run
result = await pipeline.run("Research AI trends in 2025")
print(result["output"])
```

## Framework Selection

### CLI

```bash
# List installed frameworks
empathy frameworks

# Show all frameworks (including uninstalled)
empathy frameworks --all

# Get recommendation for a use case
empathy frameworks --recommend rag
empathy frameworks --recommend multi_agent
```

### Programmatic

```python
from empathy_llm_toolkit.agent_factory import AgentFactory

# Auto-select based on use case
factory = AgentFactory(use_case="rag")  # Will use Haystack if installed

# Or specify explicitly
factory = AgentFactory(framework="langgraph")
```

## Creating Agents

### Basic Agent

```python
agent = factory.create_agent(
    name="helper",
    role="researcher",
    model_tier="capable"
)

result = await agent.invoke("What is quantum computing?")
print(result["output"])
```

### Agent with Tools

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

search_tool = factory.create_tool(
    name="search",
    description="Search the web",
    func=search_web
)

agent = factory.create_agent(
    name="researcher",
    role="researcher",
    tools=[search_tool],
    capabilities=[AgentCapability.TOOL_USE]
)
```

### Model Tiers

| Tier | Model (Anthropic) | Cost | Best For |
|------|-------------------|------|----------|
| `cheap` | Haiku | $0.25/M | Summarization, classification |
| `capable` | Sonnet | $3/M | Code generation, analysis |
| `premium` | Opus | $15/M | Architecture, synthesis |

```python
# Cost-optimized agent
summarizer = factory.create_agent(
    name="summarizer",
    role="summarizer",
    model_tier="cheap"  # Uses Haiku - 60x cheaper
)

# High-quality agent
architect = factory.create_agent(
    name="architect",
    role="architect",
    model_tier="premium"  # Uses Opus
)
```

## Creating Workflows

### Sequential Pipeline

```python
workflow = factory.create_workflow(
    name="review_pipeline",
    agents=[analyzer, reviewer, editor],
    mode="sequential"
)

result = await workflow.run("Review this code...")
```

### Parallel Execution

```python
workflow = factory.create_workflow(
    name="parallel_analysis",
    agents=[security_agent, quality_agent, perf_agent],
    mode="parallel"
)
```

### Convenience Methods

```python
# Pre-built research pipeline
pipeline = factory.create_research_pipeline(
    topic="AI in healthcare",
    include_reviewer=True
)

# Pre-built code review pipeline
review = factory.create_code_review_pipeline()
```

## Agent Roles

Built-in roles with optimized prompts:

```python
from empathy_llm_toolkit.agent_factory import AgentRole

# Standard roles
AgentRole.RESEARCHER    # Gathers information
AgentRole.WRITER        # Produces content
AgentRole.REVIEWER      # Reviews/critiques
AgentRole.EDITOR        # Refines content
AgentRole.DEBUGGER      # Finds bugs
AgentRole.SECURITY      # Security analysis
AgentRole.COORDINATOR   # Orchestrates agents

# RAG roles
AgentRole.RETRIEVER     # Document retrieval
AgentRole.SUMMARIZER    # Summarization
AgentRole.ANSWERER      # Question answering
```

## Framework-Specific Features

### LangChain

```python
factory = AgentFactory(framework=Framework.LANGCHAIN)

# Full LangChain tool support
from langchain_core.tools import StructuredTool

lc_tool = StructuredTool.from_function(my_func)
agent = factory.create_agent(
    name="agent",
    tools=[lc_tool]
)
```

### LangGraph

```python
factory = AgentFactory(framework=Framework.LANGGRAPH)

# Stateful workflows with cycles
workflow = factory.create_workflow(
    name="iterative",
    agents=[planner, executor, reviewer],
    mode="graph",
    max_iterations=5
)
```

### AutoGen

```python
factory = AgentFactory(framework=Framework.AUTOGEN)

# Multi-agent conversation
workflow = factory.create_workflow(
    name="team_chat",
    agents=[coder, reviewer, tester],
    mode="conversation"
)
```

### Haystack

```python
factory = AgentFactory(framework=Framework.HAYSTACK)

# RAG pipeline
retriever = factory.create_agent(
    name="retriever",
    role=AgentRole.RETRIEVER,
    capabilities=[AgentCapability.RETRIEVAL]
)
```

## Empathy Integration

### Cost Tracking

```python
agent = factory.create_agent(
    name="agent",
    track_costs=True  # Default
)

# Costs are tracked in .empathy/costs.json
# View with: empathy costs
```

### Pattern Learning

```python
agent = factory.create_agent(
    name="debugger",
    use_patterns=True  # Load learned patterns
)

# Patterns from patterns/debugging.json are available
```

### Empathy Levels

```python
agent = factory.create_agent(
    name="advisor",
    empathy_level=4  # Anticipatory (predicts problems)
)
```

## Example: Code Review Pipeline

```python
from empathy_llm_toolkit.agent_factory import AgentFactory, AgentRole

factory = AgentFactory(framework="langgraph")

# Create specialized agents
security = factory.create_agent(
    name="security",
    role=AgentRole.SECURITY,
    model_tier="capable",
    system_prompt="Analyze code for security vulnerabilities."
)

quality = factory.create_agent(
    name="quality",
    role=AgentRole.REVIEWER,
    model_tier="capable",
    system_prompt="Review code quality and suggest improvements."
)

coordinator = factory.create_agent(
    name="coordinator",
    role=AgentRole.COORDINATOR,
    model_tier="premium",
    system_prompt="Synthesize reviews into actionable feedback."
)

# Create workflow
pipeline = factory.create_workflow(
    name="code_review",
    agents=[security, quality, coordinator],
    mode="sequential"
)

# Run review
code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE name='{username}'"
    ...
"""

result = await pipeline.run(f"Review this code:\n{code}")
print(result["output"])
```

## CLI Reference

```bash
# List frameworks
empathy frameworks
empathy frameworks --all
empathy frameworks --json

# Get recommendation
empathy frameworks --recommend general
empathy frameworks --recommend rag
empathy frameworks --recommend multi_agent
empathy frameworks --recommend code_analysis
```

## Next Steps

- [CLI Cheatsheet](../CLI_CHEATSHEET.md) - Quick reference
- [Cost Tracking](../guides/cost-optimization.md) - Monitor savings
- [Pattern Learning](../guides/pattern-learning.md) - Automatic improvements
