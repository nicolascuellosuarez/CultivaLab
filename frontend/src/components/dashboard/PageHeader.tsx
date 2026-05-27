type PageHeaderProps = {
  title: string;
  subtitle?: string;
};

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <header className="mb-8">
      <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl lg:text-4xl">
        {title}
      </h1>
      {subtitle && (
        <p className="mt-2 text-base text-white/70 md:text-lg">{subtitle}</p>
      )}
      <div className="mt-6 h-px w-full bg-white/15" />
    </header>
  );
}
