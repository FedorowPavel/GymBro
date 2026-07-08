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
      : "Ещё не логировал",
  }));
}

export function WorkoutSessionPicker({ items, onPick }: Props) {
  const [expanded, setExpanded] = useState(false);

  const topItems = useMemo(() => items.slice(0, 3), [items]);
  const moreItems = useMemo(() => items.slice(3), [items]);

  if (items.length === 0) {
    return <div className="state">Нет упражнений с историей в этой группе.</div>;
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
            <span>{expanded ? "Скрыть редкие упражнения" : `Показать ещё (${moreItems.length})`}</span>
            <span className="workout-more-chevron">{expanded ? "▲" : "▼"}</span>
          </button>

          {expanded && <ListPicker items={toPickerItems(moreItems)} onPick={onPick} />}
        </div>
      )}
    </div>
  );
}
