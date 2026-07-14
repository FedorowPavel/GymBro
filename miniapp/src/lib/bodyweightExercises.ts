/** Slugs with equipment=bodyweight in exercises catalog. */
const BODYWEIGHT_SLUGS = new Set([
  "pull_up",
  "chin_up",
  "push_up",
  "chest_dip",
  "bench_dip",
]);

export function isBodyweightExercise(slug: string): boolean {
  return BODYWEIGHT_SLUGS.has(slug);
}

export function formatBodyweightLog(weightKg: number, reps: number, sets: number): string {
  if (weightKg > 0) {
    return `+${weightKg} кг × ${reps} × ${sets}`;
  }
  return `${reps} × ${sets}`;
}

export function parseLogWeight(weightKg: string, bodyweightMode: boolean): number | null {
  if (bodyweightMode) {
    const trimmed = weightKg.trim();
    if (trimmed === "") {
      return 0;
    }
    const n = Number(trimmed);
    return Number.isFinite(n) && n >= 0 ? n : null;
  }
  const n = Number(weightKg);
  return Number.isFinite(n) && n > 0 ? n : null;
}
