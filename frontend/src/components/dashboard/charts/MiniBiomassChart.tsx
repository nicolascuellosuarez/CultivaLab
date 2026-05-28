"use client";

import { Line, LineChart, ResponsiveContainer } from "recharts";

type DailyConditionResponse = {
  day: number;
  estimated_biomass: number;
};

export function MiniBiomassChart({ data }: { data: DailyConditionResponse[] }) {
  const chartData = data.map((d) => ({ day: d.day, biomass: d.estimated_biomass }));

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