"""Builder registry — auto-discovery and execution of SVG builders.

This implements the Builder Registry Pattern. Each builder is a class
that inherits from BaseBuilder and is decorated with @register_builder.
The build pipeline discovers all registered builders and runs them
against each theme variant.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Type

from .theme_loader import Theme


class BaseBuilder(ABC):
    """Abstract base class for all SVG builders.

    Every builder must implement `build()` which receives the
    profile config and active theme, and returns an SVG string.
    """

    # Subclasses set this via @register_builder
    builder_name: ClassVar[str] = ""

    @abstractmethod
    def build(self, config: Dict[str, Any], theme: Theme) -> str:
        """Generate SVG markup for this component.

        Args:
            config: Parsed profile.config.json.
            theme: Active theme tokens.

        Returns:
            Complete SVG string ready to be written to a file.
        """
        ...


# Global builder registry
_REGISTRY: Dict[str, Type[BaseBuilder]] = {}


def register_builder(name: str):
    """Decorator to register a builder class.

    Usage:
        @register_builder("banner")
        class BannerBuilder(BaseBuilder):
            def build(self, config, theme) -> str:
                ...

    Args:
        name: Unique identifier for this builder (used in filenames).
    """
    def decorator(cls: Type[BaseBuilder]) -> Type[BaseBuilder]:
        if name in _REGISTRY:
            raise ValueError(
                f"Builder '{name}' already registered by {_REGISTRY[name].__name__}. "
                f"Cannot register {cls.__name__}."
            )
        cls.builder_name = name
        _REGISTRY[name] = cls
        return cls
    return decorator


def get_all_builders() -> List[BaseBuilder]:
    """Return instantiated list of all registered builders.

    Returns:
        List of builder instances in registration order.
    """
    return [cls() for cls in _REGISTRY.values()]


def get_builder(name: str) -> BaseBuilder:
    """Get a single builder by name.

    Args:
        name: Registered builder name.

    Returns:
        Builder instance.

    Raises:
        KeyError: If no builder with that name exists.
    """
    if name not in _REGISTRY:
        available = list(_REGISTRY.keys())
        raise KeyError(
            f"Builder '{name}' not found. Available: {available}"
        )
    return _REGISTRY[name]()
