"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type AdminBarChartProps = {
  data: { name: string; value: number }[];
};

export function AdminBarChart({ data }: AdminBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
        <XAxis type="number" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="name"
          width={100}
          stroke="rgba(255,255,255,0.4)"
          tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 11 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1a1a",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "12px",
          }}
        />
        <Bar dataKey="value" fill="#5FA11B" radius={[0, 8, 8, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
