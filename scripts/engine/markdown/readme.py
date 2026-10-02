"""README builder — Assembles profile README.md via template tags or default fallback.

Supported template tags in README.template.md:
  - {{ header }}              : Welcome typewriter + highlights card picture
  - {{ stats }}               : GitHub Stats & Telemetry terminal banner (880px)
  - {{ stats:banner }}        : Alias for {{ stats }}
  - {{ stats:badges }}        : All GitHub telemetry badges (followers, repos, stars, views)
  - {{ banner }}              : Neovim TypeScript code manifest banner
  - {{ projects }}            : Active projects terminal banner
  - {{ stack }}               : Technology stack terminal matrix
  - {{ socials }}             : Social communication channels terminal banner (880px)
  - {{ socials:banner }}      : Alias for {{ socials }}
  - {{ socials:badges }}      : All configured social badges
  - {{ badge:<id> }}          : Single social or telemetry badge (e.g. {{ badge:telegram }}, {{ badge:followers }})
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from ..core.config import is_module_enabled


def _build_single_badge_markup(
    badge_id: str,
    label: str,
    url: str,
) -> str:
    """Build HTML picture markup for a single split-pill badge."""
    return (
        f'<a href="{url}">\n'
        f'  <picture>\n'
        f'    <source media="(prefers-color-scheme: dark)" srcset="assets/badges/{badge_id}-dark.svg">\n'
        f'    <source media="(prefers-color-scheme: light)" srcset="assets/badges/{badge_id}-light.svg">\n'
        f'    <img src="assets/badges/{badge_id}-dark.svg" height="28" alt="{label}" />\n'
        f'  </picture>\n'
        f'</a>'
    )


def _build_social_badges(config: Dict[str, Any]) -> List[str]:
    """Build markdown links for all configured active social badges."""
    socials = config.get("socials", [])
    if not socials:
        return []
    badge_links: list[str] = [
        "<!-- QUICK-ACTION SOCIAL BADGES -->",
    ]
    for item in socials:
        if not item.get("enabled", True):
            continue
        badge_id = item["id"]
        label = item.get("label", badge_id.title())
        url = item.get("url", "#")
        badge_links.append(_build_single_badge_markup(badge_id, label, url) + "\n&nbsp;")
    return badge_links


def _build_telemetry_badges(config: Dict[str, Any]) -> List[str]:
    """Build markdown links for dynamic GitHub metric badges based on active metrics."""
    handle = config.get("identity", {}).get("handle", "JharlyOk")
    stats_cfg = config.get("stats", {})
    metrics_cfg = stats_cfg.get("metrics", {})
    default_metrics = [
        {"id": "followers", "label": "Followers", "url": f"https://github.com/{handle}?tab=followers"},
        {"id": "repos", "label": "Repos", "url": f"https://github.com/{handle}?tab=repositories"},
        {"id": "stars", "label": "Stars", "url": f"https://github.com/{handle}?tab=stars"},
        {"id": "views", "label": "Visitors", "url": f"https://komarev.com/ghpvc/?username={handle}"},
    ]
    metric_links: list[str] = [
        "<!-- DYNAMIC TELEMETRY & GITHUB METRICS -->",
    ]
    for item in default_metrics:
        metric_id = item["id"]
        if not metrics_cfg.get(metric_id, True):
            continue
        label = item.get("label", metric_id.title())
        url = item["url"]
        metric_links.append(_build_single_badge_markup(metric_id, label, url) + "\n&nbsp;")
    return metric_links


def render_component(tag: str, config: Dict[str, Any]) -> str:
    """Render a single component tag into its corresponding HTML/picture markup."""
    handle = config.get("identity", {}).get("handle", "JharlyOk")
    tag_clean = tag.strip().lower()

    # Normalize aliases (e.g. asset:header -> header)
    if tag_clean.startswith("asset:"):
        tag_clean = tag_clean.split(":", 1)[1]

    # 1. Main banner/card modules
    if tag_clean == "header":
        return (
            "<!-- HEADER — unified animated welcome typewriter + 4 active systems cards -->\n"
            f'<a href="https://github.com/{handle}">\n'
            f'  <picture>\n'
            f'    <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">\n'
            f'    <source media="(prefers-color-scheme: light)" srcset="assets/header-light.svg">\n'
            f'    <img src="assets/header-dark.svg" width="100%" alt="{handle} Workspace Header" />\n'
            f'  </picture>\n'
            f'</a>'
        )
    elif tag_clean in ("stats", "stats:banner"):
        return (
            "<!-- GITHUB STATS & TELEMETRY DASHBOARD (Terminal) -->\n"
            "<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/stats-dark.svg">\n'
            '  <source media="(prefers-color-scheme: light)" srcset="assets/stats-light.svg">\n'
            f'  <img src="assets/stats-dark.svg" width="100%" alt="{handle} GitHub Stats & Telemetry" />\n'
            "</picture>"
        )
    elif tag_clean == "banner":
        return (
            "<!-- CODE MANIFEST — TypeScript profile configuration (Neovim editor) -->\n"
            "<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">\n'
            '  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">\n'
            f'  <img src="assets/banner-dark.svg" width="100%" alt="{handle} Code Manifest" />\n'
            "</picture>"
        )
    elif tag_clean == "projects":
        return (
            "<!-- ACTIVE PROJECTS — fleet portfolio overview (Terminal) -->\n"
            "<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/projects-dark.svg">\n'
            '  <source media="(prefers-color-scheme: light)" srcset="assets/projects-light.svg">\n'
            f'  <img src="assets/projects-dark.svg" width="100%" alt="{handle} Active Projects" />\n'
            "</picture>"
        )
    elif tag_clean == "stack":
        return (
            "<!-- TECHNOLOGY STACK — categorized toolchain matrix (Terminal) -->\n"
            "<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/stack-dark.svg">\n'
            '  <source media="(prefers-color-scheme: light)" srcset="assets/stack-light.svg">\n'
            f'  <img src="assets/stack-dark.svg" width="100%" alt="{handle} Technology Stack" />\n'
            "</picture>"
        )
    elif tag_clean in ("socials", "socials:banner", "connect"):
        return (
            "<!-- SOCIALS & ENDPOINTS CARD (Terminal) -->\n"
            "<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/socials-dark.svg">\n'
            '  <source media="(prefers-color-scheme: light)" srcset="assets/socials-light.svg">\n'
            f'  <img src="assets/socials-dark.svg" width="100%" alt="{handle} Communication Endpoints" />\n'
            "</picture>"
        )
    elif tag_clean in ("socials:badges", "badges:socials", "badges"):
        badges = _build_social_badges(config)
        return "\n".join(badges)
    elif tag_clean in ("stats:badges", "badges:stats", "telemetry"):
        badges = _build_telemetry_badges(config)
        return "\n".join(badges)
    elif tag_clean.startswith("badge:") or tag_clean.startswith("social:") or tag_clean.startswith("stat:"):
        badge_name = tag_clean.split(":", 1)[1]
        # Check socials
        socials = {item["id"]: item for item in config.get("socials", [])}
        if badge_name in socials:
            item = socials[badge_name]
            return _build_single_badge_markup(badge_name, item.get("label", badge_name.title()), item.get("url", "#"))
        # Check telemetry metrics
        telemetry_map = {
            "followers": {"label": "Followers", "url": f"https://github.com/{handle}?tab=followers"},
            "repos": {"label": "Repos", "url": f"https://github.com/{handle}?tab=repositories"},
            "stars": {"label": "Stars", "url": f"https://github.com/{handle}?tab=stars"},
            "views": {"label": "Visitors", "url": f"https://komarev.com/ghpvc/?username={handle}"},
        }
        if badge_name in telemetry_map:
            tinfo = telemetry_map[badge_name]
            return _build_single_badge_markup(badge_name, tinfo["label"], tinfo["url"])
        return f"<!-- Unknown badge: {badge_name} -->"
    elif tag_clean == "beacon":
        return f'<!-- VISITOR HIT BEACON -->\n<img src="https://komarev.com/ghpvc/?username={handle}" width="1" height="1" alt="" style="display:none" />'
    elif tag_clean == "footer":
        return ""

    return f"<!-- Unknown tag: {tag} -->"


def render_template(template_text: str, config: Dict[str, Any]) -> str:
    """Replace all {{ tag }} placeholders in a template with generated markup."""
    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_\-:]+)\s*\}\}")

    def _replace(match: re.Match) -> str:
        tag = match.group(1)
        return render_component(tag, config)

    return pattern.sub(_replace, template_text)


def generate_readme(config: Dict[str, Any]) -> str:
    """Generate the full GitHub profile README.md markdown string as fallback."""
    sections: list[str] = [
        '<div align="center">',
        "",
    ]

    # 1. Header
    if is_module_enabled(config, "header"):
        sections.extend([
            render_component("header", config),
            "",
            "<br><br>",
            "",
        ])

    # 2. GitHub Stats Dashboard
    if is_module_enabled(config, "stats"):
        sections.extend([
            render_component("stats", config),
            "",
            "<br><br>",
            "",
        ])

    # 3. Quick-Action Social Badges
    if is_module_enabled(config, "badges"):
        badges = _build_social_badges(config)
        if badges:
            sections.append("\n".join(badges))
            sections.extend(["", "<br><br>", ""])

    # 4. Code Manifest
    if is_module_enabled(config, "banner"):
        sections.extend([
            render_component("banner", config),
            "",
            "<br><br>",
            "",
        ])

    # 5. Active Projects
    if is_module_enabled(config, "projects"):
        sections.extend([
            render_component("projects", config),
            "",
            "<br><br>",
            "",
        ])

    # 6. Tech Stack Matrix
    if is_module_enabled(config, "stack"):
        sections.extend([
            render_component("stack", config),
            "",
            "<br><br>",
            "",
        ])

    # 7. Socials Endpoints Card
    if is_module_enabled(config, "socials") or is_module_enabled(config, "connect"):
        sections.extend([
            render_component("socials", config),
            "",
            "<br><br>",
            "",
        ])

    # 8. Dynamic Telemetry Badges
    if is_module_enabled(config, "telemetry"):
        telemetry_links = _build_telemetry_badges(config)
        if telemetry_links:
            sections.append("\n".join(telemetry_links))
            sections.extend(["", "<br><br>", ""])

    sections.append("</div>\n")
    return "\n".join(sections)


def update_readme_file(config: Dict[str, Any], readme_path: Path) -> bool:
    """Generate and write the updated README.md file using template if present."""
    template_path = readme_path.parent / "README.template.md"
    handle = config.get("identity", {}).get("handle", "JharlyOk")
    beacon_markup = f'\n<!-- VISITOR HIT BEACON -->\n<img src="https://komarev.com/ghpvc/?username={handle}" width="1" height="1" alt="" style="display:none" />\n'

    if template_path.exists():
        template_str = template_path.read_text(encoding="utf-8")
        content = render_template(template_str, config)
        # Automatically inject invisible hit beacon if not already present
        if "<!-- VISITOR HIT BEACON -->" not in content:
            if "</div>" in content:
                content = content.replace("</div>", f"{beacon_markup}</div>")
            else:
                content += beacon_markup
    else:
        content = generate_readme(config)
        if "<!-- VISITOR HIT BEACON -->" not in content:
            if "</div>" in content:
                content = content.replace("</div>", f"{beacon_markup}</div>")
            else:
                content += beacon_markup

    readme_path.write_text(content, encoding="utf-8")
    return True
