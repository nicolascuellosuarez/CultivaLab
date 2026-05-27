"use client";

import { useState } from "react";
import {
  CROP_TYPE_FIELD_COUNT,
  CROP_TYPE_FORM_SECTIONS,
  emptyCropTypeForm,
  type CropTypeFieldKey,
} from "@/lib/crop-type-fields";

type CropTypeFormModalProps = {
  open: boolean;
  mode: "create" | "edit";
  onClose: () => void;
};

export function CropTypeFormModal({
  open,
  mode,
  onClose,
}: CropTypeFormModalProps) {
  const [values, setValues] = useState(emptyCropTypeForm);

  if (!open) return null;

  const setField = (key: CropTypeFieldKey, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/70"
        aria-label="Cerrar"
        onClick={onClose}
      />
      <div className="relative flex max-h-[90vh] w-full max-w-4xl flex-col rounded-2xl border border-white/10 bg-[#141414] shadow-cultiva-glow-sm">
        <div className="border-b border-white/10 px-6 py-4">
          <h3 className="text-lg font-semibold text-white">
            {mode === "create" ? "Crear tipo de cultivo" : "Editar tipo de cultivo"}
          </h3>
          <p className="mt-1 text-sm text-white/50">
            {CROP_TYPE_FIELD_COUNT} parámetros del modelo · sin conexión API aún
          </p>
        </div>

        <form
          className="overflow-y-auto px-6 py-5"
          onSubmit={(e) => e.preventDefault()}
        >
          <div className="space-y-8">
            {CROP_TYPE_FORM_SECTIONS.map((section) => (
              <fieldset key={section.title}>
                <legend className="mb-4 text-sm font-semibold text-cultiva-green">
                  {section.title}
                </legend>
                <div className="grid gap-4 sm:grid-cols-2">
                  {section.fields.map((field) => (
                    <div
                      key={field.key}
                      className={field.key === "name" ? "sm:col-span-2" : ""}
                    >
                      <label
                        htmlFor={field.key}
                        className="mb-1.5 block text-xs font-medium text-white/55"
                      >
                        {field.label}
                      </label>
                      <input
                        id={field.key}
                        name={field.key}
                        type={field.type === "text" ? "text" : "number"}
                        step={field.type !== "integer" ? field.step ?? "any" : "1"}
                        min={field.type === "integer" ? "0" : undefined}
                        required={field.key === "name"}
                        value={values[field.key]}
                        onChange={(e) => setField(field.key, e.target.value)}
                        placeholder={field.placeholder}
                        className="cultiva-input w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm text-white outline-none focus:border-cultiva-green/40"
                      />
                    </div>
                  ))}
                </div>
              </fieldset>
            ))}
          </div>

          <div className="sticky bottom-0 mt-6 flex justify-end gap-3 border-t border-white/10 bg-[#141414] pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-full border border-white/20 px-5 py-2 text-sm text-white hover:bg-white/5"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="rounded-full bg-cultiva-green px-6 py-2 text-sm font-semibold text-cultiva-dark hover:scale-105"
            >
              {mode === "create" ? "Crear tipo" : "Guardar cambios"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
