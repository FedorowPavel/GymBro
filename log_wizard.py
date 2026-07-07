"""Telegram wizard: muscle → exercise → weight×reps×sets."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

from config import Settings
from exercise_menu import (
    ADD_EXERCISE_BTN,
    exercise_keyboard,
    exercise_name,
    main_reply_keyboard,
    muscle_group_keyboard,
    muscle_label,
    numbers_keyboard,
    numbers_keyboard_without_history,
    slug_muscle_group,
)
from workout_flow import save_structured_workout
from workout_parser import parse_weight_reps_sets
from workout_writer import get_last_log_for_exercise

logger = logging.getLogger(__name__)

WIZARD_KEY = "log_wizard"


@dataclass
class LogWizardState:
    step: str
    muscle_id: str | None = None
    slug: str | None = None


def _get_state(context: ContextTypes.DEFAULT_TYPE) -> LogWizardState | None:
    raw = context.user_data.get(WIZARD_KEY)
    if not isinstance(raw, dict):
        return None
    return LogWizardState(
        step=str(raw.get("step") or ""),
        muscle_id=raw.get("muscle_id"),
        slug=raw.get("slug"),
    )


def _set_state(context: ContextTypes.DEFAULT_TYPE, state: LogWizardState | None) -> None:
    if state is None:
        context.user_data.pop(WIZARD_KEY, None)
        return
    context.user_data[WIZARD_KEY] = {
        "step": state.step,
        "muscle_id": state.muscle_id,
        "slug": state.slug,
    }


def wizard_active(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return WIZARD_KEY in context.user_data


async def start_log_wizard(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    _set_state(context, LogWizardState(step="muscle"))
    await message.reply_text(
        "Выбери группу мышц:",
        reply_markup=muscle_group_keyboard(),
    )


async def handle_log_button(message: Message, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if message.text != ADD_EXERCISE_BTN:
        return False
    await start_log_wizard(message, context)
    return True


async def handle_wizard_text(
    settings: Settings,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
) -> bool:
    state = _get_state(context)
    if state is None or state.step != "numbers" or not state.slug:
        return False

    parsed = parse_weight_reps_sets(message.text or "")
    if parsed is None:
        await message.reply_text(
            "Не понял формат. Введи, например: 66×7×3 или 66 на 7 три подхода",
            reply_markup=main_reply_keyboard(),
        )
        return True

    weight, reps, sets = parsed
    await _save_and_confirm(settings, message, context, user_id, state.slug, weight, reps, sets)
    return True


async def handle_log_callback(
    settings: Settings,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
) -> bool:
    query = update.callback_query
    if query is None or not query.data or not query.data.startswith("log:"):
        return False

    await query.answer()
    data = query.data

    if data == "log:cancel":
        _set_state(context, None)
        if query.message:
            await query.message.edit_text("Запись отменена.")
        return True

    if data == "log:back:m":
        _set_state(context, LogWizardState(step="muscle"))
        if query.message:
            await query.message.edit_text(
                "Выбери группу мышц:",
                reply_markup=muscle_group_keyboard(),
            )
        return True

    if data.startswith("log:m:"):
        muscle_id = data.removeprefix("log:m:")
        _set_state(context, LogWizardState(step="exercise", muscle_id=muscle_id))
        if query.message:
            await query.message.edit_text(
                f"{muscle_label(muscle_id)} — выбери упражнение:",
                reply_markup=exercise_keyboard(settings, muscle_id),
            )
        return True

    if data.startswith("log:e:"):
        slug = data.removeprefix("log:e:")
        muscle_id = slug_muscle_group(settings, slug)
        _set_state(
            context,
            LogWizardState(step="numbers", muscle_id=muscle_id, slug=slug),
        )
        await _prompt_numbers(settings, query, slug)
        return True

    if data.startswith("log:back:e:"):
        slug = data.removeprefix("log:back:e:")
        muscle_id = slug_muscle_group(settings, slug)
        if muscle_id and query.message:
            _set_state(context, LogWizardState(step="exercise", muscle_id=muscle_id))
            await query.message.edit_text(
                f"{muscle_label(muscle_id)} — выбери упражнение:",
                reply_markup=exercise_keyboard(settings, muscle_id),
            )
        return True

    if data.startswith("log:s:"):
        parts = data.split(":")
        if len(parts) != 6:
            return True
        _, _, slug, weight_raw, reps_raw, sets_raw = parts
        await _save_and_confirm(
            settings,
            query.message,
            context,
            user_id,
            slug,
            float(weight_raw),
            int(reps_raw),
            int(sets_raw),
            edit_message=query.message,
        )
        return True

    return False


async def _prompt_numbers(settings: Settings, query: CallbackQuery, slug: str) -> None:
    if not query.message:
        return
    name = exercise_name(settings, slug)
    last = get_last_log_for_exercise(settings, query.from_user.id, slug)
    text = (
        f"{name}\n\n"
        "Введи вес×повторы×подходы\n"
        "Например: 66×7×3"
    )
    if last:
        weight, reps, sets = last
        text += f"\n\nИли нажми кнопку с прошлыми значениями:"
        keyboard = numbers_keyboard(slug, weight=weight, reps=reps, sets=sets)
    else:
        keyboard = numbers_keyboard_without_history(slug, settings)
    await query.message.edit_text(text, reply_markup=keyboard)


async def _save_and_confirm(
    settings: Settings,
    message: Message | None,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    slug: str,
    weight: float,
    reps: int,
    sets: int,
    *,
    edit_message: Message | None = None,
) -> None:
    name = exercise_name(settings, slug)
    saved = save_structured_workout(
        settings,
        user_id,
        slug=slug,
        exercise_name=name,
        weight_kg=weight,
        reps=reps,
        sets=sets,
        workout_date=date.today(),
    )
    _set_state(context, None)

    if saved:
        text = f"✅ Записано: {saved.summary}\n\nМожешь добавить ещё упражнение кнопкой ниже."
    else:
        text = (
            f"Не удалось записать {name} ({weight:g}×{reps}×{sets}). "
            "Проверь Supabase или попробуй позже."
        )

    target = edit_message or message
    if target is None:
        return

    try:
        if edit_message is not None:
            await edit_message.edit_text(text)
            await edit_message.reply_text("➕ Добавить ещё", reply_markup=main_reply_keyboard())
        else:
            await target.reply_text(text, reply_markup=main_reply_keyboard())
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send save confirmation")
        await target.reply_text(text, reply_markup=main_reply_keyboard())
