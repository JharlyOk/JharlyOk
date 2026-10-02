"""GitHub Stats & Telemetry Banner Builder.

Generates a unified 880px terminal card displaying:
  1. macOS terminal header with `gh telemetry --overview` prompt and live status
  2. Dynamically-sized metric cards (Repos, Stars, Network/Followers, Visitor Hits)
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
        show_repos = metrics_cfg.get("repos", True)
        show_stars = metrics_cfg.get("stars", True)
        show_followers = metrics_cfg.get("followers", True)
        show_views = metrics_cfg.get("views", True)

        statusline_cfg = stats_cfg.get("statusline", {})
        has_statusline = statusline_cfg.get("enabled", True)
        tenure_text = statusline_cfg.get("tenure", "Since 2020 (6y)")
        fleet_text = statusline_cfg.get("fleet", "13+ Autonomous Bots")
        pipeline_text = statusline_cfg.get("pipeline", "Lavalink v4 + LavaSrc")

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
            f'{handle.lower()}@dev:~$ <tspan fill="{theme.fg_default}">gh telemetry --overview</tspan></text>\n',
            # Right Live Telemetry Tag
            rect(width - 150, 10, 130, 20, rx=4, fill=theme.bg_inset),
            circle(width - 138, 20, 3.5, fill=theme.accent_success),
            f'  <text x="{width - 128}" y="24" font-family="{theme.font_mono}" font-size="10" '
            f'font-weight="700" fill="{theme.accent_success}">LIVE TELEMETRY</text>\n',
        ]

        # Candidate Metric Cards
        all_cards = [
            {
                "id": "repos",
                "label": "PUBLIC REPOS",
                "val": f"{repos} Active",
                "sub": "open source systems",
                "icon": "repo",
                "accent": theme.accent_success,
                "enabled": show_repos,
            },
            {
                "id": "stars",
                "label": "TOTAL STARS",
                "val": f"★ {stars} Earned",
                "sub": "community stargazers",
                "icon": "star",
                "accent": theme.accent_warning,
                "enabled": show_stars,
            },
            {
                "id": "followers",
                "label": "DEV NETWORK",
                "val": f"{followers} Followers",
                "sub": f"{following} following developers",
                "icon": "followers",
                "accent": theme.accent_secondary,
                "enabled": show_followers,
            },
            {
                "id": "views",
                "label": "PROFILE VIEWS",
                "val": f"{format_metric_value(views)}+ Hits",
                "sub": "live hit counter",
                "icon": "eye",
                "accent": theme.accent_primary,
                "enabled": show_views,
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
                f'<tspan fill="{theme.fg_muted}">Tenure:</tspan> {_esc(tenure_text)} '
                f'<tspan fill="{theme.border_default}">·</tspan> '
                f'<tspan fill="{theme.fg_muted}">Fleet:</tspan> {_esc(fleet_text)} '
                f'<tspan fill="{theme.border_default}">·</tspan> '
                f'<tspan fill="{theme.fg_muted}">Pipeline:</tspan> {_esc(pipeline_text)}</text>\n',
                # Right badge: Auto-synced
                f'  <text x="{bar_x + bar_w - 14}" y="{bar_y + 26}" text-anchor="end" font-family="{theme.font_mono}" '
                f'font-size="10" font-weight="600" fill="{theme.fg_muted}">'
                f'Auto-synced via <tspan fill="{theme.accent_primary}">GitHub Actions</tspan></text>\n',
            ])

        parts.append(svg_close())
        return "".join(parts)
