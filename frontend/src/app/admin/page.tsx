import Link from "next/link";
import { adminRoutes } from "@/lib/routes";
import { AdminBarChart } from "@/components/dashboard/charts/AdminBarChart";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_ADMIN_USERS, getAdminMetrics } from "@/lib/mock-data";

const ADMIN_NAME =
  MOCK_ADMIN_USERS.find((u) => u.role === "admin")?.username ?? "admin";

const growthTimeline = [
  { month: "Ene", users: 2, crops: 4, sims: 20 },
  { month: "Feb", users: 3, crops: 8, sims: 45 },
  { month: "Mar", users: 3, crops: 12, sims: 80 },
  { month: "Abr", users: 4, crops: 15, sims: 110 },
  { month: "May", users: 4, crops: 18, sims: 145 },
];

export default function AdminDashboardPage() {
  const metrics = getAdminMetrics();
  const cropsByUser = [...MOCK_ADMIN_USERS]
    .filter((u) => u.role === "user")
    .sort((a, b) => b.cropCount - a.cropCount)
    .slice(0, 5)
    .map((u) => ({ name: u.username, value: u.cropCount }));

  const hasChartData = cropsByUser.some((d) => d.value > 0);

  return (
    <>
      <PageHeader
        title={`¡Bienvenido, ${ADMIN_NAME}!`}
        subtitle="Panel de administración del laboratorio"
      />

      <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard label="Usuarios registrados" value={metrics.totalUsers} />
        <MetricCard label="Total cultivos" value={metrics.totalCrops} />
        <MetricCard label="Cultivos activos" value={metrics.activeCrops} />
        <MetricCard label="Total simulaciones" value={metrics.totalSimulations} />
        <MetricCard label="Tipos de cultivo" value={metrics.cropTypesCount} />
        <MetricCard label="Tipos en uso" value={metrics.cropTypesInUse} />
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <DashboardCard title="Cultivos por usuario (top 5)" href={adminRoutes.users} actionLabel="Ver usuarios">
          {!hasChartData ? (
            <EmptyState message="No hay información para ver" variant="banner" />
          ) : (
            <AdminBarChart data={cropsByUser} />
          )}
        </DashboardCard>

        <DashboardCard title="Evolución de registros">
          {growthTimeline.length === 0 ? (
            <EmptyState message="No hay información para ver" />
          ) : (
            <ul className="space-y-3">
              {growthTimeline.map((row) => (
                <li
                  key={row.month}
                  className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-sm"
                >
                  <span className="font-medium text-white">{row.month}</span>
                  <span className="text-white/55">
                    {row.users} usr · {row.crops} cultivos · {row.sims} sim.
                  </span>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-4 text-xs text-white/40">
            Gráfica de líneas mensual — disponible al conectar el backend.
          </p>
        </DashboardCard>
      </div>

      <div className="mt-6 flex flex-wrap gap-4">
        <Link href={adminRoutes.cropTypes} className="text-sm text-cultiva-green hover:underline">
          Gestionar tipos de cultivo →
        </Link>
      </div>
    </>
  );
}
