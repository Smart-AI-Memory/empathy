"""
Context Collector
Gathers IDE context (current file, git status, project structure) for wizards

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ContextCollector:
    """Collects context from IDE environment"""

    async def collect(self, document_uri: str, position: dict[str, int] | None = None) -> str:
        """
        Collect context for a single file

        Args:
            document_uri: File URI (file:///path/to/file.py)
            position: Optional cursor position {"line": 10, "character": 5}

        Returns:
            Rich context string for wizards
        """
        file_path = self._uri_to_path(document_uri)

        # Collect various context elements
        file_content = self._read_file(file_path)
        git_info = self._get_git_info(file_path)
        project_structure = self._get_project_structure(file_path)
        dependencies = self._get_dependencies(file_path)

        # Build context string
        context = f"""
File: {file_path}
Language: {self._detect_language(file_path)}

=== Git Information ===
Branch: {git_info['branch']}
Status: {git_info['status']}
Recent commits: {git_info['recent_commits']}

=== Project Structure ===
{project_structure}

=== Dependencies ===
{dependencies}

=== File Content ===
{file_content}
"""

        if position:
            context += f"\n=== Cursor Position ===\nLine {position['line']}, Character {position['character']}\n"

        return context

    async def collect_multi_file(self, document_uris: list[str]) -> str:
        """Collect context for multiple files"""
        contexts = []
        for uri in document_uris:
            ctx = await self.collect(uri)
            contexts.append(ctx)

        return "\n\n=== NEXT FILE ===\n\n".join(contexts)

    def _uri_to_path(self, uri: str) -> Path:
        """Convert file:// URI to filesystem path"""
        if uri.startswith("file://"):
            parsed = urlparse(uri)
            path = parsed.path
            # Handle Windows paths
            if os.name == "nt" and path.startswith("/"):
                path = path[1:]
            return Path(path)
        return Path(uri)

    def _read_file(self, path: Path) -> str:
        """Read file contents"""
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            # Limit to first 10000 characters to avoid huge context
            if len(content) > 10000:
                content = content[:10000] + "\n\n[... truncated ...]"
            return content
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return f"[Error reading file: {e}]"

    def _get_git_info(self, file_path: Path) -> dict[str, str]:
        """Get git information for file"""
        try:
            repo_root = self._find_git_root(file_path)
            if not repo_root:
                return {"branch": "N/A", "status": "Not a git repo", "recent_commits": ""}

            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()

            status = subprocess.check_output(
                ["git", "status", "--short"], cwd=repo_root, text=True, stderr=subprocess.DEVNULL
            ).strip()

            commits = subprocess.check_output(
                ["git", "log", "-5", "--oneline"],
                cwd=repo_root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()

            return {"branch": branch, "status": status or "Clean", "recent_commits": commits}
        except Exception as e:
            logger.debug(f"Error getting git info: {e}")
            return {"branch": "N/A", "status": "Error", "recent_commits": ""}

    def _find_git_root(self, path: Path) -> Path | None:
        """Find git repository root"""
        current = path.parent if path.is_file() else path
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None

    def _get_project_structure(self, file_path: Path) -> str:
        """Get project directory structure"""
        project_root = self._find_project_root(file_path)
        if not project_root:
            return "Unknown project structure"

        # Get tree of important files (exclude node_modules, .git, etc.)
        try:
            # Try tree command first
            tree = subprocess.check_output(
                ["tree", "-L", "3", "-I", "node_modules|.git|__pycache__|venv|.venv|dist|build"],
                cwd=project_root,
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return tree
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback to simple directory listing
            try:
                files = []
                for item in project_root.iterdir():
                    if item.name not in [".git", "node_modules", "__pycache__", "venv", ".venv"]:
                        files.append(f"- {item.name}")
                return f"Project root: {project_root}\n" + "\n".join(files[:20])
            except Exception as e:
                logger.debug(f"Error listing project structure: {e}")
                return f"Project root: {project_root}"

    def _find_project_root(self, path: Path) -> Path | None:
        """Find project root (git root, or parent with package.json/pyproject.toml)"""
        git_root = self._find_git_root(path)
        if git_root:
            return git_root

        # Look for package.json, pyproject.toml, etc.
        current = path.parent if path.is_file() else path
        while current != current.parent:
            if any(
                (current / marker).exists()
                for marker in ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "go.mod"]
            ):
                return current
            current = current.parent

        return None

    def _get_dependencies(self, file_path: Path) -> str:
        """Get project dependencies"""
        project_root = self._find_project_root(file_path)
        if not project_root:
            return "Unknown dependencies"

        # Check for various dependency files
        if (project_root / "package.json").exists():
            try:
                with open(project_root / "package.json") as f:
                    import json

                    pkg = json.load(f)
                    deps = list(pkg.get("dependencies", {}).keys())
                    return f"Node.js project: {', '.join(deps[:10])}"
            except Exception:
                return "Node.js project (package.json found)"

        elif (project_root / "requirements.txt").exists():
            try:
                deps = (project_root / "requirements.txt").read_text()
                lines = [l.strip() for l in deps.split("\n") if l.strip() and not l.startswith("#")]
                return "Python requirements:\n" + "\n".join(lines[:15])
            except Exception:
                return "Python project (requirements.txt found)"

        elif (project_root / "pyproject.toml").exists():
            return "Python project (pyproject.toml found)"

        elif (project_root / "Cargo.toml").exists():
            return "Rust project (Cargo.toml found)"

        elif (project_root / "go.mod").exists():
            return "Go project (go.mod found)"

        else:
            return "No dependency file found"

    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React (JSX)",
            ".tsx": "React (TSX)",
            ".java": "Java",
            ".kt": "Kotlin",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".cc": "C++",
            ".cxx": "C++",
            ".cs": "C#",
            ".swift": "Swift",
            ".m": "Objective-C",
            ".sh": "Shell",
            ".bash": "Bash",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".vue": "Vue",
            ".svelte": "Svelte",
        }
        return ext_map.get(path.suffix, "Unknown")
