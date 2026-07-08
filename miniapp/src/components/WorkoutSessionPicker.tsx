import { useMemo, useState } from "react";
import type { WorkoutSessionItem } from "../lib/progress";
import { ListPicker } from "./ListPicker";

type Props = {
  items: WorkoutSessionItem[];
  onPick: (slug: string) => void;
};

function toPickerItems(items: WorkoutSessionItem[]) {
  return items.map((it) => ({
    id: it.slug,
    title: it.name,
    subtitle: it.isLoggedToday
      ? `${it.lastWeightKg ?? 0} кг × ${it.lastReps ?? 0} × ${it.lastSets ?? 0}`
      : it.sessionCount > 0
        ? `${it.sessionCount} в истории`
        : "Не в истории",
  }));
}

export function WorkoutSessionPicker({ items, onPick }: Props) {
  const [expanded, setExpanded] = useState(false);

  const { topItems, moreItems } = useMemo(() => {
    const withHistory = items
      .filter((it) => it.sessionCount > 0)
      .sort((a, b) => b.sessionCount - a.sessionCount || a.name.localeCompare(b.name));
    const top = withHistory.slice(0, 3);
    const topSlugs = new Set(top.map((it) => it.slug));
    const more = items.filter((it) => !topSlugs.has(it.slug));
    return { topItems: top, moreItems: more };
  }, [items]);

  if (items.length === 0) {
    return <div className="state">Нет упражнений для этой группы.</div>;
  }

  if (topItems.length === 0) {
    return (
      <div className="workout-session-picker">
        <p className="subtitle" style={{ marginBottom: 12 }}>
          Пока нет истории — выбери упражнение из списка:
        </p>
        <ListPicker items={toPickerItems(items)} onPick={onPick} />
      </div>
    );
  }

  return (
    <div className="workout-session-picker">
      <ListPicker items={toPickerItems(topItems)} onPick={onPick} />

      {moreItems.length > 0 && (
        <div className="workout-more-section">
          <button
            type="button"
            className="workout-more-toggle"
            onClick={() => setExpanded((v) => !v)}
            aria-expanded={expanded}
          >
            <span>{expanded ? "Скрыть остальные" : `Показать ещё (${moreItems.length})`}</span>
            <span className="workout-more-chevron">{expanded ? "▲" : "▼"}</span>
          </button>

          {expanded && <ListPicker items={toPickerItems(moreItems)} onPick={onPick} />}
        </div>
      )}
    </div>
  );
}
