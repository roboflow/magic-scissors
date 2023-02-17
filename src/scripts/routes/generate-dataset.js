const page = require("page");

module.exports = function(state) {
    return function (ctx, next) {
        if(!state.apiKey || !state.workspace) {
            page("/");
            return;
        }

        var template = require("../../templates/generate-dataset.hbs");
        $("body").html(template({
            steps: [
                {
                    step: "Isolating Objects of Interest",
                    inProgress: true,
                },
                {
                    step: "Exporting Backgrounds",
                    inProgress: true
                },
                {
                    step: "Generating Images",
                    todo: true
                }
            ]
        }));
    };
};