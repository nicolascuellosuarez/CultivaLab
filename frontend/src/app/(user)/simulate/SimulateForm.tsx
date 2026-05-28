"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_CROPS } from "@/lib/mock-data";
import { userRoutes } from "@/lib/routes";

export function SimulateForm() {
  const searchParams = useSearchParams();
  const preselected = searchParams.get("cropId") ?? "";
  const activeCrops = MOCK_CROPS.filter((c) => c.active);
  const [cropId, setCropId] = useState(
    preselected && activeCrops.some((c) => c.id === preselected)
      ? preselected
      : activeCrops[0]?.id ?? ""
  );
  const [result, setResult] = useState<{
    biomass: number;
    water: number;
    cropId: string;
  } | null>(null);

  const crop = activeCrops.find((c) => c.id === cropId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!crop) return;
    setResult({
      biomass: crop.biomass + 28,
      water: Math.min(100, crop.waterStored + 5),
      cropId: crop.id,
    });
  };

  return (
    <>
      <PageHeader
        title="Simular cultivo"
        subtitle="Ingresa las condiciones del día para avanzar la simulación"
      />

      <DashboardCard>
        {activeCrops.length === 0 ? (
          <p className="text-center text-cultiva-green">
            No tienes cultivos activos.{" "}
            <Link href={userRoutes.cropNew} className="underline">
              Crea uno primero
            </Link>
          </p>
        ) : (
          <>
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-5">
              <label
                htmlFor="crop_select"
                className="shrink-0 rounded-full border border-cultiva-green bg-transparent px-6 py-3.5 text-sm font-semibold text-cultiva-green sm:min-w-[200px]"
              >
                Cultivo
              </label>
              <select
                id="crop_select"
                value={cropId}
                onChange={(e) => {
                  setCropId(e.target.value);
                  setResult(null);
                }}
                className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white"
              >
                {activeCrops.map((c) => (
                  <option key={c.id} value={c.id} className="bg-cultiva-dark">
                    {c.name} ({c.cropTypeName})
                  </option>
                ))}
              </select>
            </div>

            {crop && (
              <div className="mb-8 rounded-xl border border-white/10 bg-white/[0.02] p-4 text-sm text-white/70">
                <p>
                  <span className="text-white">{crop.name}</span> · {crop.cropTypeName}
                </p>
                <p className="mt-1">
                  Biomasa actual:{" "}
                  <span className="font-semibold text-cultiva-green">
                    {crop.biomass} g/m²
                  </span>{" "}
                  · Agua: {crop.waterStored} mm
                </p>
              </div>
            )}

            <form className="mx-auto max-w-2xl space-y-6" onSubmit={handleSubmit}>
              {[
                { id: "temperature", label: "Temperatura (°C)", min: -10, max: 56.7, ph: "24.5" },
                { id: "rain", label: "Lluvia (mm)", min: 0, max: 500, ph: "12" },
                { id: "sun_hours", label: "Horas de sol", min: 0, max: 16, ph: "9" },
                { id: "irrigation", label: "Riego (mm)", min: 0, max: 200, ph: "0" },
              ].map((field) => (
                <div
                  key={field.id}
                  className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-5"
                >
                  <label
                    htmlFor={field.id}
                    className="shrink-0 rounded-full border border-cultiva-green bg-transparent px-6 py-3.5 text-center text-sm font-semibold text-cultiva-green sm:min-w-[200px]"
                  >
                    {field.label}
                  </label>
                  <input
                    id={field.id}
                    name={field.id}
                    type="number"
                    min={field.min}
                    max={field.max}
                    step="any"
                    defaultValue={field.ph}
                    placeholder={field.ph}
                    className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white"
                  />
                </div>
              ))}

              <div className="flex flex-wrap justify-center gap-4 pt-4">
                <button
                  type="submit"
                  className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105"
                >
                  Simular día
                </button>
              </div>
            </form>

            {result && (
              <div className="mt-10 rounded-xl border border-cultiva-green/30 bg-cultiva-green/10 p-6 text-center">
                <p className="text-white/80">Resultado de la simulación</p>
                <p className="mt-2 text-2xl font-bold text-cultiva-green">
                  {result.biomass} g/m²
                </p>
                <p className="text-sm text-white/60">
                  Agua almacenada: {result.water} mm
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-3">
                  <Link
                    href={userRoutes.cropStats(result.cropId)}
                    className="rounded-full bg-cultiva-green px-6 py-2.5 text-sm font-semibold text-cultiva-dark"
                  >
                    Ir a estadísticas del cultivo
                  </Link>
                  <button
                    type="button"
                    onClick={() => setResult(null)}
                    className="rounded-full border border-white/20 px-6 py-2.5 text-sm text-white"
                  >
                    Simular otro día
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </DashboardCard>
    </>
  );
}
