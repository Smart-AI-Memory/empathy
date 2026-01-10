"""Test Execution and Coverage Tracking Utilities for Tier 1 Automation.

Provides explicit opt-in utilities for tracking test executions and coverage metrics.
Use these functions when you want to track test/coverage data for Tier 1 monitoring.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
import shlex
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET  # noqa: S405

# Import Element for type hints only (defusedxml doesn't expose it)
if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

from empathy_os.models import CoverageRecord, TestExecutionRecord, get_telemetry_store

logger = logging.getLogger(__name__)


def run_tests_with_tracking(
    test_suite: str = "unit",
    test_files: list[str] | None = None,
    command: str | None = None,
    workflow_id: str | None = None,
    triggered_by: str = "manual",
) -> TestExecutionRecord:
    """Run tests with explicit tracking (opt-in for Tier 1 monitoring).

    Args:
        test_suite: Test suite name (unit, integration, e2e, all)
        test_files: Specific test files to run (optional)
        command: Custom test command (defaults to pytest)
        workflow_id: Optional workflow ID to link this execution
        triggered_by: Who/what triggered this (manual, workflow, ci, pre_commit)

    Returns:
        TestExecutionRecord with execution results

    Example:
        >>> from empathy_os.workflows.test_runner import run_tests_with_tracking
        >>> result = run_tests_with_tracking(
        ...     test_suite="unit",
        ...     test_files=["tests/unit/test_config.py"],
        ... )
        >>> print(f"Tests passed: {result.success}")

    """
    execution_id = f"test-{uuid.uuid4()}"
    timestamp = datetime.utcnow().isoformat() + "Z"
    started_at = datetime.utcnow()

    # Build command
    if command is None:
        if test_files:
            files_str = " ".join(test_files)
            command = f"pytest {files_str} -v --tb=short"
        else:
            if test_suite == "all":
                command = "pytest tests/ -v --tb=short"
            else:
                command = f"pytest tests/{test_suite}/ -v --tb=short"

    # Determine working directory
    working_directory = str(Path.cwd())

    # Run tests
    logger.info(f"Running tests: {command}")
    try:
        # Use shlex.split to safely parse command without shell=True
        cmd_args = shlex.split(command)
        result = subprocess.run(
            cmd_args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        # Parse pytest output for test counts
        output = result.stdout + result.stderr
        total_tests, passed, failed, skipped, errors = _parse_pytest_output(output)

        success = result.returncode == 0
        exit_code = result.returncode

        # Parse failures from output
        failed_tests = _parse_pytest_failures(output) if failed > 0 or errors > 0 else []

    except subprocess.TimeoutExpired:
        logger.error("Test execution timed out after 600 seconds")
        total_tests, passed, failed, skipped, errors = 0, 0, 0, 0, 1
        success = False
        exit_code = 124  # Timeout exit code
        failed_tests = [{"name": "timeout", "file": "unknown", "error": "Test execution timed out"}]

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        total_tests, passed, failed, skipped, errors = 0, 0, 0, 0, 1
        success = False
        exit_code = 1
        failed_tests = [{"name": "execution_error", "file": "unknown", "error": str(e)}]

    # Calculate duration
    completed_at = datetime.utcnow()
    duration_seconds = (completed_at - started_at).total_seconds()

    # Create test execution record
    record = TestExecutionRecord(
        execution_id=execution_id,
        timestamp=timestamp,
        test_suite=test_suite,
        test_files=test_files or [],
        triggered_by=triggered_by,
        command=command,
        working_directory=working_directory,
        duration_seconds=duration_seconds,
        total_tests=total_tests,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        success=success,
        exit_code=exit_code,
        failed_tests=failed_tests,
        workflow_id=workflow_id,
    )

    # Log to telemetry store
    try:
        store = get_telemetry_store()
        store.log_test_execution(record)
        logger.info(f"Test execution tracked: {execution_id}")
    except Exception as e:
        logger.warning(f"Failed to log test execution: {e}")

    return record


def track_coverage(
    coverage_file: str = "coverage.xml",
    workflow_id: str | None = None,
) -> CoverageRecord:
    """Track test coverage from coverage.xml file (opt-in for Tier 1 monitoring).

    Args:
        coverage_file: Path to coverage.xml file
        workflow_id: Optional workflow ID to link this record

    Returns:
        CoverageRecord with coverage metrics

    Example:
        >>> from empathy_os.workflows.test_runner import track_coverage
        >>> coverage = track_coverage("coverage.xml")
        >>> print(f"Coverage: {coverage.overall_percentage:.1f}%")

    """
    record_id = f"cov-{uuid.uuid4()}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    coverage_path = Path(coverage_file)
    if not coverage_path.exists():
        raise FileNotFoundError(f"Coverage file not found: {coverage_file}")

    # Parse coverage.xml
    try:
        # Uses defusedxml when available (see imports), coverage.xml is from trusted pytest/coverage tools
        tree = ET.parse(coverage_path)  # nosec B314
        root = tree.getroot()

        # Get overall metrics
        lines_total = int(root.attrib.get("lines-valid", 0))
        lines_covered = int(root.attrib.get("lines-covered", 0))
        branches_total = int(root.attrib.get("branches-valid", 0))
        branches_covered = int(root.attrib.get("branches-covered", 0))

        if lines_total > 0:
            overall_percentage = (lines_covered / lines_total) * 100
        else:
            overall_percentage = 0.0

        # Get previous coverage if available
        previous_percentage = _get_previous_coverage()

        # Determine trend
        if previous_percentage is not None:
            change = overall_percentage - previous_percentage
            if change > 1.0:
                trend = "improving"
            elif change < -1.0:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Analyze files
        files_analyzed = _analyze_coverage_files(root)

        record = CoverageRecord(
            record_id=record_id,
            timestamp=timestamp,
            overall_percentage=overall_percentage,
            lines_total=lines_total,
            lines_covered=lines_covered,
            branches_total=branches_total,
            branches_covered=branches_covered,
            files_total=files_analyzed["total"],
            files_well_covered=files_analyzed["well_covered"],
            files_critical=files_analyzed["critical"],
            untested_files=files_analyzed["untested"],
            critical_gaps=files_analyzed["gaps"],
            previous_percentage=previous_percentage,
            trend=trend,
            coverage_format="xml",
            coverage_file=str(coverage_path),
            workflow_id=workflow_id,
        )

        # Log to telemetry store
        try:
            store = get_telemetry_store()
            store.log_coverage(record)
            logger.info(f"Coverage tracked: {record_id} ({overall_percentage:.1f}%)")
        except Exception as e:
            logger.warning(f"Failed to log coverage: {e}")

        return record

    except ET.ParseError as e:
        raise ValueError(f"Invalid coverage.xml format: {e}")


# Helper functions


def _parse_pytest_output(output: str) -> tuple[int, int, int, int, int]:
    """Parse pytest output for test counts.

    Returns:
        Tuple of (total_tests, passed, failed, skipped, errors)

    """
    import re

    # Look for pytest summary line like "5 passed, 2 failed, 1 skipped in 1.23s"
    match = re.search(r"(\d+)\s+passed", output)
    passed = int(match.group(1)) if match else 0

    match = re.search(r"(\d+)\s+failed", output)
    failed = int(match.group(1)) if match else 0

    match = re.search(r"(\d+)\s+skipped", output)
    skipped = int(match.group(1)) if match else 0

    match = re.search(r"(\d+)\s+error", output)
    errors = int(match.group(1)) if match else 0

    total_tests = passed + failed + skipped + errors

    return total_tests, passed, failed, skipped, errors


def _parse_pytest_failures(output: str) -> list[dict[str, str]]:
    """Parse pytest output for failure details.

    Returns:
        List of dicts with name, file, error, traceback

    """
    failures = []
    lines = output.split("\n")

    # Simple parser - looks for FAILED lines
    for line in lines:
        if "FAILED " in line:
            parts = line.split("::")
            if len(parts) >= 2:
                file_path = parts[0].replace("FAILED ", "").strip()
                test_name = parts[1].split()[0] if len(parts) > 1 else "unknown"

                failures.append({"name": test_name, "file": file_path, "error": "Test failed"})

    return failures[:10]  # Limit to 10 failures


def _get_previous_coverage() -> float | None:
    """Get previous coverage percentage from telemetry store.

    Returns:
        Previous coverage percentage or None

    """
    try:
        store = get_telemetry_store()
        records = store.get_coverage_history(limit=2)

        if len(records) >= 2:
            # Second-to-last record is the previous one
            return records[-2].overall_percentage
        elif len(records) == 1:
            return records[0].overall_percentage
        else:
            return None

    except Exception:
        return None


def _analyze_coverage_files(root: "Element") -> dict[str, Any]:
    """Analyze file-level coverage from XML.

    Returns:
        Dict with total, well_covered, critical, untested, gaps

    """
    files_total = 0
    files_well_covered = 0  # >= 80%
    files_critical = 0  # < 50%
    untested_files = []
    critical_gaps = []

    for package in root.findall(".//package"):
        for class_elem in package.findall("classes/class"):
            files_total += 1
            filename = class_elem.attrib.get("filename", "unknown")
            line_rate = float(class_elem.attrib.get("line-rate", 0))
            coverage_pct = line_rate * 100

            if coverage_pct >= 80:
                files_well_covered += 1
            elif coverage_pct < 50:
                files_critical += 1
                critical_gaps.append(
                    {"file": filename, "coverage": coverage_pct, "priority": "high"}
                )

            if coverage_pct == 0:
                untested_files.append(filename)

    return {
        "total": files_total,
        "well_covered": files_well_covered,
        "critical": files_critical,
        "untested": untested_files[:10],  # Limit to 10
        "gaps": critical_gaps[:10],  # Limit to 10
    }
