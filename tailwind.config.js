/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Django global templates
    './templates/**/*.html',

    // Django app templates inside the project
    './items/templates/**/*.html',

    // Safety net (covers any other templates inside the repo root)
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      keyframes: {
        // Subtle page fade-in (use on <main> or page sections)
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        // Common “fade up” for cards
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        // Slide in from left
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        // Slight scale pop for buttons/CTA
        btnPop: {
          '0%': { transform: 'scale(1)' },
          '60%': { transform: 'scale(1.03)' },
          '100%': { transform: 'scale(1)' },
        },
        // Skeleton shimmer (optional)
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 400ms ease-out both',
        'fade-in-up': 'fadeInUp 550ms cubic-bezier(0.16, 1, 0.3, 1) both',
        'slide-in-left': 'slideInLeft 450ms ease-out both',
        'btn-pop': 'btnPop 260ms ease-out both',
        'shimmer': 'shimmer 1.2s ease-in-out infinite',
      },
      // Optional: make duration/timing easier to reuse in transitions
      transitionTimingFunction: {
        'bounce-in': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
};

