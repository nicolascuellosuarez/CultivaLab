"use client";

import { adminNavItems } from "@/config/navigation";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import type { DashboardGlowKey } from "@/components/dashboard/glow-presets";
import { usePathname } from "next/navigation";

const glowByPath: Record<string, DashboardGlowKey> = {
  "/admin": "admin",
  "/admin/users": "admin-users",
  "/admin/crops": "admin-crops",
  "/admin/simulations": "admin-simulations",
  "/admin/crop-types": "admin-crop-types",
  "/admin/profile": "admin-profile",
};

function resolveGlow(pathname: string): DashboardGlowKey {
  if (
    pathname.startsWith("/admin/crops/") &&
    pathname.endsWith("/stats")
  ) {
    return "admin-crop-stats";
  }
  if (
    pathname.startsWith("/admin/simulations/") &&
    pathname !== "/admin/simulations"
  ) {
    return "admin-sim-detail";
  }
  return glowByPath[pathname] ?? "admin";
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const glowKey = resolveGlow(pathname);

  return (
    <DashboardShell glowKey={glowKey} navItems={adminNavItems} brandHref="/admin">
      {children}
    </DashboardShell>
  );
}
