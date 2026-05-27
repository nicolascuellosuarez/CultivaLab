import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cultiva: {
          green: "#5FA11B",
          dark: "#0A0A0A",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        "cultiva-glow": "0 0 80px 20px rgba(95, 161, 27, 0.35)",
        "cultiva-glow-sm": "0 0 40px 10px rgba(95, 161, 27, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;