"""Banner builder — Hero identity + code editor.

Generates a banner with two zones:
  - Top: Identity hero area with handle, role, and a subtle tech grid
  - Bottom: Code editor with TypeScript manifest

Design:
  - Full-width (880px) to fill GitHub content area
  - Distinct identity zone gives personality and visual hook
  - Code zone provides technical depth
  - Single animation: blinking cursor
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, style_block, defs_block,
    window_chrome, file_tab, code_line_numbered,
    status_bar, cursor_blink_style, text, rect, line, circle,
    _esc,
)


@register_builder("banner")
class BannerBuilder(BaseBuilder):
    """Generates the hero banner SVG."""

    WIDTH = 880
    HERO_H = 120
    HEADER_H = 36
    STATUSLINE_H = 28
    LINE_HEIGHT = 23
    CODE_PADDING_TOP = 20

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        banner_cfg = config["banner"]
        identity = config["identity"]
        stack = config.get("stack", {})

        code_lines = banner_cfg.get("code_lines", [])
        num_lines = len(code_lines)

        # Calculate total height dynamically
        code_zone_h = (
            self.HEADER_H + self.CODE_PADDING_TOP
            + (num_lines * self.LINE_HEIGHT)
            + 16 + self.STATUSLINE_H
        )
        total_h = self.HERO_H + code_zone_h

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{identity['handle']} — {identity['role']}",
            f"Profile banner for {identity['handle']}: "
            f"{identity['tagline']}",
        ))

        # ── Defs ────────────────────────────────────────────────
        gradient = (
            f'    <linearGradient id="heroBg" x1="0%" y1="0%" x2="100%" y2="100%">\n'
            f'      <stop offset="0%" stop-color="{theme.bg_canvas}" />\n'
            f'      <stop offset="100%" stop-color="{theme.bg_subtle}" />\n'
            f'    </linearGradient>\n'
        )
        parts.append(defs_block(gradient))

        # ── Styles ──────────────────────────────────────────────
        css = cursor_blink_style()
        css += (
            f'    .hero-tag {{\n'
            f'      font-family: {theme.font_mono};\n'
            f'      font-size: 10px;\n'
            f'      letter-spacing: 0.5px;\n'
            f'    }}\n'
        )
        parts.append(style_block(css))

        # ── Main container ──────────────────────────────────────
        parts.append(rect(0, 0, self.WIDTH, total_h, theme.bg_canvas, rx=10,
                          stroke=theme.border_default, stroke_width=1))

        # ── HERO ZONE ───────────────────────────────────────────
        parts.append(rect(0, 0, self.WIDTH, self.HERO_H, "url(#heroBg)", rx=10))
        # Clip bottom corners
        parts.append(rect(0, self.HERO_H - 10, self.WIDTH, 10, "url(#heroBg)"))

        # Handle name — large and bold
        parts.append(text(
            28, 42, identity["handle"], theme.fg_default, theme.font_sans,
            font_size=28, font_weight=700,
        ))

        # Role — muted, below the name
        parts.append(text(
            28, 66, identity["role"], theme.fg_muted, theme.font_sans,
            font_size=14,
        ))

        # Tagline — subtle
        parts.append(text(
            28, 86, identity["tagline"], theme.fg_subtle, theme.font_mono,
            font_size=11,
        ))

        # Tech pills in the hero (right-aligned, from stack keys)
        pill_x = self.WIDTH - 20
        pill_y = 20
        all_items = []
        for cat_data in stack.values():
            all_items.extend(cat_data.get("items", []))

        # Show up to 12 techs as subtle pills, right-aligned in 2 rows
        display_items = all_items[:12]
        row_items = [display_items[:6], display_items[6:]]

        for row_idx, row in enumerate(row_items):
            rx = pill_x
            ry = pill_y + (row_idx * 24)
            for item in reversed(row):
                pw = len(item) * 6.5 + 14
                rx -= pw + 5
                parts.append(rect(
                    rx, ry, pw, 18, theme.bg_overlay, rx=4,
                    stroke=theme.border_muted, stroke_width=0.5,
                ))
                parts.append(text(
                    rx + pw / 2, ry + 13, item, theme.fg_subtle,
                    theme.font_mono, font_size=10, text_anchor="middle",
                ))

        # Accent line between hero and code
        parts.append(rect(0, self.HERO_H - 2, self.WIDTH, 2, theme.accent_primary,
                          opacity=0.15))

        # ── CODE EDITOR ZONE ────────────────────────────────────
        editor_y = self.HERO_H

        # Editor header
        parts.append(rect(0, editor_y, self.WIDTH, self.HEADER_H,
                          theme.bg_inset))
        parts.append(line(0, editor_y + self.HEADER_H, self.WIDTH,
                          editor_y + self.HEADER_H, theme.border_default, 1))

        # Traffic lights
        dot_y = editor_y + self.HEADER_H // 2
        parts.append(circle(18, dot_y, 5, "#f85149"))
        parts.append(circle(34, dot_y, 5, "#d29922"))
        parts.append(circle(50, dot_y, 5, "#3fb950"))

        # File tabs
        tab_x = 68
        active_tab, active_w = file_tab(
            tab_x, editor_y + 5, banner_cfg["filename"], theme,
            active=True, icon_color=theme.accent_primary,
        )
        parts.append(active_tab)

        inactive_tab, _ = file_tab(
            tab_x + active_w + 6, editor_y + 5, "package.json", theme,
            active=False,
        )
        parts.append(inactive_tab)

        # Language badge
        lang = banner_cfg["language"]
        badge_w = len(lang) * 7 + 16
        parts.append(rect(
            self.WIDTH - badge_w - 14, editor_y + 8,
            badge_w, 20, theme.bg_overlay, rx=4,
            stroke=theme.border_muted, stroke_width=0.8,
        ))
        parts.append(text(
            self.WIDTH - badge_w // 2 - 14, editor_y + 22,
            lang, theme.accent_primary, theme.font_mono,
            font_size=11, font_weight=600, text_anchor="middle",
        ))

        # ── Code lines ──────────────────────────────────────────
        code_y_start = editor_y + self.HEADER_H + self.CODE_PADDING_TOP

        for i, code_line_data in enumerate(code_lines):
            tokens = code_line_data.get("tokens", [])
            is_last = (i == num_lines - 1)
            y = code_y_start + (i * self.LINE_HEIGHT)

            parts.append(code_line_numbered(
                line_num=i + 1, y=y, tokens=tokens, theme=theme,
                is_active=is_last,
            ))

        # Blinking cursor
        if code_lines:
            last_tokens = code_lines[-1].get("tokens", [])
            last_len = sum(len(t.get("text", "")) for t in last_tokens)
            cx = 52 + max(last_len * 7.8, 8)
            cy = code_y_start + ((num_lines - 1) * self.LINE_HEIGHT)
            parts.append(text(
                cx, cy, "\u2588", theme.accent_primary,
                theme.font_mono, font_size=14, css_class="cursor-blink",
            ))

        # ── Statusline ──────────────────────────────────────────
        sl_y = total_h - self.STATUSLINE_H
        parts.append(status_bar(
            0, sl_y, self.WIDTH, self.STATUSLINE_H,
            segments=[
                {"text": "NORMAL", "bg": theme.accent_primary,
                 "fg": theme.bg_inset, "bold": True},
                {"text": f"\u2003{banner_cfg['git_branch']}",
                 "fg": theme.accent_secondary, "bold": True},
                {"text": banner_cfg["filename"],
                 "fg": theme.fg_default},
                {"text": "[utf-8]", "fg": theme.fg_subtle},
                {"text": "\u25cf LSP ready", "fg": theme.accent_success},
            ],
            theme=theme,
        ))

        parts.append(svg_close())
        return "".join(parts)
