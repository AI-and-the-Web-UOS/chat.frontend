/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/src/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily:{
        'poppins': ['Poppins', 'sans-serif']
      },
      backgroundColor: {
        customGray: '#2E2E2E',
        button: '#555555',
      },
      borderColor: {
        customInputGray: '#555555',
      },
    },
  },
  plugins: [],
}

