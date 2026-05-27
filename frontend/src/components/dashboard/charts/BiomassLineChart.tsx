"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MockDailyCondition } from "@/lib/types";

type BiomassLineChartProps = {
  data: MockDailyCondition[];
  height?: number;
};

export function BiomassLineChart({ data, height = 280 }: BiomassLineChartProps) {
  const chartData = data.map((d) => ({
    day: d.day,
    biomass: d.estimatedBiomass,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
        <XAxis
          dataKey="day"
          stroke="rgba(255,255,255,0.4)"
          tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }}
          label={{ value: "Día", position: "insideBottom", offset: -4, fill: "rgba(255,255,255,0.5)" }}
        />
        <YAxis
          stroke="rgba(255,255,255,0.4)"
          tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }}
          label={{
            value: "g/m²",
            angle: -90,
            position: "insideLeft",
            fill: "rgba(255,255,255,0.5)",
          }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1a1a",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "12px",
          }}
          labelStyle={{ color: "#fff" }}
        />
        <Line
          type="monotone"
          dataKey="biomass"
          stroke="#5FA11B"
          strokeWidth={2}
          dot={{ fill: "#5FA11B", r: 3 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
