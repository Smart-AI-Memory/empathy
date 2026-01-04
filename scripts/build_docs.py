#!/usr/bin/env python3
"""Empathy Framework Documentation Builder

Builds documentation for multiple output targets:
1. PyPI/GitHub - Minimal docs for package distribution
2. Website - Full documentation for ReadTheDocs
3. eBook - PDF/ePub book format

Usage:
    python scripts/build_docs.py [target]

Targets:
    all      - Build all outputs (default)
    pypi     - Build PyPI/GitHub minimal docs
    website  - Build full website docs
    ebook    - Build PDF/ePub book
    clean    - Remove all build artifacts
    serve    - Serve website docs locally
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Project root (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
SITE_DIR = PROJECT_ROOT / "site"


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log(msg: str, color: str = Colors.BLUE) -> None:
    """Print colored log message."""
    print(f"{color}{Colors.BOLD}==>{Colors.ENDC} {msg}")


def log_success(msg: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {msg}")


def log_error(msg: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.ENDC} {msg}")


def run_command(cmd: list[str], env: dict | None = None) -> bool:
    """Run a command and return success status."""
    try:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT, env=full_env)
        return True
    except subprocess.CalledProcessError:
        log_error(f"Command failed: {' '.join(cmd)}")
        return False
    except FileNotFoundError:
        log_error(f"Command not found: {cmd[0]}")
        return False


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    log("Checking dependencies...")

    # Map package names to their import names
    required = {
        "mkdocs": "mkdocs",
        "mkdocs-material": "material",  # imports as 'material'
    }
    missing = []

    for pkg, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)

    if missing:
        log_error(f"Missing dependencies: {', '.join(missing)}")
        log("Install with: pip install -e '.[docs]'")
        return False

    log_success("All dependencies available")
    return True


def clean() -> None:
    """Remove all build artifacts."""
    log("Cleaning build artifacts...")

    dirs_to_clean = [DIST_DIR, SITE_DIR]
    for d in dirs_to_clean:
        if d.exists():
            shutil.rmtree(d)
            log_success(f"Removed {d.relative_to(PROJECT_ROOT)}")

    log_success("Clean complete")


def build_pypi() -> bool:
    """Build minimal docs for PyPI/GitHub."""
    log("Building PyPI/GitHub documentation...", Colors.HEADER)

    output_dir = DIST_DIR / "docs-pypi"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = run_command(["mkdocs", "build", "-f", "mkdocs-pypi.yml", "-d", str(output_dir)])

    if success:
        log_success(f"PyPI docs built: {output_dir.relative_to(PROJECT_ROOT)}")
    return success


def build_website() -> bool:
    """Build full website documentation."""
    log("Building website documentation...", Colors.HEADER)

    output_dir = DIST_DIR / "docs-website"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = run_command(["mkdocs", "build", "-f", "mkdocs.yml", "-d", str(output_dir)])

    if success:
        log_success(f"Website docs built: {output_dir.relative_to(PROJECT_ROOT)}")
    return success


def build_ebook() -> bool:
    """Build PDF/ePub book."""
    log("Building eBook (PDF)...", Colors.HEADER)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    output_dir = DIST_DIR / "docs-ebook"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Enable PDF export via environment variable
    success = run_command(
        ["mkdocs", "build", "-f", "mkdocs-ebook.yml", "-d", str(output_dir)],
        env={"ENABLE_PDF_EXPORT": "1"},
    )

    if success:
        pdf_path = DIST_DIR / "empathy-book.pdf"
        if pdf_path.exists():
            log_success(f"eBook PDF built: {pdf_path.relative_to(PROJECT_ROOT)}")
        else:
            log_success(f"eBook HTML built: {output_dir.relative_to(PROJECT_ROOT)}")
            log("Note: PDF generation requires mkdocs-with-pdf plugin")
            log("Install with: pip install mkdocs-with-pdf")
    return success


def serve_website() -> None:
    """Serve website docs locally for development."""
    log("Starting local documentation server...", Colors.HEADER)
    log("Press Ctrl+C to stop")

    run_command(["mkdocs", "serve", "-f", "mkdocs.yml"])


def build_all() -> bool:
    """Build all documentation outputs."""
    log("Building all documentation outputs...", Colors.HEADER)

    results = {
        "PyPI/GitHub": build_pypi(),
        "Website": build_website(),
        "eBook": build_ebook(),
    }

    print()
    log("Build Summary:", Colors.HEADER)
    print("-" * 40)

    all_success = True
    for name, success in results.items():
        status = (
            f"{Colors.GREEN}✓ SUCCESS{Colors.ENDC}"
            if success
            else f"{Colors.RED}✗ FAILED{Colors.ENDC}"
        )
        print(f"  {name}: {status}")
        if not success:
            all_success = False

    print("-" * 40)

    if all_success:
        print()
        log("All outputs built successfully!", Colors.GREEN)
        print()
        print("Output locations:")
        print("  PyPI/GitHub:  dist/docs-pypi/")
        print("  Website:      dist/docs-website/")
        print("  eBook:        dist/docs-ebook/")
        print("  PDF:          dist/empathy-book.pdf (if plugin installed)")

    return all_success


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Empathy Framework documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["all", "pypi", "website", "ebook", "clean", "serve"],
        help="Build target (default: all)",
    )
    parser.add_argument("--skip-check", action="store_true", help="Skip dependency check")

    args = parser.parse_args()

    print()
    print(f"{Colors.BOLD}Empathy Framework Documentation Builder{Colors.ENDC}")
    print("=" * 40)
    print()

    os.chdir(PROJECT_ROOT)

    if args.target == "clean":
        clean()
        return 0

    if args.target == "serve":
        serve_website()
        return 0

    if not args.skip_check and not check_dependencies():
        return 1

    targets = {
        "all": build_all,
        "pypi": build_pypi,
        "website": build_website,
        "ebook": build_ebook,
    }

    success = targets[args.target]()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
