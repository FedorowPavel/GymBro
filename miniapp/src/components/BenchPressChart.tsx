import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BenchSessionPoint } from "../lib/benchPress";

type Props = {
  data: BenchSessionPoint[];
};

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: BenchSessionPoint }>;
}) {
  if (!active || !payload?.length) {
    return null;
  }
  const point = payload[0].payload;
  return (
    <div
      style={{
        background: "var(--tg-theme-secondary-bg-color, #fff)",
        border: "1px solid rgba(0,0,0,0.08)",
        borderRadius: 8,
        padding: "8px 10px",
        fontSize: 13,
      }}
    >
      <div>{point.date}</div>
      <div>
        <strong>{point.maxWeight} кг</strong> × {point.reps} × {point.sets}
      </div>
    </div>
  );
}

export function BenchPressChart({ data }: Props) {
  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.08)" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis
            domain={["dataMin - 2", "dataMax + 2"]}
            tick={{ fontSize: 11 }}
            unit=" кг"
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="maxWeight"
            stroke="#2563eb"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#2563eb" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
