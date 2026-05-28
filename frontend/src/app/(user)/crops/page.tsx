"use client";

import Link from "next/link";
import { useMemo, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getCrops, getCropTypes, deleteCrop } from "@/lib/api";
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
  days_cycle: number;
  potential_performance: number;
};

export default function CropsListPage() {
  const router = useRouter();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropTypes, setCropTypes] = useState<CropType[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "activo" | "cosechado">("all");
  const [deleteId, setDeleteId] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [cropsData, typesData] = await Promise.all([
        getCrops(),
        getCropTypes(),
      ]);
      setCrops(cropsData);
      setCropTypes(typesData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getCropTypeInfo = (cropTypeId: string) => {
    const type = cropTypes.find(t => t.id === cropTypeId);
    return {
      name: type?.name || "Desconocido",
      cycleDays: type?.days_cycle || 0,
      potential: type?.potential_performance || 0,
    };
  };

  const filtered = useMemo(() => {
    return crops.filter((c) => {
      const typeInfo = getCropTypeInfo(c.crop_type_id);
      const matchSearch = c.name.toLowerCase().includes(search.toLowerCase());
      const matchStatus =
        statusFilter === "all" ||
        (statusFilter === "activo" && c.active) ||
        (statusFilter === "cosechado" && !c.active);
      return matchSearch && matchStatus;
    });
  }, [crops, search, statusFilter, cropTypes]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteCrop(deleteId);
      setCrops(crops.filter(c => c.id !== deleteId));
      setDeleteId(null);
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-white">Cargando...</div>;
  }

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
          message={crops.length === 0 ? "No tienes cultivos creados" : "Sin resultados"}
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
                  <th className="pb-3 pr-4 font-medium">Días</th>
                  <th className="pb-3 pr-4 font-medium">Agua</th>
                  <th className="pb-3 pr-4 font-medium">Estado</th>
                  <th className="pb-3 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((crop) => {
                  const typeInfo = getCropTypeInfo(crop.crop_type_id);
                  return (
                    <tr key={crop.id} className="border-b border-white/5">
                      <td className="py-4 pr-4 font-medium text-white">{crop.name}</td>
                      <td className="py-4 pr-4 text-white/70">{typeInfo.name}</td>
                      <td className="py-4 pr-4 text-white/70">
                        {typeInfo.cycleDays} días
                      </td>
                      <td className="py-4 pr-4 text-white/70">{crop.water_stored} mm</td>
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
                  );
                })}
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
        onConfirm={handleDelete}
      />
    </>
  );
}