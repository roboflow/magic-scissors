const page = require("page");

module.exports = function(state) {
    return function (ctx, next) {
        var template = require("../../templates/homepage.hbs");
        $("body").html(template({
            apiKey: state.apiKey
        }));

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

            var apiKey = $('#apiKey').val();
            state.apiKey = apiKey;

            // if empty, return error
            if (!apiKey) return error("API key is required");

            // if not letters and numbers, return error
            if (!/^[a-zA-Z0-9]+$/.test(apiKey)) return error("API key is malformed. It should only contain letters and numbers.");

            setLoading(true);
            validateApiKey(apiKey).then(function(response) {
                state.workspace = response.workspace;
                _.setItem("magic-scissors-api-key", apiKey);
                page("/choose-project");
            }).catch(function(e) {
                console.log(e);
                setLoading(false);
                error("API key is invalid.");
            });

            return false;
        });
    }
};