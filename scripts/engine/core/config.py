"""Config loader — reads and provides profile configuration from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import yaml


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load the profile configuration from YAML.

    Args:
        config_path: Path to profile.config.yaml.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        yaml.YAMLError: If YAML syntax is invalid.
    """
    if isinstance(config_path, str):
        config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Profile config not found at {config_path}. "
            f"Ensure config/profile.config.yaml exists."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError(f"Invalid YAML config structure at {config_path}. Root must be a mapping.")

    _validate_config(config)
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate that required top-level keys exist.

    Raises:
        KeyError: If a required section is missing.
    """
    required_sections = ["identity", "themes", "banner", "projects", "stack", "socials"]
    missing = [s for s in required_sections if s not in config]
    if missing:
        raise KeyError(
            f"Missing required sections in profile config: {missing}"
        )

    required_identity = ["handle", "role", "tagline"]
    missing_id = [k for k in required_identity if k not in config["identity"]]
    if missing_id:
        raise KeyError(
            f"Missing required identity fields: {missing_id}"
        )


def is_module_enabled(config: Dict[str, Any], module_name: str) -> bool:
    """Check if a specific profile module is enabled.

    Resolves directly from each section's own configuration (decentralized),
    with fallback to top-level modules mapping if present.
    """
    # 1. Header / Identity
    if module_name in ("header", "identity"):
        sec = config.get("identity", {}) or config.get("header", {})
        if isinstance(sec, dict) and "enabled" in sec:
            return bool(sec["enabled"])

    # 2. Neovim code manifest
    elif module_name == "banner":
        sec = config.get("banner", {})
        if isinstance(sec, dict) and "enabled" in sec:
            return bool(sec["enabled"])

    # 3. Active projects
    elif module_name == "projects":
        sec = config.get("projects", {})
        if isinstance(sec, dict) and "enabled" in sec:
            return bool(sec["enabled"])

    # 4. Tech stack matrix
    elif module_name == "stack":
        sec = config.get("stack", {})
        if isinstance(sec, dict) and "enabled" in sec:
            return bool(sec["enabled"])

    # 5. Stats dashboard (terminal card)
    elif module_name in ("stats", "stats:banner"):
        sec = config.get("stats", {})
        if isinstance(sec, dict) and "enabled" in sec:
            return bool(sec["enabled"])

    # 6. Telemetry metric badges (split-pill badges)
    elif module_name in ("telemetry", "stats:badges"):
        sec = config.get("stats", {})
        if isinstance(sec, dict) and "badges" in sec:
            return bool(sec["badges"])

    # 7. Socials terminal banner
    elif module_name in ("socials", "socials:banner", "connect"):
        sec = config.get("socials", {})
        if isinstance(sec, dict):
            if "banner" in sec:
                return bool(sec["banner"])
            if "enabled" in sec:
                return bool(sec["enabled"])

    # 8. Social badges (split-pill badges)
    elif module_name in ("badges", "socials:badges"):
        sec = config.get("socials", {})
        if isinstance(sec, dict) and "badges" in sec:
            return bool(sec["badges"])

    # Fallback to legacy top-level modules dictionary if present
    modules = config.get("modules", {})
    if module_name in modules:
        mod_val = modules[module_name]
        if isinstance(mod_val, bool):
            return mod_val
        if isinstance(mod_val, dict):
            return bool(mod_val.get("enabled", True))

    return True
