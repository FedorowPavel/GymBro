"""Inline keyboards for quick workout logging."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from config import Settings
from exercise_resolver import load_catalog

ADD_EXERCISE_BTN = "➕ Добавить упражнение"

MUSCLE_GROUPS: dict[str, str] = {
    "chest": "Грудь",
    "back": "Спина",
    "biceps": "Бицепс",
    "triceps": "Трицепс",
    "shoulders": "Плечи",
}

SLUG_MUSCLE: dict[str, str] = {
    "bench_press": "chest",
    "incline_db_press": "chest",
    "db_curl": "biceps",
    "hammer_curl": "biceps",
    "lat_pulldown": "back",
    "cable_row": "back",
    "ez_french_press": "triceps",
    "rope_pushdown": "triceps",
    "seated_db_press": "shoulders",
    "lateral_raise": "shoulders",
    "rear_delt_fly": "shoulders",
}


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(ADD_EXERCISE_BTN)]],
        resize_keyboard=True,
        is_persistent=True,
    )


def muscle_group_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for muscle_id, label in MUSCLE_GROUPS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"log:m:{muscle_id}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("Отмена", callback_data="log:cancel")])
    return InlineKeyboardMarkup(rows)


def exercise_keyboard(settings: Settings, muscle_id: str) -> InlineKeyboardMarkup:
    catalog = load_catalog(settings)
    buttons: list[InlineKeyboardButton] = []
    for slug, muscle in SLUG_MUSCLE.items():
        if muscle != muscle_id:
            continue
        meta = catalog.get(slug) or {}
        name = str(meta.get("canonical") or slug)
        buttons.append(InlineKeyboardButton(name, callback_data=f"log:e:{slug}"))

    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for button in buttons:
        row.append(button)
        if len(row) == 1:
            rows.append(row)
            row = []
    rows.append(
        [
            InlineKeyboardButton("← Группы", callback_data="log:back:m"),
            InlineKeyboardButton("Отмена", callback_data="log:cancel"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def numbers_keyboard(
    slug: str,
    *,
    weight: float,
    reps: int,
    sets: int,
) -> InlineKeyboardMarkup:
    label = f"Как в прошлый раз: {weight:g}×{reps}×{sets}"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    label,
                    callback_data=f"log:s:{slug}:{weight:g}:{reps}:{sets}",
                )
            ],
            [InlineKeyboardButton("← Упражнения", callback_data=f"log:back:e:{slug}")],
            [InlineKeyboardButton("Отмена", callback_data="log:cancel")],
        ]
    )


def numbers_keyboard_without_history(slug: str) -> InlineKeyboardMarkup:
    muscle_id = SLUG_MUSCLE.get(slug, "")
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("← Упражнения", callback_data=f"log:back:e:{slug}")],
            [InlineKeyboardButton("Отмена", callback_data="log:cancel")],
        ]
    )


def exercise_name(settings: Settings, slug: str) -> str:
    catalog = load_catalog(settings)
    meta = catalog.get(slug) or {}
    return str(meta.get("canonical") or slug)


def muscle_label(muscle_id: str) -> str:
    return MUSCLE_GROUPS.get(muscle_id, muscle_id)
