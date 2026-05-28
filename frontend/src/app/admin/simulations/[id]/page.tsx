import Link from "next/link";
import { notFound } from "next/navigation";
import { BiomassLineChart } from "@/components/dashboard/charts/BiomassLineChart";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import {
  MOCK_CROPS,
  MOCK_SIMULATIONS,
  getCropHistory,
} from "@/lib/mock-data";
import { adminRoutes } from "@/lib/routes";

type Props = { params: Promise<{ id: string }> };

export default async function AdminSimulationDetailPage({ params }: Props) {
  const { id } = await params;
  const sim = MOCK_SIMULATIONS.find((s) => s.id === id);
  if (!sim) notFound();

  const crop = MOCK_CROPS.find((c) => c.id === sim.cropId);
  const history = getCropHistory(sim.cropId).filter((h) => h.day <= sim.day);

  return (
    <>
      <PageHeader
        title={`Simulación — día ${sim.day}`}
        subtitle={`${sim.cropName} · cultivador_lab`}
      />

      <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Temperatura" value={sim.temperature} suffix="°C" />
        <MetricCard label="Lluvia" value={sim.rain} suffix="mm" />
        <MetricCard label="Horas de sol" value={sim.sunHours} suffix="h" />
        <MetricCard label="Biomasa" value={sim.estimatedBiomass} suffix="g/m²" />
      </section>

      {crop && (
        <DashboardCard title="Datos del cultivo" className="mb-8">
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-white/50">Nombre</dt>
              <dd className="font-medium text-white">{crop.name}</dd>
            </div>
            <div>
              <dt className="text-white/50">Tipo</dt>
              <dd className="text-white">{crop.cropTypeName}</dd>
            </div>
            <div>
              <dt className="text-white/50">Estado</dt>
              <dd className="text-white">{crop.active ? "Activo" : "Cosechado"}</dd>
            </div>
            <div>
              <dt className="text-white/50">Días de estrés</dt>
              <dd className="text-white">2</dd>
            </div>
          </dl>
          <Link
            href={adminRoutes.cropStats(crop.id)}
            className="mt-4 inline-block text-sm text-cultiva-green hover:underline"
          >
            Ver estadísticas completas del cultivo →
          </Link>
        </DashboardCard>
      )}

      <DashboardCard title="Evolución de biomasa hasta este día">
        {history.length > 0 ? (
          <BiomassLineChart data={history} />
        ) : (
          <p className="text-center text-lg font-semibold text-cultiva-green">
            No hay información para ver
          </p>
        )}
      </DashboardCard>

      <Link
        href={adminRoutes.simulations}
        className="mt-6 inline-block text-sm text-white/50 hover:text-white"
      >
        ← Volver a simulaciones (admin)
      </Link>
    </>
  );
}
