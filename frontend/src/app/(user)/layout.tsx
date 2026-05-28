"use client";

import { userNavItems } from "@/config/navigation";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import type { DashboardGlowKey } from "@/components/dashboard/glow-presets";
import { usePathname } from "next/navigation";

const glowByPath: Record<string, DashboardGlowKey> = {
  "/dashboard": "dashboard",
  "/crops": "crops",
  "/crops/new": "crops-new",
  "/simulate": "simulate",
  "/simulations": "simulations",
  "/profile": "profile",
};

function resolveGlow(pathname: string): DashboardGlowKey {
  if (pathname.startsWith("/crops/") && pathname.endsWith("/stats")) {
    return "stats";
  }
  return glowByPath[pathname] ?? "dashboard";
}

export default function UserAppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const glowKey = resolveGlow(pathname);

  return (
    <DashboardShell glowKey={glowKey} navItems={userNavItems} brandHref="/dashboard">
      {children}
    </DashboardShell>
  );
}
