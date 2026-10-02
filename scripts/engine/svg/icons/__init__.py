"""Vector icons catalog and loader.

Loads standalone 24x24 SVG icon files dynamically from this directory.
Provides in-memory caching for zero-overhead rendering and full backwards
compatibility with `render_icon` and `ICONS`.

Adding a new icon:
  Simply drop a 24x24 `.svg` file (e.g. `docker.svg`, `python.svg`) into this
  folder. It will be automatically discovered and available everywhere.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Mapping

_ICONS_DIR = Path(__file__).parent
_CACHE: Dict[str, str] = {}

# Built-in aliases for convenience
_ALIASES: Dict[str, str] = {
    "views": "eye",
    "users": "followers",
    "people": "followers",
    "package": "repo",
}


def _load_all_icons() -> Dict[str, str]:
    """Scan directory and load path data from all SVG files into cache."""
    if _CACHE:
        return _CACHE

    path_regex = re.compile(r'd="([^"]+)"')

    for svg_file in _ICONS_DIR.glob("*.svg"):
        icon_name = svg_file.stem.lower()
        try:
            content = svg_file.read_text(encoding="utf-8")
            match = path_regex.search(content)
            if match:
                _CACHE[icon_name] = match.group(1).strip()
        except Exception:
            pass

    # Register aliases
    for alias, target in _ALIASES.items():
        if target in _CACHE and alias not in _CACHE:
            _CACHE[alias] = _CACHE[target]

    return _CACHE


def get_icon(name: str) -> str:
    """Get the 24x24 SVG path `d` string for an icon by name."""
    cache = _load_all_icons()
    name_clean = name.lower()
    return cache.get(name_clean, cache.get("web", ""))


def render_icon(
    name: str,
    x: int | float,
    y: int | float,
    size: int | float,
    fill: str,
) -> str:
    """Render an icon scaled to `size` at position `(x, y)` with given fill color."""
    path_d = get_icon(name)
    scale = size / 24.0
    return (
        f'  <g transform="translate({x}, {y}) scale({scale:.4f})">\n'
        f'    <path d="{path_d}" fill="{fill}" />\n'
        f'  </g>\n'
    )


def list_available_icons() -> List[str]:
    """Return a sorted list of all available icon names."""
    return sorted(_load_all_icons().keys())


class _IconsProxy(Mapping[str, str]):
    """Dict-like proxy providing backwards compatibility for ICONS dictionary."""

    def __getitem__(self, key: str) -> str:
        return get_icon(key)

    def __iter__(self):
        return iter(_load_all_icons())

    def __len__(self) -> int:
        return len(_load_all_icons())

    def get(self, key: str, default: str | None = None) -> str:
        cache = _load_all_icons()
        return cache.get(key.lower(), default if default is not None else cache.get("web", ""))


ICONS = _IconsProxy()

__all__ = ["render_icon", "get_icon", "ICONS", "list_available_icons"]
