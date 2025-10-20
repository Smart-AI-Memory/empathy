#!/bin/bash
# Empathy Framework - One-Command Installation
# Usage: curl -sSL https://raw.githubusercontent.com/Deep-Study-AI/Empathy-framework/main/install.sh | bash

set -e

echo "🚀 Installing Empathy Framework..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Found Python $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip."
    exit 1
fi
echo "✓ Found pip3"

# Install the package
echo ""
echo "📦 Installing empathy-framework..."
pip3 install empathy-framework --quiet --upgrade

# Install CLI tool
echo "🔧 Setting up CLI tools..."

# Determine install location
if [ -w "/usr/local/bin" ]; then
    BIN_DIR="/usr/local/bin"
elif [ -w "$HOME/.local/bin" ]; then
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
else
    BIN_DIR="$HOME/bin"
    mkdir -p "$BIN_DIR"
fi

# Download empathy-scan script
SCRIPT_URL="https://raw.githubusercontent.com/Deep-Study-AI/Empathy-framework/main/bin/empathy-scan"
if command -v curl &> /dev/null; then
    curl -sSL "$SCRIPT_URL" -o "$BIN_DIR/empathy-scan"
elif command -v wget &> /dev/null; then
    wget -q "$SCRIPT_URL" -O "$BIN_DIR/empathy-scan"
else
    echo "⚠️  Could not download empathy-scan (no curl/wget found)"
    echo "   You can manually copy bin/empathy-scan to your PATH"
fi

chmod +x "$BIN_DIR/empathy-scan" 2>/dev/null || true

# Check if BIN_DIR is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  $BIN_DIR is not in your PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$PATH:$BIN_DIR\""
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📚 Quick Start:"
echo "   empathy-scan security app.py       # Scan a file"
echo "   empathy-scan performance ./src     # Scan a directory"
echo "   empathy-scan all ./project         # All checks"
echo ""
echo "📖 Documentation: https://github.com/Deep-Study-AI/Empathy-framework"
echo ""
