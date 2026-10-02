"""GitHub Telemetry & Metrics Fetcher.

Fetches live profile metrics from GitHub REST API & visitor counter:
  - Followers count
  - Public repositories count
  - Total stars accumulated across repositories
  - Profile visitor hits (Komarev telemetry)

Resilience:
  - Supports GITHUB_TOKEN from env to avoid rate limits (1000 req/hr).
  - Uses local cache (config/telemetry_cache.json) as fallback when offline.
  - Never crashes or blocks build if external APIs are unreachable.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_STATS: Dict[str, Any] = {
    "followers": 0,
    "following": 0,
    "repos": 8,
    "stars": 0,
    "views": 64,
    "created_at": "2020-05-27T00:00:00Z",
    "languages": {"Python": 2},
    "timestamp": "2026-10-01T00:00:00Z",
}


def _get_auth_headers() -> Dict[str, str]:
    """Build HTTP headers with User-Agent and optional GitHub token."""
    headers = {
        "User-Agent": "JharlyOk-Profile-Engine/2.0",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_telemetry(handle: str, cache_path: Path | None = None) -> Dict[str, Any]:
    """Fetch live telemetry stats for user, with automatic cache fallback."""
    stats = dict(DEFAULT_STATS)

    # 1. Load existing cache if present
    if cache_path and cache_path.exists():
        try:
            cached_data = json.loads(cache_path.read_text(encoding="utf-8"))
            stats.update(cached_data)
        except Exception:
            pass

    headers = _get_auth_headers()
    api_success = False

    # 2. Fetch user profile data (followers, public repos, following, created_at)
    try:
        req = urllib.request.Request(f"https://api.github.com/users/{handle}", headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "followers" in data:
                stats["followers"] = data["followers"]
            if "following" in data:
                stats["following"] = data["following"]
            if "public_repos" in data:
                stats["repos"] = data["public_repos"]
            if "created_at" in data:
                stats["created_at"] = data["created_at"]
            api_success = True
    except Exception:
        # Graceful fallback to cached value
        pass

    # 3. Fetch public repositories to sum total stars & language distribution
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{handle}/repos?per_page=100&type=public",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            repos_data = json.loads(resp.read().decode("utf-8"))
            if isinstance(repos_data, list):
                stats["stars"] = sum(r.get("stargazers_count", 0) for r in repos_data)
                langs: Dict[str, int] = {}
                for r in repos_data:
                    lang = r.get("language")
                    if lang:
                        langs[lang] = langs.get(lang, 0) + 1
                if langs:
                    stats["languages"] = langs
                api_success = True
    except Exception:
        pass

    # 4. Fetch visitor counter from Komarev
    try:
        req = urllib.request.Request(
            f"https://komarev.com/ghpvc/?username={handle}",
            headers={"User-Agent": "JharlyOk-Profile-Engine/2.0"},
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            svg_text = resp.read().decode("utf-8")
            matches = re.findall(r">([0-9,]+)<", svg_text)
            if matches:
                # First match is the number
                clean_num = int(matches[0].replace(",", ""))
                stats["views"] = clean_num
                api_success = True
    except Exception:
        pass

    # 5. Update cache on disk if any API call succeeded
    stats["timestamp"] = datetime.now(timezone.utc).isoformat()
    if cache_path and api_success:
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        except Exception:
            pass

    return stats


def format_metric_value(val: int | float | str) -> str:
    """Format numeric metrics into clean human-readable strings."""
    if isinstance(val, (int, float)):
        if val >= 1_000_000:
            return f"{val / 1_000_000:.1f}M"
        if val >= 1_000:
            return f"{val / 1_000:.1f}k"
        return str(int(val))
    return str(val)


# Canonical telemetry metrics definition (Single Source of Truth)
TELEMETRY_METRICS_SPEC: Dict[str, Dict[str, Any]] = {
    "followers": {
        "id": "followers",
        "default_label": "Followers",
        "icon": "followers",
        "accent": "secondary",
        "prefix": "",
        "suffix": "",
    },
    "repos": {
        "id": "repos",
        "default_label": "Public Repos",
        "icon": "repo",
        "accent": "success",
        "prefix": "",
        "suffix": "",
    },
    "stars": {
        "id": "stars",
        "default_label": "Stars Earned",
        "icon": "star",
        "accent": "warning",
        "prefix": "★ ",
        "suffix": "",
    },
    "views": {
        "id": "views",
        "default_label": "Profile Views",
        "icon": "eye",
        "accent": "primary",
        "prefix": "",
        "suffix": "+",
        "is_counter": True,
    },
}


def resolve_theme_accent(theme: Any, accent_name: str) -> str:
    """Map an accent key string (primary, secondary, etc.) to a Theme color."""
    mapping = {
        "primary": getattr(theme, "accent_primary", "#58a6ff"),
        "secondary": getattr(theme, "accent_secondary", "#bc8cff"),
        "success": getattr(theme, "accent_success", "#3fb950"),
        "warning": getattr(theme, "accent_warning", "#d29922"),
        "danger": getattr(theme, "accent_danger", "#f85149"),
    }
    return mapping.get(accent_name, getattr(theme, "accent_primary", "#58a6ff"))


def get_active_telemetry_metrics(
    config: Dict[str, Any],
    stats: Dict[str, Any],
    theme: Any,
    scope: str = "header",
) -> list[Dict[str, Any]]:
    """Extract and format active telemetry metrics, merging user config dynamically."""
    if scope == "header":
        telem_cfg = config.get("identity", {}).get("telemetry", {})
        if not telem_cfg:
            telem_cfg = config.get("header", {}).get("telemetry", {})
        if not telem_cfg.get("enabled", False):
            return []
        metrics_cfg = telem_cfg.get("metrics", {})
    else:
        metrics_cfg = config.get("stats", {}).get("metrics", {})

    stats_metrics_cfg = config.get("stats", {}).get("metrics", {})
    active: list[Dict[str, Any]] = []

    for mid, spec in TELEMETRY_METRICS_SPEC.items():
        user_override = metrics_cfg.get(mid) if isinstance(metrics_cfg, dict) else True
        if user_override is False:
            continue

        enabled = True
        label_override = None
        icon_override = None

        if isinstance(user_override, dict):
            enabled = user_override.get("enabled", True)
            label_override = user_override.get("label")
            icon_override = user_override.get("icon")

        if not enabled:
            continue

        # Inherit customized labels from stats.metrics if not explicitly overridden
        if not label_override and isinstance(stats_metrics_cfg, dict):
            stats_m = stats_metrics_cfg.get(mid)
            if isinstance(stats_m, dict) and "label" in stats_m:
                label_override = stats_m["label"]

        label = label_override or spec["default_label"]
        icon = icon_override or spec["icon"]
        raw_val = stats.get(mid, 0)
        formatted_val = format_metric_value(raw_val)
        val_str = f"{spec['prefix']}{formatted_val}{spec['suffix']}"

        accent_color = resolve_theme_accent(theme, spec["accent"])

        active.append({
            "id": mid,
            "val": val_str,
            "label": label,
            "icon": icon,
            "accent": accent_color,
            "raw": raw_val,
        })

    return active

