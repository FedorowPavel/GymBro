import WebApp from "@twa-dev/sdk";

/** Telegram user id from Mini App context, or dev fallback from env. */
export function getTelegramUserId(): number | null {
  const fromTelegram = WebApp.initDataUnsafe.user?.id;
  if (fromTelegram) {
    return fromTelegram;
  }

  const fallback = import.meta.env.VITE_DEV_TELEGRAM_USER_ID as string | undefined;
  if (fallback) {
    const parsed = Number(fallback);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

export function applyTelegramTheme(): void {
  const root = document.documentElement;
  const theme = WebApp.themeParams;
  if (theme.bg_color) root.style.setProperty("--tg-theme-bg-color", theme.bg_color);
  if (theme.text_color) root.style.setProperty("--tg-theme-text-color", theme.text_color);
  if (theme.hint_color) root.style.setProperty("--tg-theme-hint-color", theme.hint_color);
  if (theme.secondary_bg_color) {
    root.style.setProperty("--tg-theme-secondary-bg-color", theme.secondary_bg_color);
  }
}
