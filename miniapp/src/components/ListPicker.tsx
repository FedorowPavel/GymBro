type Item = {
  id: string;
  title: string;
  subtitle?: string;
};

type Props = {
  items: Item[];
  onPick: (id: string) => void;
  emptyText?: string;
};

export function ListPicker({ items, onPick, emptyText = "Нет данных" }: Props) {
  if (items.length === 0) {
    return <div className="state">{emptyText}</div>;
  }

  return (
    <ul className="picker-list">
      {items.map((item) => (
        <li key={item.id}>
          <button type="button" className="picker-item" onClick={() => onPick(item.id)}>
            <span className="picker-title">{item.title}</span>
            {item.subtitle && <span className="picker-subtitle">{item.subtitle}</span>}
          </button>
        </li>
      ))}
    </ul>
  );
}
