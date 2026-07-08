-- Mini App extra RPCs (logging, tonnage, today overview).
-- Run in Supabase SQL Editor or via MCP migration.

-- ---------------------------------------------------------------------------
-- 1) Exercise tonnage progression (sum of weight_kg * reps per session)
-- ---------------------------------------------------------------------------
create or replace function public.get_exercise_tonnage_progress(
  p_telegram_user_id bigint,
  p_exercise_slug text
)
returns table (
  workout_date date,
  tonnage numeric,
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
  per_session as (
    select
      w.workout_date,
      sum(ws.weight_kg * ws.reps) as tonnage,
      count(*)::bigint as sets_count
    from public.workouts w
    join public.workout_sets ws on ws.workout_id = w.id
    join target t on t.id = ws.exercise_id
    where w.telegram_user_id = p_telegram_user_id
    group by w.workout_date
  )
  select workout_date, tonnage, sets_count
  from per_session
  order by workout_date asc;
$$;

-- ---------------------------------------------------------------------------
-- 2) Last log for an exercise (latest workout row on any date)
-- ---------------------------------------------------------------------------
create or replace function public.get_last_exercise_log(
  p_telegram_user_id bigint,
  p_exercise_slug text
)
returns table (
  workout_date date,
  weight_kg numeric,
  reps smallint,
  sets_count bigint
)
language sql
security definer
set search_path = public
stable
as $$
  with ex as (
    select id from public.exercises where slug = p_exercise_slug limit 1
  ),
  latest_workout as (
    select
      w.id as workout_id,
      w.workout_date,
      w.created_at
    from public.workouts w
    join public.workout_sets ws on ws.workout_id = w.id
    join ex on ex.id = ws.exercise_id
    where w.telegram_user_id = p_telegram_user_id
    order by w.workout_date desc, w.created_at desc
    limit 1
  ),
  latest_sets as (
    select
      ws.weight_kg,
      ws.reps,
      ws.set_number
    from public.workout_sets ws
    join latest_workout lw on lw.workout_id = ws.workout_id
    join ex on ex.id = ws.exercise_id
  )
  select
    lw.workout_date,
    (select ls.weight_kg from latest_sets ls order by ls.set_number asc limit 1),
    (select ls.reps::smallint from latest_sets ls order by ls.set_number asc limit 1),
    (select count(*)::bigint from latest_sets)
  from latest_workout lw;
$$;

-- ---------------------------------------------------------------------------
-- 3) Log an exercise session from mini-app:
--    replace workout_sets for (workout_id, exercise_id), create workout if needed
-- ---------------------------------------------------------------------------
create or replace function public.log_exercise_session(
  p_telegram_user_id bigint,
  p_exercise_slug text,
  p_weight_kg numeric,
  p_reps int,
  p_sets_count int,
  p_workout_date date default current_date
)
returns table (
  workout_id uuid,
  replaced boolean,
  split_focus text
)
language plpgsql
security definer
set search_path = public
volatile
as $$
declare
  v_exercise_id uuid;
  v_muscle_group text;
  v_split_focus text;
  v_workout_id uuid;
  v_replaced boolean;
  latest_row record;
  r record;
  v_age_hours numeric;
begin
  if p_sets_count is null or p_sets_count <= 0 then
    raise exception 'p_sets_count must be > 0';
  end if;
  if p_reps is null or p_reps <= 0 then
    raise exception 'p_reps must be > 0';
  end if;
  if p_weight_kg is null or p_weight_kg <= 0 then
    raise exception 'p_weight_kg must be > 0';
  end if;

  select id, muscle_group
    into v_exercise_id, v_muscle_group
  from public.exercises
  where slug = p_exercise_slug
  limit 1;

  if v_exercise_id is null then
    raise exception 'Unknown exercise slug: %', p_exercise_slug;
  end if;

  -- Keep behavior close to bot's workout_writer._infer_split_focus()
  if v_muscle_group = 'chest' then
    v_split_focus := 'Chest + Biceps';
  elsif v_muscle_group = 'back' then
    v_split_focus := 'Back + Triceps';
  elsif v_muscle_group = 'legs' then
    v_split_focus := 'Legs';
  else
    v_split_focus := 'Logged';
  end if;

  -- Pick the workout row to attach to (same date, prefer matching split_focus)
  v_workout_id := null;

  for r in
    select id, split_focus, created_at
    from public.workouts
    where telegram_user_id = p_telegram_user_id
      and workout_date = p_workout_date
    order by created_at desc
    limit 5
  loop
    if r.split_focus = v_split_focus or r.split_focus = 'Logged' then
      v_workout_id := r.id;
      exit;
    end if;
  end loop;

  -- If it's "today", allow continuing the latest recent workout within 6 hours.
  if v_workout_id is null and p_workout_date = current_date then
    select id, split_focus, created_at
      into latest_row
    from public.workouts
    where telegram_user_id = p_telegram_user_id
      and workout_date = p_workout_date
    order by created_at desc
    limit 1;

    if latest_row.id is not null then
      v_age_hours := (extract(epoch from (now() - latest_row.created_at)) / 3600);
      if v_age_hours <= 6 and latest_row.split_focus in (v_split_focus, 'Logged', 'In progress') then
        v_workout_id := latest_row.id;
      end if;
    end if;
  end if;

  -- Create workout if no suitable existing row found.
  if v_workout_id is null then
    insert into public.workouts (telegram_user_id, workout_date, split_focus, notes)
    values (p_telegram_user_id, p_workout_date, v_split_focus, 'Logged via Mini App')
    returning id into v_workout_id;
  end if;

  -- Replace sets for this (workout, exercise).
  select exists (
    select 1 from public.workout_sets
    where workout_id = v_workout_id and exercise_id = v_exercise_id
  )
  into v_replaced;

  delete from public.workout_sets
  where workout_id = v_workout_id and exercise_id = v_exercise_id;

  insert into public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
  select
    v_workout_id,
    v_exercise_id,
    gs.n,
    p_weight_kg::numeric,
    p_reps::smallint
  from generate_series(1, p_sets_count) as gs(n);

  workout_id := v_workout_id;
  replaced := coalesce(v_replaced, false);
  split_focus := v_split_focus;

  return next;
end;
$$;

-- ---------------------------------------------------------------------------
-- 4) Today workout overview:
--    show exercises suggested by training_split (filtered to those with history)
--    and show last logged set values for each exercise (if already logged today)
-- ---------------------------------------------------------------------------
create or replace function public.get_today_workout_overview(
  p_telegram_user_id bigint,
  p_workout_date date
)
returns table (
  focus text,
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
  with day_label as (
    select
      case
        when extract(isodow from p_workout_date) in (1, 2) then 'Mon/Tue'
        when extract(isodow from p_workout_date) in (3, 4) then 'Wed/Thu'
        when extract(isodow from p_workout_date) in (5, 6) then 'Fri/Sat'
        else 'Fri/Sat'
      end as dl
  ),
  plan as (
    select ts.focus
    from public.training_split ts
    join day_label d on true
    where ts.telegram_user_id = p_telegram_user_id
      and ts.day_label = d.dl
    order by ts.sort_order
    limit 1
  ),
  focus_to_muscles as (
    select
      coalesce(p.focus, 'Logged') as focus,
      case
        when p.focus = 'Chest + Biceps' then array['chest','biceps']
        when p.focus = 'Back + Triceps' then array['back','triceps']
        when p.focus = 'Shoulders (+ legs sometimes)' then array['shoulders','legs']
        else array['chest','back','biceps','triceps','shoulders','legs']
      end as muscle_ids
    from plan p
  ),
  exercises_to_suggest as (
    select
      e.slug,
      e.name,
      e.muscle_group,
      f.focus
    from public.exercises e
    cross join focus_to_muscles f
    where e.muscle_group = any(f.muscle_ids)
      and exists (
        select 1
        from public.workouts w
        join public.workout_sets ws on ws.workout_id = w.id
        where w.telegram_user_id = p_telegram_user_id
          and w.workout_date is not null
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
    -- pick latest workout row per exercise for that date
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
    join public.workout_sets ws on ws.workout_id = ltw.workout_id and ws.exercise_id = ltw.exercise_id
    group by ltw.exercise_id
  )
  select
    ets.focus,
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

-- ---------------------------------------------------------------------------
-- Grants for anon key
-- ---------------------------------------------------------------------------
revoke all on function public.get_exercise_tonnage_progress(bigint, text) from public;
revoke all on function public.get_last_exercise_log(bigint, text) from public;
revoke all on function public.log_exercise_session(bigint, text, numeric, int, int, date) from public;
revoke all on function public.get_today_workout_overview(bigint, date) from public;

grant execute on function public.get_exercise_tonnage_progress(bigint, text) to anon;
grant execute on function public.get_last_exercise_log(bigint, text) to anon;
grant execute on function public.log_exercise_session(bigint, text, numeric, int, int, date) to anon;
grant execute on function public.get_today_workout_overview(bigint, date) to anon;

