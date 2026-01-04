"""XML-Enhanced Prompts for Keyboard Shortcut Generation.

These prompts follow the Keyboard Conductor design principles:
- Musical scale pattern (Scale 1: Daily, Scale 2: Frequent, Scale 3: Advanced)
- Ergonomic optimization (left-hand home row preference)
- Mnemonic quality (letter matches, memorable phrases)
"""

# Stage 1: Feature Analysis Prompt
ANALYZE_FEATURES_PROMPT = """
<prompt name="analyze_features" tier="capable">
  <system>
    You are a UX expert specializing in keyboard ergonomics and mnemonic design.
    Your goal is to analyze project features and recommend optimal keyboard shortcuts
    following the "Keyboard Conductor" musical scale pattern.

    Design Principles:
    - Scale 1 (Daily): 4 most-used features on home row
    - Scale 2 (Frequent): Next 4 features on adjacent keys
    - Scale 3 (Advanced): Remaining features logically placed
    - Left-hand priority for primary actions
    - Memorable mnemonics (letter matches like M=Morning, S=Ship)
  </system>

  <context>
    <project_name>{project_name}</project_name>
    <project_type>{project_type}</project_type>
    <total_features>{feature_count}</total_features>
    <target_layouts>qwerty, dvorak, colemak</target_layouts>
  </context>

  <input>
    <features format="yaml">
{features_yaml}
    </features>
  </input>

  <task>
    Analyze these features and provide:

    1. **Frequency Classification**: Categorize each feature as:
       - daily: Used multiple times per day (4 features max)
       - frequent: Used regularly but not constantly (4 features)
       - advanced: Used occasionally or for power users (remaining)

    2. **Groupings**: Identify natural feature groups (4-6 max):
       - Quick Actions (morning routines, ship checks)
       - Workflows (code review, testing)
       - Views (dashboard, costs)
       - Analysis (security, bugs, health)

    3. **Mnemonic Suggestions**: For each feature, suggest:
       - Primary letter (first letter match if available)
       - Alternative letter (if conflict)
       - Mnemonic phrase (e.g., "M = Morning briefing")

    4. **Conflict Detection**: Flag features that:
       - Have same first letter
       - Should share modifier patterns
       - Might conflict with OS/IDE shortcuts
  </task>

  <output format="yaml">
    Return a YAML document with this structure:

    analyzed_features:
      - id: "morning"
        frequency: "daily"
        primary_letter: "m"
        alt_letter: null
        mnemonic: "M = Morning briefing"
        group: "Quick Actions"

    suggested_groups:
      - name: "Quick Actions"
        icon: "$(zap)"
        features: ["morning", "ship", "fix", "dashboard"]

    conflict_warnings:
      - type: "letter_conflict"
        features: ["review", "refactor"]
        message: "Both start with 'r' - suggest using 'r' for review, 'f' for refactor"

    phrase_mnemonic: "My Ship Floats Daily"
  </output>
</prompt>
"""

# Stage 2: Shortcut Generation Prompt
GENERATE_SHORTCUTS_PROMPT = """
<prompt name="generate_shortcuts" tier="capable">
  <system>
    You are a keyboard layout specialist. Generate ergonomic keyboard shortcuts
    following the "Keyboard Conductor" musical scale pattern.

    The goal is to create shortcuts that:
    1. Are physically comfortable (minimize finger travel)
    2. Are memorable (use meaningful letter associations)
    3. Progress naturally (learn 4 keys, then 4 more, then rest)
    4. Work across keyboard layouts (QWERTY, Dvorak, Colemak)
  </system>

  <constraints>
    <physical_layout>
      - Prioritize left-hand home row for Scale 1 (daily) actions
      - Use adjacent keys for related actions
      - Avoid awkward stretches or pinky overuse
      - Reserve right hand for less frequent actions
    </physical_layout>

    <mnemonic_quality>
      - Prefer direct letter matches (M=Morning, S=Ship, F=Fix)
      - Use sound-alikes when letters conflict (B=Bugs, not P=Predict)
      - Create memorable phrases for groups ("My Ship Floats Daily")
      - Consider keyboard position for alternatives (adjacent keys)
    </mnemonic_quality>

    <layout_adaptation>
      QWERTY home row: A-S-D-F (left), J-K-L-; (right)
      Dvorak home row: A-O-E-U (left), H-T-N-S (right)
      Colemak home row: A-R-S-T (left), N-E-I-O (right)

      For Dvorak/Colemak, adapt mnemonics:
      - Dvorak: "AOEU - vowels for daily actions"
      - Colemak: "ARST - your daily rhythm"
    </layout_adaptation>
  </constraints>

  <input>
    <analyzed_features>{analyzed_yaml}</analyzed_features>
    <existing_shortcuts>{existing_shortcuts}</existing_shortcuts>
    <reserved_keys>{reserved_keys}</reserved_keys>
  </input>

  <output format="json">
    Generate shortcuts for each layout. Return JSON with this structure:

    {{
      "qwerty": {{
        "shortcuts": [
          {{
            "feature_id": "morning",
            "key": "m",
            "mnemonic": "M = Morning",
            "hand": "left",
            "finger": "index",
            "row": "home"
          }}
        ],
        "scale_assignments": {{
          "daily": ["m", "s", "f", "d"],
          "frequent": ["w", "r", "t", "c"],
          "advanced": ["h", "b", "a", "g", "l", "v", "p", "z"]
        }},
        "phrase_mnemonic": "My Ship Floats Daily, With Really Tested Code"
      }},
      "dvorak": {{
        "shortcuts": [...],
        "scale_assignments": {{
          "daily": ["a", "o", "e", "u"],
          "frequent": ["i", "h", "t", "n"],
          "advanced": [...]
        }},
        "phrase_mnemonic": "AOEU - vowels for daily actions"
      }},
      "colemak": {{
        "shortcuts": [...],
        "scale_assignments": {{
          "daily": ["a", "r", "s", "t"],
          "frequent": ["g", "n", "e", "i"],
          "advanced": [...]
        }},
        "phrase_mnemonic": "ARST - your daily rhythm"
      }}
    }}
  </output>
</prompt>
"""

# Stage 3: Conflict Validation Prompt
VALIDATE_SHORTCUTS_PROMPT = """
<prompt name="validate_shortcuts" tier="cheap">
  <system>
    Validate generated keyboard shortcuts for conflicts and ergonomic issues.
    Your role is to ensure the shortcuts are safe, comfortable, and memorable.
  </system>

  <input>
    <generated_shortcuts>{shortcuts_json}</generated_shortcuts>

    <platform_reserved>
      macOS: Cmd+Q (quit), Cmd+W (close), Cmd+H (hide), Cmd+M (minimize)
      Windows: Ctrl+W (close), Ctrl+Q (quit in some apps)
      Linux: Similar to Windows

      IDE (VSCode): Ctrl+S (save), Ctrl+Z (undo), Ctrl+N (new), Ctrl+O (open)
    </platform_reserved>
  </input>

  <checks>
    Verify each of these conditions:

    1. **No Duplicates**: Each key is used only once per layout

    2. **No OS Conflicts**: Shortcuts don't override critical OS shortcuts
       (after the Ctrl+Shift+E prefix, check the final key)

    3. **No IDE Conflicts**: Don't conflict with common VSCode shortcuts

    4. **Balanced Fingers**: No single finger used more than 4 times
       (distribute across fingers evenly)

    5. **No Awkward Combos**: Avoid:
       - Keys requiring hand crossing
       - Pinky + ring finger stretches
       - Consecutive same-finger keys

    6. **Mnemonic Quality**: Each shortcut has a clear, memorable association

    7. **Progressive Learning**: Scale 1 keys are easier to reach than Scale 3
  </checks>

  <output format="json">
    Return validation results:

    {{
      "valid": true,
      "conflicts": [
        {{
          "type": "duplicate",
          "key": "r",
          "features": ["review", "refactor"],
          "severity": "error"
        }}
      ],
      "warnings": [
        {{
          "type": "ergonomic",
          "key": "q",
          "message": "Pinky stretch - consider moving to Scale 3",
          "severity": "warning"
        }}
      ],
      "suggestions": [
        {{
          "feature": "refactor",
          "current_key": "r",
          "suggested_key": "x",
          "reason": "Conflicts with 'review', 'x' is available and adjacent"
        }}
      ],
      "finger_distribution": {{
        "pinky": 2,
        "ring": 3,
        "middle": 4,
        "index": 5
      }},
      "mnemonic_quality_score": 0.85
    }}
  </output>
</prompt>
"""


def format_analyze_prompt(
    project_name: str,
    project_type: str,
    feature_count: int,
    features_yaml: str,
) -> str:
    """Format the feature analysis prompt with provided data."""
    return ANALYZE_FEATURES_PROMPT.format(
        project_name=project_name,
        project_type=project_type,
        feature_count=feature_count,
        features_yaml=features_yaml,
    )


def format_generate_prompt(
    analyzed_yaml: str,
    existing_shortcuts: str = "[]",
    reserved_keys: str = "[]",
) -> str:
    """Format the shortcut generation prompt with provided data."""
    return GENERATE_SHORTCUTS_PROMPT.format(
        analyzed_yaml=analyzed_yaml,
        existing_shortcuts=existing_shortcuts,
        reserved_keys=reserved_keys,
    )


def format_validate_prompt(shortcuts_json: str) -> str:
    """Format the validation prompt with provided data."""
    return VALIDATE_SHORTCUTS_PROMPT.format(shortcuts_json=shortcuts_json)
