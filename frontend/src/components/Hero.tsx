import Link from "next/link";

const actions = [
  { label: "Registrarse", href: "/register" },
  { label: "Registro de Administrador", href: "/register-admin" },
  { label: "Iniciar Sesión", href: "/login" },
] as const;

function ActionButton({ label, href }: { label: string; href: string }) {
  return (
    <Link
      href={href}
      className="rounded-full bg-cultiva-green px-6 py-3 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm transition-transform duration-200 hover:scale-[1.03] hover:shadow-cultiva-glow md:px-8 md:py-3.5 md:text-base"
    >
      {label}
    </Link>
  );
}

export function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-6 pt-16">
      <div className="relative z-10 flex w-full max-w-4xl flex-col items-center text-center">
        <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl md:text-7xl lg:text-8xl">
          CultivaLab
        </h1>
        <p className="mt-4 text-lg text-white/90 sm:text-xl md:text-2xl">
          Simula. Cultiva. Evoluciona.
        </p>

        <div className="relative mt-12 w-full md:mt-16">
          <div
            className="pointer-events-none absolute inset-x-0 top-1/2 h-32 -translate-y-1/2 rounded-full bg-cultiva-green/30 blur-3xl"
            aria-hidden
          />
          <div className="relative flex flex-col items-stretch gap-4 sm:flex-row sm:flex-wrap sm:items-center sm:justify-center sm:gap-5">
            {actions.map((action) => (
              <ActionButton
                key={action.href}
                label={action.label}
                href={action.href}
              />
            ))}
          </div>
        </div>

        <p className="mt-10 text-base text-white/80 md:mt-12 md:text-lg">
          ¿Qué deseas hacer?
        </p>
      </div>
    </section>
  );
}
