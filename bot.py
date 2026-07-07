"""Telegram bot handlers."""

from __future__ import annotations

import asyncio
import logging

from telegram import Message, Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

from agent_service import GymBroAgentService
from config import Settings
from telegram_format import markdown_to_telegram_html

logger = logging.getLogger(__name__)

WELCOME = """Привет! Я Gym Bro — твой персональный тренер 💪

Могу:
• записать тренировку (например: жим 66×6×3)
• разобрать прогресс
• предложить план на следующую сессию

Команды:
/help — справка
/reset — новый диалог с агентом
/stop — остановить текущий запрос
"""


def _is_allowed(settings: Settings, user_id: int | None) -> bool:
    return user_id is not None and user_id in settings.allowed_user_ids


STATUS_WAITING = "🔄 Спросил агента Cursor, жду ответ…"
STATUS_SLOW = "🔄 Агент ещё думает — обычно до минуты…"


async def _keep_typing(bot, chat_id: int, stop: asyncio.Event, *, interval: float = 4.0) -> None:
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        except Exception:  # noqa: BLE001
            logger.debug("send_chat_action failed", exc_info=True)
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue


async def _slow_notice(status_msg: Message, stop: asyncio.Event) -> None:
    try:
        await asyncio.wait_for(stop.wait(), timeout=25.0)
    except asyncio.TimeoutError:
        try:
            await status_msg.edit_text(STATUS_SLOW)
        except Exception:  # noqa: BLE001
            logger.debug("slow status edit failed", exc_info=True)


async def _send_reply(message: Message, text: str, *, edit: bool = False) -> None:
    html = markdown_to_telegram_html(text)
    try:
        if edit:
            await message.edit_text(html, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text(html, parse_mode=ParseMode.HTML)
    except BadRequest:
        logger.warning("HTML parse failed, sending plain text")
        if edit:
            await message.edit_text(text)
        else:
            await message.reply_text(text)


async def _finish_status(status_msg: Message, reply: str) -> None:
    try:
        await _send_reply(status_msg, reply, edit=True)
    except Exception:  # noqa: BLE001
        logger.warning("Could not edit status message, sending new reply")
        await _send_reply(status_msg, reply, edit=False)


def _progress_preview(preview: str) -> str:
    preview = preview.strip()
    if not preview:
        return STATUS_SLOW
    if len(preview) > 300:
        preview = "…" + preview[-300:]
    return f"🔄 Агент работает…\n\n{preview}"


def build_application(settings: Settings, agent_service: GymBroAgentService) -> Application:
    request = HTTPXRequest(httpx_kwargs={"trust_env": False})
    app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .concurrent_updates(True)
        .request(request)
        .build()
    )

    async def deny(update: Update) -> None:
        if update.effective_message:
            await update.effective_message.reply_text("Доступ запрещён.")

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _is_allowed(settings, update.effective_user and update.effective_user.id):
            await deny(update)
            return
        await update.message.reply_text(WELCOME)

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await start(update, context)

    async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not _is_allowed(settings, user and user.id):
            await deny(update)
            return
        await agent_service.stop_run(user.id)
        await agent_service.reset(user.id)
        await update.message.reply_text("Диалог сброшен. Можете писать заново.")

    async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not _is_allowed(settings, user and user.id):
            await deny(update)
            return
        stopped = await agent_service.stop_run(user.id)
        if stopped:
            await update.message.reply_text("Текущий запрос остановлен.")
        else:
            await update.message.reply_text("Сейчас нет активного запроса.")

    async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.message
        if user is None or message is None or not message.text:
            return
        if not _is_allowed(settings, user.id):
            await deny(update)
            return

        status_msg = await message.reply_text(STATUS_WAITING)
        stop = asyncio.Event()

        async def on_progress(preview: str) -> None:
            try:
                await status_msg.edit_text(_progress_preview(preview))
            except Exception:  # noqa: BLE001
                logger.debug("progress edit failed", exc_info=True)

        typing_task = asyncio.create_task(_keep_typing(context.bot, message.chat_id, stop))
        slow_task = asyncio.create_task(_slow_notice(status_msg, stop))

        try:
            reply = await agent_service.ask(
                user.id,
                message.text.strip(),
                on_progress=on_progress,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Agent ask failed")
            reply = "Произошла ошибка. Попробуйте позже или /reset."
        finally:
            stop.set()
            typing_task.cancel()
            slow_task.cancel()
            await asyncio.gather(typing_task, slow_task, return_exceptions=True)

        await _finish_status(status_msg, reply)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    return app
