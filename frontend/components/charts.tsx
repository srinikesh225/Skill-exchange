"use client";

import {
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmtMonth, gapScoreColor } from "@/lib/format";

// Explicit hexes (charts sit on white surfaces; keeps SVG fills reliable).
export const CHART = {
  demand: "#0f766e",
  supply: "#b0895f",
  forecast: "#0f766e",
  grid: "#e2e6ec",
  axis: "#8a97a6",
  critical: "#c0392b",
  positive: "#2f9e6f",
};

const tooltipStyle = {
  fontSize: 12,
  borderRadius: 8,
  border: "1px solid #e2e6ec",
  boxShadow: "0 4px 16px rgba(15,23,42,0.08)",
};

/** Demand vs Supply for the top skills in a district (vertical grouped bars). */
export function DemandSupplyChart({
  data,
}: {
  data: { skill: string; demand: number; supply: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: -12 }}>
        <CartesianGrid stroke={CHART.grid} vertical={false} />
        <XAxis
          dataKey="skill"
          tick={{ fontSize: 11, fill: CHART.axis }}
          angle={-20}
          textAnchor="end"
          height={64}
          interval={0}
        />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: CHART.axis }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="demand" name="Demand index" fill={CHART.demand} radius={[3, 3, 0, 0]} />
        <Bar dataKey="supply" name="Supply index" fill={CHART.supply} radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Horizontal gap bars, coloured by severity. */
export function GapBarChart({
  data,
}: {
  data: { skill: string; gap: number; label: string }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 34)}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
        <CartesianGrid stroke={CHART.grid} horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: CHART.axis }} />
        <YAxis
          type="category"
          dataKey="skill"
          width={130}
          tick={{ fontSize: 12, fill: "#14202e" }}
        />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey="gap" name="Gap score" radius={[0, 3, 3, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={gapScoreColor(d.gap)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Historical monthly demand + 12-month forecast with an uncertainty band. */
export function TrendForecastChart({
  months,
  counts,
  forecast,
}: {
  months: string[];
  counts: number[];
  forecast: { points: number[]; lower: number[]; upper: number[] };
}) {
  const future = extendMonths(months, forecast.points.length);
  const rows: {
    label: string;
    history?: number;
    forecast?: number;
    band?: [number, number];
  }[] = months.map((m, i) => ({ label: fmtMonth(m), history: counts[i] }));

  // Bridge point so history and forecast lines connect visually.
  if (counts.length) {
    rows[rows.length - 1].forecast = counts[counts.length - 1];
    rows[rows.length - 1].band = [counts[counts.length - 1], counts[counts.length - 1]];
  }
  forecast.points.forEach((p, i) => {
    rows.push({
      label: fmtMonth(future[i]),
      forecast: p,
      band: [forecast.lower[i], forecast.upper[i]],
    });
  });

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: -12 }}>
        <CartesianGrid stroke={CHART.grid} vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 10, fill: CHART.axis }}
          interval={1}
          angle={-30}
          textAnchor="end"
          height={48}
        />
        <YAxis tick={{ fontSize: 11, fill: CHART.axis }} allowDecimals={false} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Area
          dataKey="band"
          name="Forecast range"
          stroke="none"
          fill={CHART.forecast}
          fillOpacity={0.12}
          isAnimationActive={false}
        />
        <Line
          dataKey="history"
          name="Observed postings"
          stroke={CHART.demand}
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
        <Line
          dataKey="forecast"
          name="Forecast"
          stroke={CHART.forecast}
          strokeWidth={2}
          strokeDasharray="5 4"
          dot={false}
          isAnimationActive={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function IndustryBarChart({
  data,
}: {
  data: { industry: string; postings: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 30)}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
        <CartesianGrid stroke={CHART.grid} horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11, fill: CHART.axis }} allowDecimals={false} />
        <YAxis
          type="category"
          dataKey="industry"
          width={140}
          tick={{ fontSize: 11, fill: "#14202e" }}
        />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey="postings" name="Job postings" fill={CHART.demand} radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function extendMonths(months: string[], n: number): string[] {
  if (!months.length) return [];
  const last = months[months.length - 1];
  let [y, m] = last.split("-").map((x) => parseInt(x, 10));
  const out: string[] = [];
  for (let i = 0; i < n; i++) {
    m += 1;
    if (m > 12) {
      m = 1;
      y += 1;
    }
    out.push(`${y}-${String(m).padStart(2, "0")}`);
  }
  return out;
}
