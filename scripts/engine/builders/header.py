"""Header builder — Identity hero card.

Generates a dedicated identity card with:
  - Name and role prominently displayed
  - About/bio text
  - Highlight metrics (bots, audio, AI, infra)
  - Methodology tagline
  - Subtle accent gradients

This is the first thing visitors see. It must be memorable
and communicate who you are at a glance.
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, defs_block, style_block,
    rect, text, line, circle, _esc,
)


# Icon glyphs for highlights (simple geometric representations)
_ICON_GLYPHS = {
    "bot": "\u2B23",      # Hexagon
    "audio": "\u266B",    # Music note
    "ai": "\u2B50",       # Star (will use circle instead)
    "infra": "\u2302",    # House
}


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the identity hero card SVG."""

    WIDTH = 880
    HEIGHT = 200

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])
        about_lines = identity.get("about", [])

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, self.HEIGHT,
            f"{identity['handle']} — {identity['role']}",
            identity.get("tagline", ""),
        ))

        # ── Defs ────────────────────────────────────────────────
        defs_content = (
            f'    <linearGradient id="accentLine" x1="0%" y1="0%" x2="100%" y2="0%">\n'
            f'      <stop offset="0%" stop-color="{theme.accent_primary}" stop-opacity="0.8" />\n'
            f'      <stop offset="50%" stop-color="{theme.accent_secondary}" stop-opacity="0.4" />\n'
            f'      <stop offset="100%" stop-color="{theme.accent_primary}" stop-opacity="0.1" />\n'
            f'    </linearGradient>\n'
        )
        parts.append(defs_block(defs_content))

        # ── Background ──────────────────────────────────────────
        parts.append(rect(0, 0, self.WIDTH, self.HEIGHT, theme.bg_canvas, rx=10,
                          stroke=theme.border_default, stroke_width=1))

        # Accent gradient line at top
        parts.append(rect(0, 0, self.WIDTH, 3, "url(#accentLine)", rx=10))
        parts.append(rect(0, 3, self.WIDTH, 7, theme.bg_canvas))

        # ── Left side: Identity ─────────────────────────────────
        left_x = 28
        
        # Handle name — large
        parts.append(text(
            left_x, 44, identity["handle"], theme.fg_default,
            theme.font_sans, font_size=30, font_weight=700,
        ))

        # Role — accent colored
        parts.append(text(
            left_x, 68, identity["role"], theme.accent_primary,
            theme.font_sans, font_size=14, font_weight=500,
        ))

        # About lines
        about_y = 94
        for i, about_line in enumerate(about_lines):
            parts.append(text(
                left_x, about_y + (i * 17),
                about_line, theme.fg_muted, theme.font_sans,
                font_size=12.5,
            ))

        # Methodology badge at bottom
        method = identity.get("methodology", "")
        if method:
            method_y = self.HEIGHT - 22
            parts.append(text(
                left_x, method_y, method,
                theme.fg_subtle, theme.font_mono,
                font_size=10, letter_spacing=0.5,
            ))

        # ── Right side: Highlights ──────────────────────────────
        if highlights:
            # Vertical separator
            sep_x = 520
            parts.append(line(sep_x, 20, sep_x, self.HEIGHT - 20,
                              theme.border_muted, 0.5))

            highlight_x = sep_x + 28
            highlight_y_start = 36
            card_h = 36
            card_gap = 6
            card_w = self.WIDTH - highlight_x - 20

            for i, hl in enumerate(highlights):
                y = highlight_y_start + (i * (card_h + card_gap))

                # Highlight card background
                parts.append(rect(
                    highlight_x, y, card_w, card_h,
                    theme.bg_subtle, rx=6,
                    stroke=theme.border_muted, stroke_width=0.5,
                ))

                # Icon dot (color-coded)
                icon_colors = {
                    "bot": theme.accent_primary,
                    "audio": theme.accent_secondary,
                    "ai": theme.accent_success,
                    "infra": theme.accent_warning,
                }
                icon_type = hl.get("icon", "bot")
                dot_color = icon_colors.get(icon_type, theme.accent_primary)
                parts.append(circle(
                    highlight_x + 16, y + card_h // 2, 4, dot_color,
                ))

                # Label (bold)
                parts.append(text(
                    highlight_x + 28, y + 16,
                    hl.get("label", ""), theme.fg_default,
                    theme.font_mono, font_size=12, font_weight=600,
                ))

                # Detail (muted, right-aligned)
                parts.append(text(
                    highlight_x + card_w - 12, y + 16,
                    hl.get("detail", ""), theme.fg_subtle,
                    theme.font_mono, font_size=10.5, text_anchor="end",
                ))

                # Subtle accent bar on left of card
                parts.append(rect(
                    highlight_x, y, 3, card_h,
                    dot_color, rx=1, opacity=0.5,
                ))

        parts.append(svg_close())
        return "".join(parts)
