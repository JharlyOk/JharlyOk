"""Stack matrix builder — categorized tech grid.

Generates a clean grid layout showing the user's technology stack
organized by category. Each category is a column with labeled items.

Design:
  - Terminal window with category columns
  - Items as subtle pill badges
  - Consistent spacing and alignment
  - All data from config.stack{}
"""

from __future__ import annotations

import math
from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close,
    rect, text, line,
    terminal_header, _esc,
)


@register_builder("stack")
class StackMatrixBuilder(BaseBuilder):
    """Generates the tech stack matrix SVG."""

    WIDTH = 880
    HEADER_H = 36
    COL_WIDTH = 275
    COLS_PER_ROW = 3
    CATEGORY_HEIGHT = 28
    ITEM_HEIGHT = 24
    PADDING_X = 24
    PADDING_Y = 16
    GAP_X = 10
    GAP_Y = 14

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        stack = config.get("stack", {})
        categories = list(stack.items())
        num_cats = len(categories)

        # Calculate rows needed
        num_rows = math.ceil(num_cats / self.COLS_PER_ROW)

        # Height per row = category header + max items in row + gaps
        row_heights = []
        for row_idx in range(num_rows):
            start = row_idx * self.COLS_PER_ROW
            end = min(start + self.COLS_PER_ROW, num_cats)
            max_items = max(
                len(categories[i][1]["items"])
                for i in range(start, end)
            )
            row_h = (
                self.CATEGORY_HEIGHT
                + (max_items * self.ITEM_HEIGHT)
                + self.GAP_Y * 2
            )
            row_heights.append(row_h)

        content_h = sum(row_heights) + self.PADDING_Y * 2
        total_h = self.HEADER_H + content_h

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{config['identity']['handle']} — Technology Stack",
            "Categorized overview of technologies and tools.",
        ))

        # ── Background ──────────────────────────────────────────
        parts.append(rect(
            0, 0, self.WIDTH, total_h, theme.bg_canvas, rx=10,
            stroke=theme.border_default, stroke_width=1,
        ))

        # ── Terminal Header ─────────────────────────────────────
        parts.append(terminal_header(
            self.WIDTH, "cat /etc/stack.yaml", theme,
            self.HEADER_H,
            status_text=f"{num_cats} categories",
            status_color=theme.accent_primary,
        ))

        # ── Category Grid ──────────────────────────────────────
        cursor_y = self.HEADER_H + self.PADDING_Y

        for row_idx in range(num_rows):
            start = row_idx * self.COLS_PER_ROW
            end = min(start + self.COLS_PER_ROW, num_cats)

            for col_offset, cat_idx in enumerate(range(start, end)):
                key, cat_data = categories[cat_idx]
                label = cat_data["label"]
                items = cat_data["items"]

                col_x = self.PADDING_X + (col_offset * (self.COL_WIDTH + self.GAP_X))

                # Category label
                parts.append(text(
                    col_x, cursor_y + 14,
                    label, theme.fg_muted, theme.font_mono,
                    font_size=10, font_weight=600,
                    letter_spacing=0.5,
                ))

                # Underline
                parts.append(line(
                    col_x, cursor_y + 20,
                    col_x + self.COL_WIDTH - 20, cursor_y + 20,
                    theme.border_muted, 0.5,
                ))

                # Items as pills
                item_y = cursor_y + self.CATEGORY_HEIGHT + 6

                for item_text in items:
                    pill_w = len(item_text) * 7 + 18
                    parts.append(rect(
                        col_x, item_y, pill_w, 20,
                        theme.bg_subtle, rx=4,
                        stroke=theme.border_muted, stroke_width=0.5,
                    ))
                    parts.append(text(
                        col_x + 9, item_y + 14,
                        item_text, theme.fg_default, theme.font_mono,
                        font_size=11,
                    ))
                    item_y += self.ITEM_HEIGHT

            cursor_y += row_heights[row_idx]

        parts.append(svg_close())
        return "".join(parts)
