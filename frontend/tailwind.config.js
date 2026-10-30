/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#f4f6f8",
        surface: "#ffffff",
        "surface-card": "#ffffff",
        "surface-card-hover": "#f8fafc",
        "surface-subtle": "#f1f5f9",
        border: "#e2e8f0",
        "border-subtle": "#cbd5e1",
        foreground: "#0f172a",
        brand: {
          teal: "#0a545c",
          spruce: "#083338",
          coral: "#e0533c",
          ochre: "#d97706",
          cyan: "#0891b2",
          blue: "#2563eb",
          light: "#e6f4f5",
        },
        risk: {
          fatal: "#dc2626",
          critical: "#b91c1c",
          warning: "#d97706",
          moderate: "#0284c7",
          safe: "#16a34a",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "Courier New", "monospace"]
      }
    },
  },
  plugins: [],
}
