"""SVG graphics layer — primitives, window chrome, and vector icons."""

from .primitives import (
    svg_open,
    svg_close,
    defs_block,
    style_block,
    rect,
    circle,
    text,
    tspan,
    line,
    group,
    window_chrome,
    file_tab,
    code_line_numbered,
    status_bar,
    terminal_header,
    cursor_blink_style,
    _esc,
)
from .icons import ICONS, render_icon

__all__ = [
    "svg_open",
    "svg_close",
    "defs_block",
    "style_block",
    "rect",
    "circle",
    "text",
    "tspan",
    "line",
    "group",
    "window_chrome",
    "file_tab",
    "code_line_numbered",
    "status_bar",
    "terminal_header",
    "cursor_blink_style",
    "_esc",
    "ICONS",
    "render_icon",
]
