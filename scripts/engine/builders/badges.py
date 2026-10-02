"""Badges builder — Standalone split-pill vector badges for social links & platforms.

Generates ultra-crisp, theme-adaptive SVG buttons matching GitHub Primer design system:
  - assets/badges/{id}-dark.svg
  - assets/badges/{id}-light.svg
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..core.theme import Theme
from ..svg.icons import render_icon
from ..svg.primitives import _esc


def _resolve_accent_color(accent_name: str, theme: Theme) -> str:
    """Map accent name string to theme accent color."""
    mapping = {
        "primary": theme.accent_primary,
        "secondary": theme.accent_secondary,
        "success": theme.accent_success,
        "warning": theme.accent_warning,
        "danger": theme.accent_danger,
    }
    return mapping.get(accent_name, theme.accent_primary)


def build_badge_svg(
    item: Dict[str, Any],
    theme: Theme,
) -> str:
    """Build a single split-pill badge SVG for a social/platform link."""
    icon_name = item.get("id", "web")
    label = item.get("label", icon_name.title())
    handle = item.get("display_handle", item.get("handle", ""))
    accent_key = item.get("accent", "primary")
    accent_color = _resolve_accent_color(accent_key, theme)

    height = 28
    rx = 6
    char_w = 7.0

    # Layout dimensions
    pad_left = 8
    icon_size = 14
    icon_gap = 6
    label_w = round(len(label) * char_w)
    left_w = pad_left + icon_size + icon_gap + label_w + 8

    handle_w = round(len(handle) * char_w)
    right_w = 10 + handle_w + 10
    total_w = left_w + right_w

    icon_y = (height - icon_size) / 2
    text_y = height / 2 + 3.5

    # Right side text color (contrast against accent fill)
    right_fg = theme.bg_inset if theme.name == "github-dark" else "#ffffff"

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {total_w} {height}" '
        f'width="{total_w}" height="{height}" '
        f'role="img" aria-label="{_esc(label)}: {_esc(handle)}">\n'
        f'  <defs>\n'
        f'    <clipPath id="pill-clip">\n'
        f'      <rect width="{total_w}" height="{height}" rx="{rx}" />\n'
        f'    </clipPath>\n'
        f'  </defs>\n\n'
        f'  <g clip-path="url(#pill-clip)">\n'
        f'    <!-- Left Section: Platform -->\n'
        f'    <rect x="0" y="0" width="{left_w}" height="{height}" fill="{theme.bg_overlay}" />\n'
        f'    <!-- Right Section: Handle -->\n'
        f'    <rect x="{left_w}" y="0" width="{right_w}" height="{height}" fill="{accent_color}" />\n'
        f'  </g>\n\n'
        f'  <!-- Pill Border -->\n'
        f'  <rect x="0.5" y="0.5" width="{total_w - 1}" height="{height - 1}" '
        f'rx="{rx}" fill="none" stroke="{theme.border_default}" stroke-width="1" />\n'
        f'  <line x1="{left_w}" y1="0" x2="{left_w}" y2="{height}" '
        f'stroke="{theme.border_muted}" stroke-width="1" />\n\n'
        f'  <!-- Icon -->\n'
        f'{render_icon(icon_name, pad_left, icon_y, icon_size, theme.fg_default)}'
        f'  <!-- Platform Label -->\n'
        f'  <text x="{pad_left + icon_size + icon_gap}" y="{text_y}" '
        f'font-family="{theme.font_mono}" font-size="11" font-weight="600" fill="{theme.fg_default}">'
        f'{_esc(label)}</text>\n\n'
        f'  <!-- Handle -->\n'
        f'  <text x="{left_w + 10}" y="{text_y}" '
        f'font-family="{theme.font_mono}" font-size="11" font-weight="700" fill="{right_fg}">'
        f'{_esc(handle)}</text>\n'
        f'</svg>\n'
    )
    return svg


def compile_all_badges(config: Dict[str, Any], theme: Theme, output_dir: Path) -> List[str]:
    """Compile all badges for a theme and save to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    socials: List[dict] = config.get("socials", [])
    theme_suffix = "dark" if theme.name == "github-dark" else "light"
    generated: list[str] = []

    for item in socials:
        badge_id = item["id"]
        svg_content = build_badge_svg(item, theme)
        file_path = output_dir / f"{badge_id}-{theme_suffix}.svg"
        file_path.write_text(svg_content, encoding="utf-8")
        generated.append(file_path.name)

    return generated
