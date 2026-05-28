import React from "react";

type FormFieldRowProps = {
  label: string;
  htmlFor: string;
  type?: "text" | "password";
  placeholder: string;
  autoComplete?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
};

export function FormFieldRow({
  label,
  htmlFor,
  type = "text",
  placeholder,
  autoComplete,
  value,
  onChange,
  disabled
}: FormFieldRowProps) {
  const resolvedAutoComplete =
    autoComplete ?? (type === "password" ? "new-password" : "username");
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-5">
      <label
        htmlFor={htmlFor}
        className="shrink-0 rounded-full border border-cultiva-green bg-transparent px-6 py-3.5 text-center text-sm font-semibold text-cultiva-green shadow-cultiva-glow-sm sm:min-w-[200px] sm:px-8 sm:py-4 sm:text-base"
      >
        {label}
      </label>
      <input
        id={htmlFor}
        name={htmlFor}
        type={type}
        placeholder={placeholder}
        autoComplete={resolvedAutoComplete}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="cultiva-input w-full rounded-full border border-white/10 bg-white/[0.04] px-6 py-3.5 text-base text-white outline-none transition-colors placeholder:text-white/25 focus:border-cultiva-green/40 focus:bg-white/[0.06] sm:py-4"
      />
    </div>
  );
}
