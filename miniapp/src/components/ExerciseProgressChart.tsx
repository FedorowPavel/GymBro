import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { SessionPoint } from "../lib/progress";

type Props = {
  data: SessionPoint[];
  repsMode?: boolean;
};

function CustomTooltip({
  active,
  payload,
  repsMode,
}: {
  active?: boolean;
  payload?: Array<{ payload: SessionPoint }>;
  repsMode?: boolean;
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
        {repsMode ? (
          <>
            <strong>{point.reps}</strong> × {point.sets}
          </>
        ) : (
          <>
            <strong>{point.maxWeight} кг</strong> × {point.reps} × {point.sets}
          </>
        )}
      </div>
    </div>
  );
}

export function ExerciseProgressChart({ data, repsMode = false }: Props) {
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
              domain={["dataMin - 2", "dataMax + 2"]}
              tick={{ fontSize: 11 }}
              unit={repsMode ? "" : " кг"}
            />
            <Tooltip content={<CustomTooltip repsMode={repsMode} />} />
            <Line
              type="monotone"
              dataKey={repsMode ? "reps" : "maxWeight"}
              stroke="#2563eb"
              strokeWidth={2.5}
              dot={{ r: 4, fill: "#2563eb" }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
