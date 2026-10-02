"""README builder — Assembles profile README.md dynamically based on active modules."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..core.config import is_module_enabled


def generate_readme(config: Dict[str, Any]) -> str:
    """Generate the full GitHub profile README.md markdown string."""
    handle = config["identity"]["handle"]
    socials = config.get("socials", [])

    sections: list[str] = [
        '<div align="center">',
        "",
    ]

    # 1. Header (Welcome typewriter + Highlight cards)
    if is_module_enabled(config, "header"):
        sections.extend([
            "<!-- HEADER — unified animated welcome typewriter + 4 active systems cards -->",
            f'<a href="https://github.com/{handle}">',
            "  <picture>",
            '    <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">',
            '    <source media="(prefers-color-scheme: light)" srcset="assets/header-light.svg">',
            f'    <img src="assets/header-dark.svg" width="100%" alt="{handle} Workspace Header" />',
            "  </picture>",
            "</a>",
            "",
            "<br><br>",
            "",
        ])

    # 2. Code Manifest (Neovim editor banner)
    if is_module_enabled(config, "banner"):
        sections.extend([
            "<!-- CODE MANIFEST — TypeScript profile configuration (Neovim editor) -->",
            "<picture>",
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">',
            '  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">',
            f'  <img src="assets/banner-dark.svg" width="100%" alt="{handle} Code Manifest" />',
            "</picture>",
            "",
            "<br><br>",
            "",
        ])

    # 3. Active Projects (Terminal tree)
    if is_module_enabled(config, "projects"):
        sections.extend([
            "<!-- ACTIVE PROJECTS — fleet portfolio overview (Terminal) -->",
            "<picture>",
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/projects-dark.svg">',
            '  <source media="(prefers-color-scheme: light)" srcset="assets/projects-light.svg">',
            f'  <img src="assets/projects-dark.svg" width="100%" alt="{handle} Active Projects" />',
            "</picture>",
            "",
            "<br><br>",
            "",
        ])

    # 4. Tech Stack Matrix (Terminal grid)
    if is_module_enabled(config, "stack"):
        sections.extend([
            "<!-- TECHNOLOGY STACK — categorized toolchain matrix (Terminal) -->",
            "<picture>",
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/stack-dark.svg">',
            '  <source media="(prefers-color-scheme: light)" srcset="assets/stack-light.svg">',
            f'  <img src="assets/stack-dark.svg" width="100%" alt="{handle} Technology Stack" />',
            "</picture>",
            "",
            "<br><br>",
            "",
        ])

    # 5. Connect Endpoints Card (Terminal channels)
    if is_module_enabled(config, "connect"):
        sections.extend([
            "<!-- CONNECT & ENDPOINTS CARD (Terminal) -->",
            "<picture>",
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/connect-dark.svg">',
            '  <source media="(prefers-color-scheme: light)" srcset="assets/connect-light.svg">',
            f'  <img src="assets/connect-dark.svg" width="100%" alt="{handle} Communication Endpoints" />',
            "</picture>",
            "",
            "<br><br>",
            "",
        ])

    # 6. Standalone Split-Pill Badges
    if is_module_enabled(config, "badges") and socials:
        badge_links: list[str] = [
            "<!-- STANDALONE QUICK-ACTION BADGES -->",
        ]
        for item in socials:
            badge_id = item["id"]
            label = item.get("label", badge_id.title())
            url = item.get("url", "#")
            badge_links.append(
                f'<a href="{url}">\n'
                f'  <picture>\n'
                f'    <source media="(prefers-color-scheme: dark)" srcset="assets/badges/{badge_id}-dark.svg">\n'
                f'    <source media="(prefers-color-scheme: light)" srcset="assets/badges/{badge_id}-light.svg">\n'
                f'    <img src="assets/badges/{badge_id}-dark.svg" height="28" alt="{label}" />\n'
                f'  </picture>\n'
                f'</a>\n'
                f'&nbsp;'
            )
        sections.append("\n".join(badge_links))
        sections.extend(["", "<br><br>", ""])

    # 7. Dynamic Telemetry & GitHub Metric Badges
    if is_module_enabled(config, "telemetry"):
        telemetry_cfg = config.get("telemetry", {})
        default_metrics = [
            {"id": "followers", "label": "Followers", "url": f"https://github.com/{handle}?tab=followers"},
            {"id": "repos", "label": "Repos", "url": f"https://github.com/{handle}?tab=repositories"},
            {"id": "stars", "label": "Stars", "url": f"https://github.com/{handle}?tab=stars"},
            {"id": "views", "label": "Visitors", "url": f"https://komarev.com/ghpvc/?username={handle}"},
        ]
        metrics = telemetry_cfg.get("metrics", default_metrics)
        metric_links: list[str] = [
            "<!-- DYNAMIC TELEMETRY & GITHUB METRICS -->",
        ]
        for item in metrics:
            metric_id = item["id"]
            label = item.get("label", metric_id.title())
            raw_url = item.get("url", f"https://github.com/{handle}")
            url = raw_url.replace("{handle}", handle)
            metric_links.append(
                f'<a href="{url}">\n'
                f'  <picture>\n'
                f'    <source media="(prefers-color-scheme: dark)" srcset="assets/badges/{metric_id}-dark.svg">\n'
                f'    <source media="(prefers-color-scheme: light)" srcset="assets/badges/{metric_id}-light.svg">\n'
                f'    <img src="assets/badges/{metric_id}-dark.svg" height="28" alt="{label}" />\n'
                f'  </picture>\n'
                f'</a>\n'
                f'&nbsp;'
            )
        metric_links.append(
            f'\n<!-- VISITOR HIT BEACON -->\n'
            f'<img src="https://komarev.com/ghpvc/?username={handle}" width="1" height="1" alt="" style="display:none" />'
        )
        sections.append("\n".join(metric_links))
        sections.extend(["", "<br><br>", ""])

    sections.extend([
        '<sub>Built with a custom SVG engine · Dark/Light adaptive · Config-driven · <a href="scripts/">View source</a></sub>',
        "",
        "</div>\n",
    ])

    return "\n".join(sections)


def update_readme_file(config: Dict[str, Any], readme_path: Path) -> bool:
    """Generate and write the updated README.md file."""
    content = generate_readme(config)
    readme_path.write_text(content, encoding="utf-8")
    return True
