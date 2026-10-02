"""Projects builder — terminal-style project listing.

Generates a clean terminal window showing the user's projects
in a tree-like format with name, type, description, and tech tags.

Design:
  - Terminal window with prompt in header
  - Tree structure (├─, └─) for visual hierarchy
  - Tech tags rendered as subtle inline labels
  - All data from config.projects[]
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.registry import BaseBuilder, register_builder
from ..core.theme import Theme
from ..svg.primitives import (
    svg_open, svg_close,
    rect, text, line, circle,
    terminal_header, _esc,
)


@register_builder("projects")
class ProjectsBuilder(BaseBuilder):
    """Generates the projects panel SVG."""

    WIDTH = 880
    HEADER_H = 36
    PROJECT_HEIGHT = 64
    PADDING_X = 24
    PADDING_TOP = 14

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        proj_data = config.get("projects", [])
        if isinstance(proj_data, dict):
            projects: List[dict] = proj_data.get("items", [])
        else:
            projects = proj_data or []
        num_projects = len(projects)

        # Calculate height dynamically
        content_h = (num_projects * self.PROJECT_HEIGHT) + self.PADDING_TOP + 28
        total_h = self.HEADER_H + content_h

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{config['identity']['handle']} — Active Projects",
            "Project portfolio and tech stack overview.",
        ))

        # ── Background ──────────────────────────────────────────
        parts.append(rect(
            0, 0, self.WIDTH, total_h, theme.bg_canvas, rx=10,
            stroke=theme.border_default, stroke_width=1,
        ))

        # ── Terminal Header ─────────────────────────────────────
        parts.append(terminal_header(
            self.WIDTH, "ls -la ~/projects --format=detailed", theme,
            self.HEADER_H,
            status_text=f"{num_projects} entries",
            status_color=theme.accent_primary,
        ))

        # ── Column headers ──────────────────────────────────────
        col_y = self.HEADER_H + 18
        parts.append(text(
            self.PADDING_X, col_y, "PROJECT", theme.fg_subtle,
            theme.font_mono, font_size=10, font_weight=600,
            letter_spacing=0.5,
        ))
        parts.append(text(
            200, col_y, "TYPE", theme.fg_subtle,
            theme.font_mono, font_size=10, font_weight=600,
            letter_spacing=0.5,
        ))
        parts.append(text(
            400, col_y, "DESCRIPTION", theme.fg_subtle,
            theme.font_mono, font_size=10, font_weight=600,
            letter_spacing=0.5,
        ))

        # Separator
        sep_y = col_y + 10
        parts.append(line(
            self.PADDING_X, sep_y,
            self.WIDTH - self.PADDING_X, sep_y,
            theme.border_muted, 0.5,
        ))

        # ── Project rows ────────────────────────────────────────
        row_y = sep_y + 24

        for i, project in enumerate(projects):
            is_last = (i == num_projects - 1)
            tree_char = "└─" if is_last else "├─"

            # Tree connector + project name
            parts.append(text(
                self.PADDING_X, row_y,
                tree_char, theme.fg_subtle, theme.font_mono,
                font_size=13,
            ))
            parts.append(text(
                self.PADDING_X + 26, row_y,
                project["name"], theme.fg_default, theme.font_mono,
                font_size=13, font_weight=600,
            ))

            # Type badge
            type_text = project.get("type", "")
            type_badge_w = len(type_text) * 6.5 + 14
            parts.append(rect(
                200, row_y - 12, type_badge_w, 18,
                theme.bg_overlay, rx=4,
                stroke=theme.border_muted, stroke_width=0.6,
            ))
            parts.append(text(
                200 + type_badge_w / 2, row_y,
                type_text, theme.accent_secondary, theme.font_mono,
                font_size=10, font_weight=500, text_anchor="middle",
            ))

            # Description
            desc = project.get("description", "")
            parts.append(text(
                400, row_y, desc, theme.fg_muted, theme.font_mono,
                font_size=11.5,
            ))

            # Tech tags on second line
            tag_y = row_y + 22
            tag_x = self.PADDING_X + 26

            # Continuation line
            if not is_last:
                parts.append(text(
                    self.PADDING_X, tag_y,
                    "│", theme.fg_subtle, theme.font_mono, font_size=13,
                ))

            tags = project.get("tags", [])
            for tag in tags:
                tag_w = len(tag) * 6.5 + 12
                parts.append(rect(
                    tag_x, tag_y - 11, tag_w, 16,
                    theme.bg_subtle, rx=3,
                    stroke=theme.border_muted, stroke_width=0.5,
                ))
                parts.append(text(
                    tag_x + tag_w / 2, tag_y,
                    tag, theme.accent_primary, theme.font_mono,
                    font_size=9.5, text_anchor="middle",
                ))
                tag_x += tag_w + 6

            row_y += self.PROJECT_HEIGHT

        parts.append(svg_close())
        return "".join(parts)
