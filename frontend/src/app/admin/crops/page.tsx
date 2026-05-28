"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_ADMIN_USERS, MOCK_CROPS } from "@/lib/mock-data";
import { adminRoutes } from "@/lib/routes";

export default function AdminCropsPage() {
  const [search, setSearch] = useState("");
  const [userFilter, setUserFilter] = useState("all");
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return MOCK_CROPS.filter((c) => {
      const matchSearch = c.name.toLowerCase().includes(search.toLowerCase());
      const matchUser = userFilter === "all" || userFilter === "user-1";
      return matchSearch && matchUser;
    });
  }, [search, userFilter]);

  return (
    <>
      <PageHeader title="Cultivos" subtitle="Todos los cultivos del sistema" />

      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Buscar cultivo..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="cultiva-input max-w-xs rounded-full border border-white/10 bg-white/[0.04] px-5 py-2.5 text-sm text-white"
        />
        <select
          value={userFilter}
          onChange={(e) => setUserFilter(e.target.value)}
          className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm text-white"
        >
          <option value="all" className="bg-cultiva-dark">
            Todos los usuarios
          </option>
          {MOCK_ADMIN_USERS.filter((u) => u.role === "user").map((u) => (
            <option key={u.id} value={u.id} className="bg-cultiva-dark">
              {u.username}
            </option>
          ))}
        </select>
      </div>

      <DashboardCard>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-white/50">
                <th className="pb-3 pr-4">Cultivo</th>
                <th className="pb-3 pr-4">Propietario</th>
                <th className="pb-3 pr-4">Tipo</th>
                <th className="pb-3 pr-4">Estado</th>
                <th className="pb-3 pr-4">Simulaciones</th>
                <th className="pb-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((crop) => (
                <tr key={crop.id} className="border-b border-white/5">
                  <td className="py-3 pr-4 font-medium text-white">{crop.name}</td>
                  <td className="py-3 pr-4 text-white/70">cultivador_lab</td>
                  <td className="py-3 pr-4 text-white/70">{crop.cropTypeName}</td>
                  <td className="py-3 pr-4">
                    {crop.active ? "Activo" : "Cosechado"}
                  </td>
                  <td className="py-3 pr-4 text-white/70">
                    {crop.daysSimulated}
                  </td>
                  <td className="py-3">
                    <div className="flex gap-3">
                      <Link
                        href={adminRoutes.cropStats(crop.id)}
                        className="text-cultiva-green hover:underline"
                      >
                        Ver
                      </Link>
                      <button
                        type="button"
                        onClick={() => setDeleteId(crop.id)}
                        className="text-red-400/90 hover:text-red-400"
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

      <ConfirmModal
        open={!!deleteId}
        title="Eliminar cultivo"
        message="¿Eliminar este cultivo del sistema?"
        onCancel={() => setDeleteId(null)}
        onConfirm={() => setDeleteId(null)}
      />
    </>
  );
}
