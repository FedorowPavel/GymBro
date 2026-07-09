-- Import full workout history for telegram_user_id 849995129
-- One workout row = one gym session (any muscle group combo)

BEGIN;

DELETE FROM public.workout_sets
WHERE workout_id IN (
  SELECT id FROM public.workouts WHERE telegram_user_id = 849995129
);
DELETE FROM public.workouts WHERE telegram_user_id = 849995129;

-- Helper: insert session with sets (slug, set_number, weight_kg, reps)
-- Chest + Biceps
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-03', 'Chest + Biceps', 'старт')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 61, 6), ('bench_press', 2, 61, 6), ('bench_press', 3, 61, 6),
  ('incline_db_press', 1, 20, 8), ('incline_db_press', 2, 20, 8),
  ('db_curl', 1, 11, 9), ('db_curl', 2, 11, 9), ('db_curl', 3, 11, 9),
  ('hammer_curl', 1, 9, 10), ('hammer_curl', 2, 9, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-13', 'Chest + Biceps', '+1 подход наклон, бицепс')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('incline_db_press', 1, 20, 8), ('incline_db_press', 2, 20, 8), ('incline_db_press', 3, 20, 8),
  ('db_curl', 1, 11, 10), ('db_curl', 2, 11, 10), ('db_curl', 3, 11, 10),
  ('hammer_curl', 1, 10, 10), ('hammer_curl', 2, 10, 10), ('hammer_curl', 3, 10, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-15', 'Chest', 'возврат после перерыва — только жим')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 61, 6), ('bench_press', 2, 61, 6), ('bench_press', 3, 61, 6)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-17', 'Chest + Biceps', '+1 кг')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 62, 6), ('bench_press', 2, 62, 6), ('bench_press', 3, 62, 6),
  ('incline_db_press', 1, 21, 8), ('incline_db_press', 2, 21, 8), ('incline_db_press', 3, 21, 8),
  ('db_curl', 1, 12, 8), ('db_curl', 2, 12, 8), ('db_curl', 3, 12, 8),
  ('hammer_curl', 1, 11, 9), ('hammer_curl', 2, 11, 9), ('hammer_curl', 3, 11, 9)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-19', 'Chest + Biceps', '+1 кг')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 63, 6), ('bench_press', 2, 63, 6), ('bench_press', 3, 63, 6),
  ('incline_db_press', 1, 22, 8), ('incline_db_press', 2, 22, 8), ('incline_db_press', 3, 22, 8),
  ('db_curl', 1, 13, 8), ('db_curl', 2, 13, 8), ('db_curl', 3, 13, 8),
  ('hammer_curl', 1, 12, 9), ('hammer_curl', 2, 12, 9), ('hammer_curl', 3, 12, 9)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-23', 'Chest + Biceps', '+1 кг')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 64, 6), ('bench_press', 2, 64, 6), ('bench_press', 3, 64, 6),
  ('incline_db_press', 1, 22, 8), ('incline_db_press', 2, 22, 8), ('incline_db_press', 3, 22, 8),
  ('db_curl', 1, 13, 8), ('db_curl', 2, 13, 8), ('db_curl', 3, 13, 8),
  ('hammer_curl', 1, 12, 9), ('hammer_curl', 2, 12, 9), ('hammer_curl', 3, 12, 9)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-30', 'Chest + Biceps', '+1 кг')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 65, 6), ('bench_press', 2, 65, 6), ('bench_press', 3, 65, 6),
  ('incline_db_press', 1, 24, 6), ('incline_db_press', 2, 24, 6), ('incline_db_press', 3, 24, 6),
  ('db_curl', 1, 13, 8), ('db_curl', 2, 13, 8), ('db_curl', 3, 13, 8),
  ('hammer_curl', 1, 13, 9), ('hammer_curl', 2, 13, 9), ('hammer_curl', 3, 13, 9)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-07-07', 'Chest + Biceps', '+1 кг')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('bench_press', 1, 66, 6), ('bench_press', 2, 66, 6), ('bench_press', 3, 66, 6),
  ('incline_db_press', 1, 24, 7), ('incline_db_press', 2, 24, 7), ('incline_db_press', 3, 24, 7),
  ('db_curl', 1, 14, 7), ('db_curl', 2, 14, 7), ('db_curl', 3, 14, 7),
  ('hammer_curl', 1, 13, 8), ('hammer_curl', 2, 13, 8), ('hammer_curl', 3, 13, 8)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

-- Back + Triceps
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-11', 'Back + Triceps', 'старт')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('lat_pulldown', 1, 55, 7), ('lat_pulldown', 2, 55, 7), ('lat_pulldown', 3, 55, 7),
  ('cable_row', 1, 50, 8), ('cable_row', 2, 50, 8), ('cable_row', 3, 50, 8),
  ('ez_french_press', 1, 32, 8), ('ez_french_press', 2, 32, 8), ('ez_french_press', 3, 32, 8),
  ('rope_pushdown', 1, 30, 10), ('rope_pushdown', 2, 30, 10), ('rope_pushdown', 3, 30, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-16', 'Back + Triceps', 'после травмы')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('lat_pulldown', 1, 55, 7), ('lat_pulldown', 2, 55, 7), ('lat_pulldown', 3, 55, 7),
  ('cable_row', 1, 52, 8), ('cable_row', 2, 52, 8), ('cable_row', 3, 52, 8),
  ('ez_french_press', 1, 32, 8), ('ez_french_press', 2, 32, 8), ('ez_french_press', 3, 32, 8),
  ('rope_pushdown', 1, 32.5, 10), ('rope_pushdown', 2, 32.5, 10), ('rope_pushdown', 3, 32.5, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-19', 'Back + Triceps', '+2.5 кг вертикальная тяга')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('lat_pulldown', 1, 57.5, 8), ('lat_pulldown', 2, 57.5, 8), ('lat_pulldown', 3, 57.5, 8),
  ('cable_row', 1, 55, 8), ('cable_row', 2, 55, 8), ('cable_row', 3, 55, 8),
  ('ez_french_press', 1, 33.5, 8), ('ez_french_press', 2, 33.5, 8), ('ez_french_press', 3, 33.5, 8),
  ('rope_pushdown', 1, 32.5, 10), ('rope_pushdown', 2, 32.5, 10), ('rope_pushdown', 3, 32.5, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-25', 'Back + Triceps', '+0.5 кг вертикальная тяга')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('lat_pulldown', 1, 58, 7), ('lat_pulldown', 2, 58, 7), ('lat_pulldown', 3, 58, 7),
  ('cable_row', 1, 55, 8), ('cable_row', 2, 55, 8), ('cable_row', 3, 55, 8),
  ('ez_french_press', 1, 33.5, 8), ('ez_french_press', 2, 33.5, 8), ('ez_french_press', 3, 33.5, 8),
  ('rope_pushdown', 1, 33, 10), ('rope_pushdown', 2, 33, 10), ('rope_pushdown', 3, 33, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-07-02', 'Back + Triceps', 'закрепление')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('lat_pulldown', 1, 58, 8), ('lat_pulldown', 2, 58, 8), ('lat_pulldown', 3, 58, 8),
  ('cable_row', 1, 55, 8), ('cable_row', 2, 55, 8), ('cable_row', 3, 55, 8),
  ('ez_french_press', 1, 33.5, 8), ('ez_french_press', 2, 33.5, 8), ('ez_french_press', 3, 33.5, 8),
  ('rope_pushdown', 1, 35, 8), ('rope_pushdown', 2, 35, 8), ('rope_pushdown', 3, 35, 8)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

-- Shoulders
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-13', 'Shoulders', 'старт')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('seated_db_press', 1, 19, 6), ('seated_db_press', 2, 19, 6), ('seated_db_press', 3, 19, 6),
  ('lateral_raise', 1, 8, 10), ('lateral_raise', 2, 8, 10), ('lateral_raise', 3, 8, 10),
  ('rear_delt_fly', 1, 7, 10), ('rear_delt_fly', 2, 7, 10), ('rear_delt_fly', 3, 7, 10)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-06-20', 'Shoulders', '+1 кг жим')
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, s.set_number, s.weight_kg, s.reps
FROM w
JOIN (VALUES
  ('seated_db_press', 1, 20, 6), ('seated_db_press', 2, 20, 6), ('seated_db_press', 3, 20, 6),
  ('lateral_raise', 1, 8, 10), ('lateral_raise', 2, 8, 10), ('lateral_raise', 3, 8, 10),
  ('rear_delt_fly', 1, 7, 12), ('rear_delt_fly', 2, 7, 12), ('rear_delt_fly', 3, 7, 12)
) AS s(slug, set_number, weight_kg, reps) ON true
JOIN public.exercises e ON e.slug = s.slug;

-- Legs: Выпады (lunge)
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-10-18', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 12, 12 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-11-01', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 13, 12 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-11-17', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 13, 8 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-11-30', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 14, 10 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-12-14', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 15, 10 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-12-28', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 15.5, 10 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-01-11', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 15.5, 10 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-01-25', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 15.5, 10 FROM w JOIN public.exercises e ON e.slug = 'lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-02-08', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 14, 9 FROM w JOIN public.exercises e ON e.slug = 'lunge';

-- Legs: Разгибания ног / квадрицепс (leg_extension)
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-09-22', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 30, 12 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-10-06', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 32.5, 12 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-10-20', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 32.5, 13 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-11-03', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 35, 11 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-11-17', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 35, 12 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-12-01', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 35, 14 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-12-15', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 35, 14 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2025-12-29', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 37.5, 14 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-01-12', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 37.5, 15 FROM w JOIN public.exercises e ON e.slug = 'leg_extension';

-- Legs: Выпады на месте (stationary_lunge)
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-02-14', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 6, 10 FROM w JOIN public.exercises e ON e.slug = 'stationary_lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-02-28', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 7, 10 FROM w JOIN public.exercises e ON e.slug = 'stationary_lunge';

WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-03-14', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 9, 10 FROM w JOIN public.exercises e ON e.slug = 'stationary_lunge';

-- Legs: Сгибания ног / бицепс бедра (leg_curl)
WITH w AS (
  INSERT INTO public.workouts (telegram_user_id, workout_date, split_focus, notes)
  VALUES (849995129, '2026-03-18', 'Legs', NULL)
  RETURNING id
)
INSERT INTO public.workout_sets (workout_id, exercise_id, set_number, weight_kg, reps)
SELECT w.id, e.id, 1, 20, 10 FROM w JOIN public.exercises e ON e.slug = 'leg_curl';

COMMIT;
