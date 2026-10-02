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

    Defaults to True if modules section is missing or module is not specified.
    Supports either {"header": true} or {"header": {"enabled": true}}.
    """
    modules = config.get("modules", {})
    if module_name not in modules:
        return True
    mod_val = modules[module_name]
    if isinstance(mod_val, bool):
        return mod_val
    if isinstance(mod_val, dict):
        return bool(mod_val.get("enabled", True))
    return True
