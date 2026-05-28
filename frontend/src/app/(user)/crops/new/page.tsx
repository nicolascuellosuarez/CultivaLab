"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { FormFieldRow } from "@/components/FormFieldRow";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_CROP_TYPES } from "@/lib/mock-data";
import { userRoutes } from "@/lib/routes";

export default function NewCropPage() {
  const [typeId, setTypeId] = useState(MOCK_CROP_TYPES[0]?.id ?? "");
  const [water, setWater] = useState("");

  const selectedType = MOCK_CROP_TYPES.find((t) => t.id === typeId);
  const defaultWater = selectedType
    ? Math.round((selectedType.waterOptLow + selectedType.waterOptHigh) / 2)
    : 0;

  const waterValue = water === "" ? String(defaultWater) : water;

  const typeInfo = useMemo(() => {
    if (!selectedType) return null;
    return (
      <ul className="mt-4 space-y-1 text-sm text-white/65">
        <li>Temp. óptima: {selectedType.optimalTemp}°C</li>
        <li>Agua necesaria/día: {selectedType.neededWater} mm</li>
        <li>Ciclo: {selectedType.daysCycle} días</li>
        <li>Rendimiento potencial: {selectedType.potentialPerformance} g/m²</li>
        <li>
          Agua inicial sugerida: {selectedType.waterOptLow}–{selectedType.waterOptHigh} mm
        </li>
      </ul>
    );
  }, [selectedType]);

  return (
    <>
      <PageHeader
        title="Crear nuevo cultivo"
        subtitle="Define tu parcela y comienza a simular su crecimiento"
      />

      <DashboardCard>
        <form
          className="mx-auto max-w-2xl space-y-8"
          onSubmit={(e) => e.preventDefault()}
        >
          <FormFieldRow
            label="Nombre"
            htmlFor="crop_name"
            placeholder="ej. Parcela Norte"
          />

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-5">
            <label
              htmlFor="crop_type"
              className="shrink-0 rounded-full border border-cultiva-green bg-transparent px-6 py-3.5 text-center text-sm font-semibold text-cultiva-green sm:min-w-[200px] sm:px-8 sm:py-4 sm:text-base"
            >
              Tipo de cultivo
            </label>
            <select
              id="crop_type"
              value={typeId}
              onChange={(e) => {
                setTypeId(e.target.value);
                setWater("");
              }}
              className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white outline-none focus:border-cultiva-green/40"
            >
              {MOCK_CROP_TYPES.map((t) => (
                <option key={t.id} value={t.id} className="bg-cultiva-dark">
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          {typeInfo && (
            <div className="rounded-xl border border-white/10 bg-white/[0.02] px-5 py-4">
              <p className="text-sm font-medium text-cultiva-green">
                Información del tipo
              </p>
              {typeInfo}
            </div>
          )}

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-5">
            <label
              htmlFor="water_stored"
              className="shrink-0 rounded-full border border-cultiva-green bg-transparent px-6 py-3.5 text-center text-sm font-semibold text-cultiva-green sm:min-w-[200px] sm:px-8 sm:py-4 sm:text-base"
            >
              Agua inicial
            </label>
            <input
              id="water_stored"
              type="number"
              min={selectedType?.waterOptLow}
              max={selectedType?.waterOptHigh}
              value={waterValue}
              onChange={(e) => setWater(e.target.value)}
              placeholder={`${defaultWater} mm sugerido`}
              className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white outline-none focus:border-cultiva-green/40"
            />
          </div>

          <div className="flex justify-center gap-4 pt-4">
            <button
              type="submit"
              className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105"
            >
              Crear cultivo
            </button>
            <Link
              href={userRoutes.crops}
              className="rounded-full border border-white/20 px-8 py-2.5 text-sm font-medium text-white hover:bg-white/5"
            >
              Cancelar
            </Link>
          </div>
        </form>
      </DashboardCard>
    </>
  );
}
