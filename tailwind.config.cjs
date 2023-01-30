const config = {
    mode: 'jit',
    content: ['./falert/frontend/**/*.{html,js,svelte,ts}'],

    theme: {
        extend: {},
    },

    plugins: [
        require("@tailwindcss/typography"),
        require('daisyui'),
    ],
};

module.exports = config;
