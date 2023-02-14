var colors = require("tailwindcss/colors");

module.exports = {
    mode: "jit",
    important: true,
    purge: {
        layers: ["components", "utilities"],
        content: [
            "./src/**/*.html",
            "./src/**/*.js",
            "./src/**/*.jsx",
            "./src/**/*.ts",
            "./src/**/*.hbs",
            "./src/**/*.scss",
            "./src/styles/safelist.txt"
        ],
        options: {
            safelist: [/^:/]
        }
    },
    darkMode: false, // or 'media' or 'class'
    theme: {
        extend: {
            colors: {
                "purboflow": {
                    50: "#F2E6FE",
                    100: "#E2C8FE",
                    200: "#C28DFC",
                    300: "#A351FB",
                    400: "#8315F9",
                    500: "#6706CE",
                    DEFAULT: "#6706CE",
                    600: "#5905B3",
                    700: "#4D049A",
                    800: "#3D037B",
                    900: "#2C005B"
                },
                "aquavision": {
                    100: "#CFFFF6",
                    300: "#8AFFE8",
                    500: "#00FFCE",
                    DEFAULT: "#00FFCE",
                    700: "#00EBBE",
                    900: "#00C29D"
                }
            },
            fontFamily: {
                sans: [
                    "Inter",
                    "-apple-system",
                    "BlinkMacSystemFont",
                    "Segoe UI",
                    "Roboto",
                    "Helvetica Neue",
                    "Arial",
                    "Noto Sans",
                    "sans-serif",
                    "Apple Color Emoji",
                    "Segoe UI Emoji",
                    "Segoe UI Symbol",
                    "Noto Color Emoji"
                ]
            }
        }
    }
};
