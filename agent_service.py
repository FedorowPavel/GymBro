"""Cursor SDK session per Telegram user."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from cursor_sdk import (
    AgentOptions,
    AsyncClient,
    CloudAgentOptions,
    CloudRepository,
    CursorAgentError,
    InternalServerError,
    LocalAgentOptions,
)

from config import Settings
from prompts import build_system_prompt, build_user_message

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE = 4096
ProgressCallback = Callable[[str], Awaitable[None] | None]
RetryCallback = Callable[[], Awaitable[None] | None]


class GymBroAgentService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncClient | None = None
        self._bridge_cm: Any = None
        self._agents: dict[str, Any] = {}
        self._sessions_path = settings.sessions_path
        self._sessions_path.parent.mkdir(parents=True, exist_ok=True)
        self._stored_ids: dict[str, str] = self._load_sessions()
        self._active_runs: dict[str, Any] = {}

    async def start(self) -> None:
        workspace = str(self._settings.agent_workspace)
        logger.info("Starting Cursor client (runtime=%s)", self._settings.agent_runtime)
        self._bridge_cm = await AsyncClient.launch_bridge(workspace=workspace)
        self._client = await self._bridge_cm.__aenter__()

    async def stop(self) -> None:
        for agent in self._agents.values():
            try:
                await agent.close()
            except Exception:  # noqa: BLE001
                logger.exception("Failed to close agent")
        self._agents.clear()
        if self._bridge_cm is not None:
            await self._bridge_cm.__aexit__(None, None, None)
            self._bridge_cm = None
            self._client = None

    async def ask(
        self,
        user_id: int,
        message: str,
        *,
        on_progress: ProgressCallback | None = None,
        on_retry: RetryCallback | None = None,
    ) -> str:
        logger.info("Agent ask started for user %s", user_id)
        attempts = self._settings.agent_empty_retries

        for attempt in range(1, attempts + 1):
            try:
                text = await self._ask_once(
                    user_id,
                    message,
                    on_progress=on_progress,
                    retry=attempt > 1,
                )
                if text.strip():
                    return text
                logger.warning(
                    "Empty agent reply for user %s (attempt %s/%s)",
                    user_id,
                    attempt,
                    attempts,
                )
            except InternalServerError:
                logger.warning(
                    "Cursor internal error for user %s (attempt %s/%s), resetting agent",
                    user_id,
                    attempt,
                    attempts,
                )
                await self.reset(user_id)
                if attempt == attempts:
                    return "Временный сбой на стороне Cursor. Попробуйте ещё раз или /reset."
                if on_retry is not None:
                    result = on_retry()
                    if asyncio.iscoroutine(result):
                        await result
                continue
            except CursorAgentError as err:
                logger.exception("Cursor agent failed for user %s", user_id)
                return _format_agent_error(err)

            if attempt < attempts:
                if on_retry is not None:
                    result = on_retry()
                    if asyncio.iscoroutine(result):
                        await result
                await asyncio.sleep(1.5)

        return (
            "Агент не смог сформировать ответ (пустой ответ после повторов). "
            "Напишите ещё раз или /reset."
        )

    async def stop_run(self, user_id: int) -> bool:
        key = str(user_id)
        run = self._active_runs.pop(key, None)
        if run is None:
            return False
        try:
            await run.cancel()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to cancel run for user %s", user_id)
        return True

    async def reset(self, user_id: int) -> None:
        key = str(user_id)
        agent = self._agents.pop(key, None)
        if agent is not None:
            await agent.close()
        self._stored_ids.pop(key, None)
        self._save_sessions()

    async def _ask_once(
        self,
        user_id: int,
        message: str,
        *,
        on_progress: ProgressCallback | None = None,
        retry: bool = False,
    ) -> str:
        agent = await self._get_agent(user_id)
        if retry:
            payload = (
                "Твой прошлый ответ был пустым. Ответь по-русски, кратко и по делу, "
                "используя данные Supabase из контекста этого чата. "
                "Не возвращай пустой ответ.\n\n"
                f"Вопрос пользователя: {message}"
            )
        else:
            payload = build_user_message(self._settings, user_id, message)
        run = await agent.send(payload)
        key = str(user_id)
        self._active_runs[key] = run
        try:
            text = await self._collect_run_text(
                run,
                timeout=self._settings.ask_timeout_seconds,
                on_progress=on_progress,
            )
        finally:
            self._active_runs.pop(key, None)
        logger.info("Agent ask finished for user %s (retry=%s)", user_id, retry)
        return _chunk_for_telegram(text)

    async def _collect_run_text(
        self,
        run: Any,
        *,
        timeout: float,
        on_progress: ProgressCallback | None,
    ) -> str:
        chunks: list[str] = []
        last_progress_len = 0

        async def _stream() -> None:
            nonlocal last_progress_len
            async for piece in run.iter_text():
                chunks.append(piece)
                if on_progress is None:
                    continue
                joined = "".join(chunks).strip()
                if len(joined) - last_progress_len < 80:
                    continue
                last_progress_len = len(joined)
                preview = joined[-350:] if len(joined) > 350 else joined
                result = on_progress(preview)
                if asyncio.iscoroutine(result):
                    await result
            await asyncio.wait_for(run.wait(), timeout=120)

        try:
            await asyncio.wait_for(_stream(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Agent run timed out after %ss (run_id=%s)", timeout, run.id)
            await self._safe_cancel_run(run)
            partial = "".join(chunks).strip()
            suffix = "\n\n⏱ Время ожидания истекло. /reset и попробуйте снова."
            return partial + suffix if partial else "⏱ Агент не ответил вовремя. /reset и напишите снова."
        except Exception:  # noqa: BLE001
            partial = "".join(chunks).strip()
            if partial:
                return partial
            raise

        return "".join(chunks).strip()

    async def _safe_cancel_run(self, run: Any) -> None:
        try:
            await run.cancel()
        except Exception:  # noqa: BLE001
            logger.debug("Run cancel failed or already finished", exc_info=True)

    async def _get_agent(self, user_id: int):
        if self._client is None:
            raise RuntimeError("GymBroAgentService is not started")

        key = str(user_id)
        if key in self._agents:
            return self._agents[key]

        options = self._build_agent_options()
        agent_id = self._stored_ids.get(key)
        if agent_id:
            try:
                agent = await self._client.agents.resume(agent_id, options)
                self._agents[key] = agent
                return agent
            except CursorAgentError:
                logger.warning("Resume failed for %s, creating new agent", agent_id)
                self._stored_ids.pop(key, None)

        agent = await self._client.agents.create(options)
        init_run = await agent.send(build_system_prompt(self._settings, user_id))
        await init_run.wait()
        self._agents[key] = agent
        self._stored_ids[key] = agent.agent_id
        self._save_sessions()
        return agent

    def _build_agent_options(self) -> AgentOptions:
        common = {
            "model": self._settings.cursor_model,
            "api_key": self._settings.cursor_api_key,
        }
        if self._settings.agent_runtime == "cloud":
            return AgentOptions(
                **common,
                cloud=CloudAgentOptions(
                    repos=[CloudRepository(url=self._settings.cloud_repo_url)],
                ),
            )
        return AgentOptions(
            **common,
            local=LocalAgentOptions(
                cwd=str(self._settings.agent_workspace),
                setting_sources=[],
            ),
        )

    def _load_sessions(self) -> dict[str, str]:
        if not self._sessions_path.is_file():
            return {}
        try:
            data = json.loads(self._sessions_path.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in data.items()}
        except (json.JSONDecodeError, TypeError):
            return {}

    def _save_sessions(self) -> None:
        self._sessions_path.write_text(
            json.dumps(self._stored_ids, indent=2),
            encoding="utf-8",
        )


def _chunk_for_telegram(text: str) -> str:
    text = text.strip()
    if len(text) <= TELEGRAM_MAX_MESSAGE:
        return text
    return text[: TELEGRAM_MAX_MESSAGE - 1] + "…"


def _format_agent_error(err: CursorAgentError) -> str:
    hint = "Попробуйте ещё раз или /reset."
    if isinstance(err, InternalServerError):
        return f"Временный сбой на стороне Cursor. {hint}"
    return f"Ошибка агента: {err.message}. {hint}"
