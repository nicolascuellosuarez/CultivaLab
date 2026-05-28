"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { FormFieldRow } from "@/components/FormFieldRow";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { updateUsername, updatePassword } from "@/lib/api";

export default function AdminProfilePage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [newUsername, setNewUsername] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    if (!token || role !== "admin") {
      router.push("/login");
      return;
    }
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) setUsername(storedUsername);
  }, []);

  const handleUsernameSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername.trim()) {
      setError("El nuevo nombre de usuario no puede estar vacío");
      return;
    }
    if (!currentPassword) {
      setError("Debes ingresar tu contraseña actual para cambiar el usuario");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await updateUsername(newUsername, currentPassword);
      localStorage.setItem("username", newUsername);
      setUsername(newUsername);
      setNewUsername("");
      setCurrentPassword("");
      setSuccess("Nombre de usuario actualizado correctamente");
    } catch (err: any) {
      setError(err.message || "Error al actualizar el usuario");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!oldPassword) {
      setError("Debes ingresar tu contraseña actual");
      return;
    }
    if (!newPassword || newPassword.length < 8) {
      setError("La nueva contraseña debe tener al menos 8 caracteres");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await updatePassword(oldPassword, newPassword);
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSuccess("Contraseña actualizada correctamente");
    } catch (err: any) {
      setError(err.message || "Error al actualizar la contraseña");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Mi perfil (administrador)"
        subtitle="Actualiza las credenciales de tu cuenta de administrador"
      />

      {error && (
        <div className="mb-4 rounded-lg border border-red-400/50 bg-red-400/10 p-3 text-center text-sm text-red-400">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 rounded-lg border border-cultiva-green/50 bg-cultiva-green/10 p-3 text-center text-sm text-cultiva-green">
          {success}
        </div>
      )}

      <div className="grid gap-8">
        <DashboardCard title="Cambiar nombre de usuario">
          <form className="mx-auto max-w-2xl space-y-6" onSubmit={handleUsernameSubmit}>
            <FormFieldRow
              label="Usuario actual"
              htmlFor="admin_current_username"
              placeholder={username}
              disabled
            />
            <FormFieldRow
              label="Nuevo usuario"
              htmlFor="admin_new_username"
              placeholder="Nuevo nombre de usuario"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
            />
            <FormFieldRow
              label="Contraseña actual"
              htmlFor="admin_current_password_username"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
            <div className="flex justify-center pt-2">
              <button
                type="submit"
                disabled={loading}
                className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105 disabled:opacity-50"
              >
                {loading ? "Guardando..." : "Guardar cambios"}
              </button>
            </div>
          </form>
        </DashboardCard>

        <DashboardCard title="Cambiar contraseña">
          <form className="mx-auto max-w-2xl space-y-6" onSubmit={handlePasswordSubmit}>
            <FormFieldRow
              label="Contraseña actual"
              htmlFor="admin_old_password"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
            />
            <FormFieldRow
              label="Nueva contraseña"
              htmlFor="admin_new_password"
              type="password"
              placeholder="mínimo 8 caracteres"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <FormFieldRow
              label="Confirmar"
              htmlFor="admin_confirm_password"
              type="password"
              placeholder="repite la contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <div className="flex justify-center pt-2">
              <button
                type="submit"
                disabled={loading}
                className="rounded-full bg-cultiva-green px-8 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm hover:scale-105 disabled:opacity-50"
              >
                {loading ? "Actualizando..." : "Actualizar contraseña"}
              </button>
            </div>
          </form>
        </DashboardCard>
      </div>
    </>
  );
}