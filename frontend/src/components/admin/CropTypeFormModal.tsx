"use client";

import { useState, useEffect } from "react";
import {
  CROP_TYPE_FIELD_COUNT,
  CROP_TYPE_FORM_SECTIONS,
  emptyCropTypeForm,
  type CropTypeFieldKey,
} from "@/lib/crop-type-fields";
import { createCropType, updateCropType } from "@/lib/api";

type CropTypeFormModalProps = {
  open: boolean;
  mode: "create" | "edit";
  editData?: any;
  onClose: (refresh?: boolean) => void;
};

export function CropTypeFormModal({
  open,
  mode,
  editData,
  onClose,
}: CropTypeFormModalProps) {
  const [values, setValues] = useState(emptyCropTypeForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (open && mode === "edit" && editData) {
      const formValues = { ...emptyCropTypeForm } as Record<CropTypeFieldKey, string>;
      
      for (const key in formValues) {
        const value = (editData as any)[key];
        if (value !== undefined && value !== null) {
          formValues[key as CropTypeFieldKey] = String(value);
        }
      }
      setValues(formValues);
    } else if (open && mode === "create") {
      setValues(emptyCropTypeForm);
    }
    setError("");
  }, [open, mode, editData]);

  if (!open) return null;

  const setField = (key: CropTypeFieldKey, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Convertir valores a números donde corresponda
      const payload: any = {};
      for (const key of Object.keys(values) as CropTypeFieldKey[]) {
        const value = values[key];
        if (value === "") continue;
        // Convertir números
        if (key !== "name") {
          payload[key] = parseFloat(value);
        } else {
          payload[key] = value;
        }
      }

      if (mode === "create") {
        await createCropType(payload);
      } else if (editData?.id) {
        await updateCropType(editData.id, payload);
      }
      
      onClose(true);
    } catch (err: any) {
      setError(err.message || "Error al guardar el tipo de cultivo");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/70"
        aria-label="Cerrar"
        onClick={() => onClose(false)}
      />
      <div className="relative flex max-h-[90vh] w-full max-w-4xl flex-col rounded-2xl border border-white/10 bg-[#141414] shadow-cultiva-glow-sm">
        <div className="border-b border-white/10 px-6 py-4">
          <h3 className="text-lg font-semibold text-white">
            {mode === "create" ? "Crear tipo de cultivo" : "Editar tipo de cultivo"}
          </h3>
          <p className="mt-1 text-sm text-white/50">
            {CROP_TYPE_FIELD_COUNT} parámetros del modelo
          </p>
        </div>

        <form className="overflow-y-auto px-6 py-5" onSubmit={handleSubmit}>
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
                        value={values[field.key] ?? ""}
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

          {error && (
            <div className="mt-4 text-center text-sm text-red-400">{error}</div>
          )}

          <div className="sticky bottom-0 mt-6 flex justify-end gap-3 border-t border-white/10 bg-[#141414] pt-4">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="rounded-full border border-white/20 px-5 py-2 text-sm text-white hover:bg-white/5"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-full bg-cultiva-green px-6 py-2 text-sm font-semibold text-cultiva-dark hover:scale-105 disabled:opacity-50"
            >
              {loading ? "Guardando..." : mode === "create" ? "Crear tipo" : "Guardar cambios"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}