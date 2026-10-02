"""Header builder — Animated welcome bar + visual highlights strip.

Two zones:
  1. A bar with CSS-animated cycling text (built into the SVG)
  2. Four horizontal highlight cards

The text animation uses pure CSS @keyframes opacity cycling —
no JavaScript, no external services. GitHub allows CSS in SVGs.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, style_block,
    rect, text, circle, _esc,
)


def _cycling_text_css(num_messages: int, duration_each: float = 3.0) -> str:
    """Generate CSS keyframes for cycling N text elements.

    Each message is visible for `duration_each` seconds.
    Total cycle = num_messages * duration_each.
    """
    total = num_messages * duration_each
    # Each message gets a slot: fade in (5%), hold (80%), fade out (5%), hidden (10%)
    slot_pct = 100.0 / num_messages
    fade_in = slot_pct * 0.05
    hold_start = slot_pct * 0.10
    hold_end = slot_pct * 0.85
    fade_out = slot_pct * 0.95

    css = f'    @keyframes cycle {{\n'
    css += f'      0%, {fade_in:.1f}% {{ opacity: 0; }}\n'
    css += f'      {hold_start:.1f}%, {hold_end:.1f}% {{ opacity: 1; }}\n'
    css += f'      {fade_out:.1f}%, 100% {{ opacity: 0; }}\n'
    css += f'    }}\n'

    # Each message class gets a delay
    for i in range(num_messages):
        delay = i * duration_each
        css += (
            f'    .msg-{i} {{\n'
            f'      opacity: 0;\n'
            f'      animation: cycle {total:.1f}s ease-in-out infinite;\n'
            f'      animation-delay: {delay:.1f}s;\n'
            f'    }}\n'
        )

    # Cursor blink
    css += (
        '    @keyframes blink {\n'
        '      0%, 100% { opacity: 1; }\n'
        '      50% { opacity: 0; }\n'
        '    }\n'
        '    .cursor-blink {\n'
        '      animation: blink 1.1s step-end infinite;\n'
        '    }\n'
    )

    return css


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the animated welcome + highlights header SVG."""

    WIDTH = 880
    WELCOME_H = 48
    CARD_H = 76
    CARD_GAP = 10
    CARD_RX = 8
    GAP = 8

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])
        messages = identity.get("welcome_messages", [
            "Welcome to my workspace",
        ])

        total_h = self.WELCOME_H + self.GAP + self.CARD_H
        num_cards = len(highlights) if highlights else 4
        card_w = (self.WIDTH - ((num_cards - 1) * self.CARD_GAP)) / num_cards

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{identity['handle']} — Active Systems",
            "Animated welcome and key highlights.",
        ))

        # ── CSS Animations ──────────────────────────────────────
        parts.append(style_block(_cycling_text_css(len(messages))))

        # ── Welcome Bar ─────────────────────────────────────────
        parts.append(rect(
            0, 0, self.WIDTH, self.WELCOME_H,
            theme.bg_subtle, rx=8,
            stroke=theme.border_muted, stroke_width=1,
        ))

        # Prompt symbol (static)
        parts.append(text(
            16, 30, ">_", theme.accent_primary,
            theme.font_mono, font_size=16, font_weight=700,
        ))

        # Cycling messages (stacked at same position, CSS cycles opacity)
        for i, msg in enumerate(messages):
            parts.append(text(
                48, 30, msg, theme.fg_default,
                theme.font_mono, font_size=14, font_weight=500,
                css_class=f"msg-{i}",
            ))

        # Blinking cursor (always visible)
        parts.append(text(
            self.WIDTH - 30, 30, "\u2588", theme.accent_primary,
            theme.font_mono, font_size=14, css_class="cursor-blink",
        ))

        # ── Highlight Cards ─────────────────────────────────────
        cards_y = self.WELCOME_H + self.GAP

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
                theme.bg_subtle, rx=self.CARD_RX,
                stroke=theme.border_muted, stroke_width=1,
            ))

            # Accent top bar
            parts.append(rect(x, cards_y, card_w, 3, accent, rx=self.CARD_RX))
            parts.append(rect(x, cards_y + 1, card_w, 2, accent))

            # Accent dot
            parts.append(circle(x + 16, cards_y + 28, 4, accent))

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

            # Status
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
