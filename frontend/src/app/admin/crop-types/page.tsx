"use client";

import { useState } from "react";
import { CropTypeFormModal } from "@/components/admin/CropTypeFormModal";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_CROP_TYPES, MOCK_CROPS } from "@/lib/mock-data";

export default function AdminCropTypesPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const isTypeInUse = (typeId: string) =>
    MOCK_CROPS.some((c) => c.cropTypeId === typeId && c.active);

  const openCreate = () => {
    setModalMode("create");
    setModalOpen(true);
  };

  const openEdit = () => {
    setModalMode("edit");
    setModalOpen(true);
  };

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
              {MOCK_CROP_TYPES.map((type) => {
                const inUse = isTypeInUse(type.id);
                return (
                  <tr key={type.id} className="border-b border-white/5">
                    <td className="py-3 pr-4 font-medium text-white">{type.name}</td>
                    <td className="py-3 pr-4 text-white/70">{type.optimalTemp}°C</td>
                    <td className="py-3 pr-4 text-white/70">{type.neededWater} mm</td>
                    <td className="py-3 pr-4 text-white/70">{type.neededLight} h</td>
                    <td className="py-3 pr-4 text-white/70">{type.daysCycle} días</td>
                    <td className="py-3 pr-4 text-white/70">{type.initialBiomass}</td>
                    <td className="py-3 pr-4 text-white/70">
                      {type.potentialPerformance}
                    </td>
                    <td className="py-3">
                      <div className="flex gap-3">
                        <button
                          type="button"
                          className="text-cultiva-green hover:underline"
                          onClick={openEdit}
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
        onClose={() => setModalOpen(false)}
      />

      <ConfirmModal
        open={!!deleteId}
        title="Eliminar tipo de cultivo"
        message="¿Confirmas la eliminación de este tipo?"
        onCancel={() => setDeleteId(null)}
        onConfirm={() => setDeleteId(null)}
      />
    </>
  );
}
