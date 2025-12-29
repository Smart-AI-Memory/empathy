"""
Tests for empathy_os.templates module.

Tests cover:
- Template definitions and structure
- list_templates function
- scaffold_project function
- cmd_new CLI handler
- Placeholder replacement
- File creation and directory handling
"""

from pathlib import Path
from unittest.mock import MagicMock

from empathy_os.templates import (
    TEMPLATES,
    cmd_new,
    list_templates,
    scaffold_project,
)


class TestTemplateDefinitions:
    """Test template definitions."""

    def test_all_templates_have_required_fields(self):
        """Test all templates have name, description, and files."""
        for template_id, template in TEMPLATES.items():
            assert "name" in template, f"{template_id} missing 'name'"
            assert "description" in template, f"{template_id} missing 'description'"
            assert "files" in template, f"{template_id} missing 'files'"
            assert isinstance(template["files"], dict), f"{template_id} files not dict"

    def test_minimal_template_exists(self):
        """Test minimal template is defined."""
        assert "minimal" in TEMPLATES
        assert "empathy.config.yml" in TEMPLATES["minimal"]["files"]

    def test_python_cli_template_exists(self):
        """Test python-cli template is defined."""
        assert "python-cli" in TEMPLATES
        assert "pyproject.toml" in TEMPLATES["python-cli"]["files"]

    def test_python_fastapi_template_exists(self):
        """Test python-fastapi template is defined."""
        assert "python-fastapi" in TEMPLATES
        files = TEMPLATES["python-fastapi"]["files"]
        assert "{{project_name}}/main.py" in files

    def test_python_agent_template_exists(self):
        """Test python-agent template is defined."""
        assert "python-agent" in TEMPLATES
        files = TEMPLATES["python-agent"]["files"]
        assert "{{project_name}}/agent.py" in files

    def test_templates_have_claude_rules(self):
        """Test templates include Claude Code rules."""
        for template_id, template in TEMPLATES.items():
            files = template["files"]
            has_claude = any(".claude" in f for f in files.keys())
            assert has_claude, f"{template_id} missing Claude Code rules"


class TestListTemplates:
    """Test list_templates function."""

    def test_returns_list(self):
        """Test returns a list."""
        result = list_templates()
        assert isinstance(result, list)

    def test_includes_all_templates(self):
        """Test all templates are included."""
        result = list_templates()
        template_ids = [t["id"] for t in result]

        for template_id in TEMPLATES.keys():
            assert template_id in template_ids

    def test_each_item_has_required_fields(self):
        """Test each item has id, name, description."""
        result = list_templates()

        for item in result:
            assert "id" in item
            assert "name" in item
            assert "description" in item


class TestScaffoldProject:
    """Test scaffold_project function."""

    def test_unknown_template_fails(self, tmp_path):
        """Test unknown template returns error."""
        result = scaffold_project(
            template_name="nonexistent",
            project_name="test",
            target_dir=str(tmp_path / "test"),
        )

        assert result["success"] is False
        assert "error" in result
        assert "available" in result

    def test_creates_directory(self, tmp_path):
        """Test creates project directory."""
        target = tmp_path / "new_project"
        result = scaffold_project(
            template_name="minimal",
            project_name="new_project",
            target_dir=str(target),
        )

        assert result["success"] is True
        assert target.exists()

    def test_creates_files(self, tmp_path):
        """Test creates template files."""
        target = tmp_path / "test_project"
        result = scaffold_project(
            template_name="minimal",
            project_name="test_project",
            target_dir=str(target),
        )

        assert result["success"] is True
        assert (target / "empathy.config.yml").exists()
        assert (target / ".claude" / "CLAUDE.md").exists()

    def test_replaces_project_name_placeholder(self, tmp_path):
        """Test replaces {{project_name}} in content."""
        target = tmp_path / "my_project"
        scaffold_project(
            template_name="minimal",
            project_name="my_project",
            target_dir=str(target),
        )

        config_content = (target / "empathy.config.yml").read_text()
        assert "my_project" in config_content
        assert "{{project_name}}" not in config_content

    def test_replaces_project_name_in_paths(self, tmp_path):
        """Test replaces {{project_name}} in file paths."""
        target = tmp_path / "test_cli"
        scaffold_project(
            template_name="python-cli",
            project_name="test_cli",
            target_dir=str(target),
        )

        assert (target / "test_cli" / "__init__.py").exists()
        assert (target / "test_cli" / "cli.py").exists()

    def test_replaces_class_name_placeholder(self, tmp_path):
        """Test replaces {{project_name_class}} in content."""
        target = tmp_path / "my_agent"
        scaffold_project(
            template_name="python-agent",
            project_name="my_agent",
            target_dir=str(target),
        )

        agent_content = (target / "my_agent" / "agent.py").read_text()
        assert "MyAgentAgent" in agent_content
        assert "{{project_name_class}}" not in agent_content

    def test_handles_hyphenated_names(self, tmp_path):
        """Test handles hyphenated project names for class conversion."""
        target = tmp_path / "my-cool-agent"
        scaffold_project(
            template_name="python-agent",
            project_name="my-cool-agent",
            target_dir=str(target),
        )

        agent_content = (target / "my-cool-agent" / "agent.py").read_text()
        assert "MyCoolAgentAgent" in agent_content

    def test_nonempty_directory_without_force(self, tmp_path):
        """Test fails on non-empty directory without force."""
        target = tmp_path / "existing"
        target.mkdir()
        (target / "somefile.txt").write_text("content")

        result = scaffold_project(
            template_name="minimal",
            project_name="existing",
            target_dir=str(target),
            force=False,
        )

        assert result["success"] is False
        assert "force" in result["error"].lower()

    def test_nonempty_directory_with_force(self, tmp_path):
        """Test succeeds on non-empty directory with force."""
        target = tmp_path / "existing"
        target.mkdir()
        (target / "somefile.txt").write_text("content")

        result = scaffold_project(
            template_name="minimal",
            project_name="existing",
            target_dir=str(target),
            force=True,
        )

        assert result["success"] is True

    def test_creates_patterns_directory(self, tmp_path):
        """Test creates patterns directory."""
        target = tmp_path / "test_project"
        scaffold_project(
            template_name="minimal",
            project_name="test_project",
            target_dir=str(target),
        )

        assert (target / "patterns").exists()
        assert (target / "patterns").is_dir()

    def test_returns_next_steps(self, tmp_path):
        """Test returns next steps."""
        target = tmp_path / "test"
        result = scaffold_project(
            template_name="minimal",
            project_name="test",
            target_dir=str(target),
        )

        assert "next_steps" in result
        assert len(result["next_steps"]) > 0

    def test_returns_files_created(self, tmp_path):
        """Test returns list of created files."""
        target = tmp_path / "test"
        result = scaffold_project(
            template_name="minimal",
            project_name="test",
            target_dir=str(target),
        )

        assert "files_created" in result
        assert len(result["files_created"]) > 0

    def test_gitignore_additions_handling(self, tmp_path):
        """Test .gitignore_additions are handled properly."""
        target = tmp_path / "test"
        result = scaffold_project(
            template_name="minimal",
            project_name="test",
            target_dir=str(target),
        )

        # Should create or append to .gitignore
        assert (target / ".gitignore").exists() or ".gitignore" in result.get("files_created", [])

    def test_default_target_dir(self, tmp_path, monkeypatch):
        """Test uses project name as default target dir."""
        monkeypatch.chdir(tmp_path)

        result = scaffold_project(
            template_name="minimal",
            project_name="default_dir_project",
            target_dir=None,
        )

        assert result["success"] is True
        assert Path("default_dir_project").exists()


class TestCmdNew:
    """Test cmd_new CLI handler."""

    def test_list_templates(self, capsys):
        """Test --list flag shows templates."""
        args = MagicMock()
        args.list = True
        args.template = None
        args.name = None

        result = cmd_new(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Available Templates" in captured.out
        assert "minimal" in captured.out

    def test_missing_args_shows_usage(self, capsys):
        """Test missing args shows usage."""
        args = MagicMock()
        args.list = False
        args.template = None
        args.name = None
        args.output = None
        args.force = False

        result = cmd_new(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_successful_creation(self, tmp_path, capsys):
        """Test successful project creation."""
        args = MagicMock()
        args.list = False
        args.template = "minimal"
        args.name = "test_project"
        args.output = str(tmp_path / "test_project")
        args.force = False

        result = cmd_new(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Project created" in captured.out
        assert "Next steps" in captured.out

    def test_unknown_template_error(self, tmp_path, capsys):
        """Test unknown template shows error."""
        args = MagicMock()
        args.list = False
        args.template = "nonexistent"
        args.name = "test"
        args.output = str(tmp_path / "test")
        args.force = False

        result = cmd_new(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_shows_files_created(self, tmp_path, capsys):
        """Test shows list of created files."""
        args = MagicMock()
        args.list = False
        args.template = "minimal"
        args.name = "test"
        args.output = str(tmp_path / "test")
        args.force = False

        cmd_new(args)

        captured = capsys.readouterr()
        assert "Files created" in captured.out


class TestTemplateContent:
    """Test template content is valid."""

    def test_empathy_config_is_valid_yaml(self, tmp_path):
        """Test empathy.config.yml is valid YAML."""
        import yaml

        target = tmp_path / "test"
        scaffold_project("minimal", "test", str(target))

        config_path = target / "empathy.config.yml"
        content = config_path.read_text()

        # Should not raise
        parsed = yaml.safe_load(content)
        assert parsed is not None
        assert "user_id" in parsed

    def test_python_files_are_syntactically_valid(self, tmp_path):
        """Test generated Python files are valid syntax."""
        import ast

        target = tmp_path / "test_cli"
        scaffold_project("python-cli", "test_cli", str(target))

        cli_path = target / "test_cli" / "cli.py"
        content = cli_path.read_text()

        # Should not raise SyntaxError
        ast.parse(content)

    def test_pyproject_toml_is_valid(self, tmp_path):
        """Test pyproject.toml is valid TOML."""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        target = tmp_path / "test_cli"
        scaffold_project("python-cli", "test_cli", str(target))

        toml_path = target / "pyproject.toml"
        content = toml_path.read_text()

        # Should not raise
        parsed = tomllib.loads(content)
        assert "project" in parsed
        assert parsed["project"]["name"] == "test_cli"
