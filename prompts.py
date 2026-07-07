"""Build system prompt for the Gym Bro Cursor agent."""

from __future__ import annotations

from pathlib import Path

from config import Settings
from supabase_store import fetch_profile_context, supabase_enabled


def build_system_prompt(settings: Settings, telegram_user_id: int) -> str:
    rules = _read_rules(settings.agent_workspace)
    rules_block = f"\n## Coach rules (from config/coach-rules.md)\n{rules}\n" if rules else ""

    profile_block = ""
    if supabase_enabled(settings):
        db_context = fetch_profile_context(settings, telegram_user_id)
        if db_context:
            profile_block = db_context
        else:
            profile_block = (
                "## Profile\n"
                "(Supabase configured but no data loaded — check TELEGRAM_USER_ID / profile row.)\n\n"
                + _yaml_fallback(settings)
            )
    else:
        profile_block = "## Client profile (local file)\n```yaml\n" + _yaml_fallback(settings) + "\n```"

    return f"""You are Gym Bro — a personal strength coach for one client (Pavel).

Reply in the same language the user writes (usually Russian). Be concise, practical, and encouraging without fluff.

{profile_block}

{rules_block}
## Your role
1. Help log workouts (weight × reps × sets) and give feedback on progress.
2. Suggest the next session based on history, goals, and active injuries/restrictions.
3. Never invent numbers — use only data from Supabase context above. The full workout log and key lift progressions are included; do not say older data is missing unless the context block is empty.
4. Respect all exercise bans (no barbell squat, no deadlift, no upright row, etc.).
5. Progression: +1–2 kg or +1 rep when form and recovery allow; always leave 1–2 reps in reserve.
6. Rep ranges: 5–8 base, 8–10 accessories; 3 base sets, 2–3 accessory sets.
7. Current injury context: left ankle recovering — seated/supine work only until cleared.
8. **Telegram formatting**: no Markdown tables. Use lines like **Жим:** 66 кг × 6 × 3 or bullet lists.
9. When suggesting a workout plan, list exercises with target sets/reps/weight based on last logged session.
10. You are not a doctor. Pain or acute injury → reduce load and recommend seeing a specialist.
"""


def build_user_message(settings: Settings, telegram_user_id: int, text: str) -> str:
    """Refresh latest DB snapshot before each user message (same session)."""
    if not supabase_enabled(settings):
        return text
    snapshot = fetch_profile_context(settings, telegram_user_id)
    if not snapshot:
        return text
    return (
        "[Fresh data from Supabase — use for this reply]\n"
        f"{snapshot}\n\n"
        f"---\nUser: {text}"
    )


def _yaml_fallback(settings: Settings) -> str:
    return _read_file(settings.client_profile_path)


def _read_file(path: Path) -> str:
    if not path.is_file():
        return f"# missing: {path}"
    return path.read_text(encoding="utf-8")


def _read_rules(workspace: Path) -> str:
    rules_path = workspace / "config" / "coach-rules.md"
    if not rules_path.is_file():
        return ""
    return rules_path.read_text(encoding="utf-8").strip()
