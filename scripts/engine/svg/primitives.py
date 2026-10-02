"""SVG primitives — reusable building blocks for all builders.

This module provides composable SVG components that builders use
to construct their output. Every visual element is generated through
these primitives to ensure consistency across all cards.
"""

from __future__ import annotations

from typing import List, Optional
from ..core.theme import Theme


def _esc(text: str) -> str:
    """Escape text for safe XML/SVG embedding."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_open(
    width: int,
    height: int,
    title: str,
    desc: str,
) -> str:
    """Open an SVG root element with accessibility attributes."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" '
        f'role="img" aria-labelledby="svgTitle svgDesc">\n'
        f'  <title id="svgTitle">{_esc(title)}</title>\n'
        f'  <desc id="svgDesc">{_esc(desc)}</desc>\n'
    )


def svg_close() -> str:
    """Close the SVG root element."""
    return '</svg>\n'


def defs_block(content: str) -> str:
    """Wrap content inside a <defs> element."""
    return f'  <defs>\n{content}  </defs>\n'


def style_block(css: str) -> str:
    """Wrap CSS inside a <style> element."""
    return f'  <style>\n{css}  </style>\n'


def rect(
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
    fill: str,
    rx: int | float = 0,
    stroke: Optional[str] = None,
    stroke_width: float = 1.0,
    opacity: float = 1.0,
) -> str:
    """Generate an SVG rect element."""
    attrs = (
        f'x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{rx}" fill="{fill}"'
    )
    if stroke:
        attrs += f' stroke="{stroke}" stroke-width="{stroke_width}"'
    if opacity < 1.0:
        attrs += f' opacity="{opacity}"'
    return f'  <rect {attrs} />\n'


def circle(
    cx: int | float,
    cy: int | float,
    r: int | float,
    fill: str,
    opacity: float = 1.0,
) -> str:
    """Generate an SVG circle element."""
    attrs = f'cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
    if opacity < 1.0:
        attrs += f' opacity="{opacity}"'
    return f'  <circle {attrs} />\n'


def text(
    x: int | float,
    y: int | float,
    content: str,
    fill: str,
    font_family: str,
    font_size: int | float = 13,
    font_weight: int | str = "normal",
    text_anchor: str = "start",
    letter_spacing: Optional[float] = None,
    css_class: Optional[str] = None,
    opacity: float = 1.0,
) -> str:
    """Generate a simple SVG text element."""
    attrs = (
        f'x="{x}" y="{y}" fill="{fill}" '
        f'font-family="{font_family}" font-size="{font_size}"'
    )
    if font_weight != "normal":
        attrs += f' font-weight="{font_weight}"'
    if text_anchor != "start":
        attrs += f' text-anchor="{text_anchor}"'
    if letter_spacing is not None:
        attrs += f' letter-spacing="{letter_spacing}"'
    if css_class:
        attrs += f' class="{css_class}"'
    if opacity < 1.0:
        attrs += f' opacity="{opacity}"'
    return f'  <text {attrs}>{_esc(content)}</text>\n'


def tspan(content: str, fill: str) -> str:
    """Generate a tspan element (for inline color changes within text)."""
    return f'<tspan fill="{fill}">{_esc(content)}</tspan>'


def line(
    x1: int | float,
    y1: int | float,
    x2: int | float,
    y2: int | float,
    stroke: str,
    stroke_width: float = 1.0,
) -> str:
    """Generate an SVG line element."""
    return (
        f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" />\n'
    )


def group(content: str, transform: Optional[str] = None) -> str:
    """Wrap content inside a <g> element with optional transform."""
    if transform:
        return f'  <g transform="{transform}">\n{content}  </g>\n'
    return f'  <g>\n{content}  </g>\n'


# ── Higher-level composites ────────────────────────────────────────

def window_chrome(
    width: int,
    height: int,
    theme: Theme,
    header_height: int = 42,
) -> str:
    """Render macOS-style window chrome (background + traffic lights)."""
    # Main container
    out = rect(0, 0, width, height, theme.bg_canvas, rx=10,
               stroke=theme.border_default, stroke_width=1)

    # Header bar
    out += rect(0, 0, width, header_height, theme.bg_inset, rx=10)
    out += rect(0, header_height - 10, width, 10, theme.bg_inset)
    out += line(0, header_height, width, header_height,
                theme.border_default, 1)

    # Traffic light dots with theme colors
    dot_y = header_height // 2
    out += circle(20, dot_y, 5.5, theme.accent_danger)   # Close (red)
    out += circle(38, dot_y, 5.5, theme.accent_warning)  # Minimize (yellow)
    out += circle(56, dot_y, 5.5, theme.accent_success)  # Maximize (green)

    return out


def file_tab(
    x: int,
    y: int,
    label: str,
    theme: Theme,
    active: bool = False,
    icon_color: Optional[str] = None,
) -> str:
    """Render a file tab in the window header."""
    tab_w = max(len(label) * 8 + 36, 100)
    tab_h = 26

    if active:
        bg = theme.bg_canvas
        border = theme.border_default
        text_color = theme.fg_default
    else:
        bg = theme.bg_inset
        border = "none"
        text_color = theme.fg_muted

    out = rect(x, y, tab_w, tab_h, bg, rx=6,
               stroke=border if border != "none" else None,
               stroke_width=0.8 if active else 0)

    # File icon dot
    icon = icon_color or theme.accent_primary
    out += circle(x + 12, y + tab_h // 2, 3, icon)

    # Tab label
    out += text(x + 22, y + tab_h // 2 + 4, label, text_color,
                theme.font_mono, font_size=11.5,
                font_weight=600 if active else "normal")

    return out, tab_w


def code_line_numbered(
    line_num: int,
    y: int,
    tokens: List[dict],
    theme: Theme,
    gutter_x: int = 28,
    code_x: int = 52,
    is_active: bool = False,
) -> str:
    """Render a single line of code with a line number and syntax tokens."""
    # Line number
    ln_color = theme.accent_primary if is_active else theme.fg_subtle
    ln_weight = 700 if is_active else "normal"
    out = text(gutter_x, y, str(line_num), ln_color, theme.font_mono,
               font_size=14, font_weight=ln_weight, text_anchor="end")

    if not tokens:
        return out

    # Build tspan-based colored text
    tspans = []
    for token in tokens:
        token_type = token.get("type", "punctuation")
        token_text = token.get("text", "")
        color = _resolve_syntax_color(token_type, theme)
        tspans.append(f'<tspan fill="{color}">{_esc(token_text)}</tspan>')

    tspan_str = "".join(tspans)
    out += (
        f'  <text x="{code_x}" y="{y}" '
        f'font-family="{theme.font_mono}" font-size="14">'
        f'{tspan_str}</text>\n'
    )

    return out


def status_bar(
    x: int,
    y: int,
    width: int,
    height: int,
    segments: List[dict],
    theme: Theme,
) -> str:
    """Render a Neovim-style status bar."""
    out = rect(x, y, width, height, theme.bg_inset)
    out += line(x, y, x + width, y, theme.border_default, 1)

    cursor_x = x + 8
    for seg in segments:
        seg_text = seg["text"]
        seg_fg = seg.get("fg", theme.fg_muted)
        seg_bg = seg.get("bg")
        seg_bold = seg.get("bold", False)

        if seg_bg:
            text_w = len(seg_text) * 7.5 + 16
            out += rect(cursor_x, y + 5, text_w, height - 10,
                        seg_bg, rx=3)
            out += text(
                cursor_x + text_w / 2, y + height / 2 + 4,
                seg_text, seg_fg, theme.font_mono,
                font_size=11, font_weight=700, text_anchor="middle",
            )
            cursor_x += text_w + 12
        else:
            out += text(
                cursor_x, y + height / 2 + 4,
                seg_text, seg_fg, theme.font_mono,
                font_size=11, font_weight=600 if seg_bold else "normal",
            )
            cursor_x += len(seg_text) * 7 + 12

    return out


def terminal_header(
    width: int,
    command: str,
    theme: Theme,
    header_height: int = 36,
    status_text: Optional[str] = None,
    status_color: Optional[str] = None,
) -> str:
    """Render a terminal-style header with prompt and optional status badge."""
    out = rect(0, 0, width, header_height, theme.bg_inset, rx=10)
    out += rect(0, header_height - 10, width, 10, theme.bg_inset)
    out += line(0, header_height, width, header_height,
                theme.border_default, 1)

    # Traffic lights with theme accents
    dot_y = header_height // 2
    out += circle(16, dot_y, 4.5, theme.accent_danger)
    out += circle(32, dot_y, 4.5, theme.accent_warning)
    out += circle(48, dot_y, 4.5, theme.accent_success)

    # Prompt & command
    prompt_x = 68
    prompt_parts = (
        f'<tspan fill="{theme.accent_success}" font-weight="600">'
        f'{_esc("jharlyok@dev")}</tspan>'
        f'<tspan fill="{theme.fg_subtle}">:</tspan>'
        f'<tspan fill="{theme.accent_primary}" font-weight="600">'
        f'{_esc("~")}</tspan>'
        f'<tspan fill="{theme.fg_subtle}">$ </tspan>'
        f'<tspan fill="{theme.fg_default}">{_esc(command)}</tspan>'
    )
    out += (
        f'  <text x="{prompt_x}" y="{dot_y + 4}" '
        f'font-family="{theme.font_mono}" font-size="12">'
        f'{prompt_parts}</text>\n'
    )

    if status_text:
        s_color = status_color or theme.accent_success
        badge_w = len(status_text) * 7 + 24
        badge_x = width - badge_w - 12
        out += rect(badge_x, 8, badge_w, header_height - 16,
                     theme.bg_overlay, rx=4,
                     stroke=theme.border_muted, stroke_width=0.8)
        out += circle(badge_x + 10, dot_y, 3, s_color)
        out += text(badge_x + 20, dot_y + 4, status_text, s_color,
                     theme.font_mono, font_size=10.5, font_weight=600)

    return out


def cursor_blink_style() -> str:
    """Return CSS keyframes for a blinking cursor animation."""
    return (
        '    @keyframes blink {\n'
        '      0%, 100% { opacity: 1; }\n'
        '      50% { opacity: 0; }\n'
        '    }\n'
        '    .cursor-blink {\n'
        '      animation: blink 1.1s step-end infinite;\n'
        '    }\n'
    )


def _resolve_syntax_color(token_type: str, theme: Theme) -> str:
    """Map a token type string to the corresponding theme color."""
    mapping = {
        "keyword": theme.syntax.keyword,
        "string": theme.syntax.string,
        "comment": theme.syntax.comment,
        "type": theme.syntax.type,
        "property": theme.syntax.property,
        "function": theme.syntax.function,
        "punctuation": theme.syntax.punctuation,
    }
    return mapping.get(token_type, theme.fg_default)
