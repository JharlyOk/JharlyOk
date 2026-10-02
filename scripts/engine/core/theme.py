"""Theme loader — reads and validates theme JSON files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SyntaxColors:
    """Syntax highlighting palette for code blocks."""
    keyword: str
    string: str
    comment: str
    type: str
    property: str
    function: str
    punctuation: str


@dataclass(frozen=True)
class Theme:
    """Immutable theme token set.

    Every field maps 1:1 to a Primer design-system token.
    Themes are loaded from JSON and frozen to prevent mutation.
    """
    name: str
    label: str

    # Backgrounds
    bg_canvas: str
    bg_subtle: str
    bg_inset: str
    bg_overlay: str

    # Borders
    border_default: str
    border_muted: str

    # Foreground
    fg_default: str
    fg_muted: str
    fg_subtle: str

    # Accent colors
    accent_primary: str
    accent_secondary: str
    accent_success: str
    accent_warning: str
    accent_danger: str

    # Syntax highlighting
    syntax: SyntaxColors

    # Typography (constant across themes)
    font_mono: str = field(default=(
        "'JetBrains Mono', 'SF Mono', 'Fira Code', "
        "ui-monospace, Consolas, monospace"
    ))
    font_sans: str = field(default=(
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "Helvetica, Arial, sans-serif"
    ))


def load_theme(theme_name: str, themes_dir: Path) -> Theme:
    """Load a theme from a JSON file in the themes directory.

    Args:
        theme_name: Name of the theme (e.g. 'github-dark').
        themes_dir: Path to the directory containing theme JSON files.

    Returns:
        Frozen Theme dataclass instance.

    Raises:
        FileNotFoundError: If the theme file doesn't exist.
        KeyError: If required tokens are missing from the JSON.
    """
    theme_path = themes_dir / f"{theme_name}.json"
    if not theme_path.exists():
        available = [f.stem for f in themes_dir.glob("*.json")]
        raise FileNotFoundError(
            f"Theme '{theme_name}' not found at {theme_path}. "
            f"Available themes: {available}"
        )

    with open(theme_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Theme(
        name=data["name"],
        label=data["label"],
        bg_canvas=data["bg"]["canvas"],
        bg_subtle=data["bg"]["subtle"],
        bg_inset=data["bg"]["inset"],
        bg_overlay=data["bg"]["overlay"],
        border_default=data["border"]["default"],
        border_muted=data["border"]["muted"],
        fg_default=data["fg"]["default"],
        fg_muted=data["fg"]["muted"],
        fg_subtle=data["fg"]["subtle"],
        accent_primary=data["accent"]["primary"],
        accent_secondary=data["accent"]["secondary"],
        accent_success=data["accent"]["success"],
        accent_warning=data["accent"]["warning"],
        accent_danger=data["accent"]["danger"],
        syntax=SyntaxColors(
            keyword=data["syntax"]["keyword"],
            string=data["syntax"]["string"],
            comment=data["syntax"]["comment"],
            type=data["syntax"]["type"],
            property=data["syntax"]["property"],
            function=data["syntax"]["function"],
            punctuation=data["syntax"]["punctuation"],
        ),
    )


def load_theme_pair(
    config: dict, themes_dir: Path
) -> tuple[Theme, Theme]:
    """Load both dark and light themes as specified in config.

    Args:
        config: Parsed profile.config.json dict.
        themes_dir: Path to themes directory.

    Returns:
        Tuple of (dark_theme, light_theme).
    """
    dark_name = config["themes"]["dark"]
    light_name = config["themes"]["light"]
    return load_theme(dark_name, themes_dir), load_theme(light_name, themes_dir)
