-- Common gym exercises (non-exotic). Safe to re-run: ON CONFLICT DO NOTHING.

insert into public.exercises (slug, name, muscle_group, equipment) values
  -- Chest
  ('incline_barbell_press', 'Жим штанги на наклонной', 'chest', 'barbell'),
  ('dumbbell_bench_press', 'Жим гантелей лёжа', 'chest', 'dumbbell'),
  ('dumbbell_fly', 'Разведение гантелей лёжа', 'chest', 'dumbbell'),
  ('cable_crossover', 'Сведение в кроссовере', 'chest', 'cable'),
  ('pec_deck', 'Сведение в тренажёре (пек-дек)', 'chest', 'machine'),
  ('chest_dip', 'Отжимания на брусьях (грудь)', 'chest', 'bodyweight'),
  ('push_up', 'Отжимания от пола', 'chest', 'bodyweight'),
  -- Back
  ('pull_up', 'Подтягивания', 'back', 'bodyweight'),
  ('chin_up', 'Подтягивания обратным хватом', 'back', 'bodyweight'),
  ('barbell_row', 'Тяга штанги в наклоне', 'back', 'barbell'),
  ('dumbbell_row', 'Тяга гантели в наклоне', 'back', 'dumbbell'),
  ('t_bar_row', 'Т-тяга', 'back', 'barbell'),
  ('face_pull', 'Тяга к лицу', 'back', 'cable'),
  ('straight_arm_pulldown', 'Пуловер на блоке', 'back', 'cable'),
  ('shrug', 'Шраги', 'back', 'barbell'),
  -- Biceps
  ('barbell_curl', 'Подъём штанги на бицепс', 'biceps', 'barbell'),
  ('preacher_curl', 'Сгибания на скамье Скотта', 'biceps', 'barbell'),
  ('cable_curl', 'Сгибания на блоке (бицепс)', 'biceps', 'cable'),
  ('incline_db_curl', 'Сгибания гантелей на наклонной', 'biceps', 'dumbbell'),
  ('concentration_curl', 'Концентрированные сгибания', 'biceps', 'dumbbell'),
  -- Triceps
  ('close_grip_bench_press', 'Жим узким хватом', 'triceps', 'barbell'),
  ('overhead_triceps_extension', 'Разгибания из-за головы', 'triceps', 'dumbbell'),
  ('dumbbell_kickback', 'Разгибания гантели в наклоне', 'triceps', 'dumbbell'),
  ('bench_dip', 'Отжимания от скамьи (трицепс)', 'triceps', 'bodyweight'),
  -- Shoulders
  ('barbell_overhead_press', 'Жим штанги стоя', 'shoulders', 'barbell'),
  ('arnold_press', 'Жим Арнольда', 'shoulders', 'dumbbell'),
  ('front_raise', 'Подъём гантелей перед собой', 'shoulders', 'dumbbell'),
  ('cable_lateral_raise', 'Махи в стороны на блоке', 'shoulders', 'cable'),
  -- Legs
  ('lunge', 'Выпады', 'legs', 'dumbbell'),
  ('leg_extension', 'Разгибания ног в тренажёре', 'legs', 'machine'),
  ('leg_curl', 'Сгибания ног в тренажёре', 'legs', 'machine')
on conflict (slug) do nothing;
