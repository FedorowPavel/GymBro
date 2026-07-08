import type { SupabaseClient } from "@supabase/supabase-js";

export type SessionPoint = {
  date: string;
  label: string;
  maxWeight: number;
  reps: number;
  sets: number;
};

export type TonnagePoint = {
  date: string;
  label: string;
  tonnage: number;
  sets: number;
};

export type MuscleGroupOption = {
  id: string;
  label: string;
  sessionCount: number;
};

export type ExerciseOption = {
  slug: string;
  name: string;
  sessionCount: number;
};

export type LastExerciseLog = {
  workoutDate: string;
  weightKg: number;
  reps: number;
  sets: number;
};

export type WorkoutSessionItem = {
  slug: string;
  name: string;
  muscleGroup: string;
  sessionCount: number;
  isLoggedToday: boolean;
  lastWeightKg: number | null;
  lastReps: number | null;
  lastSets: number | null;
};

type ProgressRpcRow = {
  workout_date: string;
  max_weight: number;
  reps: number;
  sets_count: number;
};

type TonnageRpcRow = {
  workout_date: string;
  tonnage: number;
  sets_count: number;
};

type LastLogRpcRow = {
  workout_date: string;
  weight_kg: number;
  reps: number;
  sets_count: number;
};

type WorkoutSessionRpcRow = {
  slug: string;
  name: string;
  muscle_group: string;
  session_count: number;
  is_logged_today: boolean;
  last_weight_kg: number | null;
  last_reps: number | null;
  last_sets_count: number | null;
};

type MuscleRpcRow = {
  muscle_group: string;
  session_count: number;
};

type ExerciseRpcRow = {
  slug: string;
  name: string;
  session_count: number;
};

function formatDateLabel(isoDate: string): string {
  const [, month, day] = isoDate.split("-");
  return `${day}.${month}`;
}

function mapProgressRows(rows: ProgressRpcRow[]): SessionPoint[] {
  return rows.map((row) => ({
    date: row.workout_date,
    label: formatDateLabel(row.workout_date),
    maxWeight: Number(row.max_weight),
    reps: Number(row.reps),
    sets: Number(row.sets_count),
  }));
}

function mapTonnageRows(rows: TonnageRpcRow[]): TonnagePoint[] {
  return rows.map((row) => ({
    date: row.workout_date,
    label: formatDateLabel(row.workout_date),
    tonnage: Number(row.tonnage),
    sets: Number(row.sets_count),
  }));
}

export async function fetchMuscleGroupsWithHistory(
  supabase: SupabaseClient,
  telegramUserId: number,
): Promise<MuscleGroupOption[]> {
  const { data, error } = await supabase.rpc("get_user_muscle_groups", {
    p_telegram_user_id: telegramUserId,
  });

  if (error) {
    throw new Error(error.message);
  }

  const rows = (data as MuscleRpcRow[]) ?? [];
  return rows.map((row) => ({
    id: row.muscle_group,
    label: row.muscle_group,
    sessionCount: Number(row.session_count),
  }));
}

export async function fetchExercisesWithHistory(
  supabase: SupabaseClient,
  telegramUserId: number,
  muscleGroup: string,
): Promise<ExerciseOption[]> {
  const { data, error } = await supabase.rpc("get_user_exercises_for_muscle", {
    p_telegram_user_id: telegramUserId,
    p_muscle_group: muscleGroup,
  });

  if (error) {
    throw new Error(error.message);
  }

  const rows = (data as ExerciseRpcRow[]) ?? [];
  return rows.map((row) => ({
    slug: row.slug,
    name: row.name,
    sessionCount: Number(row.session_count),
  }));
}

export async function fetchExerciseProgress(
  supabase: SupabaseClient,
  telegramUserId: number,
  exerciseSlug: string,
): Promise<SessionPoint[]> {
  const { data, error } = await supabase.rpc("get_exercise_progress", {
    p_telegram_user_id: telegramUserId,
    p_exercise_slug: exerciseSlug,
  });

  if (error) {
    throw new Error(error.message);
  }

  return mapProgressRows((data as ProgressRpcRow[]) ?? []);
}

export async function fetchExerciseTonnageProgress(
  supabase: SupabaseClient,
  telegramUserId: number,
  exerciseSlug: string,
): Promise<TonnagePoint[]> {
  const { data, error } = await supabase.rpc("get_exercise_tonnage_progress", {
    p_telegram_user_id: telegramUserId,
    p_exercise_slug: exerciseSlug,
  });

  if (error) {
    throw new Error(error.message);
  }

  return mapTonnageRows((data as TonnageRpcRow[]) ?? []);
}

export async function fetchLastExerciseLog(
  supabase: SupabaseClient,
  telegramUserId: number,
  exerciseSlug: string,
): Promise<LastExerciseLog | null> {
  const { data, error } = await supabase.rpc("get_last_exercise_log", {
    p_telegram_user_id: telegramUserId,
    p_exercise_slug: exerciseSlug,
  });

  if (error) {
    throw new Error(error.message);
  }

  const rows = (data as LastLogRpcRow[]) ?? [];
  const row = rows[0];
  if (!row) {
    return null;
  }

  return {
    workoutDate: row.workout_date,
    weightKg: Number(row.weight_kg),
    reps: Number(row.reps),
    sets: Number(row.sets_count),
  };
}

export async function fetchMuscleSessionOverview(
  supabase: SupabaseClient,
  telegramUserId: number,
  muscleGroup: string,
  workoutDateIso: string,
): Promise<WorkoutSessionItem[]> {
  const { data, error } = await supabase.rpc("get_muscle_session_overview", {
    p_telegram_user_id: telegramUserId,
    p_muscle_group: muscleGroup,
    p_workout_date: workoutDateIso,
  });

  if (error) {
    throw new Error(error.message);
  }

  const rows = (data as WorkoutSessionRpcRow[]) ?? [];
  return rows.map((row) => ({
    slug: row.slug,
    name: row.name,
    muscleGroup: row.muscle_group,
    sessionCount: Number(row.session_count),
    isLoggedToday: Boolean(row.is_logged_today),
    lastWeightKg: row.last_weight_kg == null ? null : Number(row.last_weight_kg),
    lastReps: row.last_reps == null ? null : Number(row.last_reps),
    lastSets: row.last_sets_count == null ? null : Number(row.last_sets_count),
  }));
}

export async function logExerciseSession(
  supabase: SupabaseClient,
  telegramUserId: number,
  exerciseSlug: string,
  weightKg: number,
  reps: number,
  sets: number,
  workoutDateIso?: string,
): Promise<{ workoutId: string; replaced: boolean; splitFocus: string }> {
  const payload: Record<string, unknown> = {
    p_telegram_user_id: telegramUserId,
    p_exercise_slug: exerciseSlug,
    p_weight_kg: weightKg,
    p_reps: reps,
    p_sets_count: sets,
  };

  if (workoutDateIso) {
    payload.p_workout_date = workoutDateIso;
  }

  const { data, error } = await supabase.rpc("log_exercise_session", payload);
  if (error) {
    throw new Error(error.message);
  }

  const row = (data as Array<{
    workout_id: string;
    replaced: boolean;
    split_focus: string;
  }>)[0];

  if (!row) {
    throw new Error("Не удалось сохранить подходы");
  }

  return {
    workoutId: row.workout_id,
    replaced: Boolean(row.replaced),
    splitFocus: row.split_focus,
  };
}
