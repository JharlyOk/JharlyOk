"""Connect builder — Terminal-style communication & social endpoints card.

Generates a unified 880px terminal card displaying all communication channels,
response SLAs, and social endpoints in a structured, high-tech grid.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from ..core.registry import BaseBuilder, register_builder
from ..core.theme import Theme
from ..svg.icons import render_icon
from ..svg.primitives import (
    svg_open, svg_close, rect, text, circle,
    terminal_header, _esc,
)


def _resolve_accent(name: str, theme: Theme) -> str:
    mapping = {
        "primary": theme.accent_primary,
        "secondary": theme.accent_secondary,
        "success": theme.accent_success,
        "warning": theme.accent_warning,
        "danger": theme.accent_danger,
    }
    return mapping.get(name, theme.accent_primary)


@register_builder("connect")
class ConnectBuilder(BaseBuilder):
    """Generates the connect endpoints terminal card SVG."""

    WIDTH = 880
    HEADER_H = 36
    COLS = 3
    CARD_H = 74
    CARD_RX = 8
    PADDING_X = 24
    PADDING_TOP = 14
    PADDING_BOTTOM = 16
    GAP_X = 12
    GAP_Y = 10

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        socials: List[dict] = config.get("socials", [])
        num_items = len(socials)
        num_rows = math.ceil(num_items / self.COLS) if num_items else 1

        content_h = (
            self.PADDING_TOP
            + (num_rows * self.CARD_H)
            + ((num_rows - 1) * self.GAP_Y)
            + self.PADDING_BOTTOM
        )
        total_h = self.HEADER_H + content_h

        card_w = (
            self.WIDTH
            - (2 * self.PADDING_X)
            - ((self.COLS - 1) * self.GAP_X)
        ) / self.COLS

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{config['identity']['handle']} — Communication Endpoints",
            "Available communication channels, social handles and response SLA.",
        ))

        # ── Defs: ClipPaths for channel cards ───────────────────
        defs_parts: list[str] = ['  <defs>']
        for i in range(num_items):
            col = i % self.COLS
            row = i // self.COLS
            x = self.PADDING_X + col * (card_w + self.GAP_X)
            y = self.HEADER_H + self.PADDING_TOP + row * (self.CARD_H + self.GAP_Y)
            defs_parts.append(
                f'    <clipPath id="conn-clip-{i}">\n'
                f'      <rect x="{x}" y="{y}" width="{card_w}" height="{self.CARD_H}" rx="{self.CARD_RX}" />\n'
                f'    </clipPath>'
            )
        defs_parts.append('  </defs>\n')
        parts.append("\n".join(defs_parts))

        # ── Outer Background ────────────────────────────────────
        parts.append(rect(
            0, 0, self.WIDTH, total_h, theme.bg_canvas, rx=10,
            stroke=theme.border_default, stroke_width=1,
        ))

        # ── Terminal Header ─────────────────────────────────────
        parts.append(terminal_header(
            self.WIDTH,
            "connect --endpoints",
            theme,
            self.HEADER_H,
            status_text="24/7 REACHABLE",
            status_color=theme.accent_success,
        ))

        # ── Endpoints Grid ──────────────────────────────────────
        for i, item in enumerate(socials):
            col = i % self.COLS
            row = i // self.COLS
            x = self.PADDING_X + col * (card_w + self.GAP_X)
            y = self.HEADER_H + self.PADDING_TOP + row * (self.CARD_H + self.GAP_Y)

            icon_id = item.get("id", "web")
            label = item.get("label", icon_id.title())
            handle = item.get("display_handle", item.get("handle", ""))
            accent = _resolve_accent(item.get("accent", "primary"), theme)
            tag = item.get("tag", "LINK")
            latency = item.get("latency", "active")

            # Card background
            parts.append(rect(
                x, y, card_w, self.CARD_H,
                theme.bg_subtle, rx=self.CARD_RX,
                stroke=theme.border_muted, stroke_width=1,
            ))

            # Top accent bar — clipped to rounded corners
            parts.append(
                f'  <rect x="{x}" y="{y}" width="{card_w}" height="3" '
                f'fill="{accent}" clip-path="url(#conn-clip-{i})" />\n'
            )

            # Icon
            parts.append(render_icon(icon_id, x + 14, y + 14, 16, accent))

            # Label (e.g. Telegram)
            parts.append(text(
                x + 36, y + 26,
                label, theme.fg_default, theme.font_mono,
                font_size=12, font_weight=700,
            ))

            # Tag pill (top right)
            tag_w = len(tag) * 6.2 + 12
            tag_x = x + card_w - tag_w - 12
            parts.append(rect(
                tag_x, y + 13, tag_w, 18,
                theme.bg_overlay, rx=3,
                stroke=theme.border_muted, stroke_width=0.8,
            ))
            parts.append(text(
                tag_x + tag_w / 2, y + 25.5,
                tag, theme.fg_subtle, theme.font_mono,
                font_size=8.5, font_weight=700, text_anchor="middle",
                letter_spacing=0.5,
            ))

            # Handle (e.g. @JharlyOk)
            parts.append(text(
                x + 14, y + 46,
                handle, accent, theme.font_mono,
                font_size=11, font_weight=600,
            ))

            # Latency / SLA line with active dot
            parts.append(circle(x + 16, y + 60, 2.5, theme.accent_success))
            parts.append(text(
                x + 23, y + 63,
                latency, theme.fg_muted, theme.font_mono,
                font_size=9.5, letter_spacing=0.2,
            ))

        parts.append(svg_close())
        return "".join(parts)
