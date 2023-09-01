/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {},
  },
  plugins: [],
  purge: {
    // ...
    options: {
      safelist: ["bg-red-500", "bg-green-500", "bg-blue-500", "bg-yellow-500"], // Add other dynamic classes here
    },
  },
};
