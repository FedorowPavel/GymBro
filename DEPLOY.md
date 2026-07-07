# Деплой Gym Bro на Railway

## 1. Закоммить и запушить

```bash
cd ~/tg-bots/gym-bro
git add -A
git status   # .env не должен быть в списке
git commit -m "Add Railway deploy"
git push
```

## 2. Railway

1. [railway.app](https://railway.app) → Login with GitHub
2. **New Project** → **Deploy from GitHub repo** → `FedorowPavel/gym-bro`
3. Railway подхватит `Dockerfile` автоматически

## 3. Variables (Settings → Variables)

| Variable | Значение |
|----------|----------|
| `TELEGRAM_BOT_TOKEN` | из @BotFather |
| `TELEGRAM_ALLOWED_USER_IDS` | `849995129` |
| `CURSOR_API_KEY` | [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations) |
| `CURSOR_MODEL` | `auto` |
| `AGENT_RUNTIME` | **`cloud`** |
| `CURSOR_CLOUD_REPO_URL` | `https://github.com/FedorowPavel/gym-bro` |
| `AGENT_ASK_TIMEOUT_SECONDS` | `300` (или `600` для долгих ответов) |
| `SUPABASE_URL` | `https://jdkoopavhaykgsghpwzx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | service_role из Supabase → Settings → API |
| `OPENAI_API_KEY` | ключ OpenAI для Whisper (голосовые) |

`TELEGRAM_USER_ID` не обязателен — бот берёт id из входящего сообщения.

Профиль и правила тренера: `config/client-profile.yaml`, `config/coach-rules.md` в репо (cloud agent клонирует GitHub).

## 4. Deploy

После variables Railway пересоберёт проект. В **Logs**:

```
Supabase enabled: https://...
Gym Bro bot is running (allowed users: ...)
Starting Cursor client (runtime=cloud)
```

## 5. Проверка

1. **Останови локальный бот** (`Ctrl+C` в терминале на Mac) — иначе два процесса дерутся за Telegram polling.
2. Напиши боту `/start`, затем вопрос про жим.

## 6. Автодеплой

Каждый `git push` в `main` → Railway пересобирает бота.

## Локально vs Railway

| | Mac | Railway |
|--|-----|---------|
| `AGENT_RUNTIME` | `local` | **`cloud`** |
| Cursor IDE | нужен открытым | не нужен |
| Supabase | те же ключи | те же ключи |
| Сессии агента | `data/sessions.json` | сбрасываются при redeploy (нормально) |

## Стоимость

Railway ~$5/мес после trial. Cursor cloud agent — по тарифу API.
