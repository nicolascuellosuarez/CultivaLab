"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getCrops, simulateDay } from "@/lib/api";
import { userRoutes } from "@/lib/routes";

type Crop = {
  id: string;
  name: string;
  active: boolean;
  water_stored: number;
};

export function SimulateForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselected = searchParams.get("cropId") ?? "";
  
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropId, setCropId] = useState("");
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<{
    biomass: number;
    water: number;
    cropId: string;
  } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchCrops();
  }, []);

  const fetchCrops = async () => {
    try {
      const cropsData = await getCrops();
      const activeCrops = cropsData.filter((c: Crop) => c.active);
      setCrops(activeCrops);
      
      let defaultCropId = "";
      if (preselected && activeCrops.some((c: Crop) => c.id === preselected)) {
        defaultCropId = preselected;
      } else if (activeCrops.length > 0) {
        defaultCropId = activeCrops[0].id;
      }
      setCropId(defaultCropId);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const crop = crops.find((c) => c.id === cropId);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!cropId) return;
    
    const formData = new FormData(e.currentTarget);
    const temperature = parseFloat(formData.get("temperature") as string);
    const rain = parseFloat(formData.get("rain") as string);
    const sun_hours = parseFloat(formData.get("sun_hours") as string);
    const irrigation = parseFloat(formData.get("irrigation") as string) || 0;

    if (isNaN(temperature) || isNaN(rain) || isNaN(sun_hours)) {
      setError("Todos los campos son obligatorios");
      return;
    }

    setSimulating(true);
    setError("");
    setResult(null);

    try {
      const updatedCrop = await simulateDay(cropId, temperature, rain, sun_hours, irrigation);
      setResult({
        biomass: updatedCrop.estimated_biomass || 0,
        water: updatedCrop.water_stored || 0,
        cropId: cropId,
      });
    } catch (err: any) {
      setError(err.message || "Error al simular el día");
    } finally {
      setSimulating(false);
    }
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Simular cultivo" subtitle="Ingresa las condiciones del día para avanzar la simulación" />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando cultivos...</p>
        </DashboardCard>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Simular cultivo"
        subtitle="Ingresa las condiciones del día para avanzar la simulación"
      />

      <DashboardCard>
        {crops.length === 0 ? (
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
                  setError("");
                }}
                className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white"
              >
                {crops.map((c) => (
                  <option key={c.id} value={c.id} className="bg-cultiva-dark">
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {crop && (
              <div className="mb-8 rounded-xl border border-white/10 bg-white/[0.02] p-4 text-sm text-white/70">
                <p>
                  <span className="text-white">{crop.name}</span>
                </p>
                <p className="mt-1">
                  Agua actual:{" "}
                  <span className="font-semibold text-cultiva-green">
                    {crop.water_stored} mm
                  </span>
                </p>
              </div>
            )}

            <form className="mx-auto max-w-2xl space-y-6" onSubmit={handleSubmit}>
              {[
                { id: "temperature", label: "Temperatura (°C)", min: -10, max: 56.7, step: "0.1", placeholder: "24.5" },
                { id: "rain", label: "Lluvia (mm)", min: 0, max: 500, step: "0.1", placeholder: "12" },
                { id: "sun_hours", label: "Horas de sol", min: 0, max: 16, step: "0.1", placeholder: "9" },
                { id: "irrigation", label: "Riego (mm)", min: 0, max: 200, step: "0.1", placeholder: "0" },
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
                    step={field.step}
                    placeholder={field.placeholder}
                    required={field.id !== "irrigation"}
                    className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-white"
                  />
                </div>
              ))}

              {error && (
                <div className="text-center text-sm text-red-400">{error}</div>
              )}

              <div className="flex flex-wrap justify-center gap-4 pt-4">
                <button
                  type="submit"
                  disabled={simulating}
                  className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105 disabled:opacity-50"
                >
                  {simulating ? "Simulando..." : "Simular día"}
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