#!/usr/bin/env python3
"""LLM Provider Call Script

Calls Empathy LLM providers (Anthropic/OpenAI) from VSCode extension.
Used by LLMChatService for Socratic refinement conversations.

Usage:
    python llm_provider_call.py '<json_args>'

Args (JSON):
    {
        "messages": [{"role": "user", "content": "..."}],
        "system_prompt": "System instructions...",
        "max_tokens": 1024,
        "temperature": 0.7
    }

Output (JSON):
    {
        "content": "LLM response text",
        "input_tokens": 123,
        "output_tokens": 456,
        "model": "claude-sonnet-4-20250514"
    }

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import os
import sys


def main():
    """Main entry point for LLM provider calls."""
    try:
        # Parse arguments from command line
        if len(sys.argv) < 2:
            print(json.dumps({"error": "No arguments provided", "fallback": True}))
            sys.exit(0)

        args = json.loads(sys.argv[1])
        messages = args.get("messages", [])
        system_prompt = args.get("system_prompt", "")
        max_tokens = args.get("max_tokens", 1024)
        temperature = args.get("temperature", 0.7)

        # Import providers
        try:
            from empathy_llm_toolkit.providers import AnthropicProvider, OpenAIProvider
        except ImportError as e:
            print(json.dumps({"error": f"Import error: {e}", "fallback": True}))
            sys.exit(0)

        # Try to get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")

        if not api_key:
            # Try to load from .env file
            env_path = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            if key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
                                api_key = value.strip('"').strip("'")
                                os.environ[key] = api_key
                                break

        if not api_key:
            print(json.dumps({"error": "No API key found", "fallback": True}))
            sys.exit(0)

        # Determine provider
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider = AnthropicProvider()
            model = "claude-sonnet-4-20250514"
        else:
            provider = OpenAIProvider()
            model = "gpt-4o-mini"

        # Build prompt
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"Human: {content}")

        prompt_parts.append("Assistant:")
        full_prompt = "\n\n".join(prompt_parts)

        # Call provider
        response = provider.generate(
            prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        result = {
            "content": response.get("content", response.get("text", str(response))),
            "input_tokens": response.get("usage", {}).get("input_tokens", 0),
            "output_tokens": response.get("usage", {}).get("output_tokens", 0),
            "model": model,
        }
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e), "fallback": True}))
        sys.exit(1)


if __name__ == "__main__":
    main()
