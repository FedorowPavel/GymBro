# RLS for Telegram Mini App (read-only via anon key).
# Run once in Supabase SQL Editor.

drop policy if exists "miniapp read exercises" on public.exercises;
drop policy if exists "miniapp read workouts" on public.workouts;
drop policy if exists "miniapp read workout_sets" on public.workout_sets;

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
