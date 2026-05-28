"use client";

import { useEffect, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import { CropStatsContent } from "@/components/crops/CropStatsContent";
import { getCropById, getCropHistory, getCropStats, getCropTypes } from "@/lib/api";

type Props = { params: Promise<{ id: string }> };

export default function AdminCropStatsPage({ params }: Props) {
  const router = useRouter();
  const [id, setId] = useState<string | null>(null);
  const [crop, setCrop] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [cropTypes, setCropTypes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    if (!token || role !== "admin") {
      router.push("/login");
      return;
    }
    
    params.then((p) => setId(p.id));
  }, []);

  useEffect(() => {
    if (!id) return;
    
    const fetchData = async () => {
      try {
        const [cropData, historyData, statsData, typesData] = await Promise.all([
          getCropById(id),
          getCropHistory(id),
          getCropStats(id),
          getCropTypes(),
        ]);
        
        setCrop(cropData);
        setHistory(historyData);
        setStats(statsData);
        setCropTypes(typesData);
      } catch (error) {
        notFound();
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id]);

  if (loading) return <div className="p-8 text-center text-white">Cargando...</div>;
  if (!crop) return notFound();

  const cropType = cropTypes.find((t) => t.id === crop.crop_type_id);
  const cropTypeName = cropType?.name || "Desconocido";

  const adaptedCrop = {
    id: crop.id,
    name: crop.name,
    cropTypeName: cropTypeName,
    active: crop.active,
    daysSimulated: history.length,
    biomass: history.length > 0 ? history[history.length - 1].estimated_biomass : 0,
    cycleDays: cropType?.days_cycle || 0,
    waterStored: crop.water_stored || 0,
    cropTypeId: crop.crop_type_id,
    performanceRatio: stats?.performance_ratio || 0,
  };

  const adaptedHistory = history.map((h) => ({
    day: h.day,
    temperature: h.temperature,
    rain: h.rain,
    sunHours: h.sun_hours,
    estimatedBiomass: h.estimated_biomass,
  }));

  const adaptedStats = {
    averageTemperature: stats?.average_temperature || 0,
    averageRain: stats?.average_rain || 0,
    averageSunHours: stats?.average_sun_hours || 0,
    totalGrowth: stats?.total_growth || 0,
    stressDays: stats?.stress_days || 0,
    performanceRatio: stats?.performance_ratio || 0,
  };

  return (
    <CropStatsContent
      crop={adaptedCrop}
      history={adaptedHistory}
      stats={adaptedStats}
      context="admin"
    />
  );
}