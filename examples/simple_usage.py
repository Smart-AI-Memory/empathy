"""
Simple Example: Using Empathy Framework without Writing Wizards

This is the easiest way to use the Empathy Framework.
No need to create custom wizards - just interact with the LLM
and the framework automatically handles empathy levels.
"""

import asyncio
import os
from empathy_llm_toolkit.core import EmpathyLLM


async def simple_example():
    """
    Dead simple usage - just talk to it!

    The framework automatically:
    - Starts at Level 1 (reactive)
    - Progresses to higher levels as you interact
    - Detects patterns and becomes proactive
    - Predicts future needs (Level 4)
    """

    # Create an instance (uses Claude by default)
    llm = EmpathyLLM(
        provider="anthropic",  # or "openai", "local"
        target_level=4,        # How smart you want it to be
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Just interact - it handles the rest!
    response = await llm.interact(
        user_id="me",
        user_input="Help me build a web API"
    )

    print(f"Assistant: {response['content']}")
    print(f"\nUsed Level {response['level_used']}: {response['level_description']}")

    # Continue the conversation - it remembers context
    response2 = await llm.interact(
        user_id="me",
        user_input="What about authentication?"
    )

    print(f"\nAssistant: {response2['content']}")

    # Get statistics about the collaboration
    stats = llm.get_statistics("me")
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    # Set your API key first:
    # export ANTHROPIC_API_KEY="your-key-here"

    asyncio.run(simple_example())
