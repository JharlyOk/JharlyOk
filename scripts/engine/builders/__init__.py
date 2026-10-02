"""SVG component builders.

Each module in this package registers itself with the builder registry.
Importing this package triggers auto-registration of all builders.
"""

from . import header
from . import banner
from . import projects
from . import stack_matrix
from . import socials
from . import stats
from . import badges
from .badges import compile_all_badges

__all__ = [
    "header",
    "banner",
    "projects",
    "stack_matrix",
    "socials",
    "stats",
    "badges",
    "compile_all_badges",
]
