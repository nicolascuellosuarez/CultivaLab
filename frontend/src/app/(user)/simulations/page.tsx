"use client";

import Link from "next/link";
import { useMemo, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getCrops, getCropHistory } from "@/lib/api";
import { userRoutes } from "@/lib/routes";

const PAGE_SIZE = 5;

type Simulation = {
  id: string;
  cropId: string;
  cropName: string;
  day: number;
  temperature: number;
  rain: number;
  sunHours: number;
  estimatedBiomass: number;
};

export default function SimulationsPage() {
  const router = useRouter();
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [sortAsc, setSortAsc] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    try {
      const crops = await getCrops();
      let allSimulations: Simulation[] = [];

      for (const crop of crops) {
        const history = await getCropHistory(crop.id);
        const cropSimulations = history.map((h: any) => ({
          id: `${crop.id}-${h.day}`,
          cropId: crop.id,
          cropName: crop.name,
          day: h.day,
          temperature: h.temperature,
          rain: h.rain,
          sunHours: h.sun_hours,
          estimatedBiomass: h.estimated_biomass,
        }));
        allSimulations = [...allSimulations, ...cropSimulations];
      }

      // Ordenar por día descendente
      allSimulations.sort((a, b) => b.day - a.day);
      setSimulations(allSimulations);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const filtered = useMemo(() => {
    const list = simulations.filter((s) =>
      s.cropName.toLowerCase().includes(search.toLowerCase())
    );
    return [...list].sort((a, b) =>
      sortAsc ? a.day - b.day : b.day - a.day
    );
  }, [simulations, search, sortAsc]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageItems = filtered.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  if (loading) {
    return (
      <>
        <PageHeader
          title="Simulaciones recientes"
          subtitle="Historial de todas tus simulaciones"
        />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando simulaciones...</p>
        </DashboardCard>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Simulaciones recientes"
        subtitle="Historial de todas tus simulaciones"
      />

      <div className="mb-6 flex flex-wrap gap-4">
        <input
          type="search"
          placeholder="Buscar por cultivo..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="cultiva-input max-w-md flex-1 rounded-full border border-white/10 bg-white/[0.04] px-5 py-2.5 text-sm text-white"
        />
        <button
          type="button"
          onClick={() => setSortAsc((v) => !v)}
          className="rounded-full border border-white/15 px-4 py-2 text-sm text-white/70 hover:bg-white/5"
        >
          Ordenar por día {sortAsc ? "↑" : "↓"}
        </button>
        <Link
          href={userRoutes.simulate()}
          className="rounded-full bg-cultiva-green px-5 py-2 text-sm font-semibold text-cultiva-dark"
        >
          Nueva simulación
        </Link>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          message="No hay simulaciones registradas"
          actionLabel="Ir a simular"
          actionHref={userRoutes.simulate()}
        />
      ) : (
        <DashboardCard>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  <th className="pb-3 pr-4">Cultivo</th>
                  <th className="pb-3 pr-4">Día</th>
                  <th className="pb-3 pr-4">Temp.</th>
                  <th className="pb-3 pr-4">Lluvia</th>
                  <th className="pb-3 pr-4">Sol</th>
                  <th className="pb-3 pr-4">Biomasa</th>
                  <th className="pb-3">Detalle</th>
                 </tr>
              </thead>
              <tbody>
                {pageItems.map((sim) => (
                  <tr key={sim.id} className="border-b border-white/5">
                    <td className="py-3 pr-4 font-medium text-white">
                      {sim.cropName}
                    </td>
                    <td className="py-3 pr-4 text-white/70">{sim.day}</td>
                    <td className="py-3 pr-4 text-white/70">{sim.temperature}°C</td>
                    <td className="py-3 pr-4 text-white/70">{sim.rain} mm</td>
                    <td className="py-3 pr-4 text-white/70">{sim.sunHours} h</td>
                    <td className="py-3 pr-4 font-semibold text-cultiva-green">
                      {sim.estimatedBiomass} g/m²
                    </td>
                    <td className="py-3">
                      <Link
                        href={userRoutes.cropStats(sim.cropId)}
                        className="text-cultiva-green hover:underline"
                      >
                        Ver detalle
                      </Link>
                    </td>
                   </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="mt-6 flex justify-center gap-2">
              <button
                type="button"
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-full border border-white/15 px-4 py-1.5 text-sm text-white/70 disabled:opacity-40"
              >
                Anterior
              </button>
              <span className="px-3 py-1.5 text-sm text-white/50">
                {page + 1} / {totalPages}
              </span>
              <button
                type="button"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-full border border-white/15 px-4 py-1.5 text-sm text-white/70 disabled:opacity-40"
              >
                Siguiente
              </button>
            </div>
          )}
        </DashboardCard>
      )}
    </>
  );
}