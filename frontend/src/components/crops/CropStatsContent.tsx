import Link from "next/link";
import { BiomassLineChart } from "@/components/dashboard/charts/BiomassLineChart";
import { ConditionsChart } from "@/components/dashboard/charts/ConditionsChart";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { adminRoutes, userRoutes } from "@/lib/routes";
import type { MockCrop, MockCropStats, MockDailyCondition } from "@/lib/types";

type CropStatsContentProps = {
  crop: MockCrop;
  history: MockDailyCondition[];
  stats: MockCropStats | null;
  context: "user" | "admin";
};

export function CropStatsContent({
  crop,
  history,
  stats,
  context,
}: CropStatsContentProps) {
  const hasData = history.length > 0 && stats;
  const isAdmin = context === "admin";

  return (
    <>
      <PageHeader
        title={crop.name}
        subtitle={`${crop.cropTypeName} · ${crop.active ? "Activo" : "Cosechado"}${isAdmin ? " · vista administrador" : ""}`}
      />

      {!hasData ? (
        <EmptyState
          message="Aún no hay simulaciones registradas"
          actionLabel={isAdmin ? undefined : "Simular primer día"}
          actionHref={isAdmin ? undefined : userRoutes.simulate(crop.id)}
        />
      ) : (
        <>
          <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <MetricCard
              label="Temp. promedio"
              value={stats.averageTemperature.toFixed(1)}
              suffix="°C"
            />
            <MetricCard
              label="Lluvia promedio"
              value={stats.averageRain.toFixed(1)}
              suffix="mm"
            />
            <MetricCard
              label="Sol promedio"
              value={stats.averageSunHours.toFixed(1)}
              suffix="h"
            />
            <MetricCard
              label="Crecimiento total"
              value={stats.totalGrowth}
              suffix="g/m²"
            />
            <MetricCard label="Días de estrés" value={stats.stressDays} />
            <MetricCard
              label="Rendimiento vs potencial"
              value={`${(stats.performanceRatio * 100).toFixed(0)}`}
              suffix="%"
            />
          </section>

          <div className="mb-8 grid gap-6 lg:grid-cols-1">
            <DashboardCard title="Evolución de biomasa">
              <BiomassLineChart data={history} />
            </DashboardCard>
            <DashboardCard title="Condiciones ambientales por día">
              <ConditionsChart data={history} />
            </DashboardCard>
          </div>

          <DashboardCard title="Historial diario">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-white/50">
                    <th className="pb-3 pr-4">Día</th>
                    <th className="pb-3 pr-4">Temp.</th>
                    <th className="pb-3 pr-4">Lluvia</th>
                    <th className="pb-3 pr-4">Sol</th>
                    <th className="pb-3">Biomasa</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((row) => (
                    <tr key={row.day} className="border-b border-white/5">
                      <td className="py-3 pr-4 text-white">{row.day}</td>
                      <td className="py-3 pr-4 text-white/70">
                        {row.temperature.toFixed(1)}°C
                      </td>
                      <td className="py-3 pr-4 text-white/70">{row.rain} mm</td>
                      <td className="py-3 pr-4 text-white/70">{row.sunHours} h</td>
                      <td className="py-3 font-medium text-cultiva-green">
                        {row.estimatedBiomass} g/m²
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </DashboardCard>
        </>
      )}

      <div className="mt-6 flex gap-4">
        {!isAdmin && crop.active && (
          <Link
            href={userRoutes.simulate(crop.id)}
            className="text-sm font-medium text-cultiva-green hover:underline"
          >
            Simular otro día
          </Link>
        )}
        <Link
          href={isAdmin ? adminRoutes.crops : userRoutes.crops}
          className="text-sm text-white/50 hover:text-white"
        >
          {isAdmin ? "← Volver a cultivos (admin)" : "← Volver a mis cultivos"}
        </Link>
      </div>
    </>
  );
}
