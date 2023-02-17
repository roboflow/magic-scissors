const async = require("async");
const page = require("page");

const { getAuth, signInAnonymously } = require("firebase/auth");

module.exports = function(state) {
    return function (ctx, next) {
        if(!state.apiKey || !state.workspace) {
            page("/");
            return;
        }

        var progress = [
            {
                step: "Isolating Objects of Interest",
                inProgress: true,
                progress: {
                    percent: 0
                }
            },
            {
                step: "Exporting Backgrounds",
                inProgress: true,
                progress: {
                    percent: 0
                }
            },
            {
                step: "Generating Images",
                todo: true,
                progress: {
                    current: 0,
                    total: state.settings?.datasetSize || 100,
                    
                    percent: 0
                }
            }
        ];

        var diffDOM = require("diff-dom");
        var dd = new diffDOM.DiffDOM();

        var render = function() {
            var template = require("../../templates/generate-dataset.hbs");
            var newHtml = template({
                steps: progress
            });

            var elem = $("body")[0];
            var diff = dd.diff(elem, '<body>' + newHtml + "</body>");
            dd.apply(elem, diff);
        };

        const auth = getAuth();
        signInAnonymously(auth)
        .then((response) => {
            state.user = response.user;
            
            render();

            async.parallel([
                function(cb) {
                    // isolate objects of interest
                    var duration = 5000 + Math.random() * 5000;
                    var start = Date.now();
                    var interval = setInterval(function() {
                        var elapsed = Date.now() - start;
                        var percent = elapsed / duration;
                        if(percent > 1) percent = 1;
                        progress[0].progress.percent = Math.round(percent * 100);
                        render();
                        if(percent >= 1) {
                            progress[0].inProgress = false;
                            progress[0].completed = true;
                            clearInterval(interval);
                            cb();
                        }
                    }, 250);
                },
                function(cb) {
                    // generate backgrounds
                    var duration = 2000 + Math.random() * 2000;
                    var start = Date.now();
                    var interval = setInterval(function() {
                        var elapsed = Date.now() - start;
                        var percent = elapsed / duration;
                        if(percent > 1) percent = 1;
                        progress[1].progress.percent = Math.round(percent * 100);
                        render();
                        if(percent >= 1) {
                            progress[1].inProgress = false;
                            progress[1].completed = true;
                            clearInterval(interval);
                            cb();
                        }
                    }, 250);
                }
            ], function() {
                // generate images
                progress[2].todo = false;
                progress[2].inProgress = true;
                render();
            });
        });
    };
};