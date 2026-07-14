import type { LastWorkoutSummary as LastWorkoutSummaryData } from "../lib/progress";
import { formatBodyweightLog, isBodyweightExercise } from "../lib/bodyweightExercises";

type Props = {
  summary: LastWorkoutSummaryData;
};

function formatExerciseLine(slug: string, weightKg: number, reps: number, sets: number): string {
  if (isBodyweightExercise(slug)) {
    return formatBodyweightLog(weightKg, reps, sets);
  }
  return `${weightKg} кг × ${reps} × ${sets}`;
}

export function LastWorkoutSummary({ summary }: Props) {
  const titleParts = [summary.dateLabel];
  if (summary.splitFocus) {
    titleParts.push(summary.splitFocus);
  }

  return (
    <section className="last-workout" aria-label="Последняя тренировка">
      <div className="last-workout-label">Последняя тренировка</div>
      <div className="last-workout-title">{titleParts.join(" · ")}</div>
      <ul className="last-workout-list">
        {summary.exercises.map((ex) => (
          <li key={ex.slug}>
            <span className="last-workout-name">{ex.name}</span>
            <span className="last-workout-meta">
              {formatExerciseLine(ex.slug, ex.weightKg, ex.reps, ex.sets)}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
