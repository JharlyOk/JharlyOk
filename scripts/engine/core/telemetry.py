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
    "repos": {
        "id": "repos",
        "default_label": "PUBLIC REPOS",
        "default_sub": "open source systems",
        "default_suffix": "Active",
        "badge_label": "Repos",
        "icon": "repo",
        "accent": "success",
        "prefix": "",
        "suffix": "",
        "url": "https://github.com/{handle}?tab=repositories",
    },
    "stars": {
        "id": "stars",
        "default_label": "TOTAL STARS",
        "default_sub": "community stargazers",
        "default_suffix": "Earned",
        "badge_label": "Stars",
        "icon": "star",
        "accent": "warning",
        "prefix": "★ ",
        "suffix": "",
        "url": "https://github.com/{handle}?tab=stars",
    },
    "followers": {
        "id": "followers",
        "default_label": "DEV NETWORK",
        "default_sub": "{following} following developers",
        "default_suffix": "Followers",
        "badge_label": "Followers",
        "icon": "followers",
        "accent": "secondary",
        "prefix": "",
        "suffix": "",
        "url": "https://github.com/{handle}?tab=followers",
    },
    "views": {
        "id": "views",
        "default_label": "PROFILE VIEWS",
        "default_sub": "live hit counter",
        "default_suffix": "Hits",
        "badge_label": "Visitors",
        "icon": "eye",
        "accent": "primary",
        "prefix": "",
        "suffix": "+",
        "is_counter": True,
        "url": "https://komarev.com/ghpvc/?username={handle}",
    },
}


def resolve_theme_accent(theme: Any, accent_name: str) -> str:
    """Map an accent key string or raw hex code to a Theme color."""
    if not accent_name:
        return getattr(theme, "accent_primary", "#58a6ff")
    if str(accent_name).startswith("#"):
        return str(accent_name)
    mapping = {
        "primary": getattr(theme, "accent_primary", "#58a6ff"),
        "secondary": getattr(theme, "accent_secondary", "#bc8cff"),
        "success": getattr(theme, "accent_success", "#3fb950"),
        "warning": getattr(theme, "accent_warning", "#d29922"),
        "danger": getattr(theme, "accent_danger", "#f85149"),
    }
    return mapping.get(str(accent_name).lower(), getattr(theme, "accent_primary", "#58a6ff"))


def get_telemetry_dashboard_cards(
    config: Dict[str, Any],
    stats: Dict[str, Any],
    theme: Any,
) -> list[Dict[str, Any]]:
    """Build candidate telemetry cards for the stats dashboard, merging user config."""
    stats_cfg = config.get("stats", {})
    metrics_cfg = stats_cfg.get("metrics", {})
    following = stats.get("following", 0)

    # Normalize metrics_cfg: support both dict ({repos: {...}}) and list ([{id: "repos", ...}])
    metrics_dict: Dict[str, Any] = {}
    if isinstance(metrics_cfg, list):
        for item in metrics_cfg:
            if isinstance(item, dict) and "id" in item:
                metrics_dict[item["id"]] = item
    elif isinstance(metrics_cfg, dict):
        metrics_dict = dict(metrics_cfg)

    # Collect metric keys: preserve user order first, then append any canonical spec keys not in config
    all_keys: list[str] = list(metrics_dict.keys())
    for default_key in TELEMETRY_METRICS_SPEC.keys():
        if default_key not in all_keys:
            all_keys.append(default_key)

    cards: list[Dict[str, Any]] = []

    for mid in all_keys:
        spec = TELEMETRY_METRICS_SPEC.get(mid, {
            "id": mid,
            "default_label": mid.replace("_", " ").upper(),
            "default_sub": "",
            "default_suffix": "",
            "icon": mid if mid in ("repo", "star", "followers", "eye", "web", "github") else "repo",
            "accent": "primary",
            "prefix": "",
            "suffix": "",
        })

        user_cfg = metrics_dict.get(mid, {})
        if isinstance(user_cfg, bool):
            enabled = user_cfg
            label = spec["default_label"]
            sub = spec.get("default_sub", "")
            suffix = spec.get("default_suffix", "")
            prefix = spec.get("prefix", "")
            icon = spec.get("icon", "repo")
            accent_key = spec.get("accent", "primary")
            custom_val = None
        elif isinstance(user_cfg, dict):
            enabled = user_cfg.get("enabled", True)
            label = user_cfg.get("label", spec.get("default_label", mid.replace("_", " ").upper()))
            sub = user_cfg.get("sub", spec.get("default_sub", ""))
            suffix = user_cfg.get("suffix", spec.get("default_suffix", ""))
            prefix = user_cfg.get("prefix", spec.get("prefix", ""))
            icon = user_cfg.get("icon", spec.get("icon", "repo"))
            accent_key = user_cfg.get("accent", spec.get("accent", "primary"))
            custom_val = user_cfg.get("display_value", user_cfg.get("value"))
        else:
            enabled = True
            label = spec.get("default_label", mid.replace("_", " ").upper())
            sub = spec.get("default_sub", "")
            suffix = spec.get("default_suffix", "")
            prefix = spec.get("prefix", "")
            icon = spec.get("icon", "repo")
            accent_key = spec.get("accent", "primary")
            custom_val = None

        if not enabled:
            continue

        if custom_val is not None:
            formatted_val = str(custom_val)
        else:
            raw_val = stats.get(mid, 0)
            formatted_val = format_metric_value(raw_val)

        extra_suffix = spec.get("suffix", "")
        val_core = f"{prefix}{formatted_val}{extra_suffix}".strip()
        val_str = f"{val_core} {suffix}".strip() if suffix else val_core

        sub_str = sub.replace("{following}", str(following))
        accent_color = resolve_theme_accent(theme, accent_key)

        cards.append({
            "id": mid,
            "label": label,
            "val": val_str,
            "sub": sub_str,
            "icon": icon,
            "accent": accent_color,
            "enabled": True,
        })

    return cards


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
    if isinstance(stats_metrics_cfg, list):
        stats_metrics_cfg = {
            m["id"]: m for m in stats_metrics_cfg if isinstance(m, dict) and "id" in m
        }

    if isinstance(metrics_cfg, list):
        metrics_cfg = {
            m["id"]: m for m in metrics_cfg if isinstance(m, dict) and "id" in m
        }

    active: list[Dict[str, Any]] = []

    for mid, spec in TELEMETRY_METRICS_SPEC.items():
        user_override = metrics_cfg.get(mid) if isinstance(metrics_cfg, dict) else True
        if user_override is False:
            continue

        enabled = True
        label_override = None
        icon_override = None
        prefix_override = None
        accent_override = None
        value_override = None

        if isinstance(user_override, dict):
            enabled = user_override.get("enabled", True)
            label_override = user_override.get("badge_label", user_override.get("label"))
            icon_override = user_override.get("icon")
            prefix_override = user_override.get("prefix")
            accent_override = user_override.get("accent")
            value_override = user_override.get("display_value", user_override.get("value"))

        if not enabled:
            continue

        # Inherit customized labels, icons, prefixes, accents from stats.metrics if not explicitly overridden
        if isinstance(stats_metrics_cfg, dict):
            stats_m = stats_metrics_cfg.get(mid)
            if isinstance(stats_m, dict):
                if not label_override and "badge_label" in stats_m:
                    label_override = stats_m["badge_label"]
                elif not label_override and "label" in stats_m:
                    label_override = stats_m["label"]
                if not icon_override and "icon" in stats_m:
                    icon_override = stats_m["icon"]
                if prefix_override is None and "prefix" in stats_m:
                    prefix_override = stats_m["prefix"]
                if not accent_override and "accent" in stats_m:
                    accent_override = stats_m["accent"]
                if value_override is None and ("display_value" in stats_m or "value" in stats_m):
                    value_override = stats_m.get("display_value", stats_m.get("value"))

        label = label_override or spec.get("badge_label", spec["default_label"])
        icon = icon_override or spec["icon"]
        prefix = spec["prefix"] if prefix_override is None else prefix_override
        accent_key = accent_override or spec["accent"]

        if value_override is not None:
            formatted_val = str(value_override)
            raw_val = value_override
        else:
            raw_val = stats.get(mid, 0)
            formatted_val = format_metric_value(raw_val)

        val_str = f"{prefix}{formatted_val}{spec.get('suffix', '')}"
        accent_color = resolve_theme_accent(theme, accent_key)

        active.append({
            "id": mid,
            "val": val_str,
            "label": label,
            "icon": icon,
            "accent": accent_color,
            "raw": raw_val,
        })

    return active

