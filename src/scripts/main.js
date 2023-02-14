/*jshint esversion:6*/

const $ = require("jquery");
const page = require("page");
const swal = require("sweetalert2");
const _ = require("lodash");

var workspace, apiKey;

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
                $.post("https://api.roboflow.com/", {
                    api_key: apiKey
                }, "JSON").then(function(response) {
                    if(!response || !response.workspace) {
                        reject(response);
                    } else {
                        resolve(response);
                    }
                }).catch(function(e) {
                    reject(e);
                });
            });
        };

        $("#apiKeyForm").keydown(function() {
            $('#errorMessage').html("").addClass("hidden");
        });

        $("#apiKeyForm").submit(function (e) {
            e.preventDefault();
            e.stopPropagation();

            apiKey = $('#apiKey').val();
            console.log('apiKey', apiKey);

            // if empty, return error
            if (!apiKey) return error("API key is required");

            // if not letters and numbers, return error
            if (!/^[a-zA-Z0-9]+$/.test(apiKey)) return error("API key is malformed. It should only contain letters and numbers.");

            setLoading(true);
            validateApiKey(apiKey).then(function(response) {
                workspace = response.workspace;
                $('body').html(workspace);
            }).catch(function() {
                setLoading(false);
                error("API key is invalid.");
            });

            return false;
        });
    });

    page.start();
});
