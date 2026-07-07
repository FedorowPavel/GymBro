"""Inline keyboards for quick workout logging."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from config import Settings
from exercise_resolver import load_catalog

ADD_EXERCISE_BTN = "➕ Добавить упражнение"
PROGRESS_BTN = "📊 Прогресс"

MUSCLE_GROUPS: dict[str, str] = {
    "chest": "Грудь",
    "back": "Спина",
    "biceps": "Бицепс",
    "triceps": "Трицепс",
    "shoulders": "Плечи",
    "legs": "Ноги",
}

_slug_muscle_cache: dict[str, str] = {}


def _load_slug_muscle(settings: Settings) -> dict[str, str]:
    if _slug_muscle_cache:
        return _slug_muscle_cache
    catalog = load_catalog(settings)
    for slug, meta in catalog.items():
        if isinstance(meta, dict) and meta.get("muscle_group"):
            _slug_muscle_cache[slug] = str(meta["muscle_group"])
    return _slug_muscle_cache


def slug_muscle_group(settings: Settings, slug: str) -> str | None:
    return _load_slug_muscle(settings).get(slug)


def main_reply_keyboard(miniapp_url: str | None = None) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = [[KeyboardButton(ADD_EXERCISE_BTN)]]
    url = (miniapp_url or "").strip()
    if url:
        rows.append([KeyboardButton(PROGRESS_BTN, web_app=WebAppInfo(url=url))])
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
    )


def progress_inline_keyboard(miniapp_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(PROGRESS_BTN, web_app=WebAppInfo(url=miniapp_url))]]
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
    slug_muscle = _load_slug_muscle(settings)
    buttons: list[InlineKeyboardButton] = []
    for slug, muscle in slug_muscle.items():
        if muscle != muscle_id:
            continue
        meta = catalog.get(slug) or {}
        name = str(meta.get("canonical") or slug)
        buttons.append(InlineKeyboardButton(name, callback_data=f"log:e:{slug}"))

    rows: list[list[InlineKeyboardButton]] = []
    for button in buttons:
        rows.append([button])
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


def numbers_keyboard_without_history(slug: str, settings: Settings) -> InlineKeyboardMarkup:
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
