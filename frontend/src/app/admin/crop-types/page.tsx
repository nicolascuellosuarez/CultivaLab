"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CropTypeFormModal } from "@/components/admin/CropTypeFormModal";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getCropTypes, deleteCropType, getCrops } from "@/lib/api";

type CropType = {
  id: string;
  name: string;
  optimal_temp: number;
  needed_water: number;
  needed_light: number;
  days_cycle: number;
  initial_biomass: number;
  potential_performance: number;
};

type Crop = {
  id: string;
  crop_type_id: string;
  active: boolean;
};

export default function AdminCropTypesPage() {
  const router = useRouter();
  const [cropTypes, setCropTypes] = useState<CropType[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [editingType, setEditingType] = useState<CropType | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    if (!token || role !== "admin") {
      router.push("/login");
      return;
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [typesData, cropsData] = await Promise.all([
        getCropTypes(),
        getCrops(),
      ]);
      setCropTypes(typesData);
      setCrops(cropsData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const isTypeInUse = (typeId: string) => {
    return crops.some((c) => c.crop_type_id === typeId && c.active);
  };

  const openCreate = () => {
    setEditingType(null);
    setModalMode("create");
    setModalOpen(true);
  };

  const openEdit = (type: CropType) => {
    setEditingType(type);
    setModalMode("edit");
    setModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteCropType(deleteId);
      await fetchData();
      setDeleteId(null);
    } catch (error) {
      console.error(error);
    }
  };

  const handleModalClose = async (refresh?: boolean) => {
    setModalOpen(false);
    if (refresh) await fetchData();
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Tipos de cultivo" subtitle="Cargando..." />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando tipos de cultivo...</p>
        </DashboardCard>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Tipos de cultivo"
        subtitle="Catálogo de especies y parámetros del modelo"
      />

      <div className="mb-6">
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-cultiva-green px-6 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105"
        >
          + Crear nuevo tipo
        </button>
      </div>

      <DashboardCard>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-white/50">
                <th className="pb-3 pr-4">Nombre</th>
                <th className="pb-3 pr-4">Temp. óptima</th>
                <th className="pb-3 pr-4">Agua/día</th>
                <th className="pb-3 pr-4">Luz</th>
                <th className="pb-3 pr-4">Ciclo</th>
                <th className="pb-3 pr-4">Biomasa ini.</th>
                <th className="pb-3 pr-4">Potencial</th>
                <th className="pb-3">Acciones</th>
               </tr>
            </thead>
            <tbody>
              {cropTypes.map((type) => {
                const inUse = isTypeInUse(type.id);
                return (
                  <tr key={type.id} className="border-b border-white/5">
                    <td className="py-3 pr-4 font-medium text-white">{type.name}</td>
                    <td className="py-3 pr-4 text-white/70">{type.optimal_temp}°C</td>
                    <td className="py-3 pr-4 text-white/70">{type.needed_water} mm</td>
                    <td className="py-3 pr-4 text-white/70">{type.needed_light} h</td>
                    <td className="py-3 pr-4 text-white/70">{type.days_cycle} días</td>
                    <td className="py-3 pr-4 text-white/70">{type.initial_biomass}</td>
                    <td className="py-3 pr-4 text-white/70">
                      {type.potential_performance}
                    </td>
                    <td className="py-3">
                      <div className="flex gap-3">
                        <button
                          type="button"
                          className="text-cultiva-green hover:underline"
                          onClick={() => openEdit(type)}
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          disabled={inUse}
                          title={
                            inUse
                              ? "Hay cultivos activos usando este tipo"
                              : undefined
                          }
                          onClick={() => !inUse && setDeleteId(type.id)}
                          className={`text-sm ${
                            inUse
                              ? "cursor-not-allowed text-white/25"
                              : "text-red-400 hover:text-red-300"
                          }`}
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

      <CropTypeFormModal
        open={modalOpen}
        mode={modalMode}
        editData={editingType}
        onClose={handleModalClose}
      />

      <ConfirmModal
        open={!!deleteId}
        title="Eliminar tipo de cultivo"
        message="¿Confirmas la eliminación de este tipo?"
        onCancel={() => setDeleteId(null)}
        onConfirm={handleDelete}
      />
    </>
  );
}