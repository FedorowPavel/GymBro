import { useEffect, useState } from "react";
import { BenchPressChart } from "./components/BenchPressChart";
import { fetchBenchPressProgress, type BenchSessionPoint } from "./lib/benchPress";
import { getSupabase, supabaseConfigured } from "./lib/supabase";
import { applyTelegramTheme, waitForTelegramUserId } from "./lib/telegram";

export default function App() {
  const [points, setPoints] = useState<BenchSessionPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    applyTelegramTheme();
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      if (!supabaseConfigured()) {
        setError("Не настроен Supabase (VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY).");
        setLoading(false);
        return;
      }

      const userId = await waitForTelegramUserId();
      if (!userId) {
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
        const data = await fetchBenchPressProgress(supabase, userId);
        if (!cancelled) {
          setPoints(data);
        }
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

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const latest = points.length > 0 ? points[points.length - 1] : null;

  return (
    <div className="app">
      <h1>Жим лёжа</h1>
      <p className="subtitle">Прогресс по всем записанным сессиям</p>

      <div className="card">
        {loading && <div className="state">Загрузка…</div>}

        {!loading && error && <div className="state error">{error}</div>}

        {!loading && !error && points.length === 0 && (
          <div className="state">Пока нет записей по жиму лёжа.</div>
        )}

        {!loading && !error && points.length > 0 && (
          <>
            {latest && (
              <p className="subtitle" style={{ marginBottom: 12 }}>
                Последняя: <strong>{latest.maxWeight} кг</strong> × {latest.reps} ×{" "}
                {latest.sets} ({latest.date})
              </p>
            )}
            <BenchPressChart data={points} />
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
