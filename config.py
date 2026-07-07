"""Gym Bro Telegram bot — configuration from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

AgentRuntime = Literal["local", "cloud"]


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    allowed_user_ids: frozenset[int]
    cursor_api_key: str
    cursor_model: str
    agent_runtime: AgentRuntime
    cloud_repo_url: str
    client_profile_path: Path
    agent_workspace: Path
    sessions_path: Path
    ask_timeout_seconds: float
    agent_empty_retries: int
    supabase_url: str
    supabase_service_role_key: str
    openai_api_key: str


def _parse_user_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if part:
            ids.add(int(part))
    if not ids:
        raise ValueError("TELEGRAM_ALLOWED_USER_IDS must list at least one user id")
    return frozenset(ids)


def load_settings() -> Settings:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        raise ValueError("CURSOR_API_KEY is required")

    project_root = Path(__file__).resolve().parent
    runtime = os.environ.get("AGENT_RUNTIME", "local").strip().lower()
    if runtime not in ("local", "cloud"):
        raise ValueError("AGENT_RUNTIME must be 'local' or 'cloud'")

    default_profile = project_root / "config" / "client-profile.yaml"
    profile_raw = os.environ.get("CLIENT_PROFILE_PATH", "").strip()
    profile_path = Path(profile_raw).expanduser() if profile_raw else default_profile

    return Settings(
        telegram_bot_token=token,
        allowed_user_ids=_parse_user_ids(
            os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "")
        ),
        cursor_api_key=api_key,
        cursor_model=os.environ.get("CURSOR_MODEL", "auto").strip() or "auto",
        agent_runtime=runtime,  # type: ignore[arg-type]
        cloud_repo_url=os.environ.get(
            "CURSOR_CLOUD_REPO_URL",
            "https://github.com/FedorowPavel/gym-bro",
        ).strip(),
        client_profile_path=profile_path,
        agent_workspace=Path(
            os.environ.get("AGENT_WORKSPACE", str(project_root))
        ).expanduser(),
        sessions_path=project_root / "data" / "sessions.json",
        ask_timeout_seconds=float(os.environ.get("AGENT_ASK_TIMEOUT_SECONDS", "300")),
        agent_empty_retries=max(1, int(os.environ.get("AGENT_EMPTY_RETRIES", "2"))),
        supabase_url=os.environ.get("SUPABASE_URL", "").strip(),
        supabase_service_role_key=os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY", ""
        ).strip(),
        openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
    )
