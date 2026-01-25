/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        surface: '#13131a',
        'surface-light': '#1a1a24',
        primary: {
          DEFAULT: '#3b82f6',
          foreground: '#ffffff',
        },
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        neutral: '#6b7280',
        border: '#27272a',
        input: '#27272a',
        ring: '#3b82f6',
        foreground: '#f9fafb',
        muted: {
          DEFAULT: '#27272a',
          foreground: '#9ca3af',
        },
        accent: {
          DEFAULT: '#1a1a24',
          foreground: '#f9fafb',
        },
        card: {
          DEFAULT: '#13131a',
          foreground: '#f9fafb',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
    },
  },
  plugins: [],
}
