"""Header builder — Typewriter welcome bar + highlight cards.

Uses SMIL `<animate>` for true typewriter effect:
  - A covering rect reveals text char-by-char (typing)
  - Then covers it back (erasing)
  - Cycles through multiple messages

Accent bars use clipPath to stay within card bounds.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, style_block,
    rect, text, circle, _esc,
)


def _typewriter_elements(
    messages: List[str],
    x: float,
    y: float,
    bar_width: float,
    bg_color: str,
    text_color: str,
    accent_color: str,
    font_family: str,
    font_size: float = 14,
) -> str:
    """Generate SVG elements for SMIL-based typewriter animation.

    Uses a covering rect per message that shrinks (typing) and grows (erasing).
    """
    n = len(messages)
    char_w = font_size * 0.62  # monospace char width approximation
    type_speed = 0.06          # seconds per character reveal
    erase_speed = 0.03         # faster erase
    hold_time = 2.0            # seconds to display full message
    gap_time = 0.4             # pause between messages

    # Calculate per-message and total timing
    timings = []
    t = 0.0
    for msg in messages:
        msg_len = len(msg)
        type_dur = msg_len * type_speed
        erase_dur = msg_len * erase_speed
        cover_w = msg_len * char_w + 20  # full cover width

        timings.append({
            "start": t,
            "type_dur": type_dur,
            "hold_end": t + type_dur + hold_time,
            "erase_dur": erase_dur,
            "cover_w": cover_w,
        })
        t += type_dur + hold_time + erase_dur + gap_time

    total_dur = t

    svg = ""

    # Blinking cursor style
    svg += "  <style>\n"
    svg += "    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }\n"
    svg += "    .cb { animation: blink 1.1s step-end infinite; }\n"
    svg += "  </style>\n"

    # Cursor (always visible, blinking)
    svg += (
        f'  <text x="{x + 4}" y="{y}" fill="{accent_color}" '
        f'font-family="{font_family}" font-size="{font_size}" '
        f'font-weight="700" class="cb">\u2588</text>\n'
    )

    for i, (msg, tm) in enumerate(zip(messages, timings)):
        cover_w = tm["cover_w"]
        type_dur = tm["type_dur"]
        erase_dur = tm["erase_dur"]
        msg_start = tm["start"]
        hold_end = tm["hold_end"]

        # Generate keyTimes and values for the cover rect animation:
        # Phase 1: hidden (cover full) until msg_start
        # Phase 2: typing (cover shrinks from cover_w to 0) — type_dur
        # Phase 3: hold (cover stays 0) — hold_time
        # Phase 4: erase (cover grows from 0 to cover_w) — erase_dur
        # Phase 5: hidden (cover full) until end

        # Normalize times to 0-1 range
        t0 = msg_start / total_dur
        t1 = (msg_start + type_dur) / total_dur
        t2 = hold_end / total_dur
        t3 = (hold_end + erase_dur) / total_dur

        # Clamp to valid keyTimes
        key_times = [0]
        values = [str(cover_w)]

        if t0 > 0.001:
            key_times.append(round(t0, 4))
            values.append(str(cover_w))

        key_times.append(round(t1, 4))
        values.append("0")

        key_times.append(round(t2, 4))
        values.append("0")

        key_times.append(round(t3, 4))
        values.append(str(cover_w))

        if t3 < 0.999:
            key_times.append(1)
            values.append(str(cover_w))

        kt_str = ";".join(str(k) for k in key_times)
        val_str = ";".join(values)

        # Text element
        svg += (
            f'  <text x="{x}" y="{y}" fill="{text_color}" '
            f'font-family="{font_family}" font-size="{font_size}" '
            f'font-weight="500">{_esc(msg)}</text>\n'
        )

        # Covering rect (same color as background, hides text)
        svg += (
            f'  <rect x="{x}" y="{y - font_size}" '
            f'width="{cover_w}" height="{font_size + 8}" fill="{bg_color}">\n'
            f'    <animate attributeName="width" '
            f'values="{val_str}" '
            f'keyTimes="{kt_str}" '
            f'dur="{total_dur:.1f}s" repeatCount="indefinite" />\n'
            f'    <animate attributeName="x" '
            f'values="{x};{x};{x};{x};{x}" '
            f'dur="{total_dur:.1f}s" repeatCount="indefinite" />\n'
            f'  </rect>\n'
        )

    return svg


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the typewriter welcome + highlights header SVG."""

    WIDTH = 880
    WELCOME_H = 48
    CARD_H = 76
    CARD_GAP = 10
    CARD_RX = 8
    GAP = 8

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])
        messages = identity.get("welcome_messages", ["Welcome"])

        total_h = self.WELCOME_H + self.GAP + self.CARD_H
        num_cards = len(highlights) if highlights else 4
        card_w = (self.WIDTH - ((num_cards - 1) * self.CARD_GAP)) / num_cards

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{identity['handle']} — Active Systems",
            identity.get("tagline", ""),
        ))

        # ── Welcome Bar ─────────────────────────────────────────
        bar_bg = theme.bg_subtle
        parts.append(rect(
            0, 0, self.WIDTH, self.WELCOME_H,
            bar_bg, rx=8,
            stroke=theme.border_muted, stroke_width=1,
        ))

        # Prompt symbol
        parts.append(text(
            16, 30, ">_", theme.accent_primary,
            theme.font_mono, font_size=16, font_weight=700,
        ))

        # Typewriter animated text
        parts.append(_typewriter_elements(
            messages=messages,
            x=50,
            y=30,
            bar_width=self.WIDTH - 70,
            bg_color=bar_bg,
            text_color=theme.fg_default,
            accent_color=theme.accent_primary,
            font_family=theme.font_mono,
            font_size=14,
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

            # Accent top line — INSIDE the card, no border-radius
            parts.append(rect(
                x + 1, cards_y + 1, card_w - 2, 2, accent,
            ))

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
