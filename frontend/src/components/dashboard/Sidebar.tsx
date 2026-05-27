"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, Menu, X } from "lucide-react";
import { useState } from "react";
import type { NavItem } from "@/config/navigation";
import { CultivaLogo } from "@/components/CultivaLogo";

type SidebarProps = {
  items: NavItem[];
  secondaryItems?: NavItem[];
  secondaryTitle?: string;
  brandHref?: string;
};

export function Sidebar({
  items,
  secondaryItems,
  secondaryTitle = "Vista usuario",
  brandHref = "/dashboard",
}: SidebarProps) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(`${href}/`);

  const navContent = (
    <>
      <Link
        href={brandHref}
        className="mb-8 flex items-center gap-3 px-2"
        onClick={() => setOpen(false)}
      >
        <CultivaLogo />
        <span className="text-lg font-semibold text-white">CultivaLab</span>
      </Link>

      <nav className="flex flex-1 flex-col gap-1">
        {items.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            onClick={() => setOpen(false)}
            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
              isActive(href)
                ? "bg-cultiva-green/15 text-cultiva-green"
                : "text-white/70 hover:bg-white/5 hover:text-white"
            }`}
          >
            <Icon className="h-5 w-5 shrink-0" />
            {label}
          </Link>
        ))}

        {secondaryItems && secondaryItems.length > 0 && (
          <>
            <p className="mb-1 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-white/35">
              {secondaryTitle}
            </p>
            {secondaryItems.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive(href)
                    ? "bg-cultiva-green/15 text-cultiva-green"
                    : "text-white/70 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {label}
              </Link>
            ))}
          </>
        )}
      </nav>

      <Link
        href="/login"
        className="mt-4 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/60 transition-colors hover:bg-white/5 hover:text-white"
      >
        <LogOut className="h-5 w-5" />
        Cerrar sesión
      </Link>
    </>
  );

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="fixed left-4 top-4 z-50 rounded-xl border border-white/10 bg-cultiva-dark/90 p-2 text-white lg:hidden"
        aria-label="Abrir menú"
      >
        <Menu className="h-6 w-6" />
      </button>

      {open && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          aria-label="Cerrar menú"
          onClick={() => setOpen(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[min(280px,85vw)] flex-col border-r border-white/10 bg-[#111111] px-4 py-6 transition-transform lg:static lg:z-auto lg:w-64 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="mb-4 self-end rounded-lg p-1 text-white/60 hover:text-white lg:hidden"
          aria-label="Cerrar menú"
        >
          <X className="h-5 w-5" />
        </button>
        {navContent}
      </aside>
    </>
  );
}
