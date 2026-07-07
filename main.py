#!/usr/bin/env python3
"""Run the Gym Bro Telegram bot locally."""

from __future__ import annotations

import asyncio
import logging
import signal

from agent_service import GymBroAgentService
from bot import build_application
from config import load_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("gym-bro")


async def main() -> None:
    settings = load_settings()
    agent_service = GymBroAgentService(settings)
    await agent_service.start()

    from supabase_store import supabase_enabled

    if supabase_enabled(settings):
        logger.info("Supabase enabled: %s", settings.supabase_url)
    else:
        logger.info("Supabase not configured — using local client-profile.yaml")

    from voice_transcriber import voice_transcription_enabled

    if voice_transcription_enabled(settings):
        logger.info("Voice transcription enabled (Whisper)")
    else:
        logger.info("Voice transcription disabled — set OPENAI_API_KEY to enable")

    if settings.miniapp_url:
        logger.info("Mini App URL configured: %s", settings.miniapp_url.rstrip("/"))
    else:
        logger.warning("MINIAPP_URL is empty — progress button disabled")

    app = build_application(settings, agent_service)
    await app.initialize()
    await app.start()

    from miniapp_setup import setup_miniapp_menu

    await setup_miniapp_menu(settings, app.bot)

    await app.updater.start_polling(drop_pending_updates=True)

    logger.info("Gym Bro bot is running (allowed users: %s)", settings.allowed_user_ids)

    stop_event = asyncio.Event()

    def _stop(*_: object) -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _stop)

    await stop_event.wait()

    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    await agent_service.stop()
    logger.info("Gym Bro bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
