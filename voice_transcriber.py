"""Transcribe Telegram voice messages via OpenAI Whisper."""

from __future__ import annotations

import asyncio
import logging
from io import BytesIO

from openai import OpenAI
from telegram import File

from config import Settings

logger = logging.getLogger(__name__)


def voice_transcription_enabled(settings: Settings) -> bool:
    return bool(settings.openai_api_key.strip())


async def transcribe_telegram_voice(
    settings: Settings,
    tg_file: File,
    *,
    language: str = "ru",
) -> str:
    if not voice_transcription_enabled(settings):
        raise ValueError("OPENAI_API_KEY is not configured")

    audio_bytes = bytes(await tg_file.download_as_bytearray())
    if not audio_bytes:
        raise ValueError("Empty voice file")

    return await asyncio.to_thread(_transcribe_bytes, settings, audio_bytes, language)


def _transcribe_bytes(settings: Settings, audio_bytes: bytes, language: str) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    audio = BytesIO(audio_bytes)
    audio.name = "voice.ogg"
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio,
        language=language,
    )
    text = (result.text or "").strip()
    if not text:
        raise ValueError("Whisper returned empty text")
    return text
