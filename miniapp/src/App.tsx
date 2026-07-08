import { useCallback, useEffect, useState } from "react";
import { ExerciseProgressChart } from "./components/ExerciseProgressChart";
import { ListPicker } from "./components/ListPicker";
import { muscleGroupLabel, sortMuscleGroups } from "./lib/muscleGroups";
import {
  fetchExerciseProgress,
  fetchExercisesWithHistory,
  fetchMuscleGroupsWithHistory,
  type ExerciseOption,
  type SessionPoint,
} from "./lib/progress";
import { getSupabase, supabaseConfigured } from "./lib/supabase";
import { applyTelegramTheme, waitForTelegramUserId } from "./lib/telegram";

type Screen =
  | { step: "muscle" }
  | { step: "exercise"; muscleGroup: string }
  | { step: "chart"; muscleGroup: string; exerciseSlug: string; exerciseName: string };

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
  const [points, setPoints] = useState<SessionPoint[]>([]);

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
        setError("Не удалось определить Telegram user id. Открой через кнопку 📊 Прогресс в боте.");
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

  const loadChart = useCallback(
    async (muscleGroup: string, exerciseSlug: string, exerciseName: string) => {
      if (!userId) {
        return;
      }
      const supabase = getSupabase();
      if (!supabase) {
        return;
      }

      setLoading(true);
      setError(null);
      setPoints([]);
      setScreen({ step: "chart", muscleGroup, exerciseSlug, exerciseName });

      try {
        const data = await fetchExerciseProgress(supabase, userId, exerciseSlug);
        setPoints(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Не удалось загрузить график";
        setError(message);
        setScreen({ step: "exercise", muscleGroup });
      } finally {
        setLoading(false);
      }
    },
    [userId],
  );

  const goBack = () => {
    setError(null);
    if (screen.step === "chart") {
      setPoints([]);
      setScreen({ step: "exercise", muscleGroup: screen.muscleGroup });
      return;
    }
    if (screen.step === "exercise") {
      setExercises([]);
      setScreen({ step: "muscle" });
    }
  };

  const title =
    screen.step === "muscle"
      ? "Прогресс"
      : screen.step === "exercise"
        ? muscleGroupLabel(screen.muscleGroup)
        : screen.exerciseName;

  const subtitle =
    screen.step === "muscle"
      ? "Выбери группу мышц"
      : screen.step === "exercise"
        ? "Выбери упражнение"
        : "Максимальный вес за сессию";

  const latest = points.length > 0 ? points[points.length - 1] : null;

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
          <ListPicker
            items={muscleGroups.map((id) => ({
              id,
              title: muscleGroupLabel(id),
            }))}
            onPick={loadExercises}
            emptyText="Пока нет записей тренировок."
          />
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
                void loadChart(screen.muscleGroup, exercise.slug, exercise.name);
              }
            }}
            emptyText="Нет упражнений с историей в этой группе."
          />
        )}

        {!loading && !error && screen.step === "chart" && points.length === 0 && (
          <div className="state">Пока нет записей по этому упражнению.</div>
        )}

        {!loading && !error && screen.step === "chart" && points.length > 0 && (
          <>
            {latest && (
              <p className="subtitle" style={{ marginBottom: 12 }}>
                Последняя: <strong>{latest.maxWeight} кг</strong> × {latest.reps} ×{" "}
                {latest.sets} ({latest.date})
              </p>
            )}
            <ExerciseProgressChart data={points} />
            <p className="legend">Ось Y — максимальный вес за сессию (кг)</p>

            <ul className="session-list">
              {[...points].reverse().slice(0, 8).map((p) => (
                <li key={p.date}>
                  <span className="date">{p.date}</span>
                  <span>
                    {p.maxWeight} кг × {p.reps} × {p.sets}
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
