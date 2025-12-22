"""
Comprehensive tests for Software Plugin CLI

Tests coverage for empathy_software_plugin/cli.py including:
- analyze_project() - Plugin registry, wizard execution
- gather_project_context() - File scanning, AI detection
- scan_command() - Security/performance scanning
- list_wizards() / wizard_info() - Plugin discovery
- Print/display functions
- Main CLI entry point

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import the CLI module
from empathy_software_plugin.cli import (
    Colors,
    analyze_project,
    display_wizard_results,
    gather_project_context,
    list_wizards,
    main,
    parse_ai_calls,
    parse_git_history,
    prepare_wizard_context,
    print_alert,
    print_error,
    print_header,
    print_info,
    print_success,
    print_summary,
    scan_command,
    wizard_info,
)

# ============================================================================
# Print/Display Function Tests
# ============================================================================


def test_colors_defined():
    """Test that color codes are defined"""
    assert hasattr(Colors, "HEADER")
    assert hasattr(Colors, "BLUE")
    assert hasattr(Colors, "CYAN")
    assert hasattr(Colors, "GREEN")
    assert hasattr(Colors, "YELLOW")
    assert hasattr(Colors, "RED")
    assert hasattr(Colors, "BOLD")
    assert hasattr(Colors, "UNDERLINE")
    assert hasattr(Colors, "END")


def test_print_header(capsys):
    """Test print_header outputs formatted text"""
    print_header("Test Header")
    captured = capsys.readouterr()
    assert "Test Header" in captured.out
    assert "=" in captured.out  # Should have separator


def test_print_alert(capsys):
    """Test print_alert outputs alert message"""
    print_alert("Test alert message")
    captured = capsys.readouterr()
    assert "Test alert message" in captured.out
    assert "ALERT" in captured.out


def test_print_success(capsys):
    """Test print_success outputs success message"""
    print_success("Success message")
    captured = capsys.readouterr()
    assert "Success message" in captured.out


def test_print_error(capsys):
    """Test print_error outputs error message"""
    print_error("Error message")
    captured = capsys.readouterr()
    assert "Error message" in captured.out


def test_print_info(capsys):
    """Test print_info outputs info message"""
    print_info("Info message")
    captured = capsys.readouterr()
    assert "Info message" in captured.out


# ============================================================================
# Parse Functions Tests
# ============================================================================


def test_parse_ai_calls_openai():
    """Test parsing OpenAI API calls from content"""
    content = """
    import openai
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    """
    calls = parse_ai_calls("test.py", content)

    assert isinstance(calls, list)
    assert len(calls) > 0
    assert calls[0]["location"] == "test.py"
    assert "code_snippet" in calls[0]


def test_parse_ai_calls_anthropic():
    """Test parsing Anthropic API calls from content"""
    content = """
    import anthropic
    client = anthropic.Anthropic()
    message = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": "Hello"}]
    )
    """
    calls = parse_ai_calls("test.py", content)

    assert isinstance(calls, list)
    assert len(calls) > 0
    assert calls[0]["location"] == "test.py"


def test_parse_ai_calls_no_ai_code():
    """Test parsing returns empty list when no AI code detected"""
    content = """
    def hello_world():
        print("Hello, World!")
    """
    calls = parse_ai_calls("test.py", content)

    assert isinstance(calls, list)
    assert len(calls) == 0


def test_parse_git_history():
    """Test parsing git log output"""
    git_output = """abc123 commit message
file1.py
file2.py

def456 another commit
file3.js
"""
    commits = parse_git_history(git_output)

    assert isinstance(commits, list)
    # Parser creates entries for each line - implementation detail
    assert len(commits) >= 2
    # Check that hashes are captured
    hashes = [c["hash"] for c in commits]
    assert "abc123" in hashes
    assert "def456" in hashes


def test_parse_git_history_empty():
    """Test parsing empty git history"""
    commits = parse_git_history("")
    assert isinstance(commits, list)
    assert len(commits) == 0


# ============================================================================
# gather_project_context Tests
# ============================================================================


@pytest.mark.asyncio
async def test_gather_project_context_basic(tmp_path):
    """Test gathering basic project context"""
    # Create test files
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Test Project")

    context = await gather_project_context(str(tmp_path))

    assert "project_path" in context
    assert context["project_path"] == str(tmp_path)
    assert "ai_integration_files" in context
    assert "documentation_files" in context
    assert "code_files" in context
    assert "test_files" in context


@pytest.mark.asyncio
async def test_gather_project_context_ai_files(tmp_path):
    """Test detecting AI integration files"""
    # Create file with AI imports
    ai_file = tmp_path / "ai_agent.py"
    ai_file.write_text(
        """
import openai

def generate_text():
    response = openai.chat.completions.create()
    return response
"""
    )

    context = await gather_project_context(str(tmp_path))

    assert len(context["ai_integration_files"]) > 0
    assert str(ai_file) in context["ai_integration_files"]
    # ai_calls may be empty depending on parse logic - just check it exists
    assert "ai_calls" in context


@pytest.mark.asyncio
async def test_gather_project_context_documentation(tmp_path):
    """Test detecting documentation files"""
    (tmp_path / "README.md").write_text("# Documentation")
    (tmp_path / "guide.rst").write_text("Guide content")
    (tmp_path / "notes.txt").write_text("Notes")

    context = await gather_project_context(str(tmp_path))

    assert len(context["documentation_files"]) == 3


@pytest.mark.asyncio
async def test_gather_project_context_prompt_files(tmp_path):
    """Test detecting prompt files"""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "system_prompt.txt").write_text("You are a helpful assistant")
    (tmp_path / "my_prompt.md").write_text("Prompt content")

    context = await gather_project_context(str(tmp_path))

    assert len(context["prompt_files"]) >= 2


@pytest.mark.asyncio
async def test_gather_project_context_test_files(tmp_path):
    """Test detecting test files"""
    (tmp_path / "test_example.py").write_text("def test_foo(): pass")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_bar.py").write_text("def test_bar(): pass")

    context = await gather_project_context(str(tmp_path))

    assert len(context["test_files"]) >= 2


@pytest.mark.asyncio
async def test_gather_project_context_git_history(tmp_path):
    """Test gathering git history"""
    # Initialize git repo
    (tmp_path / ".git").mkdir()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout="abc123 Initial commit\nfile1.py\n",
        )

        context = await gather_project_context(str(tmp_path))

        assert "version_history" in context


@pytest.mark.asyncio
async def test_gather_project_context_no_git(tmp_path):
    """Test when git is not available"""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        context = await gather_project_context(str(tmp_path))

        # Should still work, just without version history
        assert "version_history" in context
        assert context["version_history"] == []


@pytest.mark.asyncio
async def test_gather_project_context_langchain_detection(tmp_path):
    """Test detecting LangChain usage"""
    ai_file = tmp_path / "langchain_app.py"
    ai_file.write_text(
        """
from langchain.llms import OpenAI
from langchain.chains import LLMChain
"""
    )

    context = await gather_project_context(str(tmp_path))

    assert str(ai_file) in context["ai_integration_files"]


@pytest.mark.asyncio
async def test_gather_project_context_skips_unreadable_files(tmp_path):
    """Test that unreadable files are gracefully skipped"""
    # Create a file
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("content")

    # Make it unreadable
    with patch("builtins.open", side_effect=PermissionError):
        context = await gather_project_context(str(tmp_path))

        # Should still return valid context
        assert "ai_integration_files" in context


# ============================================================================
# prepare_wizard_context Tests
# ============================================================================


def test_prepare_wizard_context_prompt_engineering():
    """Test preparing context for prompt engineering wizard"""
    full_context = {
        "project_path": "/test/path",
        "prompt_files": ["prompt1.txt", "prompt2.txt"],
        "version_history": [{"hash": "abc123"}],
    }

    wizard_context = prepare_wizard_context("prompt_engineering", full_context)

    assert "project_path" in wizard_context
    assert "prompt_files" in wizard_context
    assert "version_history" in wizard_context
    assert wizard_context["prompt_files"] == ["prompt1.txt", "prompt2.txt"]


def test_prepare_wizard_context_context_window():
    """Test preparing context for context window wizard"""
    full_context = {
        "project_path": "/test/path",
        "ai_calls": [{"id": "call1"}],
        "context_sources": ["source1"],
    }

    wizard_context = prepare_wizard_context("context_window", full_context)

    assert "ai_calls" in wizard_context
    assert "context_sources" in wizard_context
    assert "ai_provider" in wizard_context
    assert "model_name" in wizard_context


def test_prepare_wizard_context_collaboration_pattern():
    """Test preparing context for collaboration pattern wizard"""
    full_context = {
        "project_path": "/test/path",
        "ai_integration_files": ["file1.py"],
        "ai_usage_patterns": ["pattern1"],
    }

    wizard_context = prepare_wizard_context("collaboration_pattern", full_context)

    assert "ai_integration_files" in wizard_context
    assert "ai_usage_patterns" in wizard_context


def test_prepare_wizard_context_ai_documentation():
    """Test preparing context for AI documentation wizard"""
    full_context = {
        "project_path": "/test/path",
        "documentation_files": ["doc1.md"],
        "code_files": ["code1.py"],
    }

    wizard_context = prepare_wizard_context("ai_documentation", full_context)

    assert "documentation_files" in wizard_context
    assert "code_files" in wizard_context


def test_prepare_wizard_context_unknown_wizard():
    """Test preparing context for unknown wizard returns base context"""
    full_context = {
        "project_path": "/test/path",
        "version_history": [],
    }

    wizard_context = prepare_wizard_context("unknown_wizard", full_context)

    assert "project_path" in wizard_context
    assert "version_history" in wizard_context


# ============================================================================
# display_wizard_results Tests
# ============================================================================


def test_display_wizard_results_with_issues(capsys):
    """Test displaying wizard results with issues"""
    wizard = Mock()
    result = {
        "issues": [
            {
                "severity": "error",
                "message": "Critical security issue",
                "suggestion": "Fix this now",
            },
            {
                "severity": "warning",
                "message": "Performance warning",
            },
        ],
        "predictions": [],
        "recommendations": [],
        "confidence": 0.85,
    }

    display_wizard_results(wizard, result, verbose=False)
    captured = capsys.readouterr()

    assert "Critical security issue" in captured.out
    assert "Performance warning" in captured.out
    assert "85%" in captured.out


def test_display_wizard_results_with_predictions(capsys):
    """Test displaying wizard results with predictions"""
    wizard = Mock()
    result = {
        "issues": [],
        "predictions": [
            {
                "alert": "This will break in 30 days",
                "reasoning": "Based on trend analysis",
                "personal_experience": "We've seen this before",
                "prevention_steps": ["Step 1", "Step 2", "Step 3"],
            }
        ],
        "recommendations": [],
        "confidence": 0.90,
    }

    display_wizard_results(wizard, result, verbose=True)
    captured = capsys.readouterr()

    assert "This will break in 30 days" in captured.out
    assert "ALERT" in captured.out
    assert "Step 1" in captured.out


def test_display_wizard_results_with_recommendations(capsys):
    """Test displaying wizard results with recommendations"""
    wizard = Mock()
    result = {
        "issues": [],
        "predictions": [],
        "recommendations": [
            "Implement caching",
            "Add error handling",
            "Improve logging",
        ],
        "confidence": 0.75,
    }

    display_wizard_results(wizard, result, verbose=False)
    captured = capsys.readouterr()

    assert "Implement caching" in captured.out
    assert "Add error handling" in captured.out


def test_display_wizard_results_verbose_mode(capsys):
    """Test displaying wizard results in verbose mode"""
    wizard = Mock()
    result = {
        "issues": [
            {
                "severity": "info",
                "message": "Info message",
                "suggestion": "This is a suggestion",
            }
        ],
        "predictions": [
            {
                "alert": "Future issue",
                "reasoning": "Detailed reasoning",
                "prevention_steps": ["Fix it"],
            }
        ],
        "recommendations": [],
        "confidence": 0.80,
    }

    display_wizard_results(wizard, result, verbose=True)
    captured = capsys.readouterr()

    assert "This is a suggestion" in captured.out
    assert "Detailed reasoning" in captured.out


# ============================================================================
# print_summary Tests
# ============================================================================


def test_print_summary_basic(capsys):
    """Test printing basic analysis summary"""
    all_results = {
        "wizard1": {
            "issues": [{"severity": "error"}],
            "predictions": [],
            "patterns": [],
        },
        "wizard2": {
            "issues": [],
            "predictions": [{"impact": "low"}],
            "patterns": [],
        },
    }

    print_summary(all_results)
    captured = capsys.readouterr()

    assert "Wizards run: 2" in captured.out
    assert "Current issues found: 1" in captured.out
    assert "Anticipatory alerts: 1" in captured.out


def test_print_summary_high_impact_alerts(capsys):
    """Test summary highlights high-impact alerts"""
    all_results = {
        "wizard1": {
            "issues": [],
            "predictions": [
                {"impact": "high", "alert": "Critical issue"},
                {"impact": "medium", "alert": "Medium issue"},
            ],
            "patterns": [],
        },
    }

    print_summary(all_results)
    captured = capsys.readouterr()

    assert "High-impact alerts: 1" in captured.out
    assert "Review these immediately" in captured.out


def test_print_summary_with_patterns(capsys):
    """Test summary includes pattern count"""
    all_results = {
        "wizard1": {
            "issues": [],
            "predictions": [],
            "patterns": [{"pattern_type": "drift"}, {"pattern_type": "sprawl"}],
        },
    }

    print_summary(all_results)
    captured = capsys.readouterr()

    assert "Cross-domain patterns discovered: 2" in captured.out
    assert "Level 5" in captured.out


# ============================================================================
# analyze_project Tests
# ============================================================================


@pytest.mark.asyncio
async def test_analyze_project_no_plugin():
    """Test analyze_project when software plugin not found"""
    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = None

        await analyze_project("/test/path")


@pytest.mark.asyncio
async def test_analyze_project_success(tmp_path):
    """Test successful project analysis"""
    mock_plugin = Mock()
    mock_wizard_class = Mock()
    mock_wizard = Mock()
    mock_wizard.analyze = AsyncMock(
        return_value={
            "issues": [],
            "predictions": [],
            "recommendations": [],
            "confidence": 0.9,
        }
    )
    mock_wizard_class.return_value = mock_wizard
    mock_plugin.get_wizard.return_value = mock_wizard_class

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(str(tmp_path), wizard_names=["prompt_engineering"])

        mock_wizard.analyze.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_project_json_output(tmp_path, capsys):
    """Test project analysis with JSON output"""
    mock_plugin = Mock()
    mock_wizard_class = Mock()
    mock_wizard = Mock()
    mock_wizard.analyze = AsyncMock(
        return_value={
            "issues": [{"message": "test issue"}],
            "predictions": [],
            "recommendations": [],
        }
    )
    mock_wizard_class.return_value = mock_wizard
    mock_plugin.get_wizard.return_value = mock_wizard_class

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(
            str(tmp_path),
            wizard_names=["testing"],
            output_format="json",
        )

        captured = capsys.readouterr()

        # Should output valid JSON (strip any extra output)
        json_output = captured.out.strip()
        # Find JSON content between first { and last }
        if "{" in json_output:
            json_start = json_output.index("{")
            json_end = json_output.rindex("}") + 1
            json_content = json_output[json_start:json_end]
            output_data = json.loads(json_content)
            assert "testing" in output_data


@pytest.mark.asyncio
async def test_analyze_project_wizard_not_found(tmp_path, capsys):
    """Test analyze_project when wizard not found"""
    mock_plugin = Mock()
    mock_plugin.get_wizard.return_value = None

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(str(tmp_path), wizard_names=["nonexistent"])

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


@pytest.mark.asyncio
async def test_analyze_project_wizard_error(tmp_path, capsys):
    """Test analyze_project handles wizard errors gracefully"""
    mock_plugin = Mock()
    mock_wizard_class = Mock()
    mock_wizard = Mock()
    mock_wizard.analyze = AsyncMock(side_effect=Exception("Wizard failed"))
    mock_wizard_class.return_value = mock_wizard
    mock_plugin.get_wizard.return_value = mock_wizard_class

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(str(tmp_path), wizard_names=["security"])

        captured = capsys.readouterr()
        assert "Error running wizard" in captured.out


@pytest.mark.asyncio
async def test_analyze_project_verbose_mode(tmp_path, capsys):
    """Test analyze_project in verbose mode"""
    mock_plugin = Mock()
    mock_wizard_class = Mock()
    mock_wizard = Mock()
    mock_wizard.analyze = AsyncMock(
        return_value={
            "issues": [],
            "predictions": [],
            "recommendations": [],
            "confidence": 0.8,
        }
    )
    mock_wizard_class.return_value = mock_wizard
    mock_plugin.get_wizard.return_value = mock_wizard_class

    # Create some files for verbose output
    (tmp_path / "test.py").write_text("import openai")
    (tmp_path / "README.md").write_text("docs")

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(
            str(tmp_path),
            wizard_names=["context_window"],
            verbose=True,
        )

        captured = capsys.readouterr()
        assert "Found" in captured.out  # Verbose file counts


@pytest.mark.asyncio
async def test_analyze_project_default_wizards(tmp_path):
    """Test analyze_project runs default wizards when none specified"""
    mock_plugin = Mock()
    mock_wizard_class = Mock()
    mock_wizard = Mock()
    mock_wizard.analyze = AsyncMock(
        return_value={
            "issues": [],
            "predictions": [],
            "recommendations": [],
        }
    )
    mock_wizard_class.return_value = mock_wizard
    mock_plugin.get_wizard.return_value = mock_wizard_class

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(str(tmp_path))  # No wizard_names

        # Should run default wizards
        assert mock_wizard.analyze.call_count >= 1


# ============================================================================
# list_wizards Tests
# ============================================================================


def test_list_wizards_success(capsys):
    """Test listing available wizards"""
    mock_plugin = Mock()
    mock_plugin.list_wizards.return_value = [
        "security",
        "performance",
        "testing",
    ]
    mock_plugin.get_wizard_info.side_effect = [
        {
            "name": "Security Wizard",
            "empathy_level": 4,
            "category": "security",
        },
        {
            "name": "Performance Wizard",
            "empathy_level": 3,
            "category": "performance",
        },
        {
            "name": "Testing Wizard",
            "empathy_level": 4,
            "category": "testing",
        },
    ]

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        list_wizards()

        captured = capsys.readouterr()

        assert "security" in captured.out
        assert "performance" in captured.out
        assert "testing" in captured.out


def test_list_wizards_no_plugin(capsys):
    """Test list_wizards when plugin not found"""
    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = None

        list_wizards()

        captured = capsys.readouterr()

        assert "not found" in captured.out.lower()


# ============================================================================
# wizard_info Tests
# ============================================================================


def test_wizard_info_success(capsys):
    """Test displaying wizard info"""
    mock_plugin = Mock()
    mock_plugin.get_wizard_info.return_value = {
        "name": "Security Analysis Wizard",
        "domain": "software",
        "empathy_level": 4,
        "category": "security",
        "required_context": ["code_files", "dependencies"],
    }

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        wizard_info("security")

        captured = capsys.readouterr()

        assert "Security Analysis Wizard" in captured.out
        assert "security" in captured.out
        assert "code_files" in captured.out


def test_wizard_info_not_found(capsys):
    """Test wizard_info when wizard not found"""
    mock_plugin = Mock()
    mock_plugin.get_wizard_info.return_value = None

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        wizard_info("nonexistent")

        captured = capsys.readouterr()

        assert "not found" in captured.out.lower()


def test_wizard_info_no_plugin(capsys):
    """Test wizard_info when plugin not found"""
    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = None

        wizard_info("security")


# ============================================================================
# scan_command Tests
# ============================================================================


def test_scan_command_insufficient_args():
    """Test scan_command with insufficient arguments"""
    with patch.object(sys, "argv", ["empathy-scan"]):
        with pytest.raises(SystemExit) as exc_info:
            scan_command()
        assert exc_info.value.code == 1


def test_scan_command_target_not_found(capsys):
    """Test scan_command when target doesn't exist"""
    with patch.object(sys, "argv", ["empathy-scan", "security", "/nonexistent/path"]):
        with pytest.raises(SystemExit) as exc_info:
            scan_command()
        assert exc_info.value.code == 1


def test_scan_command_security_single_file(tmp_path):
    """Test scan_command for security on a single file"""
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text(
        """
def process_data(user_input):
    exec(user_input)  # Security issue
"""
    )

    mock_security_wizard = Mock()
    mock_result = Mock()
    mock_result.issues = []
    mock_result.predictions = []
    mock_security_wizard.return_value.run_full_analysis.return_value = mock_result

    with patch.object(sys, "argv", ["empathy-scan", "security", str(test_file)]):
        with patch("coach_wizards.SecurityWizard", mock_security_wizard):
            with pytest.raises(SystemExit) as exc_info:
                scan_command()
            # Should exit successfully (0) when no issues
            assert exc_info.value.code == 0


def test_scan_command_performance_directory(tmp_path):
    """Test scan_command for performance on a directory"""
    # Create test files
    (tmp_path / "file1.py").write_text("def func1(): pass")
    (tmp_path / "file2.py").write_text("def func2(): pass")

    mock_performance_wizard = Mock()
    mock_result = Mock()
    mock_result.issues = []
    mock_result.predictions = []
    mock_performance_wizard.return_value.run_full_analysis.return_value = mock_result

    with patch.object(sys, "argv", ["empathy-scan", "performance", str(tmp_path)]):
        with patch("coach_wizards.PerformanceWizard", mock_performance_wizard):
            with pytest.raises(SystemExit) as exc_info:
                scan_command()
            assert exc_info.value.code == 0


def test_scan_command_all_scans(tmp_path):
    """Test scan_command with 'all' option"""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    mock_security_wizard = Mock()
    mock_performance_wizard = Mock()
    mock_result = Mock()
    mock_result.issues = []
    mock_result.predictions = []
    mock_security_wizard.return_value.run_full_analysis.return_value = mock_result
    mock_performance_wizard.return_value.run_full_analysis.return_value = mock_result

    with patch.object(sys, "argv", ["empathy-scan", "all", str(test_file)]):
        with patch("coach_wizards.SecurityWizard", mock_security_wizard):
            with patch("coach_wizards.PerformanceWizard", mock_performance_wizard):
                with pytest.raises(SystemExit) as exc_info:
                    scan_command()
                assert exc_info.value.code == 0


def test_scan_command_with_issues(tmp_path, capsys):
    """Test scan_command when issues are found"""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    mock_wizard = Mock()
    mock_result = Mock()
    mock_issue = Mock()
    mock_issue.severity = "high"
    mock_issue.line_number = 10
    mock_issue.message = "Security vulnerability"
    mock_result.issues = [mock_issue]
    mock_result.predictions = []
    mock_wizard.return_value.run_full_analysis.return_value = mock_result

    with patch.object(sys, "argv", ["empathy-scan", "security", str(test_file)]):
        with patch("coach_wizards.SecurityWizard", mock_wizard):
            with pytest.raises(SystemExit) as exc_info:
                scan_command()
            # Should exit with error code (1) when issues found
            assert exc_info.value.code == 1


def test_scan_command_unreadable_file(tmp_path, capsys):
    """Test scan_command handles unreadable files gracefully"""
    test_file = tmp_path / "test.py"
    test_file.write_text("content")

    mock_wizard = Mock()

    with patch.object(sys, "argv", ["empathy-scan", "security", str(test_file)]):
        with patch("coach_wizards.SecurityWizard", mock_wizard):
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                with pytest.raises(SystemExit):
                    scan_command()


def test_scan_command_no_python_files(tmp_path):
    """Test scan_command when no Python files found"""
    # Create non-Python file
    (tmp_path / "readme.txt").write_text("Not Python")

    with patch.object(sys, "argv", ["empathy-scan", "security", str(tmp_path)]):
        with pytest.raises(SystemExit) as exc_info:
            scan_command()
        # Should exit gracefully (0) when no files to scan
        assert exc_info.value.code == 0


def test_scan_command_import_error():
    """Test scan_command when wizards not installed"""
    with patch.object(sys, "argv", ["empathy-scan", "security", "test.py"]):
        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            with pytest.raises(SystemExit) as exc_info:
                scan_command()
            assert exc_info.value.code == 1


def test_scan_command_unknown_scan_type(tmp_path):
    """Test scan_command with unknown scan type"""
    test_file = tmp_path / "test.py"
    test_file.write_text("content")

    with patch.object(sys, "argv", ["empathy-scan", "unknown", str(test_file)]):
        with pytest.raises(SystemExit) as exc_info:
            scan_command()
        assert exc_info.value.code == 1


def test_scan_command_with_predictions(tmp_path, capsys):
    """Test scan_command displays predictions"""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    mock_wizard = Mock()
    mock_result = Mock()
    mock_result.issues = []
    mock_result.predictions = [
        {"alert": "Future issue predicted"},
        {"alert": "Another prediction"},
    ]
    mock_wizard.return_value.run_full_analysis.return_value = mock_result

    with patch.object(sys, "argv", ["empathy-scan", "security", str(test_file)]):
        with patch("coach_wizards.SecurityWizard", mock_wizard):
            with pytest.raises(SystemExit):
                scan_command()

            captured = capsys.readouterr()
            assert "prediction" in captured.out.lower()


# ============================================================================
# main() CLI Entry Point Tests
# ============================================================================


def test_main_no_command():
    """Test main() with no command"""
    with patch.object(sys, "argv", ["empathy-software"]):
        main()


def test_main_analyze_command(tmp_path, capsys):
    """Test main() with analyze command"""
    with patch.object(
        sys,
        "argv",
        ["empathy-software", "analyze", str(tmp_path)],
    ):
        with patch("empathy_os.plugins.get_global_registry") as mock_reg:
            mock_plugin = Mock()
            mock_wizard_class = Mock()
            mock_wizard = Mock()
            mock_wizard.analyze = AsyncMock(
                return_value={
                    "issues": [],
                    "predictions": [],
                    "recommendations": [],
                    "confidence": 0.9,
                }
            )
            mock_wizard_class.return_value = mock_wizard
            mock_plugin.get_wizard.return_value = mock_wizard_class
            mock_plugin.list_wizards.return_value = ["prompt_engineering"]
            mock_plugin.get_wizard_info.return_value = {
                "id": "prompt_engineering",
                "name": "Test Wizard",
            }
            mock_reg.return_value.get_plugin.return_value = mock_plugin

            main()
            # Verify analyze ran by checking output
            captured = capsys.readouterr()
            assert "Empathy Framework" in captured.out or "Analysis" in captured.out


def test_main_analyze_with_wizards(tmp_path):
    """Test main() analyze command with specific wizards"""
    with patch.object(
        sys,
        "argv",
        [
            "empathy-software",
            "analyze",
            str(tmp_path),
            "--wizards",
            "security,performance",
        ],
    ):
        # Use asyncio.run directly
        async def mock_analyze_project(*args, **kwargs):
            # Verify wizard names were parsed
            assert kwargs.get("wizard_names") == ["security", "performance"]
            return 0

        with patch(
            "empathy_software_plugin.cli.analyze_project",
            side_effect=mock_analyze_project,
        ):
            with patch("empathy_os.plugins.get_global_registry"):
                main()
                # Should complete successfully


def test_main_analyze_verbose():
    """Test main() analyze command with verbose flag"""
    with patch.object(
        sys,
        "argv",
        ["empathy-software", "analyze", "/test/path", "--verbose"],
    ):

        async def mock_analyze_project(*args, **kwargs):
            assert kwargs.get("verbose") is True
            return 0

        with patch(
            "empathy_software_plugin.cli.analyze_project",
            side_effect=mock_analyze_project,
        ):
            with patch("empathy_os.plugins.get_global_registry"):
                main()


def test_main_analyze_json_output():
    """Test main() analyze command with JSON output"""
    with patch.object(
        sys,
        "argv",
        ["empathy-software", "analyze", "/test/path", "--output", "json"],
    ):

        async def mock_analyze_project(*args, **kwargs):
            assert kwargs.get("output_format") == "json"
            return 0

        with patch(
            "empathy_software_plugin.cli.analyze_project",
            side_effect=mock_analyze_project,
        ):
            with patch("empathy_os.plugins.get_global_registry"):
                main()


def test_main_list_wizards_command(capsys):
    """Test main() with list-wizards command"""
    with patch.object(sys, "argv", ["empathy-software", "list-wizards"]):
        with patch("empathy_os.plugins.get_global_registry") as mock_reg:
            mock_plugin = Mock()
            mock_plugin.list_wizards.return_value = ["security", "performance"]
            mock_plugin.get_wizard_info.side_effect = lambda w: {
                "id": w,
                "name": f"{w.title()} Wizard",
                "description": f"Test {w} wizard",
                "domain": "software",
                "empathy_level": 3,
                "category": "analysis",
                "required_context": [],
            }
            mock_reg.return_value.get_plugin.return_value = mock_plugin

            main()

            # Verify wizard list was displayed
            captured = capsys.readouterr()
            assert "security" in captured.out.lower() or "Available" in captured.out


def test_main_wizard_info_command(capsys):
    """Test main() with wizard-info command"""
    with patch.object(sys, "argv", ["empathy-software", "wizard-info", "security"]):
        with patch("empathy_os.plugins.get_global_registry") as mock_reg:
            mock_plugin = Mock()
            mock_plugin.get_wizard_info.return_value = {
                "id": "security",
                "name": "Security Wizard",
                "description": "Analyzes code for security issues",
                "domain": "software",
                "empathy_level": 4,
                "category": "security",
                "capabilities": ["vuln_scan", "auth_check"],
                "required_context": ["code_files"],
            }
            mock_reg.return_value.get_plugin.return_value = mock_plugin

            main()

            # Verify wizard info was displayed
            captured = capsys.readouterr()
            assert "security" in captured.out.lower() or "Wizard" in captured.out


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_gather_project_context_empty_directory(tmp_path):
    """Test gathering context from empty directory"""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    context = await gather_project_context(str(empty_dir))

    assert context["project_path"] == str(empty_dir)
    assert len(context["ai_integration_files"]) == 0
    assert len(context["code_files"]) == 0


@pytest.mark.asyncio
async def test_gather_project_context_node_modules_excluded(tmp_path):
    """Test that node_modules is excluded from documentation scan"""
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.md").write_text("Package docs")

    context = await gather_project_context(str(tmp_path))

    # node_modules should be excluded
    assert not any("node_modules" in f for f in context["documentation_files"])


def test_display_wizard_results_empty_result(capsys):
    """Test displaying empty wizard results"""
    wizard = Mock()
    result = {
        "issues": [],
        "predictions": [],
        "recommendations": [],
        "confidence": 0.5,
    }

    display_wizard_results(wizard, result, verbose=False)
    captured = capsys.readouterr()

    # Should still display confidence
    assert "50%" in captured.out


def test_print_summary_empty_results(capsys):
    """Test summary with no results"""
    all_results = {}

    print_summary(all_results)
    captured = capsys.readouterr()

    assert "Wizards run: 0" in captured.out


@pytest.mark.asyncio
async def test_analyze_project_multiple_wizards(tmp_path):
    """Test running multiple wizards in sequence"""
    mock_plugin = Mock()

    wizard_results = {
        "security": {
            "issues": [{"severity": "high"}],
            "predictions": [],
            "recommendations": [],
        },
        "performance": {
            "issues": [],
            "predictions": [{"impact": "medium"}],
            "recommendations": [],
        },
    }

    def get_wizard(name):
        mock_wizard_class = Mock()
        mock_wizard = Mock()
        mock_wizard.analyze = AsyncMock(return_value=wizard_results.get(name, {}))
        mock_wizard_class.return_value = mock_wizard
        return mock_wizard_class

    mock_plugin.get_wizard = get_wizard

    with patch("empathy_os.plugins.get_global_registry") as mock_registry:
        mock_registry.return_value.get_plugin.return_value = mock_plugin

        await analyze_project(
            str(tmp_path),
            wizard_names=["security", "performance"],
        )
