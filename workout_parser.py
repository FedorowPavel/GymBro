"""Parse workout log messages from Telegram chat."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from enum import Enum

from config import Settings
from exercise_resolver import find_slugs_in_text, load_catalog

_PROGRAM_HINTS = (
    "программ",
    "пропиши",
    "план трен",
    "что делать",
    "что мне делать",
    "с чего начать",
    "напиши трен",
    "составь",
    "подскажи упражн",
)

_LOG_HINTS = (
    "сделал",
    "сделала",
    "отработал",
    "записал",
    "потренировал",
    "прошел",
    "прошёл",
    "сегодня жим",
    "сегодня сделал",
)

_WEIGHT_SETS_RE = re.compile(
    r"(?P<weight>\d+(?:[.,]\d+)?)\s*(?:кг|kg)?\s*"
    r"(?:на|x|х|×|\*|/)\s*"
    r"(?P<reps>\d+)\s*"
    r"(?:повтор\w*|rep\w*|раз\w*)?\s*"
    r"(?:(?:на|x|х|×|\*|/)\s*)?"
    r"(?P<sets>\d+)?\s*"
    r"(?:подход\w*|сет\w*|set\w*)?",
    re.IGNORECASE,
)

_SPACE_TRIPLE_RE = re.compile(
    r"(?P<weight>\d+(?:[.,]\d+)?)\s+(?P<reps>\d+)\s+(?P<sets>\d+)"
)

_DATE_RE = re.compile(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b")


class ParseConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    NONE = "none"


@dataclass(frozen=True)
class ParsedWorkoutLog:
    exercise_slug: str
    exercise_name: str
    weight_kg: float
    reps: int
    sets: int
    workout_date: date
    confidence: ParseConfidence
    raw_text: str


def _normalize(text: str) -> str:
    return text.lower().replace("ё", "е")


def _looks_like_program_request(text: str) -> bool:
    norm = _normalize(text)
    return any(hint in norm for hint in _PROGRAM_HINTS)


def _extract_numbers(text: str) -> tuple[float, int, int] | None:
    for pattern in (_WEIGHT_SETS_RE, _SPACE_TRIPLE_RE):
        match = pattern.search(text)
        if not match:
            continue
        weight = float(match.group("weight").replace(",", "."))
        reps = int(match.group("reps"))
        sets_raw = match.groupdict().get("sets")
        sets = int(sets_raw) if sets_raw else 3
        if weight > 0 and reps > 0 and sets > 0:
            return weight, reps, sets
    return None


def _parse_date(text: str, *, today: date | None = None) -> date:
    today = today or date.today()
    norm = _normalize(text)
    if "сегодня" in norm or "today" in norm:
        return today
    if "вчера" in norm or "yesterday" in norm:
        return today.fromordinal(today.toordinal() - 1)

    match = _DATE_RE.search(text)
    if match:
        day, month, year = match.groups()
        year_val = int(year) if year else today.year
        if year and len(year) == 2:
            year_val = 2000 + int(year)
        try:
            return date(year_val, int(month), int(day))
        except ValueError:
            pass
    return today


def _looks_like_workout_log(
    text: str,
    slugs: list[str],
    numbers: tuple[float, int, int] | None,
) -> bool:
    norm = _normalize(text)
    if _looks_like_program_request(text) and not numbers:
        return False
    if any(hint in norm for hint in _LOG_HINTS) and slugs:
        return True
    return bool(slugs and numbers)


def try_parse_workout_log(settings: Settings, text: str) -> ParsedWorkoutLog | None:
    """Return parsed log when message looks like exercise + weight entry."""
    text = text.strip()
    if not text:
        return None

    slugs = find_slugs_in_text(settings, text)
    numbers = _extract_numbers(text)
    if not _looks_like_workout_log(text, slugs, numbers):
        return None
    if not slugs:
        return None

    slug = slugs[0]
    catalog = load_catalog(settings)
    name = str((catalog.get(slug) or {}).get("canonical") or slug)
    workout_date = _parse_date(text)

    if numbers is None:
        return ParsedWorkoutLog(
            exercise_slug=slug,
            exercise_name=name,
            weight_kg=0,
            reps=0,
            sets=0,
            workout_date=workout_date,
            confidence=ParseConfidence.MEDIUM,
            raw_text=text,
        )

    weight, reps, sets = numbers
    confidence = ParseConfidence.HIGH if len(slugs) == 1 else ParseConfidence.MEDIUM

    return ParsedWorkoutLog(
        exercise_slug=slug,
        exercise_name=name,
        weight_kg=weight,
        reps=reps,
        sets=sets,
        workout_date=workout_date,
        confidence=confidence,
        raw_text=text,
    )


def format_log_summary(log: ParsedWorkoutLog) -> str:
    if log.confidence == ParseConfidence.MEDIUM and log.weight_kg == 0:
        return f"{log.exercise_name} (уточни вес и повторы)"
    return (
        f"{log.exercise_name}: {log.weight_kg:g} кг × {log.reps} × {log.sets} "
        f"({log.workout_date.isoformat()})"
    )
