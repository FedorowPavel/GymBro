# Gym Bro — пошаговый план

Персональный фитнес-тренер в Telegram на базе Cursor SDK (как iScout).

## Этап 0 — сейчас (MVP: локальный бот + Cursor)

- [x] Репозиторий `gym-bro` в `~/tg-bots/`
- [ ] Создать бота в [@BotFather](https://t.me/BotFather) → `TELEGRAM_BOT_TOKEN`
- [ ] Узнать свой Telegram user id ([@userinfobot](https://t.me/userinfobot)) → `TELEGRAM_ALLOWED_USER_IDS`
- [ ] API key: [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations) → `CURSOR_API_KEY`
- [ ] `cp .env.example .env` и заполнить переменные
- [ ] `./setup.sh` → `./run.sh`
- [ ] Написать боту в Telegram, проверить ответ агента

## Этап 1 — GitHub

```bash
cd ~/tg-bots/gym-bro
git init
git add .
git commit -m "Initial Gym Bro bot scaffold"
```

Создать репозиторий на GitHub `FedorowPavel/gym-bro` (веб или `gh repo create`), затем:

```bash
git remote add origin https://github.com/FedorowPavel/gym-bro.git
git branch -M main
git push -u origin main
```

Для cloud-режима на Railway позже: `AGENT_RUNTIME=cloud`, `CURSOR_CLOUD_REPO_URL=https://github.com/FedorowPavel/gym-bro`

## Этап 2 — Supabase (лог тренировок)

1. Проект на [supabase.com](https://supabase.com)
2. Таблицы: `profile`, `goals`, `injuries`, `exercises`, `workouts`, `workout_sets`
3. Seed из `config/client-profile.yaml`
4. В боте: читать профиль перед `agent.send()`, писать тренировки после парсинга ответа

## Этап 3 — Railway (деплой)

Скопировать подход из iScout: Dockerfile, secrets (`TELEGRAM_BOT_TOKEN`, `CURSOR_API_KEY`, Supabase keys).

## Этап 4 — React-дашборд (опционально)

Vercel + `supabase-js`, графики прогресса. Не в Telegram — отдельный сайт.

---

## Архитектура

```
Telegram → bot.py → agent_service.py → Cursor SDK (local/cloud)
                          ↑
              prompts.py + config/client-profile.yaml
                          ↓
              (этап 2) Supabase
```

## Команды бота

| Команда | Действие |
|---------|----------|
| `/start`, `/help` | Справка |
| `/reset` | Новый диалог с агентом |
| `/stop` | Прервать текущий запрос |
