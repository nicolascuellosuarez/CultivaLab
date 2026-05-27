"use client";

import type { ReactNode } from "react";
import type { NavItem } from "@/config/navigation";
import { DashboardGlows } from "./DashboardGlows";
import type { DashboardGlowKey } from "./glow-presets";
import { Sidebar } from "./Sidebar";

type DashboardShellProps = {
  children: ReactNode;
  glowKey: DashboardGlowKey;
  navItems: NavItem[];
  secondaryNavItems?: NavItem[];
  secondaryNavTitle?: string;
  brandHref?: string;
};

export function DashboardShell({
  children,
  glowKey,
  navItems,
  secondaryNavItems,
  secondaryNavTitle,
  brandHref,
}: DashboardShellProps) {
  return (
    <div className="relative min-h-screen bg-cultiva-dark">
      <DashboardGlows pageKey={glowKey} />
      <div className="relative z-10 flex min-h-screen">
        <Sidebar
          items={navItems}
          secondaryItems={secondaryNavItems}
          secondaryTitle={secondaryNavTitle}
          brandHref={brandHref}
        />
        <main className="min-w-0 flex-1 px-4 py-6 pt-16 lg:px-8 lg:py-8 lg:pt-8">
          <div className="mx-auto max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
