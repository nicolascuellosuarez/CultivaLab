"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_SIMULATIONS } from "@/lib/mock-data";
import { adminRoutes } from "@/lib/routes";

export default function AdminSimulationsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 6;

  const filtered = useMemo(
    () =>
      MOCK_SIMULATIONS.filter((s) =>
        s.cropName.toLowerCase().includes(search.toLowerCase())
      ),
    [search]
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const items = filtered.slice(page * pageSize, page * pageSize + pageSize);

  return (
    <>
      <PageHeader
        title="Simulaciones"
        subtitle="Registros de condiciones diarias en todo el sistema"
      />

      <div className="mb-6">
        <input
          type="search"
          placeholder="Buscar por cultivo..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="cultiva-input max-w-md rounded-full border border-white/10 bg-white/[0.04] px-5 py-2.5 text-sm text-white"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState message="No hay simulaciones registradas" />
      ) : (
        <DashboardCard>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  <th className="pb-3 pr-4">Cultivo</th>
                  <th className="pb-3 pr-4">Usuario</th>
                  <th className="pb-3 pr-4">Día</th>
                  <th className="pb-3 pr-4">Temp.</th>
                  <th className="pb-3 pr-4">Lluvia</th>
                  <th className="pb-3 pr-4">Sol</th>
                  <th className="pb-3 pr-4">Biomasa</th>
                  <th className="pb-3">Detalle</th>
                </tr>
              </thead>
              <tbody>
                {items.map((sim) => (
                  <tr key={sim.id} className="border-b border-white/5">
                    <td className="py-3 pr-4 text-white">{sim.cropName}</td>
                    <td className="py-3 pr-4 text-white/60">cultivador_lab</td>
                    <td className="py-3 pr-4 text-white/70">{sim.day}</td>
                    <td className="py-3 pr-4 text-white/70">{sim.temperature}°C</td>
                    <td className="py-3 pr-4 text-white/70">{sim.rain} mm</td>
                    <td className="py-3 pr-4 text-white/70">{sim.sunHours} h</td>
                    <td className="py-3 pr-4 font-semibold text-cultiva-green">
                      {sim.estimatedBiomass} g/m²
                    </td>
                    <td className="py-3">
                      <Link
                        href={adminRoutes.simulationDetail(sim.id)}
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
            <div className="mt-4 flex justify-center gap-2 text-sm text-white/50">
              <button
                type="button"
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
              >
                ←
              </button>
              <span>
                {page + 1}/{totalPages}
              </span>
              <button
                type="button"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
              >
                →
              </button>
            </div>
          )}
        </DashboardCard>
      )}
    </>
  );
}
