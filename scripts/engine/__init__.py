"""JharlyOk Profile Engine v2 — Modular 4-layer SVG generation system.

Architecture:
  - engine.core: Configuration loading, theme tokens, builder registry
  - engine.svg: Primitives, window chrome, vector icons
  - engine.markdown: Profile README.md assembler
  - engine.builders: Component visual builders (header, banner, projects, stack, connect, badges)
"""

from . import core
from . import svg
from . import markdown
from . import builders

__all__ = ["core", "svg", "markdown", "builders"]
