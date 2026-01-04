"""Schema definitions for keyboard shortcut generation.

Uses Pydantic models for validation and serialization.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class FrequencyTier(str, Enum):
    """Usage frequency tiers for feature prioritization."""

    DAILY = "daily"  # Scale 1: 4 most-used features
    FREQUENT = "frequent"  # Scale 2: Next 4 features
    ADVANCED = "advanced"  # Scale 3: Remaining features


class KeyboardLayout(str, Enum):
    """Supported keyboard layouts."""

    QWERTY = "qwerty"
    DVORAK = "dvorak"
    COLEMAK = "colemak"


class HandPosition(str, Enum):
    """Which hand operates the key."""

    LEFT = "left"
    RIGHT = "right"


class FingerPosition(str, Enum):
    """Which finger operates the key."""

    PINKY = "pinky"
    RING = "ring"
    MIDDLE = "middle"
    INDEX = "index"
    THUMB = "thumb"


class RowPosition(str, Enum):
    """Keyboard row position."""

    TOP = "top"  # QWERTY row
    HOME = "home"  # ASDF row
    BOTTOM = "bottom"  # ZXCV row


@dataclass
class Feature:
    """A single feature that needs a keyboard shortcut."""

    id: str  # Unique identifier (e.g., "morning", "ship")
    name: str  # Human-readable name (e.g., "Morning Briefing")
    description: str = ""
    command: str = ""  # VSCode command or CLI command
    cli_alias: str = ""  # CLI equivalent (e.g., "empathy morning")
    frequency: FrequencyTier = FrequencyTier.FREQUENT
    context: Literal["global", "editor", "explorer"] = "global"
    icon: str = "$(symbol-misc)"


@dataclass
class Category:
    """A group of related features."""

    name: str
    icon: str = "$(folder)"
    tier: FrequencyTier = FrequencyTier.FREQUENT
    features: list[Feature] = field(default_factory=list)


@dataclass
class LayoutConfig:
    """Configuration for a specific keyboard layout."""

    layout: KeyboardLayout
    home_row: list[str] = field(default_factory=list)
    mnemonic_base: str = ""

    def __post_init__(self):
        if not self.home_row:
            if self.layout == KeyboardLayout.QWERTY:
                self.home_row = ["a", "s", "d", "f"]
                self.mnemonic_base = "natural English letters"
            elif self.layout == KeyboardLayout.DVORAK:
                self.home_row = ["a", "o", "e", "u"]
                self.mnemonic_base = "vowel-centric patterns"
            elif self.layout == KeyboardLayout.COLEMAK:
                self.home_row = ["a", "r", "s", "t"]
                self.mnemonic_base = "ARST patterns"


@dataclass
class ShortcutAssignment:
    """A keyboard shortcut assignment for a feature."""

    feature_id: str
    key: str  # Single letter key (e.g., "m", "s")
    mnemonic: str  # Memory aid (e.g., "M = Morning")
    hand: HandPosition = HandPosition.LEFT
    finger: FingerPosition = FingerPosition.INDEX
    row: RowPosition = RowPosition.HOME
    layout: KeyboardLayout = KeyboardLayout.QWERTY


@dataclass
class ScaleAssignments:
    """Shortcut assignments organized by scale (learning progression)."""

    daily: list[str] = field(default_factory=list)  # Scale 1: 4 keys
    frequent: list[str] = field(default_factory=list)  # Scale 2: 4 keys
    advanced: list[str] = field(default_factory=list)  # Scale 3: remaining


@dataclass
class LayoutShortcuts:
    """Complete shortcut set for a specific layout."""

    layout: KeyboardLayout
    shortcuts: list[ShortcutAssignment] = field(default_factory=list)
    scale_assignments: ScaleAssignments = field(default_factory=ScaleAssignments)
    phrase_mnemonic: str = ""  # e.g., "My Ship Floats Daily"


@dataclass
class FeatureManifest:
    """Complete manifest for keyboard shortcut generation."""

    project_name: str
    project_type: Literal["vscode-extension", "python-cli", "custom"] = "custom"
    prefix: str = "ctrl+shift+e"  # Base chord
    categories: list[Category] = field(default_factory=list)
    layouts: list[LayoutConfig] = field(default_factory=list)

    def __post_init__(self):
        if not self.layouts:
            self.layouts = [
                LayoutConfig(layout=KeyboardLayout.QWERTY),
                LayoutConfig(layout=KeyboardLayout.DVORAK),
                LayoutConfig(layout=KeyboardLayout.COLEMAK),
            ]

    def all_features(self) -> list[Feature]:
        """Get all features across all categories."""
        features = []
        for category in self.categories:
            features.extend(category.features)
        return features

    def features_by_tier(self, tier: FrequencyTier) -> list[Feature]:
        """Get features filtered by frequency tier."""
        return [f for f in self.all_features() if f.frequency == tier]


@dataclass
class GeneratedShortcuts:
    """Complete output from keyboard shortcut generation."""

    manifest: FeatureManifest
    layouts: dict[KeyboardLayout, LayoutShortcuts] = field(default_factory=dict)
    validation_passed: bool = True
    conflicts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Keyboard layout reference data
KEYBOARD_LAYOUTS = {
    KeyboardLayout.QWERTY: {
        "top_row": list("qwertyuiop"),
        "home_row": list("asdfghjkl"),
        "bottom_row": list("zxcvbnm"),
    },
    KeyboardLayout.DVORAK: {
        "top_row": list("',.pyfgcrl"),
        "home_row": list("aoeuidhtns"),
        "bottom_row": list(";qjkxbmwvz"),
    },
    KeyboardLayout.COLEMAK: {
        "top_row": list("qwfpgjluy;"),
        "home_row": list("arstdhneio"),
        "bottom_row": list("zxcvbkm,."),
    },
}

# Reserved keys that should not be used (conflicts with OS/IDE)
RESERVED_KEYS = {
    "global": ["q", "w", "e", "x"],  # Commonly used by OS
    "ide": ["n", "o", "s", "z"],  # Commonly used by IDE (new, open, save, undo)
}
