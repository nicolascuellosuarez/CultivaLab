export function SiteFooter() {
  return (
    <footer className="fixed inset-x-0 bottom-0 z-40 bg-transparent px-6 pb-6 pt-4 md:px-10 md:pb-8">
      <div className="relative mx-auto flex min-h-[3.5rem] max-w-7xl flex-col items-center justify-end gap-3 sm:block sm:min-h-[2.5rem]">
        <p className="text-center text-sm text-white/70 md:text-base">
          Desarrollado por Nicolás Cuello - 2025
        </p>
        <p className="text-center text-xs text-white/55 sm:absolute sm:bottom-0 sm:right-0 sm:max-w-xs sm:text-right sm:text-sm">
          Software de Uso Exclusivamente académico
        </p>
      </div>
    </footer>
  );
}