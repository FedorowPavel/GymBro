"""Bridge profile updates and agent messaging."""

from __future__ import annotations

from config import Settings
from profile_parser import try_parse_body_weight_update
from supabase_store import update_profile_weight


def try_update_body_weight(
    settings: Settings,
    telegram_user_id: int,
    text: str,
) -> tuple[str, str | None] | None:
    """
    When user asks to update body weight, save to Supabase and annotate agent message.

    Returns (agent_text, saved_line) or None if not a weight-update request.
    """
    weight_kg = try_parse_body_weight_update(text)
    if weight_kg is None:
        return None

    saved = update_profile_weight(settings, telegram_user_id, weight_kg)
    if saved:
        saved_line = f"✅ Вес в профиле обновлён: {weight_kg:g} кг"
        agent_text = (
            f"{text}\n\n"
            f"[Система: вес в профиле Supabase обновлён на {weight_kg:g} кг. "
            "Подтверди пользователю. Не спрашивай подтверждения записи.]"
        )
        return agent_text, saved_line

    agent_text = (
        f"{text}\n\n"
        "[Система: пользователь просил обновить вес в профиле, "
        "но запись в Supabase не удалась. Сообщи об этом.]"
    )
    return agent_text, None
