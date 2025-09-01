/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "system-ui",
          "sans-serif",
        ],
        mono: ["SF Mono", "Monaco", "Cascadia Code", "monospace"],
      },
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3370ff",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
        },
      },
      width: {
        70: "17.5rem", // 280px
        15: "3.75rem", // 60px
        35: "8.75rem", // 140px
        50: "12.5rem", // 200px
      },
      height: {
        15: "3.75rem", // 60px
        35: "8.75rem", // 140px
        50: "12.5rem", // 200px
      },
      minHeight: {
        15: "3.75rem", // 60px
        35: "8.75rem", // 140px
        50: "12.5rem", // 200px
      },
      maxHeight: {
        30: "7.5rem", // 120px
        35: "8.75rem", // 140px
      },
      padding: {
        15: "3.75rem", // 60px
        35: "8.75rem", // 140px
        50: "12.5rem", // 200px
      },
      animation: {
        pulse: "pulse 2s infinite",
        spin: "spin 1s linear infinite",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
  ],
};
