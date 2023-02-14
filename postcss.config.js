module.exports = {
    ident: "postcss",
    plugins: {
        "postcss-import": {},
        "tailwindcss": {},
        "postcss-nested": {},
        "postcss-focus-visible": {},
        "autoprefixer": {}
    },
    cacheInclude: [/.*\.(css|scss|hbs)$/, /.tailwind\.config\.js$/]
};
