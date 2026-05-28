"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MiniBiomassChart } from "@/components/dashboard/charts/MiniBiomassChart";
import { getCrops, getCropHistory, getCropStats, getCropTypes } from "@/lib/api";
import { userRoutes } from "@/lib/routes";

type Crop = {
  id: string;
  name: string;
  crop_type_id: string;
  active: boolean;
  water_stored: number;
};

type CropType = {
  id: string;
  name: string;
};

type HistoryPoint = {
  day: number;
  estimated_biomass: number;
};

export default function UserDashboardPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropTypes, setCropTypes] = useState<CropType[]>([]);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalCrops: 0,
    activeCrops: 0,
    totalDaysSimulated: 0,
    avgPerformance: 0,
  });
  const [recentSims, setRecentSims] = useState<any[]>([]);
  const [mostActive, setMostActive] = useState<Crop | null>(null);
  const [activeHistory, setActiveHistory] = useState<HistoryPoint[]>([]);

  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) setUsername(storedUsername);
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const cropsData = await getCrops();
      const typesData = await getCropTypes();
      setCrops(cropsData);
      setCropTypes(typesData);

      let totalDays = 0;
      let activeCount = 0;
      let totalPerformance = 0;
      let allSimulations: any[] = [];
      let mostActiveCrop: Crop | null = null;
      let maxDays = 0;

      for (const crop of cropsData) {
        const history = await getCropHistory(crop.id);
        totalDays += history.length;
        if (crop.active) activeCount++;

        const stats = await getCropStats(crop.id);
        totalPerformance += stats.performance_ratio;

        const lastSim = history[history.length - 1];
        if (lastSim) {
          const cropType = typesData.find((t: CropType) => t.id === crop.crop_type_id);
          allSimulations.push({
            id: crop.id,
            cropId: crop.id,
            cropName: crop.name,
            day: lastSim.day,
            temperature: lastSim.temperature,
            rain: lastSim.rain,
            sunHours: lastSim.sun_hours,
            estimatedBiomass: lastSim.estimated_biomass,
          });
        }

        // Encontrar cultivo más activo
        if (history.length > maxDays) {
          maxDays = history.length;
          mostActiveCrop = crop;
        }
      }

      setMetrics({
        totalCrops: cropsData.length,
        activeCrops: activeCount,
        totalDaysSimulated: totalDays,
        avgPerformance: cropsData.length ? (totalPerformance / cropsData.length) * 100 : 0,
      });

      setRecentSims(allSimulations.slice(0, 5));

      if (mostActiveCrop) {
        setMostActive(mostActiveCrop);
        const history = await getCropHistory(mostActiveCrop.id);
        setActiveHistory(history.map((h: any) => ({ day: h.day, estimated_biomass: h.estimated_biomass })));
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getCropTypeName = (cropTypeId: string) => {
    const type = cropTypes.find(t => t.id === cropTypeId);
    return type ? type.name : "Desconocido";
  };

  const getCropBiomass = (crop: Crop) => {
    // Esto debería venir del historial, pero por ahora usamos un placeholder
    return "0";
  };

  if (loading) {
    return <div className="p-8 text-center text-white">Cargando...</div>;
  }

  const featuredCrops = [...crops]
    .sort((a, b) => {
      // Ordenar por días simulados (simplificado)
      return 0;
    })
    .slice(0, 4);

  return (
    <>
      <PageHeader
        title={`¡Bienvenido, ${username}!`}
        subtitle="Qué bueno tenerte por aquí"
      />

      <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total cultivos" value={metrics.totalCrops} />
        <MetricCard label="Cultivos activos" value={metrics.activeCrops} />
        <MetricCard label="Días simulados" value={metrics.totalDaysSimulated} />
        <MetricCard
          label="Rendimiento promedio"
          value={`${metrics.avgPerformance.toFixed(3)}`}
          suffix="%"
        />
      </section>

      <section className="mb-8">
        <DashboardCard
          title="Mis cultivos destacados"
          href={userRoutes.crops}
          actionLabel="Ver todos"
        >
          {featuredCrops.length === 0 ? (
            <EmptyState
              message="No tienes cultivos creados"
              actionLabel="Crear cultivo"
              actionHref={userRoutes.cropNew}
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {featuredCrops.map((crop) => (
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
                  <p className="mt-1 text-sm text-white/55">{getCropTypeName(crop.crop_type_id)}</p>
                  <p className="mt-3 text-lg font-bold text-cultiva-green">
                    {getCropBiomass(crop)} g/m²
                  </p>
                  <p className="text-xs text-white/45">
                    {/* Días simulados pendiente */}
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
                {activeHistory.length} días simulados · {getCropTypeName(mostActive.crop_type_id)}
              </p>
              <MiniBiomassChart data={activeHistory} />
            </Link>
          )}
        </DashboardCard>
      </div>
    </>
  );
}