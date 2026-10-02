"""Core engine components — configuration, themes, and builder registry."""

from .config import load_config, is_module_enabled
from .theme import Theme, SyntaxColors, load_theme, load_theme_pair
from .registry import BaseBuilder, register_builder, get_builder, get_all_builders
from .telemetry import (
    fetch_telemetry,
    format_metric_value,
    TELEMETRY_METRICS_SPEC,
    resolve_theme_accent,
    get_active_telemetry_metrics,
    get_telemetry_dashboard_cards,
)

__all__ = [
    "load_config",
    "is_module_enabled",
    "Theme",
    "SyntaxColors",
    "load_theme",
    "load_theme_pair",
    "BaseBuilder",
    "register_builder",
    "get_builder",
    "get_all_builders",
    "fetch_telemetry",
    "format_metric_value",
    "TELEMETRY_METRICS_SPEC",
    "resolve_theme_accent",
    "get_active_telemetry_metrics",
    "get_telemetry_dashboard_cards",
]

