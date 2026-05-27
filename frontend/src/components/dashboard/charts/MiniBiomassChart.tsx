"use client";

import { Line, LineChart, ResponsiveContainer } from "recharts";
import type { MockDailyCondition } from "@/lib/types";

export function MiniBiomassChart({ data }: { data: MockDailyCondition[] }) {
  const chartData = data.map((d) => ({ day: d.day, biomass: d.estimatedBiomass }));

  return (
    <ResponsiveContainer width="100%" height={120}>
      <LineChart data={chartData}>
        <Line
          type="monotone"
          dataKey="biomass"
          stroke="#5FA11B"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
