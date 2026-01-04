"""Example: Using Empathy Framework with Different LLMs

This shows how to use the EmpathyLLM wrapper with multiple providers
without needing to create custom wizards.

The framework automatically handles:
- Multi-LLM support (Claude, GPT-4, Gemini, local models)
- Empathy level progression (1-5)
- Conversation state and patterns
- Anticipatory predictions
"""

import asyncio
import os

from empathy_llm_toolkit.core import EmpathyLLM


async def example_claude_usage():
    """Example: Using Claude with Empathy Framework"""
    print("=" * 60)
    print("EXAMPLE 1: Claude (Anthropic) - Level 4 Anticipatory")
    print("=" * 60)

    # Initialize with Claude
    llm = EmpathyLLM(
        provider="anthropic",
        target_level=4,  # Level 4 Anticipatory
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        use_prompt_caching=True,  # Claude-specific feature
        use_thinking=True,  # Claude-specific feature
    )

    # Simple interaction - automatically uses appropriate empathy level
    response = await llm.interact(
        user_id="developer_123",
        user_input="I'm building a Python web API with Flask. What should I consider?",
        context={"project_type": "web_api", "language": "python"},
    )

    print(f"\nLevel Used: {response['level_used']} - {response['level_description']}")
    print(f"Response: {response['content'][:200]}...")
    print(f"\nMetadata: {response['metadata']}")

    # As you continue interacting, the framework learns and progresses to higher levels
    response2 = await llm.interact(
        user_id="developer_123",
        user_input="Now I need to add authentication",
        context={"previous_topic": "flask_api"},
    )

    print("\n--- Second Interaction ---")
    print(f"Level Used: {response2['level_used']}")
    print(f"Proactive: {response2['proactive']}")
    print(f"Response: {response2['content'][:200]}...")


async def example_openai_usage():
    """Example: Using OpenAI GPT-4 with Empathy Framework"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: OpenAI GPT-4 - Level 3 Proactive")
    print("=" * 60)

    llm = EmpathyLLM(
        provider="openai",
        target_level=3,  # Level 3 Proactive
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4-turbo-preview",
    )

    response = await llm.interact(
        user_id="data_scientist_456",
        user_input="Help me analyze this dataset for anomalies",
        context={"dataset_size": "10000 rows", "domain": "finance"},
    )

    print(f"\nLevel Used: {response['level_used']} - {response['level_description']}")
    print(f"Response: {response['content'][:200]}...")


async def example_local_model_usage():
    """Example: Using local Ollama model with Empathy Framework"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Local Model (Ollama) - Level 2 Guided")
    print("=" * 60)

    llm = EmpathyLLM(
        provider="local",
        target_level=2,  # Level 2 Guided
        model="llama2",
        endpoint="http://localhost:11434",  # Ollama default
    )

    response = await llm.interact(
        user_id="privacy_user_789",
        user_input="I need help with my code but want to keep it private",
        context={"privacy_required": True},
    )

    print(f"\nLevel Used: {response['level_used']} - {response['level_description']}")
    print(f"Response: {response['content'][:200]}...")
    print("\nNote: Running locally - zero cost, complete privacy")


async def example_switching_providers():
    """Example: Switching between providers dynamically"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Dynamic Provider Switching")
    print("=" * 60)

    # Use Claude for complex reasoning
    claude_llm = EmpathyLLM(
        provider="anthropic",
        target_level=4,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # Use GPT-4 for fast responses
    _openai_llm = EmpathyLLM(provider="openai", target_level=3, api_key=os.getenv("OPENAI_API_KEY"))

    # Use local model for sensitive data
    _local_llm = EmpathyLLM(provider="local", target_level=2, model="llama2")

    print("\nProviders initialized:")
    print("  ✓ Claude - for complex Level 4 anticipatory tasks")
    print("  ✓ GPT-4 - for fast Level 3 proactive responses")
    print("  ✓ Local - for privacy-sensitive Level 2 guided help")

    # Route to appropriate provider based on task
    task = "Predict potential security vulnerabilities in my codebase"
    print(f"\nTask: {task}")
    print("→ Routing to Claude (best for anticipatory predictions)")

    response = await claude_llm.interact(
        user_id="security_team",
        user_input=task,
        context={"codebase_size": "large", "security_critical": True},
    )

    print(f"Level Used: {response['level_used']}")
    print(f"Proactive: {response['proactive']}")


async def example_pro_tier_features():
    """Example: Pro Tier features with Claude"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Pro Tier Features (Powered by Claude)")
    print("=" * 60)

    llm = EmpathyLLM(
        provider="anthropic",
        target_level=4,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        use_prompt_caching=True,  # 90% cost reduction
        use_thinking=True,  # Show reasoning process
        model="claude-3-5-sonnet-20241022",
    )

    # Large codebase analysis (200K context)
    codebase_files = [
        {"path": "app.py", "content": "# Main application\n..."},
        {"path": "models.py", "content": "# Database models\n..."},
        {"path": "views.py", "content": "# API views\n..."},
        # ... hundreds more files fit in 200K context
    ]

    print("\nAnalyzing entire codebase (200K token context)...")
    print(f"Files: {len(codebase_files)}")

    response = await llm.interact(
        user_id="enterprise_dev",
        user_input="Analyze my entire codebase for security issues and predict future problems",
        context={"codebase_files": codebase_files},
    )

    print(f"\nLevel Used: {response['level_used']} - {response['level_description']}")
    print("Features Used:")
    print("  • Extended context: 200K tokens (whole repo)")
    print("  • Prompt caching: 90% cost savings on repeated scans")
    print(f"  • Thinking mode: {response['metadata'].get('thinking', 'N/A')[:100]}...")
    print("  • Trajectory analysis: Predicts issues before they happen")


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  Empathy Framework - Multi-LLM Usage Examples           ║")
    print("╚" + "=" * 58 + "╝")

    # Note: These examples require API keys to actually run
    # Uncomment the ones you want to try:

    # await example_claude_usage()
    # await example_openai_usage()
    # await example_local_model_usage()
    # await example_switching_providers()
    # await example_pro_tier_features()

    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    print(
        """
To run these examples:

1. Install the framework:
   pip install empathy-framework

2. Set API keys (as needed):
   export ANTHROPIC_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"

3. For local models (optional):
   # Install Ollama: https://ollama.ai
   ollama run llama2

4. Uncomment examples in main() and run:
   python examples/multi_llm_usage.py

PRICING (Pro Tier):
- $99/year includes $300/year Claude API credits
- Claude recommended for Level 4 Anticipatory features
- Free tier: Bring your own API key for any provider
    """,
    )


if __name__ == "__main__":
    asyncio.run(main())
