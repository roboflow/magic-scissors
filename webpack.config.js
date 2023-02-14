/*jshint esversion:6*/

const path = require("path");
const webpack = require("webpack");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const LiveReloadPlugin = require("webpack-livereload-plugin");
var HtmlWebpackTagsPlugin = require("html-webpack-tags-plugin");

const _ = require("lodash");

var dev = process.env.WEBPACK_ENV == "dev";

var plugins = [
    new CleanWebpackPlugin({
        cleanOnceBeforeBuildPatterns: [
            "**/*",
            "!files/**",
            "!scripts/**",
            "!images/**",
            "!maintenance/**",
            "!*.html",
            "!robots.txt",
            "!favicon.ico"
        ]
    }),
    new HtmlWebpackPlugin({
        template: "src/index.html",
        cache: false
    })
];

if (dev) {
    plugins.push(
        new HtmlWebpackTagsPlugin({
            tags: ["http://localhost:35729/livereload.js"],
            append: false,
            publicPath: false
        })
    );

    plugins.push(new LiveReloadPlugin());
}

plugins.push(
    new MiniCssExtractPlugin({
        filename: "[name].[contenthash].css",
        chunkFilename: "[name].[contenthash].css",
        ignoreOrder: true
    })
);

plugins.push(
    // Ignore all locale files of moment.js
    new webpack.IgnorePlugin({ resourceRegExp: /\.\/locale$/ })
);

module.exports = {
    mode: dev ? "development" : "production",
    devtool: dev ? "eval-source-map" : "nosources-source-map",
    optimization: {
        minimize: !dev,
        runtimeChunk: "single",
        splitChunks: {
            chunks: "all"
        }
    },
    resolve: {
        fallback: {
            fs: false,
            Buffer: false
        },
        extensions: [".tsx", ".ts", ".js"]
    },
    entry: {
        customer: [
            path.resolve(__dirname, "src/scripts/main.js"),
            path.resolve(__dirname, "src/styles/_main.scss")
        ]
    },
    module: {
        rules: [
            {
                test: /\.hbs$/,
                loader: "handlebars-loader",
                options: {
                    helperDirs: [__dirname + "/src/scripts/helpers"]
                }
            },
            {
                test: /\.s?css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            publicPath: "../"
                        }
                    },
                    "css-loader",
                    "postcss-loader"
                ]
            },
            {
                test: /\.tsx?$/,
                use: [
                    {
                        loader: "ts-loader",
                        options: {
                            logInfoToStdOut: true,
                            transpileOnly: true
                        }
                    }
                ],
                exclude: [/node_modules/, /dist/]
            },
            {
                test: /\.jsx$/,
                loader: "babel-loader",
                exclude: /node_modules/
            }
        ]
    },
    plugins: plugins,
    output: {
        filename: "[name].[contenthash].js",
        path: path.resolve(__dirname, "dist"),
        publicPath: "/"
    }
};
