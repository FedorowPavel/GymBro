import { useMemo } from "react";
import type { LastExerciseLog } from "../lib/progress";
import { formatBodyweightLog, isBodyweightExercise } from "../lib/bodyweightExercises";

type Props = {
  exerciseSlug: string;
  exerciseName: string;
  lastLog: LastExerciseLog | null;
  weightKg: string;
  reps: string;
  sets: string;
  onWeightKgChange: (v: string) => void;
  onRepsChange: (v: string) => void;
  onSetsChange: (v: string) => void;
  onRepeat: () => void;
  onSave: () => Promise<void>;
  saving: boolean;
};

function toNumberOrNull(v: string): number | null {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function parseOptionalWeight(v: string): number | null {
  const trimmed = v.trim();
  if (trimmed === "") {
    return 0;
  }
  return toNumberOrNull(trimmed);
}

export function QuickLogPanel({
  exerciseSlug,
  exerciseName,
  lastLog,
  weightKg,
  reps,
  sets,
  onWeightKgChange,
  onRepsChange,
  onSetsChange,
  onRepeat,
  onSave,
  saving,
}: Props) {
  const bodyweightMode = isBodyweightExercise(exerciseSlug);
  const weightNum = useMemo(() => parseOptionalWeight(weightKg), [weightKg]);
  const repsNum = useMemo(() => toNumberOrNull(reps), [reps]);
  const setsNum = useMemo(() => toNumberOrNull(sets), [sets]);
  const canSave = bodyweightMode
    ? repsNum !== null && setsNum !== null && repsNum > 0 && setsNum > 0 && !saving
    : weightNum !== null &&
      repsNum !== null &&
      setsNum !== null &&
      weightNum > 0 &&
      repsNum > 0 &&
      setsNum > 0 &&
      !saving;

  const lastLogLabel =
    lastLog &&
    (bodyweightMode
      ? formatBodyweightLog(lastLog.weightKg, lastLog.reps, lastLog.sets)
      : `${lastLog.weightKg} кг × ${lastLog.reps} × ${lastLog.sets}`);

  return (
    <div className="quick-log">
      <h2 className="quick-log-title">Быстрый лог</h2>
      <div className="quick-log-subtitle">{exerciseName}</div>

      {lastLog && (
        <div className="quick-log-last">
          Последнее: <strong>{lastLogLabel}</strong> ({lastLog.workoutDate})
        </div>
      )}

      <div className="quick-log-form">
        {bodyweightMode ? (
          <label className="field">
            Доп. вес (кг)
            <input
              className="input"
              type="text"
              inputMode="decimal"
              placeholder="пусто = без отягощения"
              value={weightKg}
              onChange={(e) => onWeightKgChange(e.target.value)}
            />
          </label>
        ) : (
          <label className="field">
            Вес (кг)
            <input
              className="input"
              type="text"
              inputMode="decimal"
              value={weightKg}
              onChange={(e) => onWeightKgChange(e.target.value)}
            />
          </label>
        )}

        <label className="field">
          Повторы
          <input
            className="input"
            type="text"
            inputMode="numeric"
            value={reps}
            onChange={(e) => onRepsChange(e.target.value)}
          />
        </label>

        <label className="field">
          Подходы
          <input
            className="input"
            type="text"
            inputMode="numeric"
            value={sets}
            onChange={(e) => onSetsChange(e.target.value)}
          />
        </label>
      </div>

      {bodyweightMode && (
        <p className="quick-log-hint">Для чистых подтягиваний оставь доп. вес пустым — нужны только повторы и подходы.</p>
      )}

      <div className="quick-log-actions">
        <button
          type="button"
          className="secondary-btn"
          onClick={onRepeat}
          disabled={!lastLog || saving}
        >
          Повторить прошлую
        </button>

        <button type="button" className="primary-btn" onClick={() => void onSave()} disabled={!canSave}>
          {saving ? "Сохраняю…" : "Сохранить"}
        </button>
      </div>
    </div>
  );
}
