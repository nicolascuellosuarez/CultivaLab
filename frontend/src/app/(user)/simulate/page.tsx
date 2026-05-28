import { Suspense } from "react";
import { SimulateForm } from "./SimulateForm";

export default function SimulatePage() {
  return (
    <Suspense fallback={<p className="text-white/50">Cargando...</p>}>
      <SimulateForm />
    </Suspense>
  );
}
