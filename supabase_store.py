"""Read client context from Supabase for the Cursor agent."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

from config import Settings

logger = logging.getLogger(__name__)

_client: Any | None = None


def supabase_enabled(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def _get_client(settings: Settings):
    global _client
    if _client is not None:
        return _client
    import httpx
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(trust_env=False)
    options = ClientOptions(httpx_client=http_client)
    _client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
        options=options,
    )
    return _client


def fetch_profile_context(settings: Settings, telegram_user_id: int) -> str | None:
    """Return formatted profile block from Supabase, or None on failure / disabled."""
    if not supabase_enabled(settings):
        return None
    try:
        client = _get_client(settings)
        uid = telegram_user_id

        profile = (
            client.table("profile")
            .select("*")
            .eq("telegram_user_id", uid)
            .limit(1)
            .execute()
            .data
        )
        if not profile:
            logger.warning("No profile row for telegram_user_id=%s", uid)
            return None

        goals = (
            client.table("goals")
            .select("horizon, description, status")
            .eq("telegram_user_id", uid)
            .eq("status", "active")
            .order("horizon")
            .order("sort_order")
            .execute()
            .data
        )
        injuries = (
            client.table("injuries")
            .select("body_part, status, notes, started_on")
            .eq("telegram_user_id", uid)
            .in_("status", ["active", "recovering"])
            .execute()
            .data
        )
        bans = (
            client.table("exercise_bans")
            .select("exercise_name, reason")
            .eq("telegram_user_id", uid)
            .eq("is_active", True)
            .execute()
            .data
        )
        split = (
            client.table("training_split")
            .select("day_label, focus")
            .eq("telegram_user_id", uid)
            .eq("is_active", True)
            .order("sort_order")
            .execute()
            .data
        )
        workouts = (
            client.table("workouts")
            .select("id, workout_date, split_focus, notes")
            .eq("telegram_user_id", uid)
            .order("workout_date", desc=True)
            .limit(5)
            .execute()
            .data
        )

        workout_lines = _format_recent_workouts(client, workouts)

        p = profile[0]
        lines = [
            "## Profile (from Supabase)",
            f"- Name: {p.get('display_name', '—')}",
            f"- Weight: {p.get('weight_kg')} kg, height: {p.get('height_cm')} cm",
            f"- Body type: {p.get('body_type')}, goal: {p.get('goal')}",
            f"- Notes: {p.get('notes') or '—'}",
        ]
        if p.get("nutrition"):
            lines.append(f"- Nutrition: {json.dumps(p['nutrition'], ensure_ascii=False)}")

        if split:
            lines.append("\n## Training split")
            for row in split:
                lines.append(f"- {row['day_label']}: {row['focus']}")

        if goals:
            lines.append("\n## Active goals")
            for row in goals:
                lines.append(f"- [{row['horizon']}] {row['description']}")

        if injuries:
            lines.append("\n## Injuries / limitations")
            for row in injuries:
                lines.append(
                    f"- {row['body_part']} ({row['status']}): {row.get('notes') or '—'}"
                )

        if bans:
            lines.append("\n## Banned exercises")
            for row in bans:
                lines.append(f"- {row['exercise_name']} — {row.get('reason') or 'banned'}")

        if workout_lines:
            lines.append("\n## Recent workouts (logged)")
            lines.extend(workout_lines)

        return "\n".join(lines)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to fetch Supabase context for user %s", telegram_user_id)
        return None


def _format_recent_workouts(client: Any, workouts: list[dict[str, Any]]) -> list[str]:
    if not workouts:
        return []

    workout_ids = [w["id"] for w in workouts]
    sets_rows = (
        client.table("workout_sets")
        .select("workout_id, set_number, weight_kg, reps, exercises(name, slug)")
        .in_("workout_id", workout_ids)
        .execute()
        .data
    )

    by_workout: dict[str, dict[str, list[tuple[float, int]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    workout_meta = {w["id"]: w for w in workouts}

    for row in sets_rows:
        wid = row["workout_id"]
        ex = row.get("exercises") or {}
        name = ex.get("name") or ex.get("slug") or "?"
        by_workout[wid][name].append((float(row["weight_kg"]), int(row["reps"])))

    lines: list[str] = []
    for wid in workout_ids:
        meta = workout_meta.get(wid)
        if not meta:
            continue
        date = meta.get("workout_date")
        focus = meta.get("split_focus") or ""
        header = f"### {date}" + (f" ({focus})" if focus else "")
        lines.append(header)
        exercises = by_workout.get(wid, {})
        for name, sets_data in exercises.items():
            sets_data.sort(key=lambda x: x)
            if len(sets_data) >= 1:
                w0, r0 = sets_data[0]
                if all(s == sets_data[0] for s in sets_data):
                    lines.append(f"- {name}: {w0} kg × {r0} × {len(sets_data)}")
                else:
                    detail = ", ".join(f"{w}×{r}" for w, r in sets_data)
                    lines.append(f"- {name}: {detail}")
        lines.append("")
    return lines
