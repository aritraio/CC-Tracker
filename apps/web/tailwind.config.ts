import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#F0F0F0',
        ink: '#121212',
        paper: '#FFFFFF',
        muted: '#E0E0E0',
        bauhaus: {
          red: '#D02020',
          'red-hover': '#B81B1B',
          blue: '#1040C0',
          'blue-hover': '#0C3299',
          yellow: '#F0C020',
          'yellow-hover': '#D9AC1A',
          'yellow-light': '#FFF9C4',
          green: '#008844',
        },
      },
      fontFamily: {
        sans: ['var(--font-outfit)', 'Outfit', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
      borderWidth: {
        '2': '2px',
        '3': '3px',
        '4': '4px',
        '6': '6px',
        '8': '8px',
      },
      boxShadow: {
        'bauhaus-xs': '2px 2px 0px 0px #121212',
        'bauhaus-sm': '4px 4px 0px 0px #121212',
        'bauhaus-md': '6px 6px 0px 0px #121212',
        'bauhaus-lg': '8px 8px 0px 0px #121212',
        'bauhaus-xl': '12px 12px 0px 0px #121212',
        'bauhaus-red': '4px 4px 0px 0px #D02020',
        'bauhaus-yellow': '4px 4px 0px 0px #F0C020',
      },
      borderRadius: {
        none: '0px',
        full: '9999px',
      },
    },
  },
  plugins: [],
};

export default config;
