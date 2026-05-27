type MetricCardProps = {
  label: string;
  value: string | number;
  suffix?: string;
};

export function MetricCard({ label, value, suffix }: MetricCardProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] p-5">
      <div
        className="pointer-events-none absolute -top-8 left-4 h-16 w-32 rounded-full bg-cultiva-green/20 blur-2xl"
        aria-hidden
      />
      <p className="text-xs font-medium text-white/55 md:text-sm">{label}</p>
      <p className="mt-2 text-2xl font-bold text-white md:text-3xl">
        {value}
        {suffix && (
          <span className="ml-1 text-base font-normal text-white/50">
            {suffix}
          </span>
        )}
      </p>
    </div>
  );
}
