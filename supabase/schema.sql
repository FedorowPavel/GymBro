-- Gym Bro — run in Supabase SQL Editor (Dashboard → SQL → New query)

-- Extensions
create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Profile (one row per Telegram user)
-- ---------------------------------------------------------------------------
create table if not exists public.profile (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null unique,
  display_name text,
  birth_date date,
  height_cm smallint,
  weight_kg numeric(5, 2),
  body_type text,
  occupation text,
  sleep_hours numeric(3, 1),
  goal text,
  notes text,
  nutrition jsonb default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Goals
-- ---------------------------------------------------------------------------
create table if not exists public.goals (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null references public.profile (telegram_user_id) on delete cascade,
  horizon text not null check (horizon in ('short', 'medium', 'long')),
  description text not null,
  exercise_slug text,
  target_weight_kg numeric(6, 2),
  target_reps smallint,
  status text not null default 'active' check (status in ('active', 'achieved', 'paused')),
  sort_order smallint not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists goals_user_status_idx on public.goals (telegram_user_id, status);

-- ---------------------------------------------------------------------------
-- Injuries & exercise bans
-- ---------------------------------------------------------------------------
create table if not exists public.injuries (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null references public.profile (telegram_user_id) on delete cascade,
  body_part text not null,
  injury_type text not null default 'injury',
  description text,
  status text not null default 'active' check (status in ('active', 'recovering', 'resolved')),
  started_on date,
  resolved_on date,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.exercise_bans (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null references public.profile (telegram_user_id) on delete cascade,
  exercise_name text not null,
  reason text,
  until_date date,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Training split
-- ---------------------------------------------------------------------------
create table if not exists public.training_split (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null references public.profile (telegram_user_id) on delete cascade,
  day_label text not null,
  focus text not null,
  sort_order smallint not null default 0,
  is_active boolean not null default true
);

-- ---------------------------------------------------------------------------
-- Exercises catalog + user program
-- ---------------------------------------------------------------------------
create table if not exists public.exercises (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  muscle_group text,
  equipment text,
  technique_notes text
);

create table if not exists public.user_exercises (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null references public.profile (telegram_user_id) on delete cascade,
  exercise_id uuid not null references public.exercises (id),
  split_id uuid references public.training_split (id) on delete set null,
  role text not null default 'base' check (role in ('base', 'accessory')),
  target_reps_min smallint,
  target_reps_max smallint,
  target_sets smallint,
  sort_order smallint not null default 0,
  is_active boolean not null default true,
  unique (telegram_user_id, exercise_id)
);

-- ---------------------------------------------------------------------------
-- Workouts & sets (core logging)
-- ---------------------------------------------------------------------------
create table if not exists public.workouts (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint not null references public.profile (telegram_user_id) on delete cascade,
  workout_date date not null default current_date,
  split_focus text,
  duration_min smallint,
  overall_rpe smallint check (overall_rpe between 1 and 10),
  notes text,
  created_at timestamptz not null default now()
);

create index if not exists workouts_user_date_idx on public.workouts (telegram_user_id, workout_date desc);

create table if not exists public.workout_sets (
  id uuid primary key default gen_random_uuid(),
  workout_id uuid not null references public.workouts (id) on delete cascade,
  exercise_id uuid not null references public.exercises (id),
  set_number smallint not null,
  weight_kg numeric(6, 2) not null,
  reps smallint not null,
  is_warmup boolean not null default false,
  rpe smallint check (rpe between 1 and 10),
  notes text,
  unique (workout_id, exercise_id, set_number)
);

create index if not exists workout_sets_workout_idx on public.workout_sets (workout_id);

-- ---------------------------------------------------------------------------
-- RLS: backend uses service_role key; anon key blocked by default
-- ---------------------------------------------------------------------------
alter table public.profile enable row level security;
alter table public.goals enable row level security;
alter table public.injuries enable row level security;
alter table public.exercise_bans enable row level security;
alter table public.training_split enable row level security;
alter table public.exercises enable row level security;
alter table public.user_exercises enable row level security;
alter table public.workouts enable row level security;
alter table public.workout_sets enable row level security;

-- Service role bypasses RLS. No public policies for MVP (bot-only access).
