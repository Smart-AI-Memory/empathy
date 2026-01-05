#!/usr/bin/env python3
"""
Code Analysis Wizard - Interactive Setup and Usage Guide

A friendly, step-by-step wizard to help new users get started with
the Deep Study AI code analysis system.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


class Colors:
    """Terminal colors for better UX"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class CodeAnalysisWizard:
    """Interactive wizard for code analysis"""

    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.selected_files = []
        self.selected_language = None
        self.auto_fix = False

    def print_header(self, text: str):
        """Print a styled header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
        print(f"{text.center(70)}")
        print(f"{'=' * 70}{Colors.ENDC}\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

    def get_input(self, prompt: str, default: str | None = None) -> str:
        """Get user input with optional default"""
        if default:
            full_prompt = f"{Colors.OKBLUE}{prompt} [{default}]: {Colors.ENDC}"
        else:
            full_prompt = f"{Colors.OKBLUE}{prompt}: {Colors.ENDC}"

        response = input(full_prompt).strip()
        return response if response else (default or "")

    def get_choice(self, prompt: str, options: list[str]) -> str:
        """Get user choice from a list"""
        print(f"\n{Colors.OKBLUE}{prompt}{Colors.ENDC}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        while True:
            choice = input(f"{Colors.OKBLUE}Enter choice (1-{len(options)}): {Colors.ENDC}").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            self.print_error("Invalid choice. Please try again.")

    def welcome(self):
        """Display welcome message"""
        self.print_header("🚀 Welcome to Deep Study AI Code Analysis Wizard")

        print(f"{Colors.BOLD}What can this wizard do for you?{Colors.ENDC}\n")
        print("  • Analyze your code for bugs and security issues")
        print("  • Provide personalized learning recommendations")
        print("  • Auto-fix common code quality problems")
        print("  • Support JavaScript, TypeScript, Python, Rust, and more\n")

        input(f"{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")

    def check_setup(self) -> bool:
        """Check if the system is set up correctly"""
        self.print_header("🔍 Checking System Setup")

        # Check Python virtual environment
        venv_python = self.backend_dir / "venv" / "bin" / "python"
        if venv_python.exists():
            self.print_success("Python virtual environment found")
        else:
            self.print_error("Python virtual environment not found")
            return False

        # Check analyzer module
        try:
            from services.analyzers.multi_layer_analyzer import \
                MultiLayerAnalyzer  # noqa: F401

            self.print_success("Multi-layer analyzer available")
        except ImportError:
            self.print_error("Multi-layer analyzer not found")
            return False

        # Check tools
        self.print_info("Checking analysis tools...")

        tools_found = []
        try:
            import subprocess

            if subprocess.run(["which", "pylint"], capture_output=True).returncode == 0:
                tools_found.append("Pylint (Python)")
            if (
                subprocess.run(
                    ["npx", "--no-install", "eslint", "--version"],
                    capture_output=True,
                    cwd=str(self.backend_dir.parent / "frontend"),
                ).returncode
                == 0
            ):
                tools_found.append("ESLint (JavaScript/TypeScript)")
            if subprocess.run(["which", "rustc"], capture_output=True).returncode == 0:
                tools_found.append("Rust")
        except Exception:
            pass

        if tools_found:
            for tool in tools_found:
                self.print_success(f"  {tool}")
        else:
            self.print_warning("No analysis tools found - will use basic analysis")

        print()
        return True

    def select_mode(self) -> str:
        """Select analysis mode"""
        self.print_header("📋 Select Analysis Mode")

        modes = [
            "Analyze a single file",
            "Analyze multiple files",
            "Analyze entire directory",
            "Auto-fix code quality issues",
            "Quick test (analyze sample file)",
        ]

        return self.get_choice("What would you like to do?", modes)

    def select_files(self, mode: str):
        """Select files to analyze"""
        if "Quick test" in mode:
            self.selected_files = [str(self.backend_dir / "test_sample.js")]
            self.print_info(f"Using sample file: {self.selected_files[0]}")
            return

        if "Auto-fix" in mode:
            directory = self.get_input("Enter directory to clean up", ".")
            self.selected_files = [directory]
            self.auto_fix = True
            return

        if "single file" in mode:
            while True:
                filepath = self.get_input("Enter file path to analyze")
                if os.path.exists(filepath):
                    self.selected_files = [filepath]
                    break
                else:
                    self.print_error(f"File not found: {filepath}")
                    retry = self.get_input("Try again? (y/n)", "y")
                    if retry.lower() != "y":
                        return

        elif "multiple files" in mode:
            print(
                f"\n{Colors.OKBLUE}Enter file paths (one per line, empty line to finish):{Colors.ENDC}"
            )
            while True:
                filepath = input("  File: ").strip()
                if not filepath:
                    break
                if os.path.exists(filepath):
                    self.selected_files.append(filepath)
                    self.print_success(f"Added: {filepath}")
                else:
                    self.print_error(f"File not found: {filepath}")

        elif "directory" in mode:
            directory = self.get_input("Enter directory path", ".")
            extensions = self.get_input("File extensions (comma-separated)", ".py,.js,.ts,.tsx")
            ext_list = [ext.strip() for ext in extensions.split(",")]

            # Find files
            found_files = []
            for root, dirs, files in os.walk(directory):
                # Skip common directories
                dirs[:] = [
                    d for d in dirs if d not in ["venv", "node_modules", "__pycache__", ".git"]
                ]

                for file in files:
                    if any(file.endswith(ext) for ext in ext_list):
                        found_files.append(os.path.join(root, file))

            if found_files:
                self.print_success(f"Found {len(found_files)} files")
                show = self.get_input("Show list? (y/n)", "n")
                if show.lower() == "y":
                    for f in found_files[:20]:  # Show first 20
                        print(f"  {f}")
                    if len(found_files) > 20:
                        print(f"  ... and {len(found_files) - 20} more")

                self.selected_files = found_files
            else:
                self.print_warning("No files found")

    def run_analysis(self):
        """Run the analysis"""
        if self.auto_fix:
            self.run_cleanup()
            return

        if not self.selected_files:
            self.print_warning("No files selected")
            return

        self.print_header("🔍 Running Analysis")

        try:
            from services.analyzers.multi_layer_analyzer import \
                MultiLayerAnalyzer

            analyzer = MultiLayerAnalyzer()

            for filepath in self.selected_files:
                print(f"\n{Colors.BOLD}Analyzing: {filepath}{Colors.ENDC}")
                print("-" * 70)

                try:
                    with open(filepath, encoding="utf-8") as f:
                        code = f.read()

                    # Detect language
                    ext = Path(filepath).suffix.lower()
                    lang_map = {
                        ".js": "javascript",
                        ".jsx": "javascript",
                        ".ts": "typescript",
                        ".tsx": "typescript",
                        ".py": "python",
                        ".rs": "rust",
                        ".go": "go",
                        ".java": "java",
                        ".cs": "csharp",
                        ".php": "php",
                    }
                    language = lang_map.get(ext, "javascript")

                    results = analyzer.analyze(code, language)
                    issues = results.get("rules", [])

                    if issues:
                        print(f"\n{Colors.WARNING}Found {len(issues)} issues:{Colors.ENDC}\n")

                        # Group by severity
                        errors = [i for i in issues if i.severity.value == "error"]
                        warnings = [i for i in issues if i.severity.value == "warning"]

                        if errors:
                            print(f"{Colors.FAIL}🔴 ERRORS ({len(errors)}):{Colors.ENDC}")
                            for issue in errors[:5]:
                                print(f"  Line {issue.line}: {issue.title}")
                                if issue.recommendation:
                                    print(f"    💡 {issue.recommendation}")

                        if warnings:
                            print(f"\n{Colors.WARNING}⚠️  WARNINGS ({len(warnings)}):{Colors.ENDC}")
                            for issue in warnings[:5]:
                                print(f"  Line {issue.line}: {issue.title}")
                                if issue.recommendation:
                                    print(f"    💡 {issue.recommendation}")

                        if len(issues) > 10:
                            print(
                                f"\n{Colors.OKCYAN}... and {len(issues) - 10} more issues{Colors.ENDC}"
                            )

                    else:
                        self.print_success("No issues found - excellent code quality!")

                except Exception as e:
                    self.print_error(f"Error analyzing {filepath}: {str(e)}")

        except ImportError as e:
            self.print_error(f"Failed to import analyzer: {str(e)}")

    def run_cleanup(self):
        """Run code cleanup"""
        self.print_header("🧹 Running Code Cleanup")

        directory = self.selected_files[0] if self.selected_files else "."

        try:
            import subprocess

            result = subprocess.run(
                [
                    str(self.backend_dir / "venv" / "bin" / "python"),
                    str(self.backend_dir / "cleanup_code.py"),
                    directory,
                ],
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            if result.returncode == 0:
                self.print_success("Cleanup completed successfully!")
            else:
                self.print_error("Cleanup encountered errors")
                print(result.stderr)

        except Exception as e:
            self.print_error(f"Failed to run cleanup: {str(e)}")

    def show_next_steps(self):
        """Show next steps and resources"""
        self.print_header("📚 Next Steps")

        print(f"{Colors.BOLD}Great job! Here's what you can do next:{Colors.ENDC}\n")

        print("1. 📖 Read the documentation:")
        print("   • QUICKSTART.md - Complete guide")
        print("   • CHEATSHEET.md - Quick reference")
        print("   • HOW_TO_ANALYZE_CODE.md - Detailed usage\n")

        print("2. 🔧 Use the command-line tools:")
        print("   • ./venv/bin/python analyze_code.py <file>")
        print("   • ./venv/bin/python cleanup_code.py <directory>\n")

        print("3. 🎓 Learn about Layer 5 Empathy Framework:")
        print("   • LAYER5_EMPATHY_FRAMEWORK.md - Personalized learning\n")

        print("4. ⚡ Create shortcuts:")
        print("   • Add aliases to your shell")
        print("   • Set up VS Code tasks")
        print("   • Add pre-commit hooks\n")

        self.print_success("Happy coding! 🚀")

    def run(self):
        """Run the wizard"""
        try:
            # Welcome
            self.welcome()

            # Check setup
            if not self.check_setup():
                self.print_error("Setup incomplete. Please check installation.")
                return

            # Select mode
            mode = self.select_mode()

            # Select files
            self.select_files(mode)

            # Run analysis
            if self.selected_files or self.auto_fix:
                confirm = self.get_input("\nReady to proceed? (y/n)", "y")
                if confirm.lower() == "y":
                    self.run_analysis()
                else:
                    self.print_info("Analysis cancelled")

            # Next steps
            show_next = self.get_input("\nWould you like to see next steps? (y/n)", "y")
            if show_next.lower() == "y":
                self.show_next_steps()

            # Run again?
            again = self.get_input("\nRun wizard again? (y/n)", "n")
            if again.lower() == "y":
                print("\n" * 2)
                self.run()

        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Wizard cancelled by user.{Colors.ENDC}")
        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")
            import traceback

            traceback.print_exc()


def main():
    """Main entry point"""
    wizard = CodeAnalysisWizard()
    wizard.run()


if __name__ == "__main__":
    main()
