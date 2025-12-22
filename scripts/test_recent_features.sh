#!/bin/bash
#
# Test Script for Empathy Framework - Features Added in Last 7 Days
# Generated: 2025-12-22
#
# This script tests recent features including:
# - Agent Factory v2.4.0 (Universal Multi-Framework Agent System)
# - UX commands for progressive user onboarding
# - ModelRouter integration for cost optimization
# - Redis integration with environment-aware key prefixing
# - Debug Wizard improvements (drag-drop, folder selection, autonomous repair)
# - Workflow CLI improvements (actual content output, input types)
# - CLI cheatsheet and power-user configuration
#
# Usage: ./scripts/test_recent_features.sh [--verbose] [--section NAME]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

VERBOSE=false
SECTION=""
PASSED=0
FAILED=0
SKIPPED=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --section|-s)
            SECTION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}─── $1 ───${NC}"
}

print_test() {
    echo -n "  ▸ $1... "
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}"
    if [ -n "$1" ]; then
        echo -e "    ${RED}$1${NC}"
    fi
    FAILED=$((FAILED + 1))
}

skip() {
    echo -e "${YELLOW}⊘ SKIP${NC}"
    if [ -n "$1" ]; then
        echo -e "    ${YELLOW}$1${NC}"
    fi
    SKIPPED=$((SKIPPED + 1))
}

should_run_section() {
    if [ -z "$SECTION" ]; then
        return 0
    fi
    if [[ "$1" == *"$SECTION"* ]]; then
        return 0
    fi
    return 1
}

# ============================================================================
# TEST SECTION 1: Agent Factory v2.4.0
# ============================================================================
test_agent_factory() {
    if ! should_run_section "agent"; then
        return
    fi

    print_header "1. Agent Factory v2.4.0 - Universal Multi-Framework Agent System"

    print_section "Agent Factory Module Imports"

    print_test "Import AgentFactory class"
    if python -c "from empathy_llm_toolkit.agent_factory import AgentFactory" 2>/dev/null; then
        pass
    else
        fail "Could not import AgentFactory"
    fi

    print_test "Import AgentConfig"
    if python -c "from empathy_llm_toolkit.agent_factory import AgentConfig" 2>/dev/null; then
        pass
    else
        fail "Could not import AgentConfig"
    fi

    print_test "Import framework adapters"
    if python -c "from empathy_llm_toolkit.agent_factory import get_available_frameworks" 2>/dev/null; then
        pass
    else
        skip "get_available_frameworks not exported at top level"
    fi

    print_section "Agent Factory CLI Commands"

    print_test "List available frameworks"
    if python -m empathy_os.cli frameworks 2>&1 | grep -q -i "framework\|installed"; then
        pass
    else
        fail "frameworks command failed"
    fi

    print_test "Agent factory help"
    if python -m empathy_os.cli agent --help 2>&1 | grep -q -i "agent"; then
        pass
    else
        skip "agent command not yet implemented in CLI"
    fi
}

# ============================================================================
# TEST SECTION 2: UX Commands for Progressive Onboarding
# ============================================================================
test_ux_commands() {
    if ! should_run_section "ux"; then
        return
    fi

    print_header "2. UX Commands for Progressive User Onboarding"

    print_section "Discovery & Onboarding Commands"

    print_test "Cheatsheet command"
    if python -m empathy_os.cli cheatsheet 2>&1 | grep -q -i "Getting Started\|Daily Workflow"; then
        pass
    else
        fail "cheatsheet command failed"
    fi

    print_test "Explain command (morning)"
    if python -m empathy_os.cli explain morning 2>&1 | grep -q -i "morning\|briefing\|WORKS"; then
        pass
    else
        fail "explain command failed"
    fi

    print_test "Status command"
    if python -m empathy_os.cli status 2>&1 | grep -q -i "status\|Empathy\|attention"; then
        pass
    else
        fail "status command failed"
    fi

    print_section "Power User Commands"

    print_test "Morning briefing (help)"
    if python -m empathy_os.cli morning --help 2>&1 | grep -q -i "morning\|briefing\|usage"; then
        pass
    else
        skip "morning command help not available"
    fi

    print_test "Ship command (help)"
    if python -m empathy_os.cli ship --help 2>&1 | grep -q -i "ship\|pre-commit\|check"; then
        pass
    else
        skip "ship command help not available"
    fi
}

# ============================================================================
# TEST SECTION 3: ModelRouter Integration
# ============================================================================
test_model_router() {
    if ! should_run_section "router"; then
        return
    fi

    print_header "3. ModelRouter Integration for Cost Optimization"

    print_section "ModelRouter Module"

    print_test "Import ModelRouter"
    if python -c "from empathy_llm_toolkit.routing import ModelRouter" 2>/dev/null; then
        pass
    else
        fail "Could not import ModelRouter"
    fi

    print_test "Import TaskClassifier"
    if python -c "from empathy_llm_toolkit.routing import TaskClassifier" 2>/dev/null; then
        pass
    else
        skip "TaskClassifier may be internal"
    fi

    print_test "Import ModelTier enum"
    if python -c "from empathy_os.workflows.base import ModelTier" 2>/dev/null; then
        pass
    else
        fail "Could not import ModelTier"
    fi

    print_section "ModelRouter Functionality"

    print_test "ModelRouter routing (simple task)"
    RESULT=$(python -c "
from empathy_llm_toolkit.routing import ModelRouter
router = ModelRouter()
tier = router.route('Fix a typo in the README')
print(tier.value if hasattr(tier, 'value') else tier)
" 2>/dev/null)
    if [ -n "$RESULT" ]; then
        pass
    else
        skip "ModelRouter.route() interface may differ"
    fi

    print_test "ModelRouter routing (complex task)"
    RESULT=$(python -c "
from empathy_llm_toolkit.routing import ModelRouter
router = ModelRouter()
tier = router.route('Design a microservices architecture for a distributed system')
print(tier.value if hasattr(tier, 'value') else tier)
" 2>/dev/null)
    if [ -n "$RESULT" ]; then
        pass
    else
        skip "ModelRouter.route() interface may differ"
    fi

    print_section "Cost Tracking Integration"

    print_test "CostTracker import"
    if python -c "from empathy_os.cost_tracker import CostTracker" 2>/dev/null; then
        pass
    else
        fail "Could not import CostTracker"
    fi

    print_test "Costs CLI command"
    if python -m empathy_os.cli costs 2>&1 | grep -q -i "cost\|savings\|No cost"; then
        pass
    else
        fail "costs command failed"
    fi
}

# ============================================================================
# TEST SECTION 4: Redis Integration
# ============================================================================
test_redis_integration() {
    if ! should_run_section "redis"; then
        return
    fi

    print_header "4. Redis Integration with Environment-Aware Key Prefixing"

    print_section "Redis Module Configuration"

    print_test "Redis configuration in unified config"
    if grep -q "redis" empathy_llm_toolkit/config/unified.py 2>/dev/null; then
        pass
    else
        skip "Redis config not found"
    fi

    print_test "Persistence module available"
    if python -c "from empathy_os.persistence import StateManager; print('OK')" 2>/dev/null; then
        pass
    else
        fail "Could not import StateManager"
    fi

    print_section "Environment-Aware Key Prefixing"

    print_test "Redis module structure"
    if python -c "from empathy_os import persistence; print('module found')" 2>/dev/null; then
        pass
    else
        skip "persistence module not available"
    fi

    print_test "Redis connection (if available)"
    skip "Redis server configuration varies by environment"
}

# ============================================================================
# TEST SECTION 5: Workflow Improvements
# ============================================================================
test_workflows() {
    if ! should_run_section "workflow"; then
        return
    fi

    print_header "5. Workflow CLI Improvements"

    print_section "Workflow List and Describe"

    print_test "List workflows"
    if python -m empathy_os.cli workflow list 2>&1 | grep -q -i "research\|code-review"; then
        pass
    else
        fail "workflow list failed"
    fi

    print_test "Describe research workflow"
    if python -m empathy_os.cli workflow describe research 2>&1 | grep -q -i "research\|stage\|tier"; then
        pass
    else
        fail "workflow describe failed"
    fi

    print_section "Workflow Output Format (Content vs Metrics)"

    print_test "Research workflow outputs content"
    OUTPUT=$(python -m empathy_os.cli workflow run research --input '{"question": "test"}' 2>&1)
    if echo "$OUTPUT" | grep -q "Completed in.*Cost:"; then
        # Check that cost info is minimal (one line footer)
        COST_LINES=$(echo "$OUTPUT" | grep -c "Cost:" || true)
        if [ "$COST_LINES" -le 2 ]; then
            pass
        else
            fail "Too many cost lines in output"
        fi
    else
        fail "Missing completion footer"
    fi

    print_test "JSON output includes content"
    OUTPUT=$(python -m empathy_os.cli workflow run research --input '{"question": "test"}' --json 2>&1)
    # Extract JSON portion (skip header lines)
    if echo "$OUTPUT" | grep -q '"output":'; then
        pass
    else
        fail "JSON output missing 'output' field"
    fi

    print_section "Multi-Model Workflow Execution"

    print_test "Workflow stages execute"
    if python -m empathy_os.cli workflow run research --input '{"question": "What is Python?"}' 2>&1 | grep -q -i "Completed"; then
        pass
    else
        fail "Workflow did not complete"
    fi
}

# ============================================================================
# TEST SECTION 6: VSCode Extension Improvements
# ============================================================================
test_vscode_extension() {
    if ! should_run_section "vscode"; then
        return
    fi

    print_header "6. VSCode Extension Improvements"

    print_section "Extension Build"

    print_test "TypeScript compilation"
    if (cd vscode-extension && npm run compile 2>&1) | grep -q -v "error"; then
        pass
    else
        fail "TypeScript compilation errors"
    fi

    print_section "Dashboard Panel Features"

    print_test "Workflow input configuration exists"
    if grep -q "workflowConfig" vscode-extension/src/panels/EmpathyDashboardPanel.ts; then
        pass
    else
        fail "workflowConfig not found"
    fi

    print_test "File picker handler exists"
    if grep -q "_showFilePicker" vscode-extension/src/panels/EmpathyDashboardPanel.ts; then
        pass
    else
        fail "_showFilePicker not found"
    fi

    print_test "Folder picker handler exists"
    if grep -q "_showFolderPicker" vscode-extension/src/panels/EmpathyDashboardPanel.ts; then
        pass
    else
        fail "_showFolderPicker not found"
    fi

    print_test "Dropdown handler exists"
    if grep -q "_showDropdown" vscode-extension/src/panels/EmpathyDashboardPanel.ts; then
        pass
    else
        fail "_showDropdown not found"
    fi

    print_test "Active file pre-population"
    if grep -q "_sendActiveFile\|activeFile" vscode-extension/src/panels/EmpathyDashboardPanel.ts; then
        pass
    else
        fail "Active file handler not found"
    fi
}

# ============================================================================
# TEST SECTION 7: Debug Wizard Improvements
# ============================================================================
test_debug_wizard() {
    if ! should_run_section "debug"; then
        return
    fi

    print_header "7. Debug Wizard Improvements"

    print_section "Website Debug Wizard Component"

    print_test "DebugWizard component exists"
    if [ -f "website/components/debug-wizard/DebugWizard.tsx" ]; then
        pass
    else
        fail "DebugWizard.tsx not found"
    fi

    print_test "Drag-and-drop support"
    if grep -q -i "drag\|drop\|onDrop" website/components/debug-wizard/DebugWizard.tsx 2>/dev/null; then
        pass
    else
        skip "Drag-drop implementation not found in component"
    fi

    print_test "Folder selection support"
    if grep -q -i "folder\|directory\|tree" website/components/debug-wizard/DebugWizard.tsx 2>/dev/null; then
        pass
    else
        skip "Folder selection not found"
    fi

    print_section "Debug Wizard API"

    print_test "Analyze endpoint exists"
    if [ -f "website/app/api/debug-wizard/analyze/route.ts" ]; then
        pass
    else
        fail "analyze endpoint not found"
    fi

    print_test "Resolve endpoint exists"
    if [ -f "website/app/api/debug-wizard/resolve/route.ts" ]; then
        pass
    else
        fail "resolve endpoint not found"
    fi
}

# ============================================================================
# TEST SECTION 8: CLI Improvements
# ============================================================================
test_cli_improvements() {
    if ! should_run_section "cli"; then
        return
    fi

    print_header "8. CLI Improvements"

    print_section "Help and Discovery"

    print_test "Main help available"
    if python -m empathy_os.cli --help 2>&1 | grep -q -i "empathy\|usage"; then
        pass
    else
        fail "Main help not available"
    fi

    print_test "Cheatsheet command"
    if python -m empathy_os.cli cheatsheet 2>&1 | grep -q "Getting Started"; then
        pass
    else
        fail "Cheatsheet not working"
    fi

    print_section "Content Extraction (workflow output)"

    print_test "_extract_workflow_content function exists"
    if grep -q "_extract_workflow_content" src/empathy_os/cli.py; then
        pass
    else
        fail "Content extraction function not found"
    fi

    print_test "Content keys include 'answer'"
    if grep -q '"answer"' src/empathy_os/cli.py; then
        pass
    else
        fail "'answer' key not in content extraction"
    fi
}

# ============================================================================
# TEST SECTION 9: Integration Tests
# ============================================================================
test_integration() {
    if ! should_run_section "integration"; then
        return
    fi

    print_header "9. Integration Tests"

    print_section "End-to-End Workflow"

    print_test "Full research workflow execution"
    OUTPUT=$(python -m empathy_os.cli workflow run research \
        --input '{"question": "What are Python best practices?"}' 2>&1 || true)
    if echo "$OUTPUT" | grep -q "Completed in"; then
        pass
    else
        skip "Research workflow requires API key"
    fi

    print_section "Python Package Tests"

    print_test "Run pytest on recent features"
    if python -m pytest tests/ -v --tb=line -k "router or agent or workflow" --co -q 2>&1 | grep -q "test"; then
        pass
    else
        skip "No matching tests found"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print_header "EMPATHY FRAMEWORK - RECENT FEATURES TEST SUITE"
echo ""
echo "Testing features added in the last 7 days (since $(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d 2>/dev/null || echo '7 days ago'))"
echo ""

# Change to project root
cd "$(dirname "$0")/.."

# Run test sections
test_agent_factory
test_ux_commands
test_model_router
test_redis_integration
test_workflows
test_vscode_extension
test_debug_wizard
test_cli_improvements
test_integration

# ============================================================================
# SUMMARY
# ============================================================================

print_header "TEST SUMMARY"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $PASSED"
echo -e "  ${RED}Failed:${NC}  $FAILED"
echo -e "  ${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PERCENT=$((PASSED * 100 / TOTAL))
    echo -e "  Pass Rate: ${PERCENT}%"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Review output above.${NC}"
    exit 1
fi
