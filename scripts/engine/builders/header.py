"""Header builder — Typewriter welcome bar + highlight cards.

Generates a unified SVG header containing:
  1. Terminal-style welcome bar with true SMIL typewriter animation (textPath).
     Cycles through welcome_messages smoothly (type -> hold -> backspace -> next).
  2. 4 horizontal active systems cards with clipped accent bars and status tags.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.registry import BaseBuilder, register_builder
from ..core.theme import Theme
from ..core.telemetry import format_metric_value, get_active_telemetry_metrics
from ..svg.icons import render_icon
from ..svg.primitives import (
    svg_close, rect, text, circle, _esc,
)


def _build_typewriter(
    messages: List[str],
    start_x: int | float,
    y: int | float,
    max_width: int | float,
    text_color: str,
    font_family: str,
    font_size: int | float = 13.5,
    hold_time: float = 4.5,
    type_speed: float = 0.055,
    erase_speed: float = 0.025,
) -> tuple[str, str]:
    """Generate SMIL textPath-based typewriter elements for cycling messages.
    
    Returns (defs_paths_svg, visible_texts_svg).
    """
    if not messages:
        messages = ["Welcome to my workspace"]

    n = len(messages)
    paths: list[str] = []
    texts: list[str] = []

    for i, msg in enumerate(messages):
        prev_id = f"hdr_anim_{(i - 1) % n}"
        curr_id = f"hdr_anim_{i}"
        path_id = f"hdr_path_{i}"

        msg_len = len(msg)
        type_dur = max(1.0, msg_len * type_speed)
        erase_dur = max(0.5, msg_len * erase_speed)
        total_dur = type_dur + hold_time + erase_dur

        k_type = round(type_dur / total_dur, 3)
        k_hold = round((type_dur + hold_time) / total_dur, 3)

        # First animation starts at 0s, subsequent ones chain to previous end
        begin_attr = f"0s;{prev_id}.end" if i == 0 else f"{prev_id}.end"
        dur_ms = int(total_dur * 1000)

        # Generous horizontal path width to ensure full text reveals cleanly
        w = max_width

        paths.append(
            f'    <path id="{path_id}">\n'
            f'      <animate id="{curr_id}" attributeName="d" '
            f'begin="{begin_attr}" dur="{dur_ms}ms" fill="remove" '
            f'values="m{start_x},{y} h0 ; m{start_x},{y} h{w} ; m{start_x},{y} h{w} ; m{start_x},{y} h0" '
            f'keyTimes="0; {k_type}; {k_hold}; 1" />\n'
            f'    </path>'
        )

        texts.append(
            f'  <text font-family="{font_family}" fill="{text_color}" '
            f'font-size="{font_size}" font-weight="500" dominant-baseline="middle">\n'
            f'    <textPath href="#{path_id}" xlink:href="#{path_id}">{_esc(msg)}</textPath>\n'
            f'  </text>\n'
        )

    paths_str = "\n".join(paths) + "\n"
    texts_str = "".join(texts)
    return paths_str, texts_str


def _get_active_header_metrics(
    config: Dict[str, Any],
    theme: Theme,
    stats: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Extract and format active telemetry metrics configured for the header."""
    return get_active_telemetry_metrics(config, stats, theme, scope="header")


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the unified typewriter welcome + highlights + telemetry header SVG."""

    WIDTH = 880
    WELCOME_H = 46
    GAP = 10
    CARD_H = 76
    CARD_GAP = 10
    CARD_RX = 8
    TELEMETRY_H = 34
    TELEMETRY_GAP = 10

    def build(
        self,
        config: Dict[str, Any],
        theme: Theme,
        telemetry_stats: Dict[str, Any] | None = None,
    ) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])
        messages = identity.get("welcome_messages", [
            "Hey, welcome to my workspace",
            "Building autonomous bot ecosystems",
            "13+ production bots running 24/7",
            "AI-accelerated dev with Gemini & Claude",
            "Real-time audio routing with Lavalink v4",
        ])

        # Load telemetry stats from parameter or cache fallback
        stats = telemetry_stats or {}
        if not stats:
            cache_path = Path(".cache/telemetry.json")
            if cache_path.exists():
                try:
                    stats = json.loads(cache_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

        active_metrics = _get_active_header_metrics(config, theme, stats)
        has_telemetry = len(active_metrics) > 0

        total_h = self.WELCOME_H + self.GAP + self.CARD_H
        if has_telemetry:
            total_h += self.TELEMETRY_GAP + self.TELEMETRY_H

        num_cards = len(highlights) if highlights else 4
        card_w = (self.WIDTH - ((num_cards - 1) * self.CARD_GAP)) / num_cards

        cards_y = self.WELCOME_H + self.GAP
        bar_mid_y = self.WELCOME_H / 2

        tw_cfg = identity.get("typewriter", {})
        hold_time = float(tw_cfg.get("hold_time", 4.5))
        type_speed = float(tw_cfg.get("type_speed", 0.055))
        erase_speed = float(tw_cfg.get("erase_speed", 0.025))

        # Build typewriter paths (for <defs>) and texts (for body)
        tw_paths, tw_texts = _build_typewriter(
            messages=messages,
            start_x=48,
            y=bar_mid_y + 1,
            max_width=self.WIDTH - 64,
            text_color=theme.fg_default,
            font_family=theme.font_mono,
            font_size=13.5,
            hold_time=hold_time,
            type_speed=type_speed,
            erase_speed=erase_speed,
        )

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {self.WIDTH} {total_h}" '
            f'width="{self.WIDTH}" height="{total_h}" '
            f'role="img" aria-labelledby="svgTitle svgDesc">\n'
            f'  <title id="svgTitle">{_esc(identity["handle"])} — Workspace Header</title>\n'
            f'  <desc id="svgDesc">{_esc(identity.get("tagline", "Key highlights and active systems."))}</desc>\n'
        )

        # ── Defs: Cursor blink style, Card clipPaths, & Typewriter paths ─
        defs_parts: list[str] = [
            '  <defs>',
            '    <style>',
            '      @keyframes cursorBlink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }',
            '      .hdr-cursor { animation: cursorBlink 1s step-end infinite; }',
            '    </style>',
        ]

        # ClipPaths for cards so accent bars follow the rounded corners perfectly
        for i in range(num_cards):
            x = i * (card_w + self.CARD_GAP)
            defs_parts.append(
                f'    <clipPath id="card-clip-{i}">\n'
                f'      <rect x="{x}" y="{cards_y}" width="{card_w}" height="{self.CARD_H}" rx="{self.CARD_RX}" />\n'
                f'    </clipPath>'
            )

        parts.append("\n".join(defs_parts) + "\n")
        parts.append(tw_paths)
        parts.append("  </defs>\n\n")

        # ── Welcome Bar (Body) ──────────────────────────────────
        bar_bg = theme.bg_subtle

        # Bar background
        parts.append(rect(
            0, 0, self.WIDTH, self.WELCOME_H,
            bar_bg, rx=self.CARD_RX,
            stroke=theme.border_muted, stroke_width=1,
        ))

        # Terminal prompt (>_)
        parts.append(
            f'  <text x="18" y="{bar_mid_y + 1}" '
            f'font-family="{theme.font_mono}" font-size="14" font-weight="700" dominant-baseline="middle">'
            f'<tspan fill="{theme.accent_primary}">&gt;</tspan>'
            f'<tspan fill="{theme.accent_success}" class="hdr-cursor">_</tspan>'
            f'</text>\n'
        )

        # Typewriter text elements (referencing paths in defs)
        parts.append(tw_texts)

        # Status telemetry badge on right side of Welcome Bar
        badge_text = "FLEET ACTIVE"
        badge_w = len(badge_text) * 7.2 + 26
        badge_h = 24
        badge_x = self.WIDTH - badge_w - 14
        badge_y = (self.WELCOME_H - badge_h) / 2
        parts.append(rect(
            badge_x, badge_y, badge_w, badge_h,
            theme.bg_overlay, rx=4,
            stroke=theme.border_muted, stroke_width=0.8,
        ))
        parts.append(circle(badge_x + 10, bar_mid_y, 3, theme.accent_success))
        parts.append(text(
            badge_x + 19, bar_mid_y + 3.5,
            badge_text, theme.accent_success, theme.font_mono,
            font_size=10, font_weight=700, letter_spacing=0.5,
        ))

        # ── Highlight Cards ─────────────────────────────────────
        accent_colors = {
            "bot": theme.accent_primary,
            "audio": theme.accent_secondary,
            "ai": theme.accent_success,
            "infra": theme.accent_warning,
        }

        status_map = {
            "bot": "always online",
            "audio": "real-time",
            "ai": "multi-model",
            "infra": "self-hosted",
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

            # Top accent line — clipped perfectly to card's rounded corners
            parts.append(
                f'  <rect x="{x}" y="{cards_y}" width="{card_w}" height="3" '
                f'fill="{accent}" clip-path="url(#card-clip-{i})" />\n'
            )

            # Accent dot
            parts.append(circle(x + 16, cards_y + 26, 3.5, accent))

            # Label
            parts.append(text(
                x + 28, cards_y + 30,
                hl.get("label", ""),
                theme.fg_default, theme.font_mono,
                font_size=12.5, font_weight=700,
            ))

            # Detail
            parts.append(text(
                x + 16, cards_y + 49,
                hl.get("detail", ""),
                theme.fg_muted, theme.font_mono,
                font_size=10.5,
            ))

            # Status with active telemetry dot
            status_text = status_map.get(icon_type, "")
            parts.append(circle(x + 18, cards_y + 62.5, 2.5, theme.accent_success))
            parts.append(text(
                x + 25, cards_y + 65.5,
                status_text,
                theme.fg_muted, theme.font_mono,
                font_size=9.5, letter_spacing=0.3,
            ))

        # ── Integrated Telemetry Pills Row ──────────────────────
        if has_telemetry:
            telem_y = cards_y + self.CARD_H + self.TELEMETRY_GAP
            num_pills = len(active_metrics)
            pill_gap = 10
            pill_w = (self.WIDTH - ((num_pills - 1) * pill_gap)) / num_pills

            for idx, item in enumerate(active_metrics):
                px = idx * (pill_w + pill_gap)
                py = telem_y
                accent = item["accent"]

                # Pill background
                parts.append(rect(
                    px, py, pill_w, self.TELEMETRY_H,
                    theme.bg_subtle, rx=6,
                    stroke=theme.border_muted, stroke_width=1,
                ))

                # Left accent indicator bar
                parts.append(rect(
                    px, py + 5, 2.5, self.TELEMETRY_H - 10,
                    fill=accent, rx=1.25,
                ))

                # Icon (14x14)
                parts.append(render_icon(
                    item["icon"],
                    px + 12,
                    py + (self.TELEMETRY_H - 14) / 2,
                    14,
                    accent,
                ))

                # Metric text (bold value + muted label)
                parts.append(
                    f'  <text x="{px + 34}" y="{py + self.TELEMETRY_H / 2 + 4}" '
                    f'font-family="{theme.font_mono}">\n'
                    f'    <tspan font-size="11.5" font-weight="800" fill="{theme.fg_default}">{_esc(item["val"])}</tspan>\n'
                    f'    <tspan font-size="10" font-weight="500" fill="{theme.fg_muted}">  {_esc(item["label"])}</tspan>\n'
                    f'  </text>\n'
                )

                # Right subtle status dot
                parts.append(circle(
                    px + pill_w - 14,
                    py + self.TELEMETRY_H / 2,
                    2.5,
                    fill=accent,
                ))

        parts.append(svg_close())
        return "".join(parts)

