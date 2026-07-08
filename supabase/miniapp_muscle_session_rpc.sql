-- Manual workout picker: exercises for one muscle group + today's log status.

create or replace function public.get_muscle_session_overview(
  p_telegram_user_id bigint,
  p_muscle_group text,
  p_workout_date date default current_date
)
returns table (
  slug text,
  name text,
  muscle_group text,
  is_logged_today boolean,
  last_weight_kg numeric,
  last_reps smallint,
  last_sets_count bigint
)
language sql
security definer
set search_path = public
stable
as $$
  with exercises_to_suggest as (
    select
      e.slug,
      e.name,
      e.muscle_group
    from public.exercises e
    where e.muscle_group = p_muscle_group
      and exists (
        select 1
        from public.workouts w
        join public.workout_sets ws on ws.workout_id = w.id
        where w.telegram_user_id = p_telegram_user_id
          and ws.exercise_id = e.id
      )
    order by e.name
  ),
  today_workouts as (
    select w.id, w.created_at
    from public.workouts w
    where w.telegram_user_id = p_telegram_user_id
      and w.workout_date = p_workout_date
  ),
  last_today_workout as (
    select distinct on (ws.exercise_id)
      ws.exercise_id,
      tw.id as workout_id
    from today_workouts tw
    join public.workout_sets ws on ws.workout_id = tw.id
    order by ws.exercise_id, tw.created_at desc
  ),
  last_today_sets as (
    select
      ltw.exercise_id,
      min(ws.weight_kg) as weight_kg,
      min(ws.reps)::smallint as reps,
      count(*)::bigint as sets_count
    from last_today_workout ltw
    join public.workout_sets ws
      on ws.workout_id = ltw.workout_id
     and ws.exercise_id = ltw.exercise_id
    group by ltw.exercise_id
  )
  select
    ets.slug,
    ets.name,
    ets.muscle_group,
    (lts.exercise_id is not null) as is_logged_today,
    lts.weight_kg as last_weight_kg,
    lts.reps as last_reps,
    lts.sets_count as last_sets_count
  from exercises_to_suggest ets
  left join public.exercises e on e.slug = ets.slug
  left join last_today_sets lts on lts.exercise_id = e.id
  order by is_logged_today desc, ets.name asc;
$$;

revoke all on function public.get_muscle_session_overview(bigint, text, date) from public;
grant execute on function public.get_muscle_session_overview(bigint, text, date) to anon;
