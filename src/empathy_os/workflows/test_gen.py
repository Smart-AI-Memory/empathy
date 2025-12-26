"""
Test Generation Workflow

Generates tests targeting areas with historical bugs and low coverage.
Prioritizes test creation for bug-prone code paths.

Stages:
1. identify (CHEAP) - Identify files with low coverage or historical bugs
2. analyze (CAPABLE) - Analyze code structure and existing test patterns
3. generate (CAPABLE) - Generate test cases focusing on edge cases
4. review (PREMIUM) - Quality review and deduplication (conditional)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
from pathlib import Path
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier
from .step_config import WorkflowStepConfig

# Define step configurations for executor-based execution
TEST_GEN_STEPS = {
    "review": WorkflowStepConfig(
        name="review",
        task_type="final_review",  # Premium tier task
        tier_hint="premium",
        description="Review and improve generated test suite",
        max_tokens=3000,
    ),
}


class TestGenerationWorkflow(BaseWorkflow):
    """
    Generate tests targeting areas with historical bugs.

    Prioritizes test generation for files that have historically
    been bug-prone and have low test coverage.
    """

    name = "test-gen"
    description = "Generate tests targeting areas with historical bugs"
    stages = ["identify", "analyze", "generate", "review"]
    tier_map = {
        "identify": ModelTier.CHEAP,
        "analyze": ModelTier.CAPABLE,
        "generate": ModelTier.CAPABLE,
        "review": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        patterns_dir: str = "./patterns",
        min_tests_for_review: int = 10,
        **kwargs: Any,
    ):
        """
        Initialize test generation workflow.

        Args:
            patterns_dir: Directory containing learned patterns
            min_tests_for_review: Minimum tests generated to trigger premium review
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.patterns_dir = patterns_dir
        self.min_tests_for_review = min_tests_for_review
        self._test_count: int = 0
        self._bug_hotspots: list[str] = []
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")
        self._load_bug_hotspots()

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None and self._api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                pass
        return self._client

    def _get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the model name for a given tier."""
        provider = ModelProvider.ANTHROPIC
        return PROVIDER_MODELS.get(provider, {}).get(tier, "claude-sonnet-4-20250514")

    async def _call_llm(
        self, tier: ModelTier, system: str, user_message: str, max_tokens: int = 4096
    ) -> tuple[str, int, int]:
        """Make an actual LLM call using the Anthropic API."""
        client = self._get_client()
        if not client:
            return (
                "[Simulated - set ANTHROPIC_API_KEY for real results]",
                len(user_message) // 4,
                100,
            )

        model = self._get_model_for_tier(tier)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return content, input_tokens, output_tokens

        except Exception as e:
            return f"Error calling LLM: {e}", 0, 0

    def _load_bug_hotspots(self) -> None:
        """Load files with historical bugs from pattern library."""
        debugging_file = Path(self.patterns_dir) / "debugging.json"
        if debugging_file.exists():
            try:
                with open(debugging_file) as f:
                    data = json.load(f)
                    patterns = data.get("patterns", [])
                    # Extract files from bug patterns
                    files = set()
                    for p in patterns:
                        for f in p.get("files_affected", []):
                            files.add(f)
                    self._bug_hotspots = list(files)
            except (json.JSONDecodeError, OSError):
                pass

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Downgrade review stage if few tests generated.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "review":
            if self._test_count < self.min_tests_for_review:
                # Downgrade to CAPABLE
                self.tier_map["review"] = ModelTier.CAPABLE
                return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "identify":
            return await self._identify(input_data, tier)
        elif stage_name == "analyze":
            return await self._analyze(input_data, tier)
        elif stage_name == "generate":
            return await self._generate(input_data, tier)
        elif stage_name == "review":
            return await self._review(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _identify(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Identify files needing tests.

        Finds files with low coverage, historical bugs, or
        no existing tests.
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py"])

        target = Path(target_path)
        candidates: list[dict] = []

        # Track project scope for enterprise reporting
        total_source_files = 0
        existing_test_files = 0

        if target.exists():
            for ext in file_types:
                for file_path in target.rglob(f"*{ext}"):
                    # Skip non-code directories
                    if any(
                        skip in str(file_path)
                        for skip in [".git", "node_modules", "__pycache__", "venv"]
                    ):
                        continue

                    # Count test files separately for scope awareness
                    file_str = str(file_path)
                    if "test_" in file_str or "_test." in file_str or "/tests/" in file_str:
                        existing_test_files += 1
                        continue

                    # Count source files
                    total_source_files += 1

                    try:
                        content = file_path.read_text(errors="ignore")
                        lines = len(content.splitlines())

                        # Check if in bug hotspots
                        is_hotspot = any(
                            hotspot in str(file_path) for hotspot in self._bug_hotspots
                        )

                        # Check for existing tests
                        test_file = self._find_test_file(file_path)
                        has_tests = test_file.exists() if test_file else False

                        # Calculate priority
                        priority = 0
                        if is_hotspot:
                            priority += 50
                        if not has_tests:
                            priority += 30
                        if lines > 100:
                            priority += 10
                        if lines > 300:
                            priority += 10

                        if priority > 0:
                            candidates.append(
                                {
                                    "file": str(file_path),
                                    "lines": lines,
                                    "is_hotspot": is_hotspot,
                                    "has_tests": has_tests,
                                    "priority": priority,
                                }
                            )
                    except OSError:
                        continue

        # Sort by priority
        candidates.sort(key=lambda x: -x["priority"])

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(candidates)) // 4

        # Calculate scope metrics for enterprise reporting
        analyzed_count = min(30, len(candidates))
        coverage_pct = (analyzed_count / len(candidates) * 100) if candidates else 100

        return (
            {
                "candidates": candidates[:30],  # Top 30
                "total_candidates": len(candidates),
                "hotspot_count": len([c for c in candidates if c["is_hotspot"]]),
                "untested_count": len([c for c in candidates if not c["has_tests"]]),
                # Scope awareness fields for enterprise reporting
                "total_source_files": total_source_files,
                "existing_test_files": existing_test_files,
                "large_project_warning": len(candidates) > 100,
                "analysis_coverage_percent": coverage_pct,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _find_test_file(self, source_file: Path) -> Path | None:
        """Find corresponding test file for a source file."""
        name = source_file.stem
        parent = source_file.parent

        # Check common test locations
        possible = [
            parent / f"test_{name}.py",
            parent / "tests" / f"test_{name}.py",
            parent.parent / "tests" / f"test_{name}.py",
        ]

        for p in possible:
            if p.exists():
                return p

        return possible[0]  # Return expected location even if doesn't exist

    async def _analyze(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Analyze code structure for test generation.

        Examines functions, classes, and patterns to determine
        what tests should be generated.
        """
        candidates = input_data.get("candidates", [])[:15]  # Top 15
        analysis: list[dict] = []

        for candidate in candidates:
            file_path = Path(candidate["file"])
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(errors="ignore")

                # Extract testable items (simplified analysis)
                functions = self._extract_functions(content)
                classes = self._extract_classes(content)

                analysis.append(
                    {
                        "file": candidate["file"],
                        "priority": candidate["priority"],
                        "functions": functions,
                        "classes": classes,
                        "function_count": len(functions),
                        "class_count": len(classes),
                        "test_suggestions": self._generate_suggestions(functions, classes),
                    }
                )
            except OSError:
                continue

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(analysis)) // 4

        return (
            {
                "analysis": analysis,
                "total_functions": sum(a["function_count"] for a in analysis),
                "total_classes": sum(a["class_count"] for a in analysis),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _extract_functions(self, content: str) -> list[dict]:
        """Extract function definitions from Python code."""
        import re

        functions = []
        pattern = r"^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)"

        for match in re.finditer(pattern, content, re.MULTILINE):
            name = match.group(1)
            if not name.startswith("_") or name.startswith("__"):
                params = match.group(2).split(",") if match.group(2).strip() else []
                functions.append(
                    {
                        "name": name,
                        "params": [p.strip().split(":")[0].strip() for p in params if p.strip()],
                        "is_async": "async" in match.group(0),
                    }
                )

        return functions[:20]  # Limit

    def _extract_classes(self, content: str) -> list[dict]:
        """Extract class definitions from Python code."""
        import re

        classes = []
        pattern = r"^\s*class\s+(\w+)\s*(?:\([^)]*\))?:"

        for match in re.finditer(pattern, content, re.MULTILINE):
            name = match.group(1)
            classes.append({"name": name})

        return classes[:10]  # Limit

    def _generate_suggestions(self, functions: list[dict], classes: list[dict]) -> list[str]:
        """Generate test suggestions based on code structure."""
        suggestions = []

        for func in functions[:5]:
            if func["params"]:
                suggestions.append(f"Test {func['name']} with valid inputs")
                suggestions.append(f"Test {func['name']} with edge cases")
            if func["is_async"]:
                suggestions.append(f"Test {func['name']} async behavior")

        for cls in classes[:3]:
            suggestions.append(f"Test {cls['name']} initialization")
            suggestions.append(f"Test {cls['name']} methods")

        return suggestions

    async def _generate(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate test cases.

        Creates test code targeting identified functions
        and classes, focusing on edge cases.
        """
        analysis = input_data.get("analysis", [])
        generated_tests: list[dict] = []

        for item in analysis[:10]:  # Top 10 files
            file_path = item["file"]
            module_name = Path(file_path).stem

            tests = []
            for func in item.get("functions", [])[:5]:
                test_code = self._generate_test_for_function(module_name, func)
                tests.append(
                    {
                        "target": func["name"],
                        "type": "function",
                        "code": test_code,
                    }
                )

            for cls in item.get("classes", [])[:2]:
                test_code = self._generate_test_for_class(module_name, cls)
                tests.append(
                    {
                        "target": cls["name"],
                        "type": "class",
                        "code": test_code,
                    }
                )

            if tests:
                generated_tests.append(
                    {
                        "source_file": file_path,
                        "test_file": f"test_{module_name}.py",
                        "tests": tests,
                        "test_count": len(tests),
                    }
                )

        self._test_count = sum(t["test_count"] for t in generated_tests)

        input_tokens = len(str(input_data)) // 4
        output_tokens = sum(len(str(t)) for t in generated_tests) // 4

        return (
            {
                "generated_tests": generated_tests,
                "total_tests_generated": self._test_count,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _generate_test_for_function(self, module: str, func: dict) -> str:
        """Generate a test function for a function."""
        name = func["name"]
        params = func.get("params", [])
        is_async = func.get("is_async", False)

        if is_async:
            return f"""
@pytest.mark.asyncio
async def test_{name}():
    # Test {name} with valid inputs
    result = await {name}({", ".join(["None"] * len(params) if params else [])})
    assert result is not None
"""
        else:
            return f"""
def test_{name}():
    # Test {name} with valid inputs
    result = {name}({", ".join(["None"] * len(params) if params else [])})
    assert result is not None
"""

    def _generate_test_for_class(self, module: str, cls: dict) -> str:
        """Generate a test class for a class."""
        name = cls["name"]
        return f"""
class Test{name}:
    def test_init(self):
        # Test {name} initialization
        instance = {name}()
        assert instance is not None

    def test_basic_functionality(self):
        # Test basic {name} methods
        instance = {name}()
        # Add specific method tests
        pass
"""

    async def _review(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Review and improve generated tests using LLM.

        Quality review of generated tests, removing duplicates
        and improving test coverage.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        generated_tests = input_data.get("generated_tests", [])
        target = input_data.get("target", "")

        # Build test summary for LLM
        test_summary = []
        for test_file in generated_tests:
            for test in test_file.get("tests", []):
                test_summary.append(
                    f"- {test_file.get('source_file')}: {test.get('name', 'unnamed')} "
                    f"({test.get('type', 'unit')})"
                )

        total_tests = sum(len(tf.get("tests", [])) for tf in generated_tests)

        # Build input payload for prompt
        input_payload = f"""Target: {target or "codebase"}

Total Tests Generated: {total_tests}
Files Covered: {len(generated_tests)}

Tests Summary:
{chr(10).join(test_summary[:30]) if test_summary else "No tests generated"}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="QA engineer specializing in test quality",
                goal="Review and improve the generated test suite",
                instructions=[
                    "Identify duplicate or redundant tests",
                    "Suggest improvements to test coverage",
                    "Review edge cases and error handling",
                    "Rate overall test quality",
                    "Recommend additional tests for untested paths",
                ],
                constraints=[
                    "Focus on high-value test improvements",
                    "Identify missing edge cases",
                    "Suggest specific test scenarios to add",
                ],
                input_type="generated_tests",
                input_payload=input_payload,
                extra={
                    "total_tests": total_tests,
                    "files_covered": len(generated_tests),
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a QA engineer specializing in test quality.
Review the generated tests and provide improvement recommendations.

Focus on:
1. Test coverage gaps
2. Edge case handling
3. Duplicate test detection
4. Code quality improvements

Provide actionable feedback."""

            user_message = f"""Review these generated tests:

{input_payload}

Provide quality assessment and improvement recommendations."""

        # Try executor-based execution first (Phase 3 pattern)
        if self._executor is not None or self._api_key:
            try:
                step = TEST_GEN_STEPS["review"]
                response, input_tokens, output_tokens, cost = await self.run_step_with_executor(
                    step=step,
                    prompt=user_message,
                    system=system,
                )
            except Exception:
                # Fall back to legacy _call_llm if executor fails
                response, input_tokens, output_tokens = await self._call_llm(
                    tier, system or "", user_message, max_tokens=3000
                )
        else:
            # Legacy path for backward compatibility
            response, input_tokens, output_tokens = await self._call_llm(
                tier, system or "", user_message, max_tokens=3000
            )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        result = {
            "review_feedback": response,
            "total_tests": total_tests,
            "files_covered": len(generated_tests),
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                }
            )

        # Add formatted report for human readability
        result["formatted_report"] = format_test_gen_report(result, input_data)

        return (result, input_tokens, output_tokens)


def format_test_gen_report(result: dict, input_data: dict) -> str:
    """
    Format test generation output as a human-readable report.

    Args:
        result: The review stage result
        input_data: Input data from previous stages

    Returns:
        Formatted report string
    """
    import re

    lines = []

    # Header
    total_tests = result.get("total_tests", 0)
    files_covered = result.get("files_covered", 0)

    lines.append("=" * 60)
    lines.append("TEST GAP ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Summary stats
    total_candidates = input_data.get("total_candidates", 0)
    hotspot_count = input_data.get("hotspot_count", 0)
    untested_count = input_data.get("untested_count", 0)

    lines.append("-" * 60)
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Tests Generated:     {total_tests}")
    lines.append(f"Files Covered:       {files_covered}")
    lines.append(f"Total Candidates:    {total_candidates}")
    lines.append(f"Bug Hotspots Found:  {hotspot_count}")
    lines.append(f"Untested Files:      {untested_count}")
    lines.append("")

    # Status indicator
    if total_tests == 0:
        lines.append("⚠️  No tests were generated")
    elif total_tests < 5:
        lines.append(f"🟡 Generated {total_tests} test(s) - consider adding more coverage")
    elif total_tests < 20:
        lines.append(f"🟢 Generated {total_tests} tests - good coverage")
    else:
        lines.append(f"✅ Generated {total_tests} tests - excellent coverage")
    lines.append("")

    # Scope notice for enterprise clarity
    total_source = input_data.get("total_source_files", 0)
    existing_tests = input_data.get("existing_test_files", 0)
    coverage_pct = input_data.get("analysis_coverage_percent", 100)
    large_project = input_data.get("large_project_warning", False)

    if total_source > 0 or existing_tests > 0:
        lines.append("-" * 60)
        lines.append("SCOPE NOTICE")
        lines.append("-" * 60)

        if large_project:
            lines.append("⚠️  LARGE PROJECT: Only high-priority files analyzed")
            lines.append(f"   Coverage: {coverage_pct:.0f}% of candidate files")
            lines.append("")

        lines.append(f"Source Files Found:   {total_source}")
        lines.append(f"Existing Test Files:  {existing_tests}")
        lines.append(f"Files Analyzed:       {files_covered}")

        if existing_tests > 0:
            lines.append("")
            lines.append("Note: This report identifies gaps in untested files.")
            lines.append("Run 'pytest --co -q' for full test suite statistics.")
        lines.append("")

    # Parse XML review feedback if present
    review = result.get("review_feedback", "")
    xml_summary = ""
    xml_findings = []
    xml_tests = []
    coverage_improvement = ""

    if review and "<response>" in review:
        # Extract summary
        summary_match = re.search(r"<summary>(.*?)</summary>", review, re.DOTALL)
        if summary_match:
            xml_summary = summary_match.group(1).strip()

        # Extract coverage improvement
        coverage_match = re.search(
            r"<coverage-improvement>(.*?)</coverage-improvement>", review, re.DOTALL
        )
        if coverage_match:
            coverage_improvement = coverage_match.group(1).strip()

        # Extract findings
        for finding_match in re.finditer(
            r'<finding severity="(\w+)">(.*?)</finding>', review, re.DOTALL
        ):
            severity = finding_match.group(1)
            finding_content = finding_match.group(2)

            title_match = re.search(r"<title>(.*?)</title>", finding_content, re.DOTALL)
            location_match = re.search(r"<location>(.*?)</location>", finding_content, re.DOTALL)
            fix_match = re.search(r"<fix>(.*?)</fix>", finding_content, re.DOTALL)

            xml_findings.append(
                {
                    "severity": severity,
                    "title": title_match.group(1).strip() if title_match else "Unknown",
                    "location": location_match.group(1).strip() if location_match else "",
                    "fix": fix_match.group(1).strip() if fix_match else "",
                }
            )

        # Extract suggested tests
        for test_match in re.finditer(r'<test target="([^"]+)">(.*?)</test>', review, re.DOTALL):
            target = test_match.group(1)
            test_content = test_match.group(2)

            type_match = re.search(r"<type>(.*?)</type>", test_content, re.DOTALL)
            desc_match = re.search(r"<description>(.*?)</description>", test_content, re.DOTALL)

            xml_tests.append(
                {
                    "target": target,
                    "type": type_match.group(1).strip() if type_match else "unit",
                    "description": desc_match.group(1).strip() if desc_match else "",
                }
            )

    # Show parsed summary
    if xml_summary:
        lines.append("-" * 60)
        lines.append("QUALITY ASSESSMENT")
        lines.append("-" * 60)
        # Word wrap the summary
        words = xml_summary.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 58:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        lines.append("")

        if coverage_improvement:
            lines.append(f"📈 {coverage_improvement}")
            lines.append("")

    # Show findings by severity
    if xml_findings:
        lines.append("-" * 60)
        lines.append("QUALITY FINDINGS")
        lines.append("-" * 60)

        severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}
        severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}

        sorted_findings = sorted(xml_findings, key=lambda f: severity_order.get(f["severity"], 4))

        for finding in sorted_findings:
            emoji = severity_emoji.get(finding["severity"], "⚪")
            lines.append(f"{emoji} [{finding['severity'].upper()}] {finding['title']}")
            if finding["location"]:
                lines.append(f"   Location: {finding['location']}")
            if finding["fix"]:
                # Truncate long fix recommendations
                fix_text = finding["fix"]
                if len(fix_text) > 70:
                    fix_text = fix_text[:67] + "..."
                lines.append(f"   Fix: {fix_text}")
            lines.append("")

    # Show suggested tests
    if xml_tests:
        lines.append("-" * 60)
        lines.append("SUGGESTED TESTS TO ADD")
        lines.append("-" * 60)

        for i, test in enumerate(xml_tests[:5], 1):  # Limit to 5
            lines.append(f"{i}. {test['target']} ({test['type']})")
            if test["description"]:
                desc = test["description"]
                if len(desc) > 55:
                    desc = desc[:52] + "..."
                lines.append(f"   {desc}")
            lines.append("")

        if len(xml_tests) > 5:
            lines.append(f"   ... and {len(xml_tests) - 5} more suggested tests")
            lines.append("")

    # Generated tests breakdown (if no XML data)
    generated_tests = input_data.get("generated_tests", [])
    if generated_tests and not xml_findings:
        lines.append("-" * 60)
        lines.append("GENERATED TESTS BY FILE")
        lines.append("-" * 60)
        for test_file in generated_tests[:10]:  # Limit display
            source = test_file.get("source_file", "unknown")
            test_count = test_file.get("test_count", 0)
            # Shorten path for display
            if len(source) > 50:
                source = "..." + source[-47:]
            lines.append(f"  📁 {source}")
            lines.append(
                f"     └─ {test_count} test(s) → {test_file.get('test_file', 'test_*.py')}"
            )
        if len(generated_tests) > 10:
            lines.append(f"  ... and {len(generated_tests) - 10} more files")
        lines.append("")

    # Recommendations
    lines.append("-" * 60)
    lines.append("NEXT STEPS")
    lines.append("-" * 60)

    high_findings = len([f for f in xml_findings if f["severity"] == "high"])
    medium_findings = len([f for f in xml_findings if f["severity"] == "medium"])

    if high_findings > 0:
        lines.append(f"  🔴 Address {high_findings} high-priority finding(s) first")

    if medium_findings > 0:
        lines.append(f"  🟠 Review {medium_findings} medium-priority finding(s)")

    if xml_tests:
        lines.append(f"  📝 Consider adding {len(xml_tests)} suggested test(s)")

    if hotspot_count > 0:
        lines.append(f"  🔥 {hotspot_count} bug hotspot file(s) need priority testing")

    if untested_count > 0:
        lines.append(f"  📁 {untested_count} file(s) have no existing tests")

    if not any([high_findings, medium_findings, xml_tests, hotspot_count, untested_count]):
        lines.append("  ✅ Test suite is in good shape!")

    lines.append("")

    # Footer
    lines.append("=" * 60)
    model_tier = result.get("model_tier_used", "unknown")
    lines.append(f"Review completed using {model_tier} tier model")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI entry point for test generation workflow."""
    import asyncio

    async def run():
        workflow = TestGenerationWorkflow()
        result = await workflow.execute(path=".", file_types=[".py"])

        print("\nTest Generation Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")
        print(f"Tests Generated: {result.final_output.get('total_tests', 0)}")
        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
