import { useCallback, useEffect, useMemo, useState } from "react";
import { FloatingRestTimer } from "./components/FloatingRestTimer";
import { ExerciseProgressChart } from "./components/ExerciseProgressChart";
import { ExerciseTonnageChart } from "./components/ExerciseTonnageChart";
import { ListPicker } from "./components/ListPicker";
import { QuickLogPanel } from "./components/QuickLogPanel";
import { WorkoutSessionPicker } from "./components/WorkoutSessionPicker";
import { muscleGroupLabel, sortMuscleGroups, WORKOUT_PICKER_ORDER } from "./lib/muscleGroups";
import {
  fetchExerciseProgress,
  fetchExerciseTonnageProgress,
  fetchExercisesWithHistory,
  fetchMuscleGroupsWithHistory,
  fetchLastExerciseLog,
  fetchMuscleSessionOverview,
  logExerciseSession,
  type ExerciseOption,
  type LastExerciseLog,
  type SessionPoint,
  type TonnagePoint,
  type WorkoutSessionItem,
} from "./lib/progress";
import { getSupabase, supabaseConfigured } from "./lib/supabase";
import { applyTelegramTheme, waitForTelegramUserId } from "./lib/telegram";

type Screen =
  | { step: "muscle" }
  | { step: "exercise"; muscleGroup: string }
  | { step: "pick_workout" }
  | { step: "workout_session"; muscleGroup: string }
  | {
      step: "chart";
      muscleGroup: string;
      exerciseSlug: string;
      exerciseName: string;
      fromWorkout: boolean;
    };

function sessionLabel(count: number): string {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) {
    return `${count} тренировка`;
  }
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return `${count} тренировки`;
  }
  return `${count} тренировок`;
}

export default function App() {
  const [screen, setScreen] = useState<Screen>({ step: "muscle" });
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [muscleGroups, setMuscleGroups] = useState<string[]>([]);
  const [exercises, setExercises] = useState<ExerciseOption[]>([]);
  const [maxPoints, setMaxPoints] = useState<SessionPoint[]>([]);
  const [tonnagePoints, setTonnagePoints] = useState<TonnagePoint[]>([]);

  const [metric, setMetric] = useState<"max" | "tonnage">("max");
  const [lastLog, setLastLog] = useState<LastExerciseLog | null>(null);

  // Quick log form values
  const [weightKg, setWeightKg] = useState<string>("");
  const [reps, setReps] = useState<string>("");
  const [sets, setSets] = useState<string>("");
  const [saving, setSaving] = useState(false);

  // Workout session (manual muscle pick)
  const [workoutSessionItems, setWorkoutSessionItems] = useState<WorkoutSessionItem[]>([]);

  useEffect(() => {
    applyTelegramTheme();
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      setLoading(true);
      setError(null);

      if (!supabaseConfigured()) {
        setError("Не настроен Supabase (VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY).");
        setLoading(false);
        return;
      }

      const id = await waitForTelegramUserId();
      if (!id) {
        setError("Не удалось определить Telegram user id. Открой через кнопку 📊 Динамика в боте.");
        setLoading(false);
        return;
      }

      const supabase = getSupabase();
      if (!supabase) {
        setError("Ошибка инициализации Supabase.");
        setLoading(false);
        return;
      }

      try {
        const groups = await fetchMuscleGroupsWithHistory(supabase, id);
        if (cancelled) {
          return;
        }
        setUserId(id);
        setMuscleGroups(sortMuscleGroups(groups.map((g) => g.id)));
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : "Не удалось загрузить данные";
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const loadExercises = useCallback(
    async (muscleGroup: string) => {
      if (!userId) {
        return;
      }
      const supabase = getSupabase();
      if (!supabase) {
        return;
      }

      setLoading(true);
      setError(null);
      setExercises([]);
      setScreen({ step: "exercise", muscleGroup });

      try {
        const list = await fetchExercisesWithHistory(supabase, userId, muscleGroup);
        setExercises(list);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Не удалось загрузить упражнения";
        setError(message);
        setScreen({ step: "muscle" });
      } finally {
        setLoading(false);
      }
    },
    [userId],
  );

  function todayIsoLocal(): string {
    const d = new Date();
    // Convert to local date (avoid UTC shift).
    const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
  }

  const loadChart = useCallback(
    async (
      muscleGroup: string,
      exerciseSlug: string,
      exerciseName: string,
      fromWorkout: boolean,
    ) => {
      if (!userId) return;
      const supabase = getSupabase();
      if (!supabase) return;

      setMetric("max");
      setLoading(true);
      setError(null);
      setSaving(false);
      setMaxPoints([]);
      setTonnagePoints([]);
      setLastLog(null);
      setWeightKg("");
      setReps("");
      setSets("");
      setScreen({ step: "chart", muscleGroup, exerciseSlug, exerciseName, fromWorkout });

      try {
        const [maxData, tonnageData, last] = await Promise.all([
          fetchExerciseProgress(supabase, userId, exerciseSlug),
          fetchExerciseTonnageProgress(supabase, userId, exerciseSlug),
          fetchLastExerciseLog(supabase, userId, exerciseSlug),
        ]);

        setMaxPoints(maxData);
        setTonnagePoints(tonnageData);
        setLastLog(last);

        if (last) {
          setWeightKg(String(last.weightKg));
          setReps(String(last.reps));
          setSets(String(last.sets));
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "Не удалось загрузить данные";
        setError(message);
        setScreen({ step: "exercise", muscleGroup });
      } finally {
        setLoading(false);
      }
    },
    [userId],
  );

  const loadWorkoutSession = useCallback(
    async (muscleGroup: string) => {
      if (!userId) return;
      const supabase = getSupabase();
      if (!supabase) return;

      setLoading(true);
      setError(null);
      setWorkoutSessionItems([]);
      setScreen({ step: "workout_session", muscleGroup });

      try {
        const items = await fetchMuscleSessionOverview(
          supabase,
          userId,
          muscleGroup,
          todayIsoLocal(),
        );
        setWorkoutSessionItems(items);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Не удалось загрузить упражнения тренировки";
        setError(message);
        setScreen({ step: "pick_workout" });
      } finally {
        setLoading(false);
      }
    },
    [userId],
  );

  const openPickWorkout = useCallback(() => {
    setError(null);
    setWorkoutSessionItems([]);
    setScreen({ step: "pick_workout" });
  }, []);

  const refreshChartAfterSave = useCallback(
    async (exerciseSlug: string) => {
      if (!userId) return;
      const supabase = getSupabase();
      if (!supabase) return;

      setError(null);
      setSaving(false);

      try {
        const [maxData, tonnageData, last] = await Promise.all([
          fetchExerciseProgress(supabase, userId, exerciseSlug),
          fetchExerciseTonnageProgress(supabase, userId, exerciseSlug),
          fetchLastExerciseLog(supabase, userId, exerciseSlug),
        ]);

        setMaxPoints(maxData);
        setTonnagePoints(tonnageData);
        setLastLog(last);
        if (last) {
          setWeightKg(String(last.weightKg));
          setReps(String(last.reps));
          setSets(String(last.sets));
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "Не удалось обновить после сохранения";
        setError(message);
      }
    },
    [userId],
  );

  const goBack = () => {
    setError(null);
    if (screen.step === "chart") {
      setMaxPoints([]);
      setTonnagePoints([]);
      if (screen.fromWorkout) {
        void loadWorkoutSession(screen.muscleGroup);
        return;
      }
      setScreen({ step: "exercise", muscleGroup: screen.muscleGroup });
      return;
    }
    if (screen.step === "exercise") {
      setExercises([]);
      setScreen({ step: "muscle" });
      return;
    }
    if (screen.step === "workout_session") {
      setWorkoutSessionItems([]);
      setScreen({ step: "pick_workout" });
      return;
    }
    if (screen.step === "pick_workout") {
      setScreen({ step: "muscle" });
    }
  };

  const title =
    screen.step === "muscle"
      ? "Динамика"
      : screen.step === "exercise"
        ? muscleGroupLabel(screen.muscleGroup)
        : screen.step === "pick_workout"
          ? "Выбрать тренировку"
          : screen.step === "workout_session"
            ? muscleGroupLabel(screen.muscleGroup)
            : screen.exerciseName;

  const subtitle =
    screen.step === "muscle"
      ? "Выбери группу мышц"
      : screen.step === "exercise"
        ? "Выбери упражнение"
        : screen.step === "pick_workout"
          ? "Какая тренировка сегодня?"
          : screen.step === "workout_session"
            ? "Логируй упражнения"
            : metric === "max"
              ? "Максимальный вес за сессию"
              : "Тоннаж за сессию";

  const latestMax = useMemo(() => {
    if (maxPoints.length === 0) return null;
    return maxPoints[maxPoints.length - 1];
  }, [maxPoints]);

  const latestTonnage = useMemo(() => {
    if (tonnagePoints.length === 0) return null;
    return tonnagePoints[tonnagePoints.length - 1];
  }, [tonnagePoints]);

  const prMax = useMemo(() => {
    if (maxPoints.length === 0) return null;
    const max = Math.max(...maxPoints.map((p) => p.maxWeight));
    const p = maxPoints.find((x) => x.maxWeight === max) ?? null;
    return p;
  }, [maxPoints]);

  const prTonnage = useMemo(() => {
    if (tonnagePoints.length === 0) return null;
    const maxT = Math.max(...tonnagePoints.map((p) => p.tonnage));
    const p = tonnagePoints.find((x) => x.tonnage === maxT) ?? null;
    return p;
  }, [tonnagePoints]);

  const currentExercise = screen.step === "chart" ? screen : null;

  return (
    <div className="app">
      <header className="app-header">
        {screen.step !== "muscle" && (
          <button type="button" className="back-btn" onClick={goBack} aria-label="Назад">
            ←
          </button>
        )}
        <div className="app-header-text">
          <h1>{title}</h1>
          <p className="subtitle">{subtitle}</p>
        </div>
      </header>

      <div className="card">
        {loading && <div className="state">Загрузка…</div>}

        {!loading && error && <div className="state error">{error}</div>}

        {!loading && !error && screen.step === "muscle" && (
          <>
            <div className="today-btn-row">
              <button type="button" className="today-btn" onClick={openPickWorkout}>
                Выбрать тренировку
              </button>
            </div>
            <ListPicker
              items={muscleGroups.map((id) => ({
                id,
                title: muscleGroupLabel(id),
              }))}
              onPick={loadExercises}
              emptyText="Пока нет записей тренировок."
            />
          </>
        )}

        {!loading && !error && screen.step === "exercise" && (
          <ListPicker
            items={exercises.map((ex) => ({
              id: ex.slug,
              title: ex.name,
              subtitle: sessionLabel(ex.sessionCount),
            }))}
            onPick={(slug) => {
              const exercise = exercises.find((ex) => ex.slug === slug);
              if (exercise) {
                void loadChart(screen.muscleGroup, exercise.slug, exercise.name, false);
              }
            }}
            emptyText="Нет упражнений с историей в этой группе."
          />
        )}

        {!loading && !error && screen.step === "pick_workout" && (
          <ListPicker
            items={WORKOUT_PICKER_ORDER.map((id) => ({
              id,
              title: muscleGroupLabel(id),
            }))}
            onPick={(muscleGroup) => void loadWorkoutSession(muscleGroup)}
            emptyText="Нет групп мышц."
          />
        )}

        {!loading && !error && screen.step === "workout_session" && (
          <WorkoutSessionPicker
            key={screen.muscleGroup}
            items={workoutSessionItems}
            onPick={(slug) => {
              const item = workoutSessionItems.find((x) => x.slug === slug);
              if (!item) return;
              void loadChart(screen.muscleGroup, item.slug, item.name, true);
            }}
          />
        )}

        {!loading && !error && screen.step === "chart" && maxPoints.length === 0 && currentExercise && (
          <>
            <div className="state">Пока нет записей по этому упражнению.</div>
            <QuickLogPanel
              exerciseName={currentExercise.exerciseName}
              lastLog={lastLog}
              weightKg={weightKg}
              reps={reps}
              sets={sets}
              onWeightKgChange={setWeightKg}
              onRepsChange={setReps}
              onSetsChange={setSets}
              onRepeat={() => {
                if (!lastLog) return;
                setWeightKg(String(lastLog.weightKg));
                setReps(String(lastLog.reps));
                setSets(String(lastLog.sets));
              }}
              onSave={async () => {
                if (!userId) return;
                const supabase = getSupabase();
                if (!supabase) return;
                const w = Number(weightKg);
                if (!Number.isFinite(w) || w <= 0) {
                  setError("Введи корректный вес (кг).");
                  return;
                }
                const r = Number(reps);
                const s = Number(sets);
                if (!Number.isFinite(r) || !Number.isFinite(s) || r <= 0 || s <= 0) {
                  setError("Повторы и подходы должны быть > 0.");
                  return;
                }

                setSaving(true);
                setError(null);
                try {
                  await logExerciseSession(
                    supabase,
                    userId,
                    currentExercise.exerciseSlug,
                    w,
                    r,
                    s,
                  );
                  await refreshChartAfterSave(currentExercise.exerciseSlug);
                } catch (err) {
                  const message = err instanceof Error ? err.message : "Не удалось сохранить";
                  setError(message);
                } finally {
                  setSaving(false);
                }
              }}
              saving={saving}
            />
          </>
        )}

        {!loading && !error && screen.step === "chart" && maxPoints.length > 0 && currentExercise && (
          <>
            <div className="metric-toggle">
              <button
                type="button"
                className={`chip-btn ${metric === "max" ? "active" : ""}`}
                onClick={() => setMetric("max")}
              >
                Вес (max)
              </button>
              <button
                type="button"
                className={`chip-btn ${metric === "tonnage" ? "active" : ""}`}
                onClick={() => setMetric("tonnage")}
              >
                Тоннаж
              </button>
            </div>

            {metric === "max" && latestMax && (
              <p className="subtitle" style={{ marginBottom: 10 }}>
                Последняя: <strong>{latestMax.maxWeight} кг</strong> × {latestMax.reps} ×{" "}
                {latestMax.sets} ({latestMax.date})
              </p>
            )}

            {metric === "tonnage" && latestTonnage && (
              <p className="subtitle" style={{ marginBottom: 10 }}>
                Последняя: <strong>{latestTonnage.tonnage.toFixed(1)}</strong> ton ({latestTonnage.date})
              </p>
            )}

            {metric === "max" && prMax && (
              <p className="subtitle" style={{ marginBottom: 12 }}>
                PR: <strong>{prMax.maxWeight} кг</strong> × {prMax.reps} × {prMax.sets} ({prMax.date})
              </p>
            )}

            {metric === "tonnage" && prTonnage && (
              <p className="subtitle" style={{ marginBottom: 12 }}>
                PR тоннажа: <strong>{prTonnage.tonnage.toFixed(1)}</strong> ton ({prTonnage.date})
              </p>
            )}

            {metric === "max" && <ExerciseProgressChart data={maxPoints} />}
            {metric === "tonnage" && <ExerciseTonnageChart data={tonnagePoints} />}
            <p className="legend">
              {metric === "max" ? "Ось Y — максимальный вес за сессию (кг)" : "Ось Y — тоннаяж за сессию"}
            </p>

            <ul className="session-list">
              {[...maxPoints]
                .reverse()
                .slice(0, 8)
                .map((p) => (
                  <li key={p.date}>
                    <span className="date">{p.date}</span>
                    <span>
                      {p.maxWeight} кг × {p.reps} × {p.sets}
                    </span>
                  </li>
                ))}
            </ul>

            <QuickLogPanel
              exerciseName={currentExercise.exerciseName}
              lastLog={lastLog}
              weightKg={weightKg}
              reps={reps}
              sets={sets}
              onWeightKgChange={setWeightKg}
              onRepsChange={setReps}
              onSetsChange={setSets}
              onRepeat={() => {
                if (!lastLog) return;
                setWeightKg(String(lastLog.weightKg));
                setReps(String(lastLog.reps));
                setSets(String(lastLog.sets));
              }}
              onSave={async () => {
                if (!userId) return;
                const supabase = getSupabase();
                if (!supabase) return;
                const w = Number(weightKg);
                if (!Number.isFinite(w) || w <= 0) {
                  setError("Введи корректный вес (кг).");
                  return;
                }
                const r = Number(reps);
                const s = Number(sets);
                if (!Number.isFinite(r) || !Number.isFinite(s) || r <= 0 || s <= 0) {
                  setError("Повторы и подходы должны быть > 0.");
                  return;
                }

                setSaving(true);
                setError(null);
                try {
                  await logExerciseSession(
                    supabase,
                    userId,
                    currentExercise.exerciseSlug,
                    w,
                    r,
                    s,
                  );
                  await refreshChartAfterSave(currentExercise.exerciseSlug);
                } catch (err) {
                  const message = err instanceof Error ? err.message : "Не удалось сохранить";
                  setError(message);
                } finally {
                  setSaving(false);
                }
              }}
              saving={saving}
            />
          </>
        )}
      </div>

      <FloatingRestTimer />
    </div>
  );
}
