"""Resolve user chat phrases to exercise slugs via config/exercise-aliases.yaml."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from config import Settings

logger = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    return text.lower().replace("ё", "е").strip()


@lru_cache(maxsize=4)
def _load_catalog(path: str) -> dict[str, dict[str, Any]]:
    file_path = Path(path)
    if not file_path.is_file():
        logger.warning("Exercise aliases file missing: %s", file_path)
        return {}
    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def aliases_path(settings: Settings) -> Path:
    return settings.agent_workspace / "config" / "exercise-aliases.yaml"


def load_catalog(settings: Settings) -> dict[str, dict[str, Any]]:
    return _load_catalog(str(aliases_path(settings)))


def _alias_entries(catalog: dict[str, dict[str, Any]]) -> list[tuple[str, str, str]]:
    """Return (alias_normalized, slug, canonical) sorted longest alias first."""
    entries: list[tuple[str, str, str]] = []
    for slug, meta in catalog.items():
        if not isinstance(meta, dict):
            continue
        canonical = str(meta.get("canonical") or slug)
        aliases = meta.get("aliases") or []
        seen: set[str] = set()
        for alias in aliases:
            norm = _normalize(str(alias))
            if not norm or norm in seen:
                continue
            seen.add(norm)
            entries.append((norm, slug, canonical))
        canon_norm = _normalize(canonical)
        if canon_norm and canon_norm not in seen:
            entries.append((canon_norm, slug, canonical))
    entries.sort(key=lambda item: len(item[0]), reverse=True)
    return entries


def find_slugs_in_text(settings: Settings, text: str) -> list[str]:
    """Return unique exercise slugs mentioned in user text (order of first match)."""
    catalog = load_catalog(settings)
    if not catalog or not text.strip():
        return []

    normalized = _normalize(text)
    found: list[str] = []
    used_spans: list[tuple[int, int]] = []

    for alias, slug, _canonical in _alias_entries(catalog):
        start = 0
        while True:
            idx = normalized.find(alias, start)
            if idx == -1:
                break
            end = idx + len(alias)
            overlaps = any(not (end <= s or idx >= e) for s, e in used_spans)
            if not overlaps:
                if slug not in found:
                    found.append(slug)
                used_spans.append((idx, end))
            start = idx + 1

    return found


def format_alias_reference(settings: Settings) -> str:
    """Compact alias map for the agent system context."""
    catalog = load_catalog(settings)
    if not catalog:
        return ""

    lines = [
        "## Exercise name aliases (user chat → database)",
        "When the user names an exercise informally, map it to the canonical name and slug below.",
        "",
    ]
    for slug, meta in catalog.items():
        if not isinstance(meta, dict):
            continue
        canonical = meta.get("canonical") or slug
        aliases = meta.get("aliases") or []
        short = ", ".join(f"«{a}»" for a in aliases[:6])
        extra = len(aliases) - 6
        if extra > 0:
            short += f" (+{extra} more)"
        lines.append(f"- **{canonical}** (`{slug}`): {short}")
    return "\n".join(lines)


def describe_matches(settings: Settings, slugs: list[str]) -> str:
    catalog = load_catalog(settings)
    if not slugs:
        return ""

    lines = ["## Exercises detected in user message"]
    for slug in slugs:
        meta = catalog.get(slug) or {}
        canonical = meta.get("canonical") or slug
        lines.append(f"- User likely means: **{canonical}** (slug: `{slug}`)")
    lines.append("")
    lines.append("Use progression data for these slugs below. Do not say the exercise is missing from the log.")
    return "\n".join(lines)


def all_progression_slugs(settings: Settings) -> list[tuple[str, str]]:
    catalog = load_catalog(settings)
    result: list[tuple[str, str]] = []
    for slug, meta in catalog.items():
        if isinstance(meta, dict):
            result.append((slug, str(meta.get("canonical") or slug)))
    return result
