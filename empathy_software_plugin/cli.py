"""
Empathy Framework - Software Development CLI

Command-line interface for running AI development wizards on your codebase.

Usage:
    empathy-software analyze /path/to/project
    empathy-software analyze /path/to/project --wizards prompt,context,collaboration
    empathy-software list-wizards
    empathy-software wizard-info testing

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from empathy_os.plugins import get_global_registry


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print("=" * len(text))


def print_alert(text: str):
    """Print alert message"""
    print(f"{Colors.YELLOW}[ALERT]{Colors.END} {text}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ{Colors.END} {text}")


async def analyze_project(
    project_path: str,
    wizard_names: List[str] = None,
    output_format: str = 'text',
    verbose: bool = False
):
    """
    Analyze a project with AI development wizards.

    Args:
        project_path: Path to project root
        wizard_names: List of wizard names to run (or None for all)
        output_format: 'text' or 'json'
        verbose: Show detailed output
    """
    print_header(f"Empathy Framework - AI Development Analysis")
    print(f"Project: {project_path}\n")

    # Get registry
    registry = get_global_registry()
    software_plugin = registry.get_plugin('software')

    if not software_plugin:
        print_error("Software plugin not found. Is it installed?")
        return 1

    # Determine which wizards to run
    if wizard_names:
        wizards_to_run = wizard_names
    else:
        # Run all AI development wizards
        wizards_to_run = [
            'prompt_engineering',
            'context_window',
            'collaboration_pattern',
            'ai_documentation'
        ]

    # Gather context
    print_info("Gathering project context...")
    context = await gather_project_context(project_path)

    if verbose:
        print_info(f"Found {len(context.get('ai_integration_files', []))} AI integration files")
        print_info(f"Found {len(context.get('documentation_files', []))} documentation files")

    # Run wizards
    all_results = {}

    for wizard_name in wizards_to_run:
        print_header(f"Running {wizard_name.replace('_', ' ').title()} Wizard")

        WizardClass = software_plugin.get_wizard(wizard_name)
        if not WizardClass:
            print_error(f"Wizard '{wizard_name}' not found")
            continue

        wizard = WizardClass()

        try:
            # Prepare wizard-specific context
            wizard_context = prepare_wizard_context(wizard_name, context)

            # Run analysis
            result = await wizard.analyze(wizard_context)
            all_results[wizard_name] = result

            # Display results
            if output_format == 'text':
                display_wizard_results(wizard, result, verbose)
            else:
                # JSON output handled at end
                pass

        except Exception as e:
            print_error(f"Error running wizard: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

    # Output results
    if output_format == 'json':
        print(json.dumps(all_results, indent=2, default=str))
    else:
        print_summary(all_results)

    return 0


async def gather_project_context(project_path: str) -> Dict[str, Any]:
    """
    Gather context about the project.

    Returns dictionary with all context needed by wizards.
    """
    project_root = Path(project_path)

    context = {
        'project_path': str(project_root),
        'ai_integration_files': [],
        'documentation_files': [],
        'prompt_files': [],
        'code_files': [],
        'test_files': [],
        'ai_calls': [],
        'context_sources': [],
        'ai_usage_patterns': [],
        'version_history': []
    }

    # Find AI integration files
    for pattern in ['**/*.py', '**/*.js', '**/*.ts']:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                # Check if file has AI integration
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if any(ai_lib in content for ai_lib in [
                            'openai', 'anthropic', 'langchain', 'llama', 'ai.generate'
                        ]):
                            context['ai_integration_files'].append(str(file_path))

                            # Parse AI calls
                            context['ai_calls'].extend(
                                parse_ai_calls(str(file_path), content)
                            )
                except Exception:
                    pass  # Skip files that can't be parsed

                # All Python/JS/TS files are code files
                context['code_files'].append(str(file_path))

    # Find documentation files
    for pattern in ['**/*.md', '**/*.rst', '**/*.txt']:
        for file_path in project_root.glob(pattern):
            if file_path.is_file() and 'node_modules' not in str(file_path):
                context['documentation_files'].append(str(file_path))

    # Find prompt files (common patterns)
    for pattern in ['**/prompts/**/*', '**/*prompt*.txt', '**/*prompt*.md']:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                context['prompt_files'].append(str(file_path))

    # Find test files
    for pattern in ['**/test_*.py', '**/*_test.py', '**/tests/**/*.py']:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                context['test_files'].append(str(file_path))

    # Get git history if available
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', '--oneline', '--name-only', '-50'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            context['version_history'] = parse_git_history(result.stdout)
    except Exception:
        pass  # Skip if git not available or fails

    return context


def parse_ai_calls(file_path: str, content: str) -> List[Dict[str, Any]]:
    """Parse AI API calls from file content"""
    # Simplified parser - in production, use AST
    calls = []

    # Look for common AI call patterns
    if 'openai.chat' in content or 'anthropic.messages' in content:
        calls.append({
            'id': f"{file_path}:ai_call",
            'location': file_path,
            'code_snippet': content[:500],  # First 500 chars as sample
            'prompt_size': len(content),
            'conversation_id': None  # Could detect from context
        })

    return calls


def parse_git_history(git_output: str) -> List[Dict[str, Any]]:
    """Parse git log output into structured history"""
    commits = []
    current_commit = None

    for line in git_output.split('\n'):
        if line and not line.startswith(' '):
            # New commit
            if current_commit:
                commits.append(current_commit)
            current_commit = {
                'hash': line.split()[0],
                'files': []
            }
        elif line and current_commit:
            # File in commit
            current_commit['files'].append(line.strip())

    if current_commit:
        commits.append(current_commit)

    return commits


def prepare_wizard_context(wizard_name: str, full_context: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare context specific to a wizard's requirements"""

    base_context = {
        'project_path': full_context['project_path'],
        'version_history': full_context.get('version_history', [])
    }

    if wizard_name == 'prompt_engineering':
        return {
            **base_context,
            'prompt_files': full_context.get('prompt_files', []),
        }

    elif wizard_name == 'context_window':
        return {
            **base_context,
            'ai_calls': full_context.get('ai_calls', []),
            'context_sources': full_context.get('context_sources', []),
            'ai_provider': 'anthropic',  # Could detect from code
            'model_name': 'claude-3-sonnet',
        }

    elif wizard_name == 'collaboration_pattern':
        return {
            **base_context,
            'ai_integration_files': full_context.get('ai_integration_files', []),
            'ai_usage_patterns': full_context.get('ai_usage_patterns', []),
        }

    elif wizard_name == 'ai_documentation':
        return {
            **base_context,
            'documentation_files': full_context.get('documentation_files', []),
            'code_files': full_context.get('code_files', []),
        }

    return base_context


def display_wizard_results(wizard, result: Dict[str, Any], verbose: bool):
    """Display wizard results in human-readable format"""

    # Issues
    issues = result.get('issues', [])
    if issues:
        print(f"\n{Colors.BOLD}Current Issues:{Colors.END}")
        for issue in issues:
            severity = issue.get('severity', 'info')
            marker = {
                'error': f"{Colors.RED}✗{Colors.END}",
                'warning': f"{Colors.YELLOW}⚠{Colors.END}",
                'info': f"{Colors.CYAN}ℹ{Colors.END}"
            }.get(severity, 'ℹ')

            print(f"  {marker} {issue.get('message', 'No message')}")
            if verbose and 'suggestion' in issue:
                print(f"    → {issue['suggestion']}")

    # Predictions (Level 4!)
    predictions = result.get('predictions', [])
    if predictions:
        print(f"\n{Colors.BOLD}Anticipatory Alerts (Level 4):{Colors.END}")
        for pred in predictions:
            print(f"\n  {Colors.YELLOW}[ALERT]{Colors.END} {pred.get('alert', '')}")

            if verbose:
                if 'reasoning' in pred:
                    print(f"    Reasoning: {pred['reasoning']}")
                if 'personal_experience' in pred:
                    print(f"    {Colors.CYAN}Experience:{Colors.END} {pred['personal_experience']}")

            print(f"    {Colors.BOLD}Prevention steps:{Colors.END}")
            for i, step in enumerate(pred.get('prevention_steps', [])[:3], 1):
                print(f"      {i}. {step}")

    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        for rec in recommendations[:5]:  # Top 5
            if rec.strip():
                print(f"  • {rec}")

    # Confidence
    confidence = result.get('confidence', 0)
    print(f"\n{Colors.BOLD}Analysis Confidence:{Colors.END} {confidence:.0%}")


def print_summary(all_results: Dict[str, Dict[str, Any]]):
    """Print overall summary of analysis"""
    print_header("Analysis Summary")

    total_issues = sum(len(r.get('issues', [])) for r in all_results.values())
    total_predictions = sum(len(r.get('predictions', [])) for r in all_results.values())

    print(f"\nWizards run: {len(all_results)}")
    print(f"Current issues found: {total_issues}")
    print(f"Anticipatory alerts: {total_predictions}")

    high_impact = sum(
        1 for r in all_results.values()
        for p in r.get('predictions', [])
        if p.get('impact') == 'high'
    )

    if high_impact > 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}High-impact alerts: {high_impact}{Colors.END}")
        print("Review these immediately to prevent future issues.")

    # Extract patterns
    all_patterns = []
    for result in all_results.values():
        all_patterns.extend(result.get('patterns', []))

    if all_patterns:
        print(f"\nCross-domain patterns discovered: {len(all_patterns)}")
        print("These patterns can be applied to other domains (Level 5 Systems Empathy)")


def list_wizards():
    """List available wizards"""
    print_header("Available AI Development Wizards")

    registry = get_global_registry()
    software_plugin = registry.get_plugin('software')

    if not software_plugin:
        print_error("Software plugin not found")
        return 1

    wizards = software_plugin.list_wizards()

    for wizard_id in wizards:
        info = software_plugin.get_wizard_info(wizard_id)
        if info:
            print(f"\n{Colors.BOLD}{wizard_id}{Colors.END}")
            print(f"  Name: {info['name']}")
            print(f"  Level: {info['empathy_level']} ({'Anticipatory' if info['empathy_level'] == 4 else 'Other'})")
            print(f"  Category: {info.get('category', 'N/A')}")

    return 0


def wizard_info(wizard_id: str):
    """Show detailed info about a wizard"""
    registry = get_global_registry()
    software_plugin = registry.get_plugin('software')

    if not software_plugin:
        print_error("Software plugin not found")
        return 1

    info = software_plugin.get_wizard_info(wizard_id)
    if not info:
        print_error(f"Wizard '{wizard_id}' not found")
        return 1

    print_header(f"Wizard: {info['name']}")
    print(f"ID: {wizard_id}")
    print(f"Domain: {info['domain']}")
    print(f"Empathy Level: {info['empathy_level']}")
    print(f"Category: {info.get('category', 'N/A')}")

    print(f"\n{Colors.BOLD}Required Context:{Colors.END}")
    for ctx in info.get('required_context', []):
        print(f"  • {ctx}")

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Empathy Framework - AI Development Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  empathy-software analyze /path/to/project
  empathy-software analyze . --wizards prompt_engineering,context_window
  empathy-software analyze . --verbose --output json
  empathy-software list-wizards
  empathy-software wizard-info prompt_engineering
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a project')
    analyze_parser.add_argument('path', help='Path to project')
    analyze_parser.add_argument(
        '--wizards',
        help='Comma-separated list of wizards to run',
        default=None
    )
    analyze_parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    analyze_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )

    # List wizards command
    subparsers.add_parser('list-wizards', help='List available wizards')

    # Wizard info command
    info_parser = subparsers.add_parser('wizard-info', help='Show wizard details')
    info_parser.add_argument('wizard_id', help='Wizard identifier')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == 'analyze':
        wizard_names = None
        if args.wizards:
            wizard_names = [w.strip() for w in args.wizards.split(',')]

        return asyncio.run(analyze_project(
            args.path,
            wizard_names=wizard_names,
            output_format=args.output,
            verbose=args.verbose
        ))

    elif args.command == 'list-wizards':
        return list_wizards()

    elif args.command == 'wizard-info':
        return wizard_info(args.wizard_id)

    return 0


if __name__ == '__main__':
    sys.exit(main())
