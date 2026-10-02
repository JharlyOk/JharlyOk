"""Header builder — Welcome tagline + visual highlights strip.

Two zones:
  1. A terminal-styled one-liner with a personal mission/tagline
  2. Four horizontal highlight cards showing active systems

The sidebar says WHO you are.
This card says WHAT drives you + WHAT you build.
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, style_block, cursor_blink_style,
    rect, text, line, circle, _esc,
)


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the welcome + highlights header SVG."""

    WIDTH = 880
    TAGLINE_H = 48
    CARD_H = 76
    CARD_GAP = 10
    CARD_RX = 8

    @property
    def HEIGHT(self):
        return self.TAGLINE_H + self.CARD_H + 8

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])
        total_h = self.TAGLINE_H + self.CARD_H + 8

        num_cards = len(highlights) if highlights else 4
        card_w = (self.WIDTH - ((num_cards - 1) * self.CARD_GAP)) / num_cards

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{identity['handle']} — Active Systems",
            identity.get("tagline", ""),
        ))

        # ── Styles ──────────────────────────────────────────────
        parts.append(style_block(cursor_blink_style()))

        # ── Tagline Zone ────────────────────────────────────────
        # Background bar
        parts.append(rect(
            0, 0, self.WIDTH, self.TAGLINE_H,
            theme.bg_inset, rx=8,
            stroke=theme.border_default, stroke_width=1,
        ))

        # Prompt symbol
        parts.append(text(
            16, 30, ">_", theme.accent_primary,
            theme.font_mono, font_size=16, font_weight=700,
        ))

        # Tagline text
        tagline = identity.get("tagline", "")
        parts.append(text(
            48, 30, tagline, theme.fg_default,
            theme.font_mono, font_size=13, font_weight=500,
        ))

        # Subtle blinking cursor at end
        cursor_x = 48 + len(tagline) * 7.6
        parts.append(text(
            min(cursor_x, self.WIDTH - 30), 30,
            "\u2588", theme.accent_primary,
            theme.font_mono, font_size=13, css_class="cursor-blink",
        ))

        # ── Highlight Cards ─────────────────────────────────────
        cards_y = self.TAGLINE_H + 8

        accent_colors = {
            "bot": theme.accent_primary,
            "audio": theme.accent_secondary,
            "ai": theme.accent_success,
            "infra": theme.accent_warning,
        }

        for i, hl in enumerate(highlights):
            x = i * (card_w + self.CARD_GAP)
            icon_type = hl.get("icon", "bot")
            accent = accent_colors.get(icon_type, theme.accent_primary)

            # Card background
            parts.append(rect(
                x, cards_y, card_w, self.CARD_H,
                theme.bg_inset, rx=self.CARD_RX,
                stroke=theme.border_default, stroke_width=1,
            ))

            # Accent top bar (not left — top feels more like a status indicator)
            parts.append(rect(
                x, cards_y, card_w, 3,
                accent, rx=self.CARD_RX,
            ))
            # Fix bottom of accent bar
            parts.append(rect(x, cards_y + 1, card_w, 2, accent))

            # Accent dot
            parts.append(circle(
                x + 16, cards_y + 28, 4, accent,
            ))

            # Label
            parts.append(text(
                x + 28, cards_y + 32,
                hl.get("label", ""),
                theme.fg_default, theme.font_mono,
                font_size=12.5, font_weight=700,
            ))

            # Detail
            parts.append(text(
                x + 16, cards_y + 52,
                hl.get("detail", ""),
                theme.fg_muted, theme.font_mono,
                font_size=10.5,
            ))

            # Subtle status line
            status_map = {
                "bot": "always online",
                "audio": "real-time",
                "ai": "multi-model",
                "infra": "self-hosted",
            }
            parts.append(text(
                x + 16, cards_y + 68,
                status_map.get(icon_type, ""),
                theme.fg_subtle, theme.font_mono,
                font_size=9, letter_spacing=0.5,
            ))

        parts.append(svg_close())
        return "".join(parts)
