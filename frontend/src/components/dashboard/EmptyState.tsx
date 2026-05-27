import Link from "next/link";

type EmptyStateProps = {
  message: string;
  actionLabel?: string;
  actionHref?: string;
  variant?: "card" | "banner";
};

export function EmptyState({
  message,
  actionLabel,
  actionHref,
  variant = "card",
}: EmptyStateProps) {
  if (variant === "banner") {
    return (
      <div className="flex items-center gap-4 py-8">
        <div className="h-px flex-1 bg-white/15" />
        <span className="shrink-0 text-sm font-medium text-white/40">
          {message}
        </span>
        <div className="h-px flex-1 bg-white/15" />
      </div>
    );
  }

  return (
    <div className="flex min-h-[160px] flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] px-6 py-10 text-center">
      <p className="text-2xl font-semibold text-cultiva-green md:text-3xl">
        {message}
      </p>
      {actionLabel && actionHref && (
        <Link
          href={actionHref}
          className="mt-6 inline-flex rounded-full bg-cultiva-green px-6 py-2.5 text-sm font-semibold text-cultiva-dark transition-transform hover:scale-105"
        >
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
