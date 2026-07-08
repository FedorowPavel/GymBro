import type { SupabaseClient } from "@supabase/supabase-js";

export type SessionPoint = {
  date: string;
  label: string;
  maxWeight: number;
  reps: number;
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

type ProgressRpcRow = {
  workout_date: string;
  max_weight: number;
  reps: number;
  sets_count: number;
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
