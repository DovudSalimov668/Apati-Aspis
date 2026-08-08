/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#F7F8FA',
        surface: '#FFFFFF',
        border: '#E2E5EA',
        textPrimary: '#14181F',
        textSecondary: '#5B6472',
        brand: {
          50: '#EEF4FF',
          500: '#2F5EFF',
          600: '#2447D6',
          700: '#1B36A8',
        },
        riskLow: {
          text: '#1C8A5B',
          bg: '#E7F7EF',
        },
        riskMod: {
          text: '#B9821A',
          bg: '#FFF4DF',
        },
        riskHigh: {
          text: '#D14343',
          bg: '#FDEAEA',
        },
        riskCrit: {
          text: '#8F1E3B',
          bg: '#F7E3E9',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
