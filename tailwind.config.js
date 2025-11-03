/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './templates/**/*.html', // Scan the top-level templates dir (for allauth)
    './store/templates/**/*.html',
    './services/templates/**/*.html', // Add other apps if they exist
    // Add any other paths that contain Tailwind classes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}