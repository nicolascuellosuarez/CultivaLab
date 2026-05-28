"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { adminRoutes } from "@/lib/routes";
import { AdminBarChart } from "@/components/dashboard/charts/AdminBarChart";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { EmptyState } from "@/components/dashboard/EmptyState";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getUsers, getAdminCrops, getCropTypes } from "@/lib/api";

type User = {
  id: string;
  username: string;
  role: string;
};

type Crop = {
  id: string;
  name: string;
  user_id: string;
  active: boolean;
};

type CropType = {
  id: string;
  name: string;
};

export default function AdminDashboardPage() {
  const router = useRouter();
  const [adminName, setAdminName] = useState("");
  const [users, setUsers] = useState<User[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropTypes, setCropTypes] = useState<CropType[]>([]);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalUsers: 0,
    totalCrops: 0,
    activeCrops: 0,
    totalSimulations: 0,
    cropTypesCount: 0,
    cropTypesInUse: 0,
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    const username = localStorage.getItem("username");
    
    if (!token || role !== "admin") {
      router.push("/login");
      return;
    }
    
    setAdminName(username || "Admin");
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [usersData, cropsData, cropTypesData] = await Promise.all([
        getUsers(),
        getAdminCrops(),
        getCropTypes(),
      ]);

      setUsers(usersData);
      setCrops(cropsData);
      setCropTypes(cropTypesData);

      // Calcular simulaciones (condiciones diarias)
      let totalSims = 0;
      for (const crop of cropsData) {
        // Si tienes un endpoint para contar condiciones, úsalo. Por ahora asumimos 0.
        totalSims += 0;
      }

      const cropTypesInUse = new Set(cropsData.map((c: any) => c.crop_type_id)).size;

      setMetrics({
        totalUsers: usersData.length,
        totalCrops: cropsData.length,
        activeCrops: cropsData.filter((c: any) => c.active).length,
        totalSimulations: totalSims,
        cropTypesCount: cropTypesData.length,
        cropTypesInUse: cropTypesInUse,
      });
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const cropsByUser = users
    .filter(u => u.role === "user")
    .map(u => ({
      name: u.username,
      value: crops.filter(c => c.user_id === u.id).length,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);

  const hasChartData = cropsByUser.some(d => d.value > 0);

  if (loading) {
    return (
      <>
        <PageHeader title="Panel de Administración" subtitle="Cargando datos..." />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando...</p>
        </DashboardCard>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title={`¡Bienvenido, ${adminName}!`}
        subtitle="Panel de administración del laboratorio"
      />

      <section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard label="Usuarios registrados" value={metrics.totalUsers} />
        <MetricCard label="Total cultivos" value={metrics.totalCrops} />
        <MetricCard label="Cultivos activos" value={metrics.activeCrops} />
        <MetricCard label="Total simulaciones" value={metrics.totalSimulations} />
        <MetricCard label="Tipos de cultivo" value={metrics.cropTypesCount} />
        <MetricCard label="Tipos en uso" value={metrics.cropTypesInUse} />
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <DashboardCard title="Cultivos por usuario (top 5)" href={adminRoutes.users} actionLabel="Ver usuarios">
          {!hasChartData ? (
            <EmptyState message="No hay información para ver" variant="banner" />
          ) : (
            <AdminBarChart data={cropsByUser} />
          )}
        </DashboardCard>

        <DashboardCard title="Estadísticas generales">
          <div className="space-y-3">
            <div className="rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-sm">
              <span className="text-white/55">Total de cultivos activos: </span>
              <span className="font-semibold text-cultiva-green">{metrics.activeCrops}</span>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-sm">
              <span className="text-white/55">Tipos de cultivo disponibles: </span>
              <span className="font-semibold text-cultiva-green">{metrics.cropTypesCount}</span>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-sm">
              <span className="text-white/55">Usuarios registrados: </span>
              <span className="font-semibold text-cultiva-green">{metrics.totalUsers}</span>
            </div>
          </div>
        </DashboardCard>
      </div>

      <div className="mt-6 flex flex-wrap gap-4">
        <Link href={adminRoutes.cropTypes} className="text-sm text-cultiva-green hover:underline">
          Gestionar tipos de cultivo →
        </Link>
        <Link href={adminRoutes.users} className="text-sm text-cultiva-green hover:underline">
          Gestionar usuarios →
        </Link>
      </div>
    </>
  );
}