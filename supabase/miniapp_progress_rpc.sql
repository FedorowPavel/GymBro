-- Progress mini app RPCs. Run in Supabase SQL Editor (or via MCP migration).

create or replace function public.get_user_muscle_groups(p_telegram_user_id bigint)
returns table (muscle_group text, session_count bigint)
language sql
security definer
set search_path = public
stable
as $$
  select
    e.muscle_group,
    count(distinct w.workout_date)::bigint as session_count
  from public.workouts w
  join public.workout_sets ws on ws.workout_id = w.id
  join public.exercises e on e.id = ws.exercise_id
  where w.telegram_user_id = p_telegram_user_id
    and e.muscle_group is not null
    and e.muscle_group <> ''
  group by e.muscle_group
  order by e.muscle_group;
$$;

create or replace function public.get_user_exercises_for_muscle(
  p_telegram_user_id bigint,
  p_muscle_group text
)
returns table (slug text, name text, session_count bigint)
language sql
security definer
set search_path = public
stable
as $$
  select
    e.slug,
    e.name,
    count(distinct w.workout_date)::bigint as session_count
  from public.workouts w
  join public.workout_sets ws on ws.workout_id = w.id
  join public.exercises e on e.id = ws.exercise_id
  where w.telegram_user_id = p_telegram_user_id
    and e.muscle_group = p_muscle_group
  group by e.slug, e.name
  order by e.name;
$$;

create or replace function public.get_exercise_progress(
  p_telegram_user_id bigint,
  p_exercise_slug text
)
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
  with target as (
    select id from public.exercises where slug = p_exercise_slug limit 1
  ),
  sessions as (
    select
      w.workout_date,
      max(ws.weight_kg) as max_weight
    from public.workouts w
    join public.workout_sets ws on ws.workout_id = w.id
    join target t on t.id = ws.exercise_id
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
    join target t on t.id = ws.exercise_id
    where ws.weight_kg = s.max_weight
    group by s.workout_date, s.max_weight
  )
  select workout_date, max_weight, reps::smallint, sets_count
  from top_sets
  order by workout_date asc;
$$;

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
  select * from public.get_exercise_progress(p_telegram_user_id, 'bench_press');
$$;

revoke all on function public.get_user_muscle_groups(bigint) from public;
revoke all on function public.get_user_exercises_for_muscle(bigint, text) from public;
revoke all on function public.get_exercise_progress(bigint, text) from public;
revoke all on function public.get_bench_press_progress(bigint) from public;

grant execute on function public.get_user_muscle_groups(bigint) to anon;
grant execute on function public.get_user_exercises_for_muscle(bigint, text) to anon;
grant execute on function public.get_exercise_progress(bigint, text) to anon;
grant execute on function public.get_bench_press_progress(bigint) to anon;
