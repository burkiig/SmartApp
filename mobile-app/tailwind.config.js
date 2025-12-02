/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./contexts/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5', // Indigo-600 (tasarımdaki mavi-mor)
        'primary-dark': '#4338CA', // Indigo-700
        'primary-light': '#EEF2FF', // Indigo-50
        secondary: '#8B5CF6', // Violet-500 (tasarımdaki mor)
        'secondary-light': '#F5F3FF', // Violet-50
        success: '#10B981', // Green-500
        'success-light': '#D1FAE5', // Green-100
        warning: '#F59E0B', // Amber-500
        'warning-light': '#FEF3C7', // Amber-100
        danger: '#EF4444', // Red-500
        late: '#F59E0B', // Amber-500 (Late durumu)
        present: '#10B981', // Green-500 (Present durumu)
        background: '#F9FAFB', // Gray-50
        card: '#FFFFFF',
      },
    },
  },
  plugins: [],
}

