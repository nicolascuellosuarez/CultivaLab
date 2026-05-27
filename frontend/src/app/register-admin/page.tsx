import Link from "next/link";
import { FormFieldRow } from "@/components/FormFieldRow";
import { PageShell } from "@/components/PageShell";

export default function RegisterAdminPage() {
  return (
    <PageShell glowVariant="register-admin">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 pb-32 pt-24 md:px-10 md:pt-28 lg:px-12">
        <div className="mb-6 flex items-center gap-2.5">
          <span
            className="h-2.5 w-2.5 shrink-0 rounded-full bg-cultiva-green shadow-[0_0_12px_rgba(95,161,27,0.8)]"
            aria-hidden
          />
          <span className="text-sm font-medium text-white md:text-base">
            Registro de Administrador
          </span>
        </div>

        <h1 className="max-w-3xl text-3xl font-bold leading-tight tracking-tight text-white sm:text-4xl md:text-5xl lg:text-[3.25rem]">
          ¡Bienvenido, Administrador del Laboratorio!
        </h1>

        <p className="mt-5 max-w-2xl text-base leading-relaxed text-white/85 md:text-lg">
          Ingresa un usuario, contraseña y la llave de acceso maestra para
          crear la cuenta de administrador
        </p>

        <form className="relative mt-12 space-y-8 md:mt-1 md:space-y-10">
          <div
            className="pointer-events-none absolute -left-8 top-1/2 h-40 w-full max-w-xl -translate-y-1/2 rounded-full bg-cultiva-green/20 blur-3xl"
            aria-hidden
          />

          <div className="relative space-y-8 md:space-y-10">
            <FormFieldRow
              label="Usuario"
              htmlFor="username"
              placeholder="ej. admin_lab"
            />
            <FormFieldRow
              label="Contraseña"
              htmlFor="password"
              type="password"
              placeholder="Mínimo 8 caracteres"
            />
            <FormFieldRow
              label="Llave maestra"
              htmlFor="admin_key"
              type="password"
              placeholder="Llave de acceso maestra del administrador"
              autoComplete="off"
            />
          </div>

          <div className="relative flex w-full justify-center pt-4">
            <div
              className="pointer-events-none absolute inset-x-0 top-1/2 h-24 -translate-y-1/2 rounded-full bg-cultiva-green/25 blur-2xl"
              aria-hidden
            />
            <button
              type="submit"
              className="relative inline-flex items-center justify-center rounded-full bg-cultiva-green px-7 py-2.5 text-sm font-semibold text-cultiva-dark shadow-cultiva-glow-sm transition-all duration-200 hover:scale-105 hover:shadow-cultiva-glow"
            >
              Registrar administrador
            </button>
          </div>
        </form>

        <p className="mt-10 text-sm text-white/60">
          ¿Ya tienes cuenta?{" "}
          <Link
            href="/login"
            className="font-medium text-cultiva-green underline-offset-4 hover:underline"
          >
            Iniciar sesión
          </Link>
        </p>
      </section>
    </PageShell>
  );
}
