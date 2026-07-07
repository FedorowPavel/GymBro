# Gym Bro

Персональный фитнес-тренер в Telegram на Cursor SDK (по образцу [iScout](../iScout)).

## Быстрый старт

```bash
cd ~/tg-bots/gym-bro
chmod +x setup.sh run.sh
./setup.sh
# отредактируй .env
./run.sh
```

## Переменные окружения

См. `.env.example`. Минимум:

- `TELEGRAM_BOT_TOKEN` — от @BotFather
- `TELEGRAM_ALLOWED_USER_IDS` — твой Telegram user id
- `CURSOR_API_KEY` — [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations)

Локально: `AGENT_RUNTIME=local` (нужен Cursor на Mac).

## Структура

| Файл | Назначение |
|------|------------|
| `bot.py` | Telegram handlers |
| `agent_service.py` | Cursor SDK, сессии |
| `prompts.py` | System prompt тренера |
| `config/client-profile.yaml` | Твой профиль (позже → Supabase) |
| `config/coach-rules.md` | Железные правила тренировок |
| `PLAN.md` | Пошаговый план развития |

## Команды в Telegram

- `/start`, `/help` — справка
- `/reset` — новый диалог
- `/stop` — прервать запрос

Подробный план: [PLAN.md](./PLAN.md)
