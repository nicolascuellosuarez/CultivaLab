"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getAdminCrops, getUsers, getCropTypes, deleteCrop } from "@/lib/api";
import { adminRoutes } from "@/lib/routes";

type User = {
  id: string;
  username: string;
  role: string;
};

type CropType = {
  id: string;
  name: string;
};

type Crop = {
  id: string;
  name: string;
  user_id: string;
  crop_type_id: string;
  active: boolean;
};

export default function AdminCropsPage() {
  const router = useRouter();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [cropTypes, setCropTypes] = useState<CropType[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [userFilter, setUserFilter] = useState("all");
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
      const [cropsData, usersData, cropTypesData] = await Promise.all([
        getAdminCrops(),
        getUsers(),
        getCropTypes(),
      ]);
      setCrops(cropsData);
      setUsers(usersData.filter((u: User) => u.role === "user"));
      setCropTypes(cropTypesData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getUserName = (userId: string) => {
    const user = users.find((u) => u.id === userId);
    return user?.username || "Desconocido";
  };

  const getCropTypeName = (typeId: string) => {
    const type = cropTypes.find((t) => t.id === typeId);
    return type?.name || "Desconocido";
  };

  const filtered = useMemo(() => {
    return crops.filter((c) => {
      const matchSearch = c.name.toLowerCase().includes(search.toLowerCase());
      const matchUser = userFilter === "all" || c.user_id === userFilter;
      return matchSearch && matchUser;
    });
  }, [crops, search, userFilter]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteCrop(deleteId);
      await fetchData();
      setDeleteId(null);
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Cultivos" subtitle="Todos los cultivos del sistema" />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando...</p>
        </DashboardCard>
      </>
    );
  }

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
          {users.map((u) => (
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
                <th className="pb-3">Acciones</th>
               </tr>
            </thead>
            <tbody>
              {filtered.map((crop) => (
                <tr key={crop.id} className="border-b border-white/5">
                  <td className="py-3 pr-4 font-medium text-white">{crop.name}</td>
                  <td className="py-3 pr-4 text-white/70">{getUserName(crop.user_id)}</td>
                  <td className="py-3 pr-4 text-white/70">{getCropTypeName(crop.crop_type_id)}</td>
                  <td className="py-3 pr-4">
                    {crop.active ? "Activo" : "Cosechado"}
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
        onConfirm={handleDelete}
      />
    </>
  );
}