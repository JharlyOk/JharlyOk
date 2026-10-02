"""GitHub Stats & Telemetry Banner Builder.

Generates a unified 880px terminal card displaying:
  1. macOS terminal header with configurable prompt command and live status tag
  2. Dynamically-sized metric cards (Repos, Stars, Network/Followers, Visitor Hits)
     with fully customizable titles, subtitles, and suffixes
  3. Optional bottom system telemetry statusline with developer tenure, bot fleet count & audio pipeline
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..core.registry import BaseBuilder, register_builder
from ..core.theme import Theme
from ..core.telemetry import format_metric_value
from ..svg.icons import render_icon
from ..svg.primitives import (
    svg_open, svg_close, rect, text, circle, line, _esc,
)


@register_builder("stats")
class StatsBuilder(BaseBuilder):
    """Generates the 880px GitHub stats and telemetry dashboard card."""

    builder_name = "stats"

    def build(
        self,
        config: Dict[str, Any],
        theme: Theme,
        telemetry_stats: Dict[str, Any] | None = None,
    ) -> str:
        # Load stats from passed param, cache or defaults
        stats = telemetry_stats or {}
        if not stats:
            cache_path = Path(".cache/telemetry.json")
            if cache_path.exists():
                try:
                    stats = json.loads(cache_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

        handle = config.get("identity", {}).get("handle", "JharlyOk")
        repos = stats.get("repos", 8)
        stars = stats.get("stars", 0)
        followers = stats.get("followers", 0)
        following = stats.get("following", 2)
        views = stats.get("views", 81)

        # Granular configuration from profile.config.yaml
        stats_cfg = config.get("stats", {})
        metrics_cfg = stats_cfg.get("metrics", {})

        def _get_metric_cfg(key: str, default_label: str, default_sub: str, default_suffix: str) -> dict:
            val = metrics_cfg.get(key, {})
            if isinstance(val, bool):
                return {
                    "enabled": val,
                    "label": default_label,
                    "sub": default_sub,
                    "suffix": default_suffix,
                }
            elif isinstance(val, dict):
                return {
                    "enabled": val.get("enabled", True),
                    "label": val.get("label", default_label),
                    "sub": val.get("sub", default_sub),
                    "suffix": val.get("suffix", default_suffix),
                }
            return {
                "enabled": True,
                "label": default_label,
                "sub": default_sub,
                "suffix": default_suffix,
            }

        cfg_repos = _get_metric_cfg("repos", "PUBLIC REPOS", "open source systems", "Active")
        cfg_stars = _get_metric_cfg("stars", "TOTAL STARS", "community stargazers", "Earned")
        cfg_followers = _get_metric_cfg("followers", "DEV NETWORK", "{following} following developers", "Followers")
        cfg_views = _get_metric_cfg("views", "PROFILE VIEWS", "live hit counter", "Hits")

        followers_sub = cfg_followers["sub"].replace("{following}", str(following))
        command_text = stats_cfg.get("command", "gh telemetry --overview")
        badge_text = stats_cfg.get("badge_text", "LIVE TELEMETRY")

        statusline_cfg = stats_cfg.get("statusline", {})
        has_statusline = statusline_cfg.get("enabled", True)
        tenure_label = statusline_cfg.get("tenure_label", "Tenure:")
        tenure_text = statusline_cfg.get("tenure", "Since 2020 (6y)")
        fleet_label = statusline_cfg.get("fleet_label", "Fleet:")
        fleet_text = statusline_cfg.get("fleet", "13+ Autonomous Bots")
        pipeline_label = statusline_cfg.get("pipeline_label", "Pipeline:")
        pipeline_text = statusline_cfg.get("pipeline", "Lavalink v4 + LavaSrc")
        sync_text = statusline_cfg.get("sync_text", "Auto-synced via")

        width = 880
        height = 196 if has_statusline else 142
        rx = 10

        parts: list[str] = [
            svg_open(
                width,
                height,
                f"{handle} GitHub Stats & Telemetry Dashboard",
                "Live developer telemetry, repositories, stars, network, and profile overview",
            ),
            # Background Card
            rect(0, 0, width, height, rx=rx, fill=theme.bg_canvas, stroke=theme.border_default),
            # Window Chrome Header
            rect(0, 0, width, 38, rx=rx, fill=theme.bg_subtle),
            rect(0, 28, width, 10, fill=theme.bg_subtle),
            line(0, 38, width, 38, stroke=theme.border_muted),
            # macOS Window Controls
            circle(18, 19, 6, fill="#ff5f56"),
            circle(38, 19, 6, fill="#ffbd2e"),
            circle(58, 19, 6, fill="#27c93f"),
            # Prompt text
            f'  <text x="82" y="23" font-family="{theme.font_mono}" font-size="12" '
            f'font-weight="600" fill="{theme.fg_muted}">'
            f'{handle.lower()}@dev:~$ <tspan fill="{theme.fg_default}">{_esc(command_text)}</tspan></text>\n',
            # Right Live Telemetry Tag
            rect(width - 150, 10, 130, 20, rx=4, fill=theme.bg_inset),
            circle(width - 138, 20, 3.5, fill=theme.accent_success),
            f'  <text x="{width - 128}" y="24" font-family="{theme.font_mono}" font-size="10" '
            f'font-weight="700" fill="{theme.accent_success}">{_esc(badge_text)}</text>\n',
        ]

        # Candidate Metric Cards
        all_cards = [
            {
                "id": "repos",
                "label": cfg_repos["label"],
                "val": f"{repos} {cfg_repos['suffix']}".strip(),
                "sub": cfg_repos["sub"],
                "icon": "repo",
                "accent": theme.accent_success,
                "enabled": cfg_repos["enabled"],
            },
            {
                "id": "stars",
                "label": cfg_stars["label"],
                "val": f"★ {stars} {cfg_stars['suffix']}".strip(),
                "sub": cfg_stars["sub"],
                "icon": "star",
                "accent": theme.accent_warning,
                "enabled": cfg_stars["enabled"],
            },
            {
                "id": "followers",
                "label": cfg_followers["label"],
                "val": f"{followers} {cfg_followers['suffix']}".strip(),
                "sub": followers_sub,
                "icon": "followers",
                "accent": theme.accent_secondary,
                "enabled": cfg_followers["enabled"],
            },
            {
                "id": "views",
                "label": cfg_views["label"],
                "val": f"{format_metric_value(views)}+ {cfg_views['suffix']}".strip(),
                "sub": cfg_views["sub"],
                "icon": "eye",
                "accent": theme.accent_primary,
                "enabled": cfg_views["enabled"],
            },
        ]

        active_cards = [c for c in all_cards if c["enabled"]]
        num_cards = len(active_cards)

        start_x = 20
        start_y = 48
        card_h = 76
        gap = 12
        total_span = 840

        if num_cards > 0:
            card_w = (total_span - ((num_cards - 1) * gap)) / num_cards
            for i, c in enumerate(active_cards):
                cx = start_x + i * (card_w + gap)
                cy = start_y

                parts.extend([
                    # Card Background & Border
                    rect(cx, cy, card_w, card_h, rx=6, fill=theme.bg_overlay, stroke=theme.border_muted),
                    # Left Accent Bar
                    rect(cx, cy + 8, 3, card_h - 16, rx=1.5, fill=c["accent"]),
                    # Icon (16x16)
                    render_icon(c["icon"], cx + 12, cy + 12, 16, c["accent"]),
                    # Label
                    f'  <text x="{cx + 34}" y="{cy + 24}" font-family="{theme.font_mono}" font-size="10" '
                    f'font-weight="700" letter-spacing="0.5" fill="{theme.fg_muted}">{_esc(c["label"])}</text>\n',
                    # Main Value
                    f'  <text x="{cx + 12}" y="{cy + 48}" font-family="{theme.font_mono}" font-size="15" '
                    f'font-weight="800" fill="{theme.fg_default}">{_esc(c["val"])}</text>\n',
                    # Subtext
                    f'  <text x="{cx + 12}" y="{cy + 65}" font-family="{theme.font_mono}" font-size="9.5" '
                    f'font-weight="500" fill="{theme.fg_subtle}">{_esc(c["sub"])}</text>\n',
                ])

        # Bottom System Telemetry Statusline (if enabled)
        if has_statusline:
            bar_x = 20
            bar_y = 136
            bar_w = 840
            bar_h = 42
            parts.extend([
                rect(bar_x, bar_y, bar_w, bar_h, rx=6, fill=theme.bg_subtle, stroke=theme.border_muted),
                # Icon / Terminal Symbol
                f'  <text x="{bar_x + 14}" y="{bar_y + 26}" font-family="{theme.font_mono}" font-size="13" '
                f'font-weight="800" fill="{theme.accent_primary}">❯</text>\n',
                # Status items separated by dots
                f'  <text x="{bar_x + 32}" y="{bar_y + 26}" font-family="{theme.font_mono}" font-size="11" '
                f'font-weight="600" fill="{theme.fg_default}">'
                f'<tspan fill="{theme.fg_muted}">{_esc(tenure_label)}</tspan> {_esc(tenure_text)} '
                f'<tspan fill="{theme.border_default}">·</tspan> '
                f'<tspan fill="{theme.fg_muted}">{_esc(fleet_label)}</tspan> {_esc(fleet_text)} '
                f'<tspan fill="{theme.border_default}">·</tspan> '
                f'<tspan fill="{theme.fg_muted}">{_esc(pipeline_label)}</tspan> {_esc(pipeline_text)}</text>\n',
                # Right badge: Auto-synced
                f'  <text x="{bar_x + bar_w - 14}" y="{bar_y + 26}" text-anchor="end" font-family="{theme.font_mono}" '
                f'font-size="10" font-weight="600" fill="{theme.fg_muted}">'
                f'{_esc(sync_text)} <tspan fill="{theme.accent_primary}">GitHub Actions</tspan></text>\n',
            ])

        parts.append(svg_close())
        return "".join(parts)
