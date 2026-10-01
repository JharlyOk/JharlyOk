"""Banner builder — Neovim/VS Code editor card with TypeScript manifest.

Generates a clean code-editor-style banner showing the user's profile
as a TypeScript config object. Uses theme-aware syntax highlighting,
macOS window chrome, file tabs, and a Neovim statusline.

Design principles:
  - Single panel. No split view, no gimmicks.
  - The only animation: a blinking cursor on the last line.
  - Uses GitHub Primer colors for native feel.
  - All data comes from config — zero hardcoded values.
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close, style_block,
    window_chrome, file_tab, code_line_numbered,
    status_bar, cursor_blink_style, text, rect, line,
)


@register_builder("banner")
class BannerBuilder(BaseBuilder):
    """Generates the hero banner SVG."""

    WIDTH = 800
    HEIGHT = 490
    HEADER_H = 44
    STATUSLINE_H = 30
    CODE_START_Y = 70
    LINE_HEIGHT = 24

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        banner_cfg = config["banner"]
        identity = config["identity"]

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, self.HEIGHT,
            f"{identity['handle']} — {identity['role']}",
            f"Profile banner for {identity['handle']}: "
            f"{identity['tagline']}",
        ))

        # ── Styles ──────────────────────────────────────────────
        parts.append(style_block(cursor_blink_style()))

        # ── Window Chrome ───────────────────────────────────────
        parts.append(window_chrome(
            self.WIDTH, self.HEIGHT, theme, self.HEADER_H,
        ))

        # ── File Tabs ───────────────────────────────────────────
        tab_y = 8
        tab_x = 76

        active_tab, active_w = file_tab(
            tab_x, tab_y, banner_cfg["filename"], theme,
            active=True, icon_color=theme.accent_primary,
        )
        parts.append(active_tab)

        # Second inactive tab (decorative)
        inactive_tab, _ = file_tab(
            tab_x + active_w + 6, tab_y, "tsconfig.json", theme,
            active=False,
        )
        parts.append(inactive_tab)

        # ── Filepath breadcrumb ─────────────────────────────────
        parts.append(text(
            16, self.HEADER_H + 18,
            f"{banner_cfg['filepath']}{banner_cfg['filename']}",
            theme.fg_muted, theme.font_mono, font_size=11,
        ))

        # ── Language badge (right side) ─────────────────────────
        lang = banner_cfg["language"]
        badge_w = len(lang) * 7 + 16
        parts.append(rect(
            self.WIDTH - badge_w - 16, self.HEADER_H + 6,
            badge_w, 20, theme.bg_overlay, rx=4,
            stroke=theme.border_muted, stroke_width=0.8,
        ))
        parts.append(text(
            self.WIDTH - badge_w // 2 - 16, self.HEADER_H + 20,
            lang, theme.accent_primary, theme.font_mono,
            font_size=11, font_weight=600, text_anchor="middle",
        ))

        # ── Separator line below breadcrumb ─────────────────────
        sep_y = self.HEADER_H + 30
        parts.append(line(0, sep_y, self.WIDTH, sep_y,
                          theme.border_muted, 0.5))

        # ── Code Buffer ────────────────────────────────────────
        code_lines = banner_cfg.get("code_lines", [])
        code_y_start = sep_y + 22

        for i, code_line_data in enumerate(code_lines):
            tokens = code_line_data.get("tokens", [])
            is_last = (i == len(code_lines) - 1)
            y = code_y_start + (i * self.LINE_HEIGHT)

            parts.append(code_line_numbered(
                line_num=i + 1,
                y=y,
                tokens=tokens,
                theme=theme,
                is_active=is_last,
            ))

        # ── Blinking cursor on last code line ───────────────────
        if code_lines:
            last_line_tokens = code_lines[-1].get("tokens", [])
            last_text_len = sum(len(t.get("text", "")) for t in last_line_tokens)
            cursor_x = 52 + max(last_text_len * 7.8, 8)
            cursor_y = code_y_start + ((len(code_lines) - 1) * self.LINE_HEIGHT)
            parts.append(text(
                cursor_x, cursor_y, "█", theme.accent_primary,
                theme.font_mono, font_size=13, css_class="cursor-blink",
            ))

        # ── Neovim Statusline ───────────────────────────────────
        sl_y = self.HEIGHT - self.STATUSLINE_H
        parts.append(status_bar(
            0, sl_y, self.WIDTH, self.STATUSLINE_H,
            segments=[
                {"text": "NORMAL", "bg": theme.accent_primary,
                 "fg": theme.bg_inset, "bold": True},
                {"text": f" {banner_cfg['git_branch']}",
                 "fg": theme.accent_secondary, "bold": True},
                {"text": banner_cfg["filename"],
                 "fg": theme.fg_default},
                {"text": "[utf-8 · lf]", "fg": theme.fg_subtle},
                {"text": "● LSP ready", "fg": theme.accent_success},
            ],
            theme=theme,
        ))

        parts.append(svg_close())
        return "".join(parts)
