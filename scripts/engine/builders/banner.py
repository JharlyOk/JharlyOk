"""Banner builder — Clean code editor card.

Generates a Neovim/VS Code-style editor showing the user's profile
as a TypeScript config object. Just code — identity is handled by
the separate header card.

Design:
  - Full-width editor panel (880px)
  - Syntax highlighting from theme tokens
  - Single animation: blinking cursor
  - macOS window chrome + Neovim statusline
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, style_block,
    window_chrome, file_tab, code_line_numbered,
    status_bar, cursor_blink_style, text, rect, line, circle,
)


@register_builder("banner")
class BannerBuilder(BaseBuilder):
    """Generates the code editor banner SVG."""

    WIDTH = 880
    HEADER_H = 40
    STATUSLINE_H = 28
    LINE_HEIGHT = 23

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        banner_cfg = config["banner"]
        identity = config["identity"]

        code_lines = banner_cfg.get("code_lines", [])
        num_lines = len(code_lines)

        # Dynamic height based on code lines
        code_area_h = (num_lines * self.LINE_HEIGHT) + 24
        total_h = self.HEADER_H + code_area_h + self.STATUSLINE_H

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{identity['handle']} — Code Manifest",
            f"TypeScript profile manifest for {identity['handle']}.",
        ))

        # ── Styles ──────────────────────────────────────────────
        parts.append(style_block(cursor_blink_style()))

        # ── Window Chrome ───────────────────────────────────────
        parts.append(window_chrome(
            self.WIDTH, total_h, theme, self.HEADER_H,
        ))

        # ── File Tabs ───────────────────────────────────────────
        tab_y = 7
        tab_x = 72

        active_tab, active_w = file_tab(
            tab_x, tab_y, banner_cfg["filename"], theme,
            active=True, icon_color=theme.accent_primary,
        )
        parts.append(active_tab)

        inactive_tab, _ = file_tab(
            tab_x + active_w + 6, tab_y, "package.json", theme,
            active=False,
        )
        parts.append(inactive_tab)

        # Language badge (right side of header)
        lang = banner_cfg["language"]
        badge_w = len(lang) * 7 + 16
        parts.append(rect(
            self.WIDTH - badge_w - 14, 10,
            badge_w, 20, theme.bg_overlay, rx=4,
            stroke=theme.border_muted, stroke_width=0.8,
        ))
        parts.append(text(
            self.WIDTH - badge_w // 2 - 14, 24,
            lang, theme.accent_primary, theme.font_mono,
            font_size=11, font_weight=600, text_anchor="middle",
        ))

        # ── Code Lines ──────────────────────────────────────────
        code_y_start = self.HEADER_H + 18

        for i, code_line_data in enumerate(code_lines):
            tokens = code_line_data.get("tokens", [])
            is_last = (i == num_lines - 1)
            y = code_y_start + (i * self.LINE_HEIGHT)

            parts.append(code_line_numbered(
                line_num=i + 1, y=y, tokens=tokens, theme=theme,
                is_active=is_last,
            ))

        # Blinking cursor on last line
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
