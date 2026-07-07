"""Telegram bot handlers."""

from __future__ import annotations

import asyncio
import logging

from telegram import Message, ReplyKeyboardRemove, Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

from agent_service import GymBroAgentService
from config import Settings
from exercise_menu import PROGRESS_BTN, main_reply_keyboard, progress_inline_keyboard
from log_wizard import handle_log_button, handle_log_callback, handle_wizard_text, start_log_wizard
from telegram_format import markdown_to_telegram_html
from voice_transcriber import transcribe_telegram_voice, voice_transcription_enabled
from workout_flow import prepare_agent_message

logger = logging.getLogger(__name__)

WELCOME = """Привет! Я Gym Bro — твой персональный тренер 💪

Могу:
• записать подходы кнопками (➕ Добавить упражнение) или текстом/голосом
• составить программу на тренировку
• разобрать прогресс

Команды:
/help — справка
/log — добавить упражнение кнопками
/stats — график прогресса
/reset — новый диалог с агентом
/stop — остановить текущий запрос
"""

STATUS_WAITING = "🔄 Спросил агента Cursor, жду ответ…"
STATUS_SLOW = "🔄 Агент ещё думает — обычно до минуты…"
STATUS_TRANSCRIBING = "🎤 Распознаю голосовое…"


def _is_allowed(settings: Settings, user_id: int | None) -> bool:
    return user_id is not None and user_id in settings.allowed_user_ids


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


async def _process_user_text(
    settings: Settings,
    agent_service: GymBroAgentService,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    user_text: str,
    *,
    status_msg: Message,
    header: str | None = None,
) -> None:
    stop = asyncio.Event()

    async def on_progress(preview: str) -> None:
        try:
            await status_msg.edit_text(_progress_preview(preview))
        except Exception:  # noqa: BLE001
            logger.debug("progress edit failed", exc_info=True)

    typing_task = asyncio.create_task(_keep_typing(context.bot, message.chat_id, stop))
    slow_task = asyncio.create_task(_slow_notice(status_msg, stop))

    async def on_retry() -> None:
        try:
            await status_msg.edit_text("🔄 Пустой ответ, повторяю запрос к агенту…")
        except Exception:  # noqa: BLE001
            logger.debug("retry status edit failed", exc_info=True)

    try:
        if header:
            try:
                await status_msg.edit_text(f"{header}\n\n{STATUS_WAITING}")
            except Exception:  # noqa: BLE001
                logger.debug("header status edit failed", exc_info=True)

        agent_text, saved_line = prepare_agent_message(settings, user_id, user_text)
        reply = await agent_service.ask(
            user_id,
            agent_text,
            on_progress=on_progress,
            on_retry=on_retry,
        )
        if saved_line:
            reply = f"{saved_line}\n\n{reply}"
        if header:
            reply = f"{header}\n\n{reply}"
    except Exception:  # noqa: BLE001
        logger.exception("Agent ask failed")
        reply = "Произошла ошибка. Попробуйте позже или /reset."
        if header:
            reply = f"{header}\n\n{reply}"
    finally:
        stop.set()
        typing_task.cancel()
        slow_task.cancel()
        await asyncio.gather(typing_task, slow_task, return_exceptions=True)

    await _finish_status(status_msg, reply)


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

        url = settings.miniapp_url.strip().rstrip("/")
        user_id = update.effective_user.id
        await update.message.reply_text("Обновляю меню…", reply_markup=ReplyKeyboardRemove())

        keyboard = main_reply_keyboard(url or None, telegram_user_id=user_id)
        await update.message.reply_text(WELCOME, reply_markup=keyboard)

        if url:
            await update.message.reply_text(
                "График жима — нажми кнопку:",
                reply_markup=progress_inline_keyboard(url, user_id),
            )
        else:
            await update.message.reply_text(
                "⚠️ MINIAPP_URL не задан в Railway (сервис **бота**, не miniapp).\n"
                "Добавь URL miniapp-сервиса и redeploy бота — появится кнопка 📊 Прогресс."
            )

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await start(update, context)

    async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _is_allowed(settings, update.effective_user and update.effective_user.id):
            await deny(update)
            return
        if not settings.miniapp_url:
            await update.message.reply_text(
                "Mini App не настроен. Добавь MINIAPP_URL в переменные бота на Railway."
            )
            return
        url = settings.miniapp_url.strip().rstrip("/")
        await update.message.reply_text(
            "Жим лёжа — прогресс:",
            reply_markup=progress_inline_keyboard(url, update.effective_user.id),
        )

    async def log_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.message
        if not _is_allowed(settings, user and user.id):
            await deny(update)
            return
        if message:
            await start_log_wizard(message, context)

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

        if await handle_log_button(message, context):
            return
        if message.text == PROGRESS_BTN:
            return
        if await handle_wizard_text(settings, message, context, user.id):
            return

        status_msg = await message.reply_text(STATUS_WAITING)
        await _process_user_text(
            settings,
            agent_service,
            message,
            context,
            user.id,
            message.text.strip(),
            status_msg=status_msg,
        )

    async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.message
        if user is None or message is None:
            return
        if not _is_allowed(settings, user.id):
            await deny(update)
            return

        audio = message.voice or message.audio
        if audio is None:
            return

        if not voice_transcription_enabled(settings):
            await message.reply_text(
                "Голосовые не настроены. Добавь OPENAI_API_KEY в .env или Railway Variables."
            )
            return

        status_msg = await message.reply_text(STATUS_TRANSCRIBING)
        try:
            tg_file = await audio.get_file()
            user_text = await transcribe_telegram_voice(settings, tg_file)
        except Exception:  # noqa: BLE001
            logger.exception("Voice transcription failed for user %s", user.id)
            await _finish_status(
                status_msg,
                "Не удалось распознать голосовое. Попробуй ещё раз или напиши текстом.",
            )
            return

        header = f"🎤 Распознал: {user_text}"
        await _process_user_text(
            settings,
            agent_service,
            message,
            context,
            user.id,
            user_text,
            status_msg=status_msg,
            header=header,
        )

    async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not _is_allowed(settings, user and user.id):
            if update.callback_query:
                await update.callback_query.answer("Доступ запрещён.", show_alert=True)
            return
        await handle_log_callback(settings, update, context, user.id)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("log", log_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, on_voice))
    return app
