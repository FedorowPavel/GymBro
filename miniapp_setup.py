import logging

from telegram import MenuButtonWebApp, WebAppInfo

from config import Settings

logger = logging.getLogger(__name__)


async def setup_miniapp_menu(settings: Settings, bot) -> None:
    """Set Telegram menu button → Mini App (if MINIAPP_URL is configured)."""
    url = settings.miniapp_url.strip().rstrip("/")
    if not url:
        logger.info("MINIAPP_URL not set — menu button skipped")
        return
    if not url.startswith("https://"):
        logger.warning("MINIAPP_URL must be https:// — got: %s", url)
        return
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="📊 Прогресс",
                web_app=WebAppInfo(url=url),
            )
        )
        logger.info("Mini App menu button set: %s", url)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to set Mini App menu button")
