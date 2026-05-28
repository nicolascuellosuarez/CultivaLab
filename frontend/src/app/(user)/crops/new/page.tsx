"use client";

import Link from "next/link";
import { useMemo, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { FormFieldRow } from "@/components/FormFieldRow";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getCropTypes, createCrop } from "@/lib/api";
import { userRoutes } from "@/lib/routes";

type CropType = {
  id: string;
  name: string;
  optimal_temp: number;
  needed_water: number;
  days_cycle: number;
  potential_performance: number;
  water_opt_low: number;
  water_opt_high: number;
};

export default function NewCropPage() {
  const router = useRouter();
  const [cropTypes, setCropTypes] = useState<CropType[]>([]);
  const [loading, setLoading] = useState(true);
  const [typeId, setTypeId] = useState("");
  const [name, setName] = useState("");
  const [water, setWater] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchCropTypes();
  }, []);

  const fetchCropTypes = async () => {
    try {
      const types = await getCropTypes();
      setCropTypes(types);
      if (types.length > 0) {
        setTypeId(types[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectedType = cropTypes.find((t) => t.id === typeId);
  const defaultWater = selectedType
    ? Math.round((selectedType.water_opt_low + selectedType.water_opt_high) / 2)
    : 0;

  const waterValue = water === "" ? String(defaultWater) : water;

  const typeInfo = useMemo(() => {
    if (!selectedType) return null;
    return (
      <ul className="mt-4 space-y-1 text-sm text-white/65">
        <li>Temp. óptima: {selectedType.optimal_temp}°C</li>
        <li>Agua necesaria/día: {selectedType.needed_water} mm</li>
        <li>Ciclo: {selectedType.days_cycle} días</li>
        <li>Rendimiento potencial: {selectedType.potential_performance} g/m²</li>
        <li>
          Agua inicial sugerida: {selectedType.water_opt_low}–{selectedType.water_opt_high} mm
        </li>
      </ul>
    );
  }, [selectedType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("El nombre del cultivo es obligatorio");
      return;
    }
    if (!typeId) {
      setError("Debes seleccionar un tipo de cultivo");
      return;
    }
    const waterNum = parseFloat(waterValue);
    if (isNaN(waterNum) || waterNum < (selectedType?.water_opt_low || 0)) {
      setError(`El agua inicial debe ser al menos ${selectedType?.water_opt_low} mm`);
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await createCrop(name, typeId, waterNum);
      router.push(userRoutes.crops);
    } catch (err: any) {
      setError(err.message || "Error al crear el cultivo");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-white">Cargando tipos de cultivo...</div>;
  }

  if (cropTypes.length === 0) {
    return (
      <div className="p-8 text-center text-white">
        <p>No hay tipos de cultivo disponibles.</p>
        <Link href="/admin/crop-types" className="mt-4 inline-block text-cultiva-green">
          Gestionar tipos
        </Link>
      </div>
    );
  }

  return (
    <>
      <PageHeader
        title="Crear nuevo cultivo"
        subtitle="Define tu parcela y comienza a simular su crecimiento"
      />

      <DashboardCard>
        <form className="mx-auto max-w-2xl space-y-8" onSubmit={handleSubmit}>
          <FormFieldRow
            label="Nombre"
            htmlFor="crop_name"
            placeholder="ej. Parcela Norte"
            value={name}
            onChange={(e) => setName(e.target.value)}
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
              {cropTypes.map((t) => (
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
              step="0.1"
              min={selectedType?.water_opt_low}
              max={selectedType?.water_opt_high}
              value={waterValue}
              onChange={(e) => setWater(e.target.value)}
              placeholder={`${defaultWater} mm sugerido`}
              className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white outline-none focus:border-cultiva-green/40"
            />
          </div>

          {error && (
            <div className="text-center text-sm text-red-400">{error}</div>
          )}

          <div className="flex justify-center gap-4 pt-4">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105 disabled:opacity-50"
            >
              {submitting ? "Creando..." : "Crear cultivo"}
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