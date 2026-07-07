from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from config import Settings
from supabase_store import supabase_enabled
from workout_parser import ParsedWorkoutLog, format_log_summary

logger = logging.getLogger(__name__)

_SPLIT_BY_MUSCLE: dict[frozenset[str], str] = {
    frozenset({"chest", "biceps"}): "Chest + Biceps",
    frozenset({"back", "triceps"}): "Back + Triceps",
    frozenset({"shoulders"}): "Shoulders",
    frozenset({"chest"}): "Chest",
    frozenset({"biceps"}): "Biceps",
    frozenset({"back"}): "Back",
    frozenset({"triceps"}): "Triceps",
}


@dataclass(frozen=True)
class SaveWorkoutResult:
    summary: str
    workout_id: str
    replaced: bool


def save_workout_log(
    settings: Settings,
    telegram_user_id: int,
    log: ParsedWorkoutLog,
) -> SaveWorkoutResult | None:
    if not supabase_enabled(settings):
        return None
    if log.weight_kg <= 0 or log.reps <= 0 or log.sets <= 0:
        return None

    try:
        from supabase_store import _get_client

        client = _get_client(settings)
        exercise = (
            client.table("exercises")
            .select("id, muscle_group")
            .eq("slug", log.exercise_slug)
            .limit(1)
            .execute()
            .data
        )
        if not exercise:
            logger.warning("Exercise slug not in DB: %s", log.exercise_slug)
            return None

        exercise_id = exercise[0]["id"]
        muscle = exercise[0].get("muscle_group") or ""
        split_focus = _infer_split_focus(muscle)

        workout_id, replaced = _get_or_create_workout(
            client,
            telegram_user_id,
            log.workout_date,
            split_focus,
        )

        _replace_exercise_sets(
            client,
            workout_id,
            exercise_id,
            log.weight_kg,
            log.reps,
            log.sets,
        )

        return SaveWorkoutResult(
            summary=format_log_summary(log),
            workout_id=workout_id,
            replaced=replaced,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to save workout log for user %s", telegram_user_id)
        return None


def get_last_log_for_exercise(
    settings: Settings,
    telegram_user_id: int,
    exercise_slug: str,
) -> tuple[float, int, int] | None:
    if not supabase_enabled(settings):
        return None
    try:
        from supabase_store import _get_client

        client = _get_client(settings)
        exercise = (
            client.table("exercises")
            .select("id")
            .eq("slug", exercise_slug)
            .limit(1)
            .execute()
            .data
        )
        if not exercise:
            return None
        exercise_id = exercise[0]["id"]

        workouts = (
            client.table("workouts")
            .select("id, workout_date")
            .eq("telegram_user_id", telegram_user_id)
            .order("workout_date", desc=True)
            .limit(40)
            .execute()
            .data
        )
        for workout in workouts or []:
            sets = (
                client.table("workout_sets")
                .select("weight_kg, reps, set_number")
                .eq("workout_id", workout["id"])
                .eq("exercise_id", exercise_id)
                .order("set_number")
                .execute()
                .data
            )
            if not sets:
                continue
            weight = float(sets[0]["weight_kg"])
            reps = int(sets[0]["reps"])
            return weight, reps, len(sets)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load last log for %s", exercise_slug)
        return None


def _infer_split_focus(muscle_group: str) -> str:
    key = frozenset({muscle_group}) if muscle_group else frozenset()
    if key in _SPLIT_BY_MUSCLE:
        return _SPLIT_BY_MUSCLE[key]
    if muscle_group == "chest":
        return "Chest + Biceps"
    if muscle_group == "back":
        return "Back + Triceps"
    return "Logged"


def _get_or_create_workout(
    client: Any,
    telegram_user_id: int,
    workout_date: date,
    split_focus: str,
) -> tuple[str, bool]:
    date_str = workout_date.isoformat()
    existing = (
        client.table("workouts")
        .select("id, created_at, split_focus")
        .eq("telegram_user_id", telegram_user_id)
        .eq("workout_date", date_str)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
        .data
    )

    for row in existing or []:
        if row.get("split_focus") == split_focus or row.get("split_focus") == "Logged":
            return str(row["id"]), False

    if existing:
        latest = existing[0]
        created = _parse_ts(latest.get("created_at"))
        if created and workout_date == date.today():
            age_hours = (datetime.now(timezone.utc) - created).total_seconds() / 3600
            if age_hours <= 6 and latest.get("split_focus") in {
                split_focus,
                "Logged",
                "In progress",
            }:
                return str(latest["id"]), False

    inserted = (
        client.table("workouts")
        .insert(
            {
                "telegram_user_id": telegram_user_id,
                "workout_date": date_str,
                "split_focus": split_focus,
                "notes": "Logged via Telegram",
            }
        )
        .execute()
        .data
    )
    return str(inserted[0]["id"]), False


def _replace_exercise_sets(
    client: Any,
    workout_id: str,
    exercise_id: str,
    weight_kg: float,
    reps: int,
    num_sets: int,
) -> None:
    existing = (
        client.table("workout_sets")
        .select("id")
        .eq("workout_id", workout_id)
        .eq("exercise_id", exercise_id)
        .execute()
        .data
    )
    if existing:
        for row in existing:
            client.table("workout_sets").delete().eq("id", row["id"]).execute()

    rows = [
        {
            "workout_id": workout_id,
            "exercise_id": exercise_id,
            "set_number": n,
            "weight_kg": weight_kg,
            "reps": reps,
        }
        for n in range(1, num_sets + 1)
    ]
    client.table("workout_sets").insert(rows).execute()


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
