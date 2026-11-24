/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        scientific: {
          950: '#03231e',
          900: '#063d34',
          800: '#0d574b',
          700: '#116e5f',
          600: '#178a77',
          500: '#1faa93',
          400: '#34d399',
          300: '#6ee7b7',
          200: '#a7f3d0',
          100: '#ccfbf1',
          50: '#f0fdf9',
        },
        ivory: {
          50: '#fdfdfc',
          100: '#f9faf8',
          200: '#f1f4f1',
          300: '#e5e9e5',
        },
        slate: {
          850: '#162032',
          950: '#090d16',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
