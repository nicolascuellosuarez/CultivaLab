"use client";

import { useMemo, useState } from "react";
import { ConfirmModal } from "@/components/dashboard/ConfirmModal";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_ADMIN_USERS } from "@/lib/mock-data";

export default function AdminUsersPage() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<"all" | "user" | "admin">("all");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 5;

  const filtered = useMemo(() => {
    return MOCK_ADMIN_USERS.filter((u) => {
      const matchSearch = u.username.toLowerCase().includes(search.toLowerCase());
      const matchRole = roleFilter === "all" || u.role === roleFilter;
      return matchSearch && matchRole;
    });
  }, [search, roleFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const items = filtered.slice(page * pageSize, page * pageSize + pageSize);

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
                <th className="pb-3 pr-4">Simulaciones</th>
                <th className="pb-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((user) => (
                <tr key={user.id} className="border-b border-white/5">
                  <td className="py-3 pr-4 font-medium text-white">
                    {user.username}
                  </td>
                  <td className="py-3 pr-4 capitalize text-white/70">{user.role}</td>
                  <td className="py-3 pr-4 text-white/70">{user.cropCount}</td>
                  <td className="py-3 pr-4 text-white/70">
                    {user.simulationCount}
                  </td>
                  <td className="py-3">
                    <button
                      type="button"
                      onClick={() => setDeleteId(user.id)}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      Eliminar usuario
                    </button>
                  </td>
                </tr>
              ))}
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
        onConfirm={() => setDeleteId(null)}
      />
    </>
  );
}
