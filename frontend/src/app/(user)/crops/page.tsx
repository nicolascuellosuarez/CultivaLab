"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_CROPS } from "@/lib/mock-data";
import { userRoutes } from "@/lib/routes";

export default function CropsListPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "activo" | "cosechado">("all");
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return MOCK_CROPS.filter((c) => {
      const matchSearch = c.name.toLowerCase().includes(search.toLowerCase());
      const matchStatus =
        statusFilter === "all" ||
        (statusFilter === "activo" && c.active) ||
        (statusFilter === "cosechado" && !c.active);
      return matchSearch && matchStatus;
    });
  }, [search, statusFilter]);

  return (
    <>
      <PageHeader
        title="Mis cultivos"
        subtitle="Gestiona y consulta el estado de tus parcelas"
      />

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <input
          type="search"
          placeholder="Buscar por nombre..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="cultiva-input max-w-md rounded-full border border-white/10 bg-white/[0.04] px-5 py-2.5 text-sm text-white"
        />
        <div className="flex flex-wrap gap-2">
          {(["all", "activo", "cosechado"] as const).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setStatusFilter(s)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                statusFilter === s
                  ? "bg-cultiva-green text-cultiva-dark"
                  : "border border-white/15 text-white/70 hover:bg-white/5"
              }`}
            >
              {s === "all" ? "Todos" : s === "activo" ? "Activos" : "Cosechados"}
            </button>
          ))}
          <Link
            href={userRoutes.cropNew}
            className="rounded-full bg-cultiva-green px-5 py-2 text-sm font-semibold text-cultiva-dark"
          >
            + Crear cultivo
          </Link>
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          message={MOCK_CROPS.length === 0 ? "No tienes cultivos creados" : "Sin resultados"}
          actionLabel="Crear primer cultivo"
          actionHref={userRoutes.cropNew}
        />
      ) : (
        <DashboardCard>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/50">
                  <th className="pb-3 pr-4 font-medium">Nombre</th>
                  <th className="pb-3 pr-4 font-medium">Tipo</th>
                  <th className="pb-3 pr-4 font-medium">Biomasa</th>
                  <th className="pb-3 pr-4 font-medium">Días</th>
                  <th className="pb-3 pr-4 font-medium">Agua</th>
                  <th className="pb-3 pr-4 font-medium">Estado</th>
                  <th className="pb-3 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((crop) => (
                  <tr key={crop.id} className="border-b border-white/5">
                    <td className="py-4 pr-4 font-medium text-white">{crop.name}</td>
                    <td className="py-4 pr-4 text-white/70">{crop.cropTypeName}</td>
                    <td className="py-4 pr-4 font-bold text-cultiva-green">
                      {crop.biomass} g/m²
                    </td>
                    <td className="py-4 pr-4 text-white/70">
                      {crop.daysSimulated}/{crop.cycleDays}
                    </td>
                    <td className="py-4 pr-4 text-white/70">{crop.waterStored} mm</td>
                    <td className="py-4 pr-4">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          crop.active
                            ? "bg-cultiva-green/20 text-cultiva-green"
                            : "bg-white/10 text-white/50"
                        }`}
                      >
                        {crop.active ? "Activo" : "Cosechado"}
                      </span>
                    </td>
                    <td className="py-4">
                      <div className="flex flex-wrap gap-2">
                        <Link
                          href={userRoutes.cropStats(crop.id)}
                          className="text-xs font-medium text-cultiva-green hover:underline"
                        >
                          Estadísticas
                        </Link>
                        {crop.active && (
                          <Link
                            href={userRoutes.simulate(crop.id)}
                            className="text-xs font-medium text-white/70 hover:text-white"
                          >
                            Simular
                          </Link>
                        )}
                        <button
                          type="button"
                          onClick={() => setDeleteId(crop.id)}
                          className="text-xs font-medium text-red-400/90 hover:text-red-400"
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </DashboardCard>
      )}

      <ConfirmModal
        open={!!deleteId}
        title="Eliminar cultivo"
        message="¿Estás seguro de que deseas eliminar este cultivo? Esta acción no se puede deshacer."
        onCancel={() => setDeleteId(null)}
        onConfirm={() => setDeleteId(null)}
      />
    </>
  );
}
