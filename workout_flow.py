"""Bridge workout parsing, saving, and agent messaging."""

from __future__ import annotations

from datetime import date

from config import Settings
from profile_parser import try_parse_body_weight_kg
from supabase_store import update_profile_weight
from workout_parser import ParseConfidence, ParsedWorkoutLog, format_log_summary, try_parse_workout_log
from workout_writer import save_workout_log


def save_structured_workout(
    settings: Settings,
    telegram_user_id: int,
    *,
    slug: str,
    exercise_name: str,
    weight_kg: float,
    reps: int,
    sets: int,
    workout_date: date,
):
    log = ParsedWorkoutLog(
        exercise_slug=slug,
        exercise_name=exercise_name,
        weight_kg=weight_kg,
        reps=reps,
        sets=sets,
        workout_date=workout_date,
        confidence=ParseConfidence.HIGH,
        raw_text=f"{exercise_name} {weight_kg:g}×{reps}×{sets}",
    )
    return save_workout_log(settings, telegram_user_id, log)


def prepare_agent_message(
    settings: Settings,
    telegram_user_id: int,
    text: str,
) -> tuple[str, str | None]:
    """
    Returns (message_for_agent, optional_saved_line_for_user).

  - Program / questions → unchanged text
  - Clear workout log → save to Supabase, tell agent data is saved
  - Ambiguous log → agent asks to clarify (no save)
    """
    body_weight = try_parse_body_weight_kg(text)
    if body_weight is not None:
        if update_profile_weight(settings, telegram_user_id, body_weight):
            saved_line = f"✅ Вес обновлён: {body_weight:g} кг"
            agent_text = (
                f"{text}\n\n"
                f"[Система: вес в профиле Supabase обновлён до {body_weight:g} кг. "
                "Подтверди коротко, не спрашивай подтверждения записи.]"
            )
            return agent_text, saved_line

        agent_text = (
            f"{text}\n\n"
            "[Система: пользователь просит обновить вес в профиле, "
            "но запись в Supabase не удалась. Сообщи об этом.]"
        )
        return agent_text, None

    parsed = try_parse_workout_log(settings, text)
    if parsed is None:
        return text, None

    if parsed.confidence == ParseConfidence.HIGH:
        saved = save_workout_log(settings, telegram_user_id, parsed)
        preview = format_log_summary(parsed)
        if saved:
            saved_line = f"✅ Записано: {saved.summary}"
            agent_text = (
                f"{text}\n\n"
                f"[Система: тренировка уже сохранена в Supabase — {saved.summary}. "
                "Кратко прокомментируй прогресс по сравнению с прошлыми сессиями. "
                "Не спрашивай подтверждения записи.]"
            )
            return agent_text, saved_line

        agent_text = (
            f"{text}\n\n"
            f"[Система: распознан лог тренировки ({preview}), но запись в Supabase не удалась. "
            "Сообщи об этом и попроси повторить сообщение чуть позже.]"
        )
        return agent_text, None

    preview = format_log_summary(parsed)
    agent_text = (
        f"{text}\n\n"
        f"[Система: похоже на лог тренировки ({preview}), но данных недостаточно для записи. "
        "Помоги уточнить или предложи формат: «жим 66 на 6 три подхода».]"
    )
    return agent_text, None
