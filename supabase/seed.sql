-- Gym Bro seed — replace 849995129 with your Telegram user id if different

insert into public.profile (
  telegram_user_id,
  display_name,
  birth_date,
  height_cm,
  weight_kg,
  body_type,
  occupation,
  sleep_hours,
  goal,
  notes,
  nutrition
) values (
  849995129,
  'Pavel',
  '1993-02-01',
  173,
  74,
  'ectomorph',
  'programmer',
  8,
  'strength + moderate hypertrophy (+2-3 kg lean mass)',
  'Left ankle recovering since 2026-06-16. Lower back: no barbell squat/deadlift.',
  '{"calories_bulk":"2500-2600","calories_cut":"2200-2300","protein_g":"120-130","fat_g":"70-80","carbs_g":"200-250"}'::jsonb
) on conflict (telegram_user_id) do update set
  weight_kg = excluded.weight_kg,
  goal = excluded.goal,
  notes = excluded.notes,
  nutrition = excluded.nutrition,
  updated_at = now();

insert into public.training_split (telegram_user_id, day_label, focus, sort_order) values
  (849995129, 'Mon/Tue', 'Chest + Biceps', 1),
  (849995129, 'Wed/Thu', 'Back + Triceps', 2),
  (849995129, 'Fri/Sat', 'Shoulders (+ legs sometimes)', 3)
on conflict do nothing;

insert into public.goals (telegram_user_id, horizon, description, sort_order) values
  (849995129, 'short', 'Bench 67-68x5-6', 1),
  (849995129, 'short', 'Vertical pulldown 60x8', 2),
  (849995129, 'short', 'Horizontal row 56-57x8', 3),
  (849995129, 'short', 'DB press 24-25x8', 4),
  (849995129, 'medium', 'Bench 70x5-6', 1),
  (849995129, 'medium', 'Weighted pull-ups: 10 BW then +2.5kg', 2),
  (849995129, 'long', '74-75 kg at same body fat', 1)
on conflict do nothing;

insert into public.injuries (telegram_user_id, body_part, injury_type, status, started_on, notes) values
  (849995129, 'left ankle', 'injury', 'recovering', '2026-06-16', 'Seated/supine only, no running yet'),
  (849995129, 'lower back', 'chronic', 'active', null, 'No barbell squat or deadlift')
on conflict do nothing;

insert into public.exercise_bans (telegram_user_id, exercise_name, reason) values
  (849995129, 'barbell squat', 'lower back'),
  (849995129, 'deadlift', 'lower back'),
  (849995129, 'barbell upright row', 'shoulder'),
  (849995129, 'straight bar french press', 'elbows'),
  (849995129, 'hyperextension', 'ankle + lower back'),
  (849995129, 'leg-supported rows', 'ankle')
on conflict do nothing;

insert into public.exercises (slug, name, muscle_group, equipment) values
  ('bench_press', 'Жим лёжа', 'chest', 'barbell'),
  ('incline_db_press', 'Жим гантелей на наклонной', 'chest', 'dumbbell'),
  ('db_curl', 'Подъём гантелей на бицепс', 'biceps', 'dumbbell'),
  ('hammer_curl', 'Молотки', 'biceps', 'dumbbell'),
  ('lat_pulldown', 'Тяга вертикального блока', 'back', 'cable'),
  ('cable_row', 'Тяга горизонтального блока', 'back', 'cable'),
  ('ez_french_press', 'Французский жим (EZ)', 'triceps', 'ez_bar'),
  ('rope_pushdown', 'Разгибания на блоке (верёвка)', 'triceps', 'cable'),
  ('seated_db_press', 'Жим гантелей сидя', 'shoulders', 'dumbbell'),
  ('lateral_raise', 'Разведения стоя', 'shoulders', 'dumbbell'),
  ('rear_delt_fly', 'Разведения в наклоне', 'shoulders', 'dumbbell')
on conflict (slug) do nothing;

-- Baseline lifts (July) as one workout snapshot
with w as (
  insert into public.workouts (telegram_user_id, workout_date, split_focus, notes)
  values (849995129, '2026-07-01', 'baseline', 'Imported from client profile (July baseline)')
  returning id
),
e as (select id, slug from public.exercises)
insert into public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
select w.id, e.id, s.set_number, s.weight_kg, s.reps
from w
cross join (values
  ('bench_press', 1, 66, 6), ('bench_press', 2, 66, 6), ('bench_press', 3, 66, 6),
  ('incline_db_press', 1, 24, 7), ('incline_db_press', 2, 24, 7), ('incline_db_press', 3, 24, 7),
  ('lat_pulldown', 1, 58, 8), ('lat_pulldown', 2, 58, 8), ('lat_pulldown', 3, 58, 8),
  ('cable_row', 1, 55, 8), ('cable_row', 2, 55, 8), ('cable_row', 3, 55, 8),
  ('seated_db_press', 1, 20, 6), ('seated_db_press', 2, 20, 6), ('seated_db_press', 3, 20, 6),
  ('ez_french_press', 1, 33.5, 8), ('ez_french_press', 2, 33.5, 8), ('ez_french_press', 3, 33.5, 8)
) as s(slug, set_number, weight_kg, reps)
join e on e.slug = s.slug;
