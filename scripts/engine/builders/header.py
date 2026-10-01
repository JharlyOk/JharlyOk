"""Header builder — Visual highlights strip.

Generates a compact horizontal card showing 4 key highlights
as visual metric cards. This COMPLEMENTS the GitHub sidebar bio
instead of competing with it.

The sidebar says WHO you are.
This card shows WHAT you build — at a glance.

Design:
  - 4 horizontal cards with accent-colored left borders
  - Bold metric label + subtle detail
  - No name, no role, no bio (sidebar handles that)
  - Clean Primer colors, no gradients
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close,
    rect, text, circle, _esc,
)


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the visual highlights strip SVG."""

    WIDTH = 880
    HEIGHT = 86
    CARD_GAP = 12
    CARD_RX = 8
    PADDING_X = 0

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])

        num_cards = len(highlights) if highlights else 4
        card_w = (self.WIDTH - (self.PADDING_X * 2) - ((num_cards - 1) * self.CARD_GAP)) / num_cards

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, self.HEIGHT,
            f"{identity['handle']} — Active Systems",
            "Key highlights and active systems overview.",
        ))

        # Icon/accent colors
        accent_colors = {
            "bot": theme.accent_primary,
            "audio": theme.accent_secondary,
            "ai": theme.accent_success,
            "infra": theme.accent_warning,
        }

        # ── Highlight Cards ─────────────────────────────────────
        for i, hl in enumerate(highlights):
            x = self.PADDING_X + i * (card_w + self.CARD_GAP)
            icon_type = hl.get("icon", "bot")
            accent = accent_colors.get(icon_type, theme.accent_primary)

            # Card background
            parts.append(rect(
                x, 0, card_w, self.HEIGHT,
                theme.bg_subtle, rx=self.CARD_RX,
                stroke=theme.border_muted, stroke_width=0.8,
            ))

            # Accent left border (3px bar)
            parts.append(rect(
                x, 0, 4, self.HEIGHT,
                accent, rx=self.CARD_RX,
            ))
            # Fix right side of accent bar (no rounded corners)
            parts.append(rect(x + 2, 0, 2, self.HEIGHT, accent))

            # Accent dot
            parts.append(circle(
                x + 20, 28, 5, accent,
            ))

            # Label (large, bold)
            parts.append(text(
                x + 34, 32,
                hl.get("label", ""),
                theme.fg_default, theme.font_mono,
                font_size=13, font_weight=700,
            ))

            # Detail line
            parts.append(text(
                x + 20, 56,
                hl.get("detail", ""),
                theme.fg_muted, theme.font_mono,
                font_size=11,
            ))

            # Methodology/subtitle (very subtle, bottom)
            method_text = {
                "bot": "24/7 uptime",
                "audio": "real-time",
                "ai": "multi-model",
                "infra": "self-hosted",
            }
            parts.append(text(
                x + 20, 74,
                method_text.get(icon_type, ""),
                theme.fg_subtle, theme.font_mono,
                font_size=9.5, letter_spacing=0.3,
            ))

        parts.append(svg_close())
        return "".join(parts)
