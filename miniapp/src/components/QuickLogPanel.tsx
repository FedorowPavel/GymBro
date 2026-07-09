import { useMemo } from "react";
import type { LastExerciseLog } from "../lib/progress";

type Props = {
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

export function QuickLogPanel({
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
  const weightNum = useMemo(() => toNumberOrNull(weightKg), [weightKg]);
  const repsNum = useMemo(() => toNumberOrNull(reps), [reps]);
  const setsNum = useMemo(() => toNumberOrNull(sets), [sets]);
  const canSave =
    weightNum !== null &&
    repsNum !== null &&
    setsNum !== null &&
    weightNum > 0 &&
    repsNum > 0 &&
    setsNum > 0 &&
    !saving;

  return (
    <div className="quick-log">
      <h2 className="quick-log-title">Быстрый лог</h2>
      <div className="quick-log-subtitle">{exerciseName}</div>

      {lastLog && (
        <div className="quick-log-last">
          Последнее: <strong>{lastLog.weightKg} кг</strong> × {lastLog.reps} × {lastLog.sets} (
          {lastLog.workoutDate})
        </div>
      )}

      <div className="quick-log-form">
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

