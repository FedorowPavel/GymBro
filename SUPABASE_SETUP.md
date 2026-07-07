# Подключение Supabase к Gym Bro

MCP для Supabase у агента **нет** — таблицы создаёшь в дашборде, ключи кладёшь в `.env`. Код бота подключим на следующем шаге.

## Шаг 1 — проект в Supabase

1. [supabase.com/dashboard](https://supabase.com/dashboard) → **New project**
2. Имя: `gym-bro` (или любое)
3. Пароль БД — сохрани (для SQL Editor, боту не нужен)
4. Регион — ближайший (eu-central и т.п.)

## Шаг 2 — SQL: таблицы

1. **SQL Editor** → **New query**
2. Скопируй весь файл [`supabase/schema.sql`](./supabase/schema.sql)
3. **Run**

## Шаг 3 — SQL: твои данные

1. Открой [`supabase/seed.sql`](./supabase/seed.sql)
2. Если Telegram id не `849995129` — замени во всех строках
3. Вставь в SQL Editor → **Run**

Проверка: **Table Editor** → `profile` — одна строка с твоим id.

## Шаг 4 — API keys

**Project Settings** → **API**:

| Переменная | Где взять |
|------------|-----------|
| `SUPABASE_URL` | Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | `service_role` (secret) |

Для бота на Railway/локально используй **service_role** — бот единственный клиент, RLS закрыт.

Добавь в `.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
TELEGRAM_USER_ID=849995129
```

`service_role` **никогда** не коммить и не класть во фронтенд.

## Шаг 5 — проверка из терминала

```bash
cd ~/tg-bots/gym-bro
.venv/bin/pip install supabase
.venv/bin/python -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
c = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])
r = c.table('profile').select('*').eq('telegram_user_id', int(os.environ['TELEGRAM_USER_ID'])).execute()
print(r.data)
"
```

Должен напечатать твой профиль.

## Шаг 6 — интеграция в бота (следующий коммит)

После того как SQL и ключи работают, в боте:

- читать профиль / цели / последние тренировки из Supabase перед ответом агента;
- позже — парсить «жим 66×6×3» и писать в `workout_sets`.

`config/client-profile.yaml` останется запасным вариантом, если Supabase не настроен.

## Опционально: Supabase MCP в Cursor

Чтобы агент в IDE мог ходить в БД:

1. [supabase.com/dashboard](https://supabase.com/dashboard) → проект → **Connect** → MCP
2. Cursor → Settings → MCP → добавить Supabase server

Это для разработки в Cursor, не для Telegram-бота на Railway.
