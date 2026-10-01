"""Header builder — Terminal-style identity card.

Generates a terminal window running `whoami --verbose` that outputs
the user's identity in a neofetch-inspired format. Consistent with
the terminal aesthetic of projects and stack cards.

Design:
  - Same terminal chrome as other cards
  - Structured output with key-value pairs
  - Highlight metrics inline
  - No gradients, no dashboard widgets
"""

from __future__ import annotations

from typing import Any, Dict

from ..registry import BaseBuilder, register_builder
from ..theme_loader import Theme
from ..svg_primitives import (
    svg_open, svg_close,
    rect, text, line, circle,
    terminal_header, _esc,
)


@register_builder("header")
class HeaderBuilder(BaseBuilder):
    """Generates the terminal-style identity card SVG."""

    WIDTH = 880
    HEADER_H = 36
    LINE_H = 20
    PADDING_X = 24
    KEY_X = 40        # After the prompt symbol
    VAL_X = 200       # Value column
    SECTION_GAP = 10  # Extra gap between sections

    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        identity = config["identity"]
        highlights = identity.get("highlights", [])
        about_lines = identity.get("about", [])
        contact = config.get("contact", {})

        # Build the terminal output lines
        output_lines = self._build_output(identity, highlights, about_lines, contact)

        # Calculate height
        content_h = len(output_lines) * self.LINE_H + 28
        total_h = self.HEADER_H + content_h

        parts: list[str] = []

        # ── SVG Root ────────────────────────────────────────────
        parts.append(svg_open(
            self.WIDTH, total_h,
            f"{identity['handle']} — {identity['role']}",
            identity.get("tagline", ""),
        ))

        # ── Background ──────────────────────────────────────────
        parts.append(rect(0, 0, self.WIDTH, total_h, theme.bg_canvas, rx=10,
                          stroke=theme.border_default, stroke_width=1))

        # ── Terminal Header ─────────────────────────────────────
        parts.append(terminal_header(
            self.WIDTH, "whoami --verbose", theme,
            self.HEADER_H,
            status_text="identity",
            status_color=theme.accent_primary,
        ))

        # ── Output Lines ────────────────────────────────────────
        y = self.HEADER_H + 22

        for entry in output_lines:
            kind = entry.get("kind", "kv")

            if kind == "blank":
                y += self.SECTION_GAP
                continue

            if kind == "section":
                # Section header with subtle accent
                parts.append(text(
                    self.PADDING_X, y, entry["text"],
                    theme.accent_primary, theme.font_mono,
                    font_size=11, font_weight=600, letter_spacing=0.5,
                ))
                y += self.LINE_H
                # Underline
                parts.append(line(
                    self.PADDING_X, y - 8,
                    self.PADDING_X + len(entry["text"]) * 7, y - 8,
                    theme.accent_primary, 0.3,
                ))
                continue

            if kind == "kv":
                key = entry.get("key", "")
                val = entry.get("val", "")
                val_color = entry.get("color", theme.fg_default)

                # Key (muted)
                parts.append(text(
                    self.KEY_X, y, key, theme.fg_subtle,
                    theme.font_mono, font_size=12,
                ))
                # Value
                parts.append(text(
                    self.VAL_X, y, val, val_color,
                    theme.font_mono, font_size=12, font_weight=500,
                ))
                y += self.LINE_H
                continue

            if kind == "text":
                parts.append(text(
                    self.KEY_X, y, entry["text"],
                    theme.fg_muted, theme.font_mono, font_size=11.5,
                ))
                y += self.LINE_H
                continue

            if kind == "highlight":
                # Dot + label + detail
                dot_color = entry.get("dot", theme.accent_primary)
                parts.append(circle(
                    self.KEY_X + 4, y - 4, 3.5, dot_color,
                ))
                parts.append(text(
                    self.KEY_X + 16, y, entry.get("label", ""),
                    theme.fg_default, theme.font_mono,
                    font_size=12, font_weight=600,
                ))
                parts.append(text(
                    self.KEY_X + 200, y, entry.get("detail", ""),
                    theme.fg_subtle, theme.font_mono,
                    font_size=11,
                ))
                y += self.LINE_H
                continue

        parts.append(svg_close())
        return "".join(parts)

    def _build_output(
        self,
        identity: dict,
        highlights: list,
        about_lines: list,
        contact: dict,
    ) -> list[dict]:
        """Build structured output lines for the terminal display."""

        icon_colors_map = {
            "bot": "#58a6ff",
            "audio": "#bc8cff",
            "ai": "#3fb950",
            "infra": "#d29922",
        }

        lines: list[dict] = []

        # Identity section
        lines.append({"kind": "section", "text": "IDENTITY"})
        lines.append({"kind": "kv", "key": "handle", "val": f"@{identity['handle']}"})
        lines.append({"kind": "kv", "key": "role", "val": identity["role"],
                       "color": "#58a6ff"})
        lines.append({"kind": "kv", "key": "method", "val": identity.get("methodology", "")})

        lines.append({"kind": "blank"})

        # About section
        lines.append({"kind": "section", "text": "ABOUT"})
        for about in about_lines:
            lines.append({"kind": "text", "text": about})

        lines.append({"kind": "blank"})

        # Highlights
        lines.append({"kind": "section", "text": "ACTIVE SYSTEMS"})
        for hl in highlights:
            icon_type = hl.get("icon", "bot")
            lines.append({
                "kind": "highlight",
                "label": hl.get("label", ""),
                "detail": hl.get("detail", ""),
                "dot": icon_colors_map.get(icon_type, "#58a6ff"),
            })

        lines.append({"kind": "blank"})

        # Contact
        if contact:
            lines.append({"kind": "section", "text": "REACH"})
            if contact.get("telegram"):
                lines.append({"kind": "kv", "key": "telegram",
                               "val": contact["telegram"]})
            if contact.get("discord"):
                lines.append({"kind": "kv", "key": "discord",
                               "val": contact["discord"]})
            if contact.get("email"):
                lines.append({"kind": "kv", "key": "email",
                               "val": contact["email"]})

        return lines
