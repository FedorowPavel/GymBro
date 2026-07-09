import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TonnagePoint } from "../lib/progress";

type Props = {
  data: TonnagePoint[];
};

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: TonnagePoint }>;
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
        <strong>{point.tonnage.toFixed(0)}</strong> кг
      </div>
      <div>{point.sets} подход(ов)</div>
    </div>
  );
}

export function ExerciseTonnageChart({ data }: Props) {
  const chartWidth = Math.max(280, data.length * 52);

  return (
    <div className="chart-scroll">
      <div className="chart-inner" style={{ width: chartWidth }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.08)" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis
              width={44}
              domain={["dataMin - 5", "dataMax + 5"]}
              tick={{ fontSize: 11 }}
              unit=" кг"
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="tonnage"
              stroke="#16a34a"
              strokeWidth={2.5}
              dot={{ r: 4, fill: "#16a34a" }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
