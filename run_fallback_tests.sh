#!/bin/bash
# Helper script to run fallback tests with API key from .env file

# Load API key from .env
if [ -f .env ]; then
    export $(cat .env | grep ANTHROPIC_API_KEY | xargs)
    echo "✅ Loaded ANTHROPIC_API_KEY from .env"
else
    echo "❌ No .env file found"
    exit 1
fi

# Verify key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not found in .env"
    exit 1
fi

echo "🔑 API Key: ${ANTHROPIC_API_KEY:0:10}..."
echo ""

# Run the test
if [ "$1" == "full" ]; then
    echo "🔬 Running FULL test suite..."
    python tests/test_fallback_suite.py --full
elif [ "$1" == "example" ]; then
    echo "📚 Running examples..."
    python examples/sonnet_opus_fallback_example.py
elif [ "$1" == "analysis" ]; then
    echo "📊 Running cost analysis..."
    python -m empathy_os.telemetry.cli sonnet-opus-analysis --days "${2:-30}"
else
    echo "🚀 Running QUICK test suite..."
    python tests/test_fallback_suite.py --quick
fi
