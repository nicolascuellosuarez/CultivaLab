import { CultivaLogo } from "./CultivaLogo";

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 bg-transparent">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 md:px-10">
        <div className="flex items-center gap-3">
          <CultivaLogo className="h-9 w-9 shrink-0" />
          <span className="text-lg font-semibold tracking-tight text-white md:text-xl">
            CultivaLab
          </span>
        </div>

        <span className="rounded-full border border-[#F5F5F5] bg-transparent px-4 py-2 text-sm font-medium text-[#F5F5F5] md:px-5 md:py-2.5 md:text-base">
          Agricultura de Precisión
        </span>
      </div>
    </header>
  );
}
