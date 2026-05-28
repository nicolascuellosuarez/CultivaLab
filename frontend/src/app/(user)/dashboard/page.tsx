import Link from "next/link";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MiniBiomassChart } from "@/components/dashboard/charts/MiniBiomassChart";
import {
  MOCK_CROPS,
  MOCK_SIMULATIONS,
  MOCK_USER,
  getCropHistory,
  getMostActiveCrop,
  getUserMetrics,
} from "@/lib/mock-data";
import { userRoutes } from "@/lib/routes";

export default function UserDashboardPage() {
  const metrics = getUserMetrics();
  const featured = [...MOCK_CROPS]
    .sort((a, b) => b.daysSimulated - a.daysSimulated)
    .slice(0, 4);
  const recentSims = MOCK_SIMULATIONS.slice(0, 5);
  const mostActive = getMostActiveCrop();
  const activeHistory = mostActive ? getCropHistory(mostActive.id) : [];

  return (
    <>
      <PageHeader
        title={`¡Bienvenido, ${MOCK_USER.username}!`}
        subtitle="Qué bueno tenerte por aquí"
      />

      <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total cultivos" value={metrics.totalCrops} />
        <MetricCard label="Cultivos activos" value={metrics.activeCrops} />
        <MetricCard label="Días simulados" value={metrics.totalDaysSimulated} />
        <MetricCard
          label="Rendimiento promedio"
          value={`${(metrics.avgPerformance * 100).toFixed(0)}`}
          suffix="%"
        />
      </section>

      <section className="mb-8">
        <DashboardCard
          title="Mis cultivos destacados"
          href={userRoutes.crops}
          actionLabel="Ver todos"
        >
          {featured.length === 0 ? (
            <EmptyState
              message="No tienes cultivos creados"
              actionLabel="Crear cultivo"
              actionHref={userRoutes.cropNew}
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {featured.map((crop) => (
                <Link
                  key={crop.id}
                  href={userRoutes.cropStats(crop.id)}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors hover:border-cultiva-green/30"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-white">{crop.name}</h4>
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                        crop.active
                          ? "bg-cultiva-green/20 text-cultiva-green"
                          : "bg-white/10 text-white/50"
                      }`}
                    >
                      {crop.active ? "Activo" : "Cosechado"}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-white/55">{crop.cropTypeName}</p>
                  <p className="mt-3 text-lg font-bold text-cultiva-green">
                    {crop.biomass} g/m²
                  </p>
                  <p className="text-xs text-white/45">
                    {crop.daysSimulated} días simulados
                  </p>
                </Link>
              ))}
            </div>
          )}
        </DashboardCard>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <DashboardCard title="Simulaciones recientes" href={userRoutes.simulations} actionLabel="Ver todas">
          {recentSims.length === 0 ? (
            <EmptyState message="No hay simulaciones recientes" variant="banner" />
          ) : (
            <ul className="divide-y divide-white/10">
              {recentSims.map((sim) => (
                <li key={sim.id}>
                  <Link
                    href={userRoutes.cropStats(sim.cropId)}
                    className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm transition-colors hover:text-cultiva-green"
                  >
                    <span className="font-medium text-white">{sim.cropName}</span>
                    <span className="text-white/50">
                      Día {sim.day} · {sim.temperature}°C · {sim.rain}mm · {sim.sunHours}h sol
                    </span>
                    <span className="font-semibold text-cultiva-green">
                      {sim.estimatedBiomass} g/m²
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </DashboardCard>

        <DashboardCard
          title="Cultivo más activo"
          href={mostActive ? userRoutes.cropStats(mostActive.id) : undefined}
          actionLabel={mostActive ? "Ver estadísticas" : undefined}
        >
          {!mostActive || activeHistory.length === 0 ? (
            <EmptyState message="No hay información para ver" />
          ) : (
            <Link
              href={userRoutes.cropStats(mostActive.id)}
              className="block transition-opacity hover:opacity-90"
            >
              <p className="mb-2 font-semibold text-white">{mostActive.name}</p>
              <p className="mb-4 text-sm text-white/55">
                {mostActive.daysSimulated} días simulados · {mostActive.cropTypeName}
              </p>
              <MiniBiomassChart data={activeHistory} />
            </Link>
          )}
        </DashboardCard>
      </div>
    </>
  );
}
