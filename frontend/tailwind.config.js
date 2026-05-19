/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#0f0f12',
          card: '#18181f',
          elevated: '#22222c',
          border: '#2e2e3a',
        },
        cream: {
          DEFAULT: '#f6f5f1',
          muted: '#eeede8',
          dark: '#e8e6e0',
        },
        ink: {
          DEFAULT: '#141414',
          muted: '#5c5c5c',
          faint: '#8a8a8a',
        },
        accent: {
          DEFAULT: '#2d6a4f',
          light: '#40916c',
          muted: '#1b4332',
          soft: '#d8f3dc',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 4px 24px -4px rgba(20, 20, 20, 0.08)',
        'soft-lg': '0 12px 40px -8px rgba(20, 20, 20, 0.12)',
        card: '0 2px 12px -2px rgba(20, 20, 20, 0.06)',
      },
      backgroundImage: {
        'hero-gradient':
          'radial-gradient(ellipse 90% 60% at 50% -10%, rgba(64, 145, 108, 0.12), transparent 70%)',
        'hero-gradient-dark':
          'radial-gradient(ellipse 90% 60% at 50% -10%, rgba(64, 145, 108, 0.18), transparent 70%)',
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
};
