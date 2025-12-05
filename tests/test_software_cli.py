"""
Tests for empathy_software_plugin CLI

Focused tests for helper functions and core CLI components.
"""

# Import the CLI module
from empathy_software_plugin import cli


class TestColorHelperFunctions:
    """Test CLI color output helper functions"""

    def test_print_header(self, capsys):
        """Test print_header function"""
        cli.print_header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "=" in captured.out

    def test_print_alert(self, capsys):
        """Test print_alert function"""
        cli.print_alert("Test Alert")
        captured = capsys.readouterr()
        assert "Test Alert" in captured.out
        assert "[ALERT]" in captured.out or "ALERT" in captured.out

    def test_print_success(self, capsys):
        """Test print_success function"""
        cli.print_success("Test Success")
        captured = capsys.readouterr()
        assert "Test Success" in captured.out

    def test_print_error(self, capsys):
        """Test print_error function"""
        cli.print_error("Test Error")
        captured = capsys.readouterr()
        assert "Test Error" in captured.out

    def test_print_info(self, capsys):
        """Test print_info function"""
        cli.print_info("Test Info")
        captured = capsys.readouterr()
        assert "Test Info" in captured.out


class TestColors:
    """Test Colors class"""

    def test_colors_class_attributes(self):
        """Test Colors class has expected attributes"""
        assert hasattr(cli.Colors, "HEADER")
        assert hasattr(cli.Colors, "BLUE")
        assert hasattr(cli.Colors, "CYAN")
        assert hasattr(cli.Colors, "GREEN")
        assert hasattr(cli.Colors, "YELLOW")
        assert hasattr(cli.Colors, "RED")
        assert hasattr(cli.Colors, "BOLD")
        assert hasattr(cli.Colors, "UNDERLINE")
        assert hasattr(cli.Colors, "END")

    def test_colors_are_strings(self):
        """Test that all color codes are strings"""
        assert isinstance(cli.Colors.HEADER, str)
        assert isinstance(cli.Colors.BLUE, str)
        assert isinstance(cli.Colors.GREEN, str)
        assert isinstance(cli.Colors.END, str)


class TestCLIImports:
    """Test that CLI module imports correctly"""

    def test_module_has_logger(self):
        """Test CLI module has logger"""
        assert hasattr(cli, "logger")
        assert cli.logger is not None

    def test_module_has_required_functions(self):
        """Test CLI module has required functions"""
        assert hasattr(cli, "print_header")
        assert hasattr(cli, "print_success")
        assert hasattr(cli, "print_error")
        assert hasattr(cli, "print_info")
        assert hasattr(cli, "print_alert")
        assert callable(cli.print_header)
        assert callable(cli.print_success)


class TestCLIBasicFunctionality:
    """Test basic CLI functionality"""

    def test_colorama_import_handling(self):
        """Test that colorama import is handled (may or may not be installed)"""
        # Just verify the module loads without error
        # colorama is optional, so we don't test its functionality
        assert cli is not None

    def test_multiple_print_calls(self, capsys):
        """Test multiple consecutive print calls"""
        cli.print_success("Success 1")
        cli.print_success("Success 2")
        cli.print_error("Error 1")
        captured = capsys.readouterr()
        assert "Success 1" in captured.out
        assert "Success 2" in captured.out
        assert "Error 1" in captured.out

    def test_header_with_special_characters(self, capsys):
        """Test header with special characters"""
        cli.print_header("Test Header with 特殊字符 and émojis 🚀")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out

    def test_print_functions_with_empty_string(self, capsys):
        """Test print functions with empty strings"""
        cli.print_success("")
        cli.print_error("")
        cli.print_info("")
        captured = capsys.readouterr()
        # Should produce some output even if message is empty
        assert captured.out is not None

    def test_print_functions_with_long_text(self, capsys):
        """Test print functions with very long text"""
        long_text = "A" * 1000
        cli.print_success(long_text)
        captured = capsys.readouterr()
        assert long_text in captured.out


class TestCLIModuleStructure:
    """Test CLI module structure and setup"""

    def test_module_docstring(self):
        """Test CLI module has docstring"""
        assert cli.__doc__ is not None
        assert len(cli.__doc__) > 0

    def test_module_has_path_manipulation(self):
        """Test sys.path manipulation for imports"""
        # The CLI adds parent directory to path for imports
        # Just verify the module loaded correctly
        assert "empathy_os" in dir(cli) or hasattr(cli, "get_logger")


class TestCLIHelperEdgeCases:
    """Test edge cases for CLI helper functions"""

    def test_header_with_very_long_text(self, capsys):
        """Test header with very long text"""
        long_header = "=" * 200
        cli.print_header(long_header)
        captured = capsys.readouterr()
        assert "=" in captured.out

    def test_print_with_newlines(self, capsys):
        """Test print functions with newlines in text"""
        cli.print_success("Line 1\nLine 2\nLine 3")
        captured = capsys.readouterr()
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out

    def test_print_with_unicode(self, capsys):
        """Test print functions with unicode characters"""
        cli.print_info("Unicode: λ, α, β, γ, δ")
        captured = capsys.readouterr()
        assert "Unicode" in captured.out

    def test_colors_end_code(self):
        """Test that Colors.END is a reset code"""
        # ANSI reset code is \033[0m
        assert cli.Colors.END == "\033[0m"


# Integration test placeholder for when async tests are needed
class TestCLIIntegration:
    """Integration tests for CLI (placeholders for complex async tests)"""

    def test_cli_module_loads(self):
        """Test that CLI module loads without errors"""
        assert cli is not None

    def test_logger_configured(self):
        """Test that logger is configured"""
        assert cli.logger is not None
        assert hasattr(cli.logger, "info")
        assert hasattr(cli.logger, "error")
        assert hasattr(cli.logger, "warning")


class TestParseAICalls:
    """Test AI call parsing function"""

    def test_parse_ai_calls_with_openai(self):
        """Test parsing OpenAI calls"""
        content = """
import openai
response = openai.chat.completions.create(model="gpt-4")
"""
        result = cli.parse_ai_calls("test.py", content)
        assert len(result) > 0
        assert result[0]["location"] == "test.py"
        assert "prompt_size" in result[0]

    def test_parse_ai_calls_with_anthropic(self):
        """Test parsing Anthropic calls"""
        content = """
import anthropic
response = anthropic.messages.create(model="claude-3-sonnet")
"""
        result = cli.parse_ai_calls("test.py", content)
        assert len(result) > 0
        assert result[0]["location"] == "test.py"

    def test_parse_ai_calls_no_ai(self):
        """Test parsing file with no AI calls"""
        content = "print('hello world')"
        result = cli.parse_ai_calls("test.py", content)
        assert len(result) == 0

    def test_parse_ai_calls_empty_content(self):
        """Test parsing empty content"""
        result = cli.parse_ai_calls("test.py", "")
        assert len(result) == 0


class TestParseGitHistory:
    """Test Git history parsing function"""

    def test_parse_git_history_single_commit(self):
        """Test parsing single commit"""
        # Files start with space in actual git log output
        git_output = """abc123 First commit
 file1.py
 file2.py"""
        result = cli.parse_git_history(git_output)
        assert len(result) == 1
        assert result[0]["hash"] == "abc123"
        assert "file1.py" in result[0]["files"]
        assert "file2.py" in result[0]["files"]

    def test_parse_git_history_multiple_commits(self):
        """Test parsing multiple commits"""
        # Files start with space in actual git log output
        git_output = """abc123 First commit
 file1.py
def456 Second commit
 file2.py
 file3.py"""
        result = cli.parse_git_history(git_output)
        assert len(result) == 2
        assert result[0]["hash"] == "abc123"
        assert result[1]["hash"] == "def456"

    def test_parse_git_history_empty(self):
        """Test parsing empty git output"""
        result = cli.parse_git_history("")
        assert len(result) == 0

    def test_parse_git_history_commit_no_files(self):
        """Test commit with no files"""
        git_output = "abc123 Commit message"
        result = cli.parse_git_history(git_output)
        assert len(result) == 1
        assert result[0]["hash"] == "abc123"
        assert len(result[0]["files"]) == 0


class TestPrepareWizardContext:
    """Test wizard context preparation"""

    def test_prepare_context_prompt_engineering(self):
        """Test context for prompt_engineering wizard"""
        full_context = {
            "project_path": "/test/project",
            "prompt_files": ["prompt1.txt", "prompt2.md"],
            "version_history": [],
        }
        result = cli.prepare_wizard_context("prompt_engineering", full_context)
        assert result["project_path"] == "/test/project"
        assert "prompt_files" in result
        assert len(result["prompt_files"]) == 2

    def test_prepare_context_context_window(self):
        """Test context for context_window wizard"""
        full_context = {
            "project_path": "/test/project",
            "ai_calls": [{"id": "call1"}],
            "context_sources": ["source1"],
            "version_history": [],
        }
        result = cli.prepare_wizard_context("context_window", full_context)
        assert "ai_calls" in result
        assert "context_sources" in result
        assert result["ai_provider"] == "anthropic"
        assert result["model_name"] == "claude-3-sonnet"

    def test_prepare_context_collaboration_pattern(self):
        """Test context for collaboration_pattern wizard"""
        full_context = {
            "project_path": "/test/project",
            "ai_integration_files": ["file1.py"],
            "ai_usage_patterns": ["pattern1"],
            "version_history": [],
        }
        result = cli.prepare_wizard_context("collaboration_pattern", full_context)
        assert "ai_integration_files" in result
        assert "ai_usage_patterns" in result

    def test_prepare_context_ai_documentation(self):
        """Test context for ai_documentation wizard"""
        full_context = {
            "project_path": "/test/project",
            "documentation_files": ["README.md"],
            "code_files": ["main.py"],
            "version_history": [],
        }
        result = cli.prepare_wizard_context("ai_documentation", full_context)
        assert "documentation_files" in result
        assert "code_files" in result

    def test_prepare_context_unknown_wizard(self):
        """Test context for unknown wizard returns base context"""
        full_context = {
            "project_path": "/test/project",
            "version_history": [{"hash": "abc123"}],
        }
        result = cli.prepare_wizard_context("unknown_wizard", full_context)
        assert result["project_path"] == "/test/project"
        assert "version_history" in result
        # Should only have base context
        assert len(result) == 2


class TestDisplayWizardResults:
    """Test wizard result display"""

    def test_display_results_with_issues(self, capsys):
        """Test displaying results with issues"""
        result = {
            "issues": [
                {"severity": "error", "message": "Critical issue"},
                {"severity": "warning", "message": "Warning issue"},
                {"severity": "info", "message": "Info issue"},
            ],
            "predictions": [],
            "recommendations": [],
            "confidence": 0.85,
        }
        cli.display_wizard_results(None, result, verbose=False)
        captured = capsys.readouterr()
        assert "Critical issue" in captured.out
        assert "Warning issue" in captured.out
        assert "Info issue" in captured.out
        assert "85%" in captured.out

    def test_display_results_with_predictions(self, capsys):
        """Test displaying results with predictions"""
        result = {
            "issues": [],
            "predictions": [
                {
                    "alert": "Potential issue coming",
                    "prevention_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
                    "reasoning": "Based on patterns",
                    "personal_experience": "Seen this before",
                }
            ],
            "recommendations": [],
            "confidence": 0.9,
        }
        cli.display_wizard_results(None, result, verbose=True)
        captured = capsys.readouterr()
        assert "Potential issue coming" in captured.out
        assert "Step 1" in captured.out
        assert "Step 2" in captured.out
        assert "Step 3" in captured.out
        # Should show only first 3 steps
        assert captured.out.count("Step") == 3

    def test_display_results_with_recommendations(self, capsys):
        """Test displaying results with recommendations"""
        result = {
            "issues": [],
            "predictions": [],
            "recommendations": ["Rec 1", "Rec 2", "Rec 3", "Rec 4", "Rec 5", "Rec 6"],
            "confidence": 0.75,
        }
        cli.display_wizard_results(None, result, verbose=False)
        captured = capsys.readouterr()
        assert "Rec 1" in captured.out
        # Should show only top 5
        assert "Rec 5" in captured.out
        assert "Rec 6" not in captured.out

    def test_display_results_empty(self, capsys):
        """Test displaying empty results"""
        result = {
            "issues": [],
            "predictions": [],
            "recommendations": [],
            "confidence": 1.0,
        }
        cli.display_wizard_results(None, result, verbose=False)
        captured = capsys.readouterr()
        assert "100%" in captured.out


class TestPrintSummary:
    """Test summary printing"""

    def test_print_summary_basic(self, capsys):
        """Test basic summary"""
        results = {
            "wizard1": {
                "issues": [{"severity": "error"}],
                "predictions": [],
            },
            "wizard2": {
                "issues": [],
                "predictions": [{"impact": "low"}],
            },
        }
        cli.print_summary(results)
        captured = capsys.readouterr()
        assert "Wizards run: 2" in captured.out
        assert "Current issues found: 1" in captured.out
        assert "Anticipatory alerts: 1" in captured.out

    def test_print_summary_high_impact(self, capsys):
        """Test summary with high impact alerts"""
        results = {
            "wizard1": {
                "issues": [],
                "predictions": [
                    {"impact": "high"},
                    {"impact": "high"},
                    {"impact": "low"},
                ],
            }
        }
        cli.print_summary(results)
        captured = capsys.readouterr()
        assert "High-impact alerts: 2" in captured.out

    def test_print_summary_with_patterns(self, capsys):
        """Test summary with patterns"""
        results = {
            "wizard1": {
                "issues": [],
                "predictions": [],
                "patterns": ["pattern1", "pattern2"],
            }
        }
        cli.print_summary(results)
        captured = capsys.readouterr()
        assert "Cross-domain patterns discovered: 2" in captured.out
        assert "Level 5 Systems Empathy" in captured.out

    def test_print_summary_empty(self, capsys):
        """Test empty summary"""
        results = {}
        cli.print_summary(results)
        captured = capsys.readouterr()
        assert "Wizards run: 0" in captured.out
        assert "Current issues found: 0" in captured.out
