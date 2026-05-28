"use client";

import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { FormFieldRow } from "@/components/FormFieldRow";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { MOCK_ADMIN_USERS } from "@/lib/mock-data";

const ADMIN_USERNAME =
  MOCK_ADMIN_USERS.find((u) => u.role === "admin")?.username ?? "admin_lab";

export default function AdminProfilePage() {
  return (
    <>
      <PageHeader
        title="Mi perfil (administrador)"
        subtitle="Actualiza las credenciales de tu cuenta de administrador"
      />

      <div className="grid gap-8">
        <DashboardCard title="Cambiar nombre de usuario">
          <form
            className="mx-auto max-w-2xl space-y-6"
            onSubmit={(e) => e.preventDefault()}
          >
            <FormFieldRow
              label="Nuevo usuario"
              htmlFor="admin_new_username"
              placeholder={ADMIN_USERNAME}
            />
            <FormFieldRow
              label="Contraseña actual"
              htmlFor="admin_current_password_username"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
            />
            <div className="flex justify-center pt-2">
              <button
                type="submit"
                className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105"
              >
                Guardar cambios
              </button>
            </div>
          </form>
        </DashboardCard>

        <DashboardCard title="Cambiar contraseña">
          <form
            className="mx-auto max-w-2xl space-y-6"
            onSubmit={(e) => e.preventDefault()}
          >
            <FormFieldRow
              label="Contraseña actual"
              htmlFor="admin_old_password"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
            />
            <FormFieldRow
              label="Nueva contraseña"
              htmlFor="admin_new_password"
              type="password"
              placeholder="mínimo 8 caracteres"
            />
            <FormFieldRow
              label="Confirmar"
              htmlFor="admin_confirm_password"
              type="password"
              placeholder="repite la contraseña"
            />
            <div className="flex justify-center pt-2">
              <button
                type="submit"
                className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105"
              >
                Actualizar contraseña
              </button>
            </div>
          </form>
        </DashboardCard>
      </div>
    </>
  );
}
