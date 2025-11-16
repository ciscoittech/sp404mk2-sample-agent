/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Tailwind v4 reads colors from @theme block in globals.css
      // No need to define colors here with OKLCH values
    },
  },
  plugins: [],
}
