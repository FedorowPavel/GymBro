import logging

from telegram import MenuButtonDefault

from config import Settings

logger = logging.getLogger(__name__)


async def setup_miniapp_menu(settings: Settings, bot) -> None:
    """Reset Telegram menu button to default (no Web App icon left of input)."""
    del settings  # kept for call site compatibility
    try:
        await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
        logger.info("Telegram menu button reset to default")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to reset Telegram menu button")
