/*jshint esversion:6*/

const $ = require("jquery");
const page = require("page");
const swal = require("sweetalert2");
const _ = require("lodash");

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

    page("/", function (ctx, next) {
        var template = require("../templates/homepage.hbs");
        $("body").html(template());

        var error = function(message) {
            $('#errorMessage').html("Error: " + message).removeClass("hidden");
            return false;
        };

        var setLoading = function(loading) {
            if(loading) {
                $('#submitButtonContainer').addClass("hidden");
                $('#loadingContainer').removeClass("hidden");
            } else {
                $('#submitButtonContainer').removeClass("hidden");
                $('#loadingContainer').addClass("hidden");
            }
        };

        var validateApiKey = function(apiKey) {
            return new Promise(function(resolve, reject) {
                setLoading(true);
                setTimeout(function() {
                    setLoading(false);
                    resolve(false);
                }, 1000);
            });
        };

        $("#apiKeyForm").keydown(function() {
            $('#errorMessage').html("").addClass("hidden");
        });

        $("#apiKeyForm").submit(function (e) {
            e.preventDefault();
            e.stopPropagation();

            var apiKey = $('#apiKey').val();
            console.log('apiKey', apiKey);

            // if empty, return error
            if (!apiKey) return error("API key is required");

            // if not letters and numbers, return error
            if (!/^[a-zA-Z0-9]+$/.test(apiKey)) return error("API key is malformed. It should only contain letters and numbers.");

            validateApiKey(apiKey).then(function(isValid) {
                if(!isValid) return error("API key is invalid.");
            });

            return false;
        });
    });

    page.start();
});
