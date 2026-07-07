import type { SupabaseClient } from "@supabase/supabase-js";

export type BenchSessionPoint = {
  date: string;
  label: string;
  maxWeight: number;
  reps: number;
  sets: number;
};

function formatDateLabel(isoDate: string): string {
  const [, month, day] = isoDate.split("-");
  return `${day}.${month}`;
}

function asOne<T>(value: T | T[]): T {
  return Array.isArray(value) ? value[0] : value;
}

export async function fetchBenchPressProgress(
  supabase: SupabaseClient,
  telegramUserId: number,
): Promise<BenchSessionPoint[]> {
  const { data, error } = await supabase
    .from("workout_sets")
    .select(
      `
      weight_kg,
      reps,
      set_number,
      workouts!inner (
        workout_date,
        telegram_user_id
      ),
      exercises!inner (
        slug
      )
    `,
    )
    .eq("exercises.slug", "bench_press")
    .eq("workouts.telegram_user_id", telegramUserId);

  if (error) {
    throw new Error(error.message);
  }

  const byDate = new Map<
    string,
    Array<{ weight_kg: number; reps: number; set_number: number }>
  >();

  for (const row of data ?? []) {
    const workout = asOne(row.workouts as { workout_date: string } | { workout_date: string }[]);
    const date = workout.workout_date;
    const bucket = byDate.get(date) ?? [];
    bucket.push({
      weight_kg: Number(row.weight_kg),
      reps: Number(row.reps),
      set_number: Number(row.set_number),
    });
    byDate.set(date, bucket);
  }

  const points: BenchSessionPoint[] = [];

  for (const [date, sets] of byDate.entries()) {
    const maxWeight = Math.max(...sets.map((s) => s.weight_kg));
    const topSets = sets.filter((s) => s.weight_kg === maxWeight);
    const reps = Math.max(...topSets.map((s) => s.reps));
    points.push({
      date,
      label: formatDateLabel(date),
      maxWeight,
      reps,
      sets: sets.length,
    });
  }

  points.sort((a, b) => a.date.localeCompare(b.date));
  return points;
}
