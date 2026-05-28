"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BiomassLineChart } from "@/components/dashboard/charts/BiomassLineChart";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getCropById, getCropHistory, getCropStats, getCropTypes } from "@/lib/api";
import { adminRoutes } from "@/lib/routes";

type Props = { params: Promise<{ id: string }> };

export default function AdminSimulationDetailPage({ params }: Props) {
  const router = useRouter();
  const [id, setId] = useState<string | null>(null);
  const [crop, setCrop] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [cropTypes, setCropTypes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [day, setDay] = useState<number | null>(null);
  const [simData, setSimData] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    if (!token || role !== "admin") {
      router.push("/login");
      return;
    }
    
    params.then((p) => setId(p.id));
  }, []);

  useEffect(() => {
    if (!id) return;
    
    const fetchData = async () => {
      try {
        // El id recibido es: "cropId-day" (ej. "abc123-5")
        const lastHyphenIndex = id.lastIndexOf("-");
        const cropId = id.substring(0, lastHyphenIndex);
        const dayStr = id.substring(lastHyphenIndex + 1);
        const simDay = parseInt(dayStr, 10);
        setDay(simDay);
        
        const [cropData, historyData, statsData, typesData] = await Promise.all([
          getCropById(cropId),
          getCropHistory(cropId),
          getCropStats(cropId),
          getCropTypes(),
        ]);
        
        setCrop(cropData);
        setHistory(historyData);
        setStats(statsData);
        setCropTypes(typesData);
        
        // Encontrar la simulación específica por día
        const simEntry = historyData.find((h: any) => h.day === simDay);
        setSimData(simEntry);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <>
        <PageHeader title="Simulación" subtitle="Cargando..." />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando...</p>
        </DashboardCard>
      </>
    );
  }

  if (!simData || !crop) {
    return (
      <>
        <PageHeader title="Simulación" subtitle="No encontrada" />
        <DashboardCard>
          <p className="text-center text-white/50">Simulación no encontrada</p>
          <Link href={adminRoutes.simulations} className="mt-4 block text-center text-cultiva-green">
            Volver a simulaciones
          </Link>
        </DashboardCard>
      </>
    );
  }

  const cropType = cropTypes.find((t) => t.id === crop.crop_type_id);
  const cropTypeName = cropType?.name || "Desconocido";
  const userName = localStorage.getItem("username") || "admin";

  // Filtrar historial solo hasta el día de esta simulación
  const historyUpToDay = history.filter((h) => h.day <= day!);

  return (
    <>
      <PageHeader
        title={`Simulación — día ${simData.day}`}
        subtitle={`${crop.name} · ${userName}`}
      />

      <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Temperatura" value={simData.temperature} suffix="°C" />
        <MetricCard label="Lluvia" value={simData.rain} suffix="mm" />
        <MetricCard label="Horas de sol" value={simData.sun_hours} suffix="h" />
        <MetricCard label="Biomasa" value={simData.estimated_biomass.toFixed(1)} suffix="g/m²" />
      </section>

      <DashboardCard title="Datos del cultivo" className="mb-8">
        <dl className="grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-white/50">Nombre</dt>
            <dd className="font-medium text-white">{crop.name}</dd>
          </div>
          <div>
            <dt className="text-white/50">Tipo</dt>
            <dd className="text-white">{cropTypeName}</dd>
          </div>
          <div>
            <dt className="text-white/50">Estado</dt>
            <dd className="text-white">{crop.active ? "Activo" : "Cosechado"}</dd>
          </div>
          <div>
            <dt className="text-white/50">Días de estrés</dt>
            <dd className="text-white">{stats?.stress_days || 0}</dd>
          </div>
        </dl>
        <Link
          href={adminRoutes.cropStats(crop.id)}
          className="mt-4 inline-block text-sm text-cultiva-green hover:underline"
        >
          Ver estadísticas completas del cultivo →
        </Link>
      </DashboardCard>

      <DashboardCard title="Evolución de biomasa hasta este día">
        {historyUpToDay.length > 0 ? (
          <BiomassLineChart data={historyUpToDay} />
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