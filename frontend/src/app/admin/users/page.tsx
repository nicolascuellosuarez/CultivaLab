"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { getUsers, getAdminCrops, getCropHistory, deleteUser } from "@/lib/api";

type User = {
  id: string;
  username: string;
  role: string;
};

type Crop = {
  id: string;
  user_id: string;
};

export default function AdminUsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<"all" | "user" | "admin">("all");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 5;

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
      const [usersData, cropsData] = await Promise.all([
        getUsers(),
        getAdminCrops(),
      ]);
      setUsers(usersData);
      setCrops(cropsData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getUserCropCount = (userId: string) => {
    return crops.filter((c) => c.user_id === userId).length;
  };

  const getUserSimulationCount = async (userId: string) => {
    const userCrops = crops.filter((c) => c.user_id === userId);
    let totalSims = 0;
    for (const crop of userCrops) {
      try {
        const history = await getCropHistory(crop.id);
        totalSims += history.length;
      } catch (error) {
        console.error(error);
      }
    }
    return totalSims;
  };

  const filtered = useMemo(() => {
    return users.filter((u) => {
      const matchSearch = u.username.toLowerCase().includes(search.toLowerCase());
      const matchRole = roleFilter === "all" || u.role === roleFilter;
      return matchSearch && matchRole;
    });
  }, [users, search, roleFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const items = filtered.slice(page * pageSize, page * pageSize + pageSize);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteUser(deleteId);
      await fetchData();
      setDeleteId(null);
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Usuarios" subtitle="Cargando..." />
        <DashboardCard>
          <p className="text-center text-white/50">Cargando usuarios...</p>
        </DashboardCard>
      </>
    );
  }

  return (
    <>
      <PageHeader title="Usuarios" subtitle="Gestión de cuentas del sistema" />

      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Buscar usuario..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="cultiva-input max-w-xs rounded-full border border-white/10 bg-white/[0.04] px-5 py-2.5 text-sm text-white"
        />
        {(["all", "user", "admin"] as const).map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRoleFilter(r)}
            className={`rounded-full px-4 py-2 text-sm ${
              roleFilter === r
                ? "bg-cultiva-green text-cultiva-dark"
                : "border border-white/15 text-white/70"
            }`}
          >
            {r === "all" ? "Todos" : r === "user" ? "Usuario" : "Admin"}
          </button>
        ))}
      </div>

      <DashboardCard>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-white/50">
                <th className="pb-3 pr-4">Usuario</th>
                <th className="pb-3 pr-4">Rol</th>
                <th className="pb-3 pr-4">Cultivos</th>
                <th className="pb-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((user) => {
                const cropCount = getUserCropCount(user.id);
                return (
                  <tr key={user.id} className="border-b border-white/5">
                    <td className="py-3 pr-4 font-medium text-white">
                      {user.username}
                    </td>
                    <td className="py-3 pr-4 capitalize text-white/70">{user.role}</td>
                    <td className="py-3 pr-4 text-white/70">{cropCount}</td>
                    <td className="py-3">
                      {user.role !== "admin" && (
                        <button
                          type="button"
                          onClick={() => setDeleteId(user.id)}
                          className="text-xs text-red-400 hover:text-red-300"
                        >
                          Eliminar usuario
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="mt-4 flex justify-center gap-2 text-sm text-white/50">
            <button
              type="button"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="disabled:opacity-40"
            >
              ←
            </button>
            <span>
              {page + 1}/{totalPages}
            </span>
            <button
              type="button"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="disabled:opacity-40"
            >
              →
            </button>
          </div>
        )}
      </DashboardCard>

      <ConfirmModal
        open={!!deleteId}
        title="Eliminar usuario"
        message="Se eliminarán también sus cultivos y simulaciones. ¿Continuar?"
        onCancel={() => setDeleteId(null)}
        onConfirm={handleDelete}
      />
    </>
  );
}