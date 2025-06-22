/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx,html}", // Adjust this to match your project structure
  ],
  theme: {
    extend: {
      backgroundImage: {
        'star-gradient': 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)',
        'star-grid': 'repeating-linear-gradient(135deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 40px), repeating-linear-gradient(45deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 40px)',
      },
      colors: {
        'cyber': '#00ffe0',
      },
    },
  },
  plugins: [],
}

