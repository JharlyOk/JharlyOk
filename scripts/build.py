#!/usr/bin/env python3
"""Profile build script — compiles all SVG assets for dark & light themes.

Usage:
    python scripts/build.py                  # Build all components
    python scripts/build.py --only banner    # Build only the banner
    python scripts/build.py --list           # List registered builders

The script:
  1. Loads profile.config.json
  2. Loads the dark and light theme JSONs
  3. Discovers all registered builders
  4. Runs each builder against both themes
  5. Writes assets/{name}-dark.svg and assets/{name}-light.svg
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Resolve project root (one level up from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from engine.core.config import load_config, is_module_enabled
from engine.core.theme import load_theme_pair
from engine.core.registry import get_all_builders, get_builder
from engine.markdown.readme import update_readme_file
from engine.builders.badges import compile_all_badges

# Import builders to trigger registration
import engine.builders  # noqa: F401


def _log(msg: str) -> None:
    """Print a message with safe encoding for all platforms."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="JharlyOk Profile Engine -- SVG asset compiler.",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Build only a specific component (e.g. 'banner').",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all registered builders and exit.",
    )
    parser.add_argument(
        "--no-readme", action="store_true",
        help="Skip automatic README.md synchronization.",
    )
    args = parser.parse_args()

    # Paths
    config_path = PROJECT_ROOT / "config" / "profile.config.json"
    themes_dir = PROJECT_ROOT / "themes"
    assets_dir = PROJECT_ROOT / "assets"
    readme_path = PROJECT_ROOT / "README.md"

    # Load config
    config = load_config(config_path)
    _log(f"  [ok] Config loaded: {config['identity']['handle']}")

    # Load themes
    dark_theme, light_theme = load_theme_pair(config, themes_dir)
    _log(f"  [ok] Themes loaded: {dark_theme.label} / {light_theme.label}")

    # Discover builders
    if args.list:
        builders = get_all_builders()
        _log(f"\n  Registered builders ({len(builders)}):")
        for b in builders:
            _log(f"    - {b.builder_name}")
        return

    if args.only:
        builders = [get_builder(args.only)]
    else:
        all_builders = get_all_builders()
        builders = []
        for b in all_builders:
            if is_module_enabled(config, b.builder_name):
                builders.append(b)
            else:
                _log(f"  [skip] {b.builder_name} (disabled in config.modules)")

    _log(f"  [ok] Active builders: {[b.builder_name for b in builders]}")

    # Ensure assets directory exists
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Build all assets
    _log("")
    total_start = time.perf_counter()

    for builder in builders:
        name = builder.builder_name
        start = time.perf_counter()

        # Build dark variant
        dark_svg = builder.build(config, dark_theme)
        dark_path = assets_dir / f"{name}-dark.svg"
        dark_path.write_text(dark_svg, encoding="utf-8")

        # Build light variant
        light_svg = builder.build(config, light_theme)
        light_path = assets_dir / f"{name}-light.svg"
        light_path.write_text(light_svg, encoding="utf-8")

        elapsed = (time.perf_counter() - start) * 1000
        dark_kb = len(dark_svg.encode("utf-8")) / 1024
        light_kb = len(light_svg.encode("utf-8")) / 1024

        _log(
            f"  > {name:.<20s} "
            f"dark: {dark_kb:.1f}KB  light: {light_kb:.1f}KB  "
            f"({elapsed:.0f}ms)"
        )

    # Build standalone badges
    total_badges = 0
    if is_module_enabled(config, "badges"):
        badges_dir = assets_dir / "badges"
        dark_badges = compile_all_badges(config, dark_theme, badges_dir)
        light_badges = compile_all_badges(config, light_theme, badges_dir)
        total_badges = len(dark_badges) + len(light_badges)
        _log(f"  > badges.............. {total_badges} vector badges generated in assets/badges/")
    else:
        _log("  [skip] badges (disabled in config.modules)")

    # Sync README.md if not disabled
    if not args.no_readme and not args.only:
        update_readme_file(config, readme_path)
        _log("  [ok] README.md synchronized with active modules")

    total_elapsed = (time.perf_counter() - total_start) * 1000
    total_files = len(builders) * 2 + total_badges
    _log(f"\n  [ok] Done: {total_files} files compiled in {total_elapsed:.0f}ms")
    _log(f"  [ok] Output: {assets_dir.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
