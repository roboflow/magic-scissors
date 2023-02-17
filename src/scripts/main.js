/*jshint esversion:6*/

const $ = require("jquery");
const page = require("page");
const swal = require("sweetalert2");
const _ = require("lodash");

const state = {
    workspace: null,
    apiKey: null
};

$(function () {
    window.$ = $;

    _.mixin({
        getItem: function (k) {
            try {
                return localStorage.getItem(k);
            } catch (e) {
                return localStorageFallback[k] || null;
            }
        },
        setItem: function (k, v) {
            try {
                localStorage.setItem(k, v);
            } catch (e) {
                localStorageFallback[k] = v;
            }
        },
        removeItem: function (k) {
            try {
                localStorage.removeItem(k);
            } catch (e) {
                delete localStorageFallback[k];
            }
        },
        clear: function () {
            try {
                localStorage.clear();
            } catch (e) {
                localStorageFallback = {};
            }
        }
    });

    var apiKey = _.getItem("magic-scissors-api-key");
    if(apiKey) {
        state.apiKey = apiKey;
    }

    var loading = function(ctx, next) {
        $('body').html(require("../templates/loading.hbs")());
        setTimeout(function() {
            next();
        }, 0);
    };

    page("/", require(__dirname + "/routes/homepage.js")(state));
    page("/choose-project", loading, require(__dirname + "/routes/choose-project.js")(state));
    page("/choose-backgrounds", loading, require(__dirname + "/routes/choose-backgrounds.js")(state));
    page("/output-settings", require(__dirname + "/routes/output-settings.js")(state));
    page("/generate-dataset", loading, require(__dirname + "/routes/generate-dataset.js")(state));

    page.start();
});
