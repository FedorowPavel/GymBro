import WebApp from "@twa-dev/sdk";

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
        initDataUnsafe?: {
          user?: { id?: number };
        };
        ready?: () => void;
      };
    };
  }
}

function parseUserIdFromInitData(initData: string): number | null {
  if (!initData) {
    return null;
  }
  const params = new URLSearchParams(initData);
  const userRaw = params.get("user");
  if (!userRaw) {
    return null;
  }
  try {
    const user = JSON.parse(userRaw) as { id?: number };
    return typeof user.id === "number" ? user.id : null;
  } catch {
    return null;
  }
}

function readUserIdFromUrl(): number | null {
  const fromQuery = new URLSearchParams(window.location.search).get("uid");
  if (!fromQuery) {
    return null;
  }
  const parsed = Number(fromQuery);
  return Number.isFinite(parsed) ? parsed : null;
}

function readUserIdFromSdk(): number | null {
  const fromUnsafe = WebApp.initDataUnsafe.user?.id;
  if (fromUnsafe) {
    return fromUnsafe;
  }

  const fromWindowUnsafe = window.Telegram?.WebApp?.initDataUnsafe?.user?.id;
  if (fromWindowUnsafe) {
    return fromWindowUnsafe;
  }

  const initData = WebApp.initData || window.Telegram?.WebApp?.initData || "";
  return parseUserIdFromInitData(initData);
}

/** Telegram user id from Mini App context, URL ?uid=, or dev fallback. */
export function getTelegramUserId(): number | null {
  const fromTelegram = readUserIdFromSdk();
  if (fromTelegram) {
    return fromTelegram;
  }

  const fromUrl = readUserIdFromUrl();
  if (fromUrl) {
    return fromUrl;
  }

  const fallback = import.meta.env.VITE_DEV_TELEGRAM_USER_ID as string | undefined;
  if (fallback) {
    const parsed = Number(fallback);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

/** Wait until Telegram injects user id (first paint can be too early). */
export function waitForTelegramUserId(timeoutMs = 3000): Promise<number | null> {
  return new Promise((resolve) => {
    const started = Date.now();

    const tick = () => {
      const id = getTelegramUserId();
      if (id) {
        resolve(id);
        return;
      }
      if (Date.now() - started >= timeoutMs) {
        resolve(null);
        return;
      }
      window.setTimeout(tick, 100);
    };

    tick();
  });
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
