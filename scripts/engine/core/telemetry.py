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
