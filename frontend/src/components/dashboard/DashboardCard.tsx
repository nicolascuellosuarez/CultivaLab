import Link from "next/link";
import type { ReactNode } from "react";

type DashboardCardProps = {
  title?: string;
  children: ReactNode;
  className?: string;
  href?: string;
  actionLabel?: string;
};

export function DashboardCard({
  title,
  children,
  className = "",
  href,
  actionLabel,
}: DashboardCardProps) {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-white/[0.04] p-5 backdrop-blur-sm md:p-6 ${className}`}
    >
      {(title || (href && actionLabel)) && (
        <div className="mb-4 flex items-center justify-between gap-3">
          {title && (
            <h3 className="text-sm font-semibold text-white/90 md:text-base">
              {title}
            </h3>
          )}
          {href && actionLabel && (
            <Link
              href={href}
              className="text-xs font-medium text-cultiva-green hover:underline md:text-sm"
            >
              {actionLabel}
            </Link>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
