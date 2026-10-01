"""SVG component builders.

Each module in this package registers itself with the builder registry.
Importing this package triggers auto-registration of all builders.
"""

from . import header
from . import banner
from . import projects
from . import stack_matrix
