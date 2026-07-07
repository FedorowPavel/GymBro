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

---

## Mini App (второй сервис на Railway)

Один репозиторий, **два сервиса** в проекте Railway.

### 1. Новый сервис

1. В проекте Railway → **+ New** → **GitHub Repo** → тот же `gym-bro`
2. **Settings → Root Directory** → `miniapp`
3. Railway подхватит `miniapp/Dockerfile`

### 2. Variables (miniapp service)

| Variable | Значение |
|----------|----------|
| `VITE_SUPABASE_URL` | `https://jdkoopavhaykgsghpwzx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | **anon** key из Supabase → Settings → API (не service_role!) |

Railway передаёт их как build args при `docker build`.

### 3. Supabase RLS

Один раз выполни `supabase/miniapp_rls.sql` в SQL Editor (read-only для anon).

### 4. URL Mini App → бот

1. Скопируй публичный URL miniapp-сервиса, например `https://gym-bro-miniapp.up.railway.app`
2. В **bot** service (Python, корень репо) добавь variable:
   - `MINIAPP_URL` = этот URL (без `/` в конце)
3. Redeploy **бота** → в Logs: `Mini App URL configured: https://...`
4. В Telegram: `/start` → сообщение «График жима» с inline-кнопкой

**Частая ошибка:** `MINIAPP_URL` добавили в miniapp-сервис — нужно в **бот**.

### 5. BotFather (для Web App кнопок)

В @BotFather:

1. `/mybots` → GymBro → **Bot Settings** → **Configure Mini App** → **Enable** → вставь тот же URL
2. `/setdomain` → выбери бота → домен: `up.railway.app` (или полный `xxx.up.railway.app`)

Без домена inline Web App кнопка может не работать — тогда жми **🌐 Открыть в браузере**.

### 6. BotFather Menu Button (опционально)

Можно также указать Web App URL в @BotFather → Bot Settings → Menu Button.

### 6. Локальная разработка miniapp

```bash
cd miniapp
cp .env.example .env   # anon key + VITE_DEV_TELEGRAM_USER_ID
npm install
npm run dev
```

Открой `http://localhost:5173` — без Telegram сработает dev user id.

---

## Локально vs Railway

| | Mac | Railway |
|--|-----|---------|
| `AGENT_RUNTIME` | `local` | **`cloud`** |
| Cursor IDE | нужен открытым | не нужен |
| Supabase | те же ключи | те же ключи |
| Сессии агента | `data/sessions.json` | сбрасываются при redeploy (нормально) |

## Стоимость

Railway ~$5/мес после trial. Cursor cloud agent — по тарифу API.
