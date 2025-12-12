#!/bin/bash
#
# Empathy Memory Panel - Build Script
#
# Usage:
#   ./build.sh              # Full build
#   ./build.sh clean        # Clean build artifacts
#   ./build.sh install      # Install in VS Code
#   ./build.sh dev          # Development mode
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Install from https://nodejs.org/"
        exit 1
    fi
    print_success "Node.js $(node --version)"

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm not found"
        exit 1
    fi
    print_success "npm $(npm --version)"

    # Check VS Code
    if ! command -v code &> /dev/null; then
        print_info "VS Code CLI not found (optional)"
    else
        print_success "VS Code CLI available"
    fi

    # Check Python (for backend)
    if ! command -v python3 &> /dev/null; then
        print_info "Python 3 not found (needed for backend)"
    else
        print_success "Python $(python3 --version)"
    fi

    echo ""
}

# Clean build artifacts
clean() {
    print_header "Cleaning Build Artifacts"

    if [ -d "out" ]; then
        rm -rf out
        print_success "Removed out/"
    fi

    if [ -d "node_modules" ]; then
        rm -rf node_modules
        print_success "Removed node_modules/"
    fi

    if [ -f "*.vsix" ]; then
        rm -f *.vsix
        print_success "Removed *.vsix"
    fi

    if [ -f "package-lock.json" ]; then
        rm -f package-lock.json
        print_success "Removed package-lock.json"
    fi

    echo ""
}

# Install dependencies
install_deps() {
    print_header "Installing Dependencies"

    npm install
    print_success "Dependencies installed"

    echo ""
}

# Compile TypeScript
compile() {
    print_header "Compiling TypeScript"

    npm run compile
    print_success "TypeScript compiled"

    echo ""
}

# Run linter
lint() {
    print_header "Running Linter"

    npm run lint
    print_success "Linting passed"

    echo ""
}

# Package extension
package() {
    print_header "Packaging Extension"

    # Check if vsce is available
    if ! command -v vsce &> /dev/null; then
        print_info "Installing vsce (VS Code Extension Manager)"
        npm install -g @vscode/vsce
    fi

    vsce package
    print_success "Extension packaged"

    # Find the .vsix file
    VSIX_FILE=$(ls -t *.vsix 2>/dev/null | head -1)
    if [ -n "$VSIX_FILE" ]; then
        print_success "Created: $VSIX_FILE"
    fi

    echo ""
}

# Install in VS Code
install_vscode() {
    print_header "Installing in VS Code"

    # Find the .vsix file
    VSIX_FILE=$(ls -t *.vsix 2>/dev/null | head -1)

    if [ -z "$VSIX_FILE" ]; then
        print_error "No .vsix file found. Run './build.sh' first."
        exit 1
    fi

    if ! command -v code &> /dev/null; then
        print_error "VS Code CLI not found. Install from https://code.visualstudio.com/"
        print_info "Or install manually: Extensions > ... > Install from VSIX"
        exit 1
    fi

    code --install-extension "$VSIX_FILE"
    print_success "Extension installed in VS Code"
    print_info "Reload VS Code to activate"

    echo ""
}

# Full build
build() {
    print_header "Building Empathy Memory Panel Extension"
    echo ""

    check_prerequisites
    install_deps
    compile
    lint
    package

    print_success "Build complete!"
    echo ""

    # Show next steps
    print_header "Next Steps"
    echo "1. Install extension:"
    echo "   ./build.sh install"
    echo ""
    echo "2. Or manually:"
    echo "   code --install-extension $(ls -t *.vsix | head -1)"
    echo ""
    echo "3. Start backend API:"
    echo "   python api_server_example.py"
    echo ""
    echo "4. Open VS Code and find 'Empathy Memory' in Activity Bar"
    echo ""
}

# Development mode
dev() {
    print_header "Development Mode"

    print_info "Starting TypeScript watch mode..."
    print_info "Press F5 in VS Code to launch Extension Development Host"
    print_info "Press Ctrl+C to stop"
    echo ""

    npm run watch
}

# Main script
case "${1:-build}" in
    clean)
        clean
        ;;
    deps)
        check_prerequisites
        install_deps
        ;;
    compile)
        compile
        ;;
    lint)
        lint
        ;;
    package)
        compile
        package
        ;;
    install)
        install_vscode
        ;;
    dev)
        check_prerequisites
        install_deps
        dev
        ;;
    build)
        build
        ;;
    *)
        echo "Usage: $0 {build|clean|deps|compile|lint|package|install|dev}"
        echo ""
        echo "Commands:"
        echo "  build      Full build (default)"
        echo "  clean      Remove build artifacts"
        echo "  deps       Install dependencies"
        echo "  compile    Compile TypeScript"
        echo "  lint       Run linter"
        echo "  package    Create .vsix package"
        echo "  install    Install in VS Code"
        echo "  dev        Development watch mode"
        exit 1
        ;;
esac
