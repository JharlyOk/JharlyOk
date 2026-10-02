"""Header builder — Highlight cards strip.

Generates 4 horizontal cards showing active systems.
The typing animation is handled externally by readme-typing-svg
(configured in build.py from welcome_messages in config).
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close,
    rect, text, circle,
)


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the highlights strip SVG."""

    WIDTH = 880
    CARD_H = 76
    CARD_GAP = 10
    CARD_RX = 8

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])

        num_cards = len(highlights) if highlights else 4
        card_w = (self.WIDTH - ((num_cards - 1) * self.CARD_GAP)) / num_cards

        parts: list[str] = []

        parts.append(svg_open(
            self.WIDTH, self.CARD_H,
            f"{identity['handle']} — Active Systems",
            "Key highlights and active systems.",
        ))

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
                x, 0, card_w, self.CARD_H,
                theme.bg_subtle, rx=self.CARD_RX,
                stroke=theme.border_muted, stroke_width=1,
            ))

            # Accent top line — inset inside card, no border-radius
            parts.append(rect(x + 1, 1, card_w - 2, 2, accent))

            # Accent dot
            parts.append(circle(x + 16, 28, 4, accent))

            # Label
            parts.append(text(
                x + 28, 32,
                hl.get("label", ""),
                theme.fg_default, theme.font_mono,
                font_size=12.5, font_weight=700,
            ))

            # Detail
            parts.append(text(
                x + 16, 52,
                hl.get("detail", ""),
                theme.fg_muted, theme.font_mono,
                font_size=10.5,
            ))

            # Status
            status_map = {
                "bot": "always online",
                "audio": "real-time",
                "ai": "multi-model",
                "infra": "self-hosted",
            }
            parts.append(text(
                x + 16, 68,
                status_map.get(icon_type, ""),
                theme.fg_subtle, theme.font_mono,
                font_size=9, letter_spacing=0.5,
            ))

        parts.append(svg_close())
        return "".join(parts)
