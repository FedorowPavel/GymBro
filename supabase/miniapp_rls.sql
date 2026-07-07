# RLS for Telegram Mini App (read-only via anon key).
# Run once in Supabase SQL Editor (Dashboard → SQL → New query).

drop policy if exists "miniapp read profile" on public.profile;
drop policy if exists "miniapp read exercises" on public.exercises;
drop policy if exists "miniapp read workouts" on public.workouts;
drop policy if exists "miniapp read workout_sets" on public.workout_sets;

-- Needed so workout policies can see registered users.
create policy "miniapp read profile"
  on public.profile
  for select
  to anon
  using (true);

create policy "miniapp read exercises"
  on public.exercises
  for select
  to anon
  using (true);

create policy "miniapp read workouts"
  on public.workouts
  for select
  to anon
  using (
    telegram_user_id in (select telegram_user_id from public.profile)
  );

create policy "miniapp read workout_sets"
  on public.workout_sets
  for select
  to anon
  using (
    exists (
      select 1
      from public.workouts w
      where w.id = workout_id
        and w.telegram_user_id in (select telegram_user_id from public.profile)
    )
  );

-- ---------------------------------------------------------------------------
-- RPC: bench press progress (security definer — works even if RLS is strict)
-- ---------------------------------------------------------------------------
create or replace function public.get_bench_press_progress(p_telegram_user_id bigint)
returns table (
  workout_date date,
  max_weight numeric,
  reps smallint,
  sets_count bigint
)
language sql
security definer
set search_path = public
stable
as $$
  with bench as (
    select id from public.exercises where slug = 'bench_press' limit 1
  ),
  sessions as (
    select
      w.workout_date,
      max(ws.weight_kg) as max_weight
    from public.workouts w
    join public.workout_sets ws on ws.workout_id = w.id
    join bench b on b.id = ws.exercise_id
    where w.telegram_user_id = p_telegram_user_id
    group by w.workout_date
  ),
  top_sets as (
    select
      s.workout_date,
      s.max_weight,
      max(ws.reps) as reps,
      count(*)::bigint as sets_count
    from sessions s
    join public.workouts w
      on w.workout_date = s.workout_date
     and w.telegram_user_id = p_telegram_user_id
    join public.workout_sets ws on ws.workout_id = w.id
    join bench b on b.id = ws.exercise_id
    where ws.weight_kg = s.max_weight
    group by s.workout_date, s.max_weight
  )
  select workout_date, max_weight, reps::smallint, sets_count
  from top_sets
  order by workout_date asc;
$$;

revoke all on function public.get_bench_press_progress(bigint) from public;
grant execute on function public.get_bench_press_progress(bigint) to anon;
