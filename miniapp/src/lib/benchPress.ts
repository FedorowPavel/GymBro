import type { SupabaseClient } from "@supabase/supabase-js";

export type BenchSessionPoint = {
  date: string;
  label: string;
  maxWeight: number;
  reps: number;
  sets: number;
};

type RpcRow = {
  workout_date: string;
  max_weight: number;
  reps: number;
  sets_count: number;
};

function formatDateLabel(isoDate: string): string {
  const [, month, day] = isoDate.split("-");
  return `${day}.${month}`;
}

function mapRpcRows(rows: RpcRow[]): BenchSessionPoint[] {
  return rows.map((row) => ({
    date: row.workout_date,
    label: formatDateLabel(row.workout_date),
    maxWeight: Number(row.max_weight),
    reps: Number(row.reps),
    sets: Number(row.sets_count),
  }));
}

async function fetchViaRpc(
  supabase: SupabaseClient,
  telegramUserId: number,
): Promise<BenchSessionPoint[] | null> {
  const { data, error } = await supabase.rpc("get_bench_press_progress", {
    p_telegram_user_id: telegramUserId,
  });

  if (error) {
    // Function not deployed yet — fall back to direct table queries.
    if (error.code === "PGRST202" || error.message.includes("get_bench_press_progress")) {
      return null;
    }
    throw new Error(error.message);
  }

  return mapRpcRows((data as RpcRow[]) ?? []);
}

async function fetchViaTables(
  supabase: SupabaseClient,
  telegramUserId: number,
): Promise<BenchSessionPoint[]> {
  const { data: exercise, error: exerciseError } = await supabase
    .from("exercises")
    .select("id")
    .eq("slug", "bench_press")
    .maybeSingle();

  if (exerciseError) {
    throw new Error(exerciseError.message);
  }
  if (!exercise) {
    return [];
  }

  const { data: workouts, error: workoutsError } = await supabase
    .from("workouts")
    .select("id, workout_date")
    .eq("telegram_user_id", telegramUserId)
    .order("workout_date", { ascending: true });

  if (workoutsError) {
    throw new Error(workoutsError.message);
  }
  if (!workouts?.length) {
    return [];
  }

  const workoutIds = workouts.map((w) => w.id);
  const dateByWorkoutId = new Map(workouts.map((w) => [w.id, w.workout_date]));

  const { data: sets, error: setsError } = await supabase
    .from("workout_sets")
    .select("workout_id, weight_kg, reps, set_number")
    .eq("exercise_id", exercise.id)
    .in("workout_id", workoutIds);

  if (setsError) {
    throw new Error(setsError.message);
  }
  if (!sets?.length) {
    return [];
  }

  const byDate = new Map<
    string,
    Array<{ weight_kg: number; reps: number; set_number: number }>
  >();

  for (const row of sets) {
    const date = dateByWorkoutId.get(row.workout_id);
    if (!date) {
      continue;
    }
    const bucket = byDate.get(date) ?? [];
    bucket.push({
      weight_kg: Number(row.weight_kg),
      reps: Number(row.reps),
      set_number: Number(row.set_number),
    });
    byDate.set(date, bucket);
  }

  const points: BenchSessionPoint[] = [];

  for (const [date, sessionSets] of byDate.entries()) {
    const maxWeight = Math.max(...sessionSets.map((s) => s.weight_kg));
    const topSets = sessionSets.filter((s) => s.weight_kg === maxWeight);
    const reps = Math.max(...topSets.map((s) => s.reps));
    points.push({
      date,
      label: formatDateLabel(date),
      maxWeight,
      reps,
      sets: sessionSets.length,
    });
  }

  points.sort((a, b) => a.date.localeCompare(b.date));
  return points;
}

export async function fetchBenchPressProgress(
  supabase: SupabaseClient,
  telegramUserId: number,
): Promise<BenchSessionPoint[]> {
  const viaRpc = await fetchViaRpc(supabase, telegramUserId);
  if (viaRpc !== null) {
    return viaRpc;
  }
  return fetchViaTables(supabase, telegramUserId);
}
