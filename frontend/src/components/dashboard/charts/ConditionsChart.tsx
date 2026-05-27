"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MockDailyCondition } from "@/lib/types";

export function ConditionsChart({ data }: { data: MockDailyCondition[] }) {
  const chartData = data.map((d) => ({
    day: d.day,
    temp: d.temperature,
    rain: d.rain,
    sun: d.sunHours,
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
        <XAxis dataKey="day" stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }} />
        <YAxis stroke="rgba(255,255,255,0.4)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1a1a1a",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "12px",
          }}
        />
        <Legend wrapperStyle={{ color: "rgba(255,255,255,0.7)", fontSize: 12 }} />
        <Line type="monotone" dataKey="temp" name="Temp °C" stroke="#5FA11B" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="rain" name="Lluvia mm" stroke="#8fbc8f" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="sun" name="Sol h" stroke="#c5e99b" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
