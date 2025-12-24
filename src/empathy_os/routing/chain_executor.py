"""
Chain Executor

Executes wizard chains based on triggers and conditions.
Handles auto-chaining, approval workflows, and chain tracking.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .wizard_registry import WizardRegistry


@dataclass
class ChainTrigger:
    """A trigger condition for auto-chaining."""

    condition: str
    next_wizard: str
    approval_required: bool = False
    reason: str = ""


@dataclass
class ChainConfig:
    """Configuration for a wizard's chaining behavior."""

    wizard_name: str
    auto_chain: bool = True
    description: str = ""
    triggers: list[ChainTrigger] = field(default_factory=list)


@dataclass
class ChainStep:
    """A step in an executed chain."""

    wizard_name: str
    triggered_by: str  # condition or manual
    approval_required: bool
    approved: bool | None = None  # None = pending
    result: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class ChainExecution:
    """Record of a chain execution."""

    chain_id: str
    initial_wizard: str
    steps: list[ChainStep] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    status: str = "running"  # running, completed, waiting_approval, failed
    current_step: int = 0


class ChainExecutor:
    """
    Executes wizard chains based on configuration and results.

    Usage:
        executor = ChainExecutor()

        # Check for triggered chains after a wizard run
        result = {"high_severity_count": 5, "vulnerability_type": "injection"}
        next_steps = executor.get_triggered_chains("security-audit", result)

        # Execute a chain template
        execution = await executor.execute_template("full-security-review", input_data)
    """

    def __init__(
        self,
        config_path: str | Path = ".empathy/wizard_chains.yaml",
    ):
        """
        Initialize the chain executor.

        Args:
            config_path: Path to wizard_chains.yaml
        """
        self.config_path = Path(config_path)
        self._configs: dict[str, ChainConfig] = {}
        self._templates: dict[str, list[str]] = {}
        self._global_settings: dict[str, Any] = {}
        self._registry = WizardRegistry()
        self._executions: list[ChainExecution] = []

        self._load_config()

    def _load_config(self) -> None:
        """Load chain configuration from YAML file."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path) as f:
                data = yaml.safe_load(f) or {}

            # Load global settings
            self._global_settings = data.get("global", {})

            # Load chain configs
            chains = data.get("chains", {})
            for wizard_name, config in chains.items():
                triggers = []
                for t in config.get("triggers", []):
                    triggers.append(
                        ChainTrigger(
                            condition=t.get("condition", ""),
                            next_wizard=t.get("next", ""),
                            approval_required=t.get("approval_required", False),
                            reason=t.get("reason", ""),
                        )
                    )

                self._configs[wizard_name] = ChainConfig(
                    wizard_name=wizard_name,
                    auto_chain=config.get("auto_chain", True),
                    description=config.get("description", ""),
                    triggers=triggers,
                )

            # Load templates
            templates = data.get("templates", {})
            for name, template in templates.items():
                self._templates[name] = template.get("steps", [])

        except (yaml.YAMLError, OSError) as e:
            print(f"Warning: Could not load chain config: {e}")

    def get_triggered_chains(
        self,
        wizard_name: str,
        result: dict[str, Any],
    ) -> list[ChainTrigger]:
        """
        Get triggered chain steps based on wizard result.

        Args:
            wizard_name: The wizard that just completed
            result: The wizard's result dictionary

        Returns:
            List of triggered ChainTriggers
        """
        if not self._global_settings.get("auto_chain_enabled", True):
            return []

        config = self._configs.get(wizard_name)
        if not config or not config.auto_chain:
            return []

        triggered = []
        for trigger in config.triggers:
            if self._evaluate_condition(trigger.condition, result):
                triggered.append(trigger)

        return triggered

    def _evaluate_condition(
        self,
        condition: str,
        context: dict[str, Any],
    ) -> bool:
        """
        Evaluate a trigger condition against a result context.

        Supports:
        - Comparisons: var > 0, var == 'value', var < 10
        - Boolean: var == true, var == false
        - Existence: var != null

        Args:
            condition: The condition string
            context: The result dictionary to evaluate against

        Returns:
            True if condition is met
        """
        if not condition:
            return False

        # Parse comparison operators
        operators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: float(a) > float(b) if _is_numeric(a) and _is_numeric(b) else False,
            "<": lambda a, b: float(a) < float(b) if _is_numeric(a) and _is_numeric(b) else False,
            ">=": lambda a, b: float(a) >= float(b) if _is_numeric(a) and _is_numeric(b) else False,
            "<=": lambda a, b: float(a) <= float(b) if _is_numeric(a) and _is_numeric(b) else False,
        }

        for op_str, op_func in operators.items():
            if op_str in condition:
                parts = condition.split(op_str)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value_str = parts[1].strip()

                    # Get actual value from context
                    actual = context.get(var_name)
                    if actual is None:
                        # Try nested access
                        actual = _get_nested(context, var_name)

                    if actual is None:
                        return False

                    # Parse expected value
                    expected = _parse_value(value_str)

                    try:
                        return bool(op_func(actual, expected))
                    except (ValueError, TypeError):
                        return False

        return False

    def should_trigger_chain(
        self,
        wizard_name: str,
        result: dict[str, Any],
    ) -> tuple[bool, list[ChainTrigger]]:
        """
        Check if a chain should be triggered and return triggers.

        Args:
            wizard_name: The wizard that completed
            result: The wizard's result

        Returns:
            Tuple of (should_trigger, list_of_triggers)
        """
        triggers = self.get_triggered_chains(wizard_name, result)
        return len(triggers) > 0, triggers

    def get_chain_config(self, wizard_name: str) -> ChainConfig | None:
        """Get chain configuration for a wizard."""
        return self._configs.get(wizard_name)

    def get_template(self, template_name: str) -> list[str] | None:
        """Get a chain template by name."""
        return self._templates.get(template_name)

    def list_templates(self) -> dict[str, list[str]]:
        """List all available chain templates."""
        return dict(self._templates)

    def create_execution(
        self,
        initial_wizard: str,
        triggered_steps: list[ChainTrigger] | None = None,
    ) -> ChainExecution:
        """
        Create a new chain execution record.

        Args:
            initial_wizard: The starting wizard
            triggered_steps: Optional list of triggered next steps

        Returns:
            ChainExecution object
        """
        execution = ChainExecution(
            chain_id=f"chain_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            initial_wizard=initial_wizard,
        )

        # Add initial step
        execution.steps.append(
            ChainStep(
                wizard_name=initial_wizard,
                triggered_by="manual",
                approval_required=False,
                approved=True,
            )
        )

        # Add triggered steps
        if triggered_steps:
            for trigger in triggered_steps:
                execution.steps.append(
                    ChainStep(
                        wizard_name=trigger.next_wizard,
                        triggered_by=trigger.condition,
                        approval_required=trigger.approval_required,
                    )
                )

        self._executions.append(execution)
        return execution

    def approve_step(self, execution: ChainExecution, step_index: int) -> bool:
        """Approve a pending step in a chain execution."""
        if step_index < len(execution.steps):
            execution.steps[step_index].approved = True
            return True
        return False

    def reject_step(self, execution: ChainExecution, step_index: int) -> bool:
        """Reject a pending step in a chain execution."""
        if step_index < len(execution.steps):
            execution.steps[step_index].approved = False
            return True
        return False

    def get_next_step(self, execution: ChainExecution) -> ChainStep | None:
        """Get the next step to execute in a chain."""
        max_depth = self._global_settings.get("max_chain_depth", 3)

        for i, step in enumerate(execution.steps):
            if i >= max_depth:
                break

            # Skip completed steps
            if step.completed_at is not None:
                continue

            # Check approval
            if step.approval_required and step.approved is None:
                execution.status = "waiting_approval"
                return None

            if step.approval_required and step.approved is False:
                continue  # Skip rejected steps

            return step

        return None

    def complete_step(
        self,
        execution: ChainExecution,
        step: ChainStep,
        result: dict[str, Any],
    ) -> list[ChainTrigger]:
        """
        Mark a step as complete and check for new triggers.

        Args:
            execution: The chain execution
            step: The step that completed
            result: The step's result

        Returns:
            List of newly triggered steps
        """
        step.completed_at = datetime.now()
        step.result = result

        # Check for new triggers
        new_triggers = self.get_triggered_chains(step.wizard_name, result)

        # Add new steps (if not already in chain)
        existing_wizards = {s.wizard_name for s in execution.steps}
        for trigger in new_triggers:
            if trigger.next_wizard not in existing_wizards:
                execution.steps.append(
                    ChainStep(
                        wizard_name=trigger.next_wizard,
                        triggered_by=trigger.condition,
                        approval_required=trigger.approval_required,
                    )
                )

        # Check if chain is complete
        all_done = all(
            s.completed_at is not None or (s.approval_required and s.approved is False)
            for s in execution.steps
        )
        if all_done:
            execution.status = "completed"
            execution.completed_at = datetime.now()

        return new_triggers


def _is_numeric(value: Any) -> bool:
    """Check if a value is numeric."""
    if isinstance(value, int | float):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False


def _parse_value(value_str: str) -> Any:
    """Parse a value string to appropriate type."""
    value_str = value_str.strip().strip("'\"")

    # Boolean
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False
    if value_str.lower() == "null":
        return None

    # Number
    try:
        if "." in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # String
    return value_str


def _get_nested(obj: dict[str, Any], path: str) -> Any:
    """Get a nested value from a dictionary using dot notation."""
    parts = path.split(".")
    current: Any = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current
