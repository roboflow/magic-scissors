const async = require("async");
const page = require("page");
const _ = require("lodash");

const { getAuth, signInAnonymously } = require("firebase/auth");

module.exports = function(state) {
    return function (ctx, next) {
        if(!state.apiKey || !state.workspace) {
            page("/");
            return;
        }

        // window.state = state;

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
                    $.get([
                        "https://api.roboflow.com",
                        state.objectsOfInterest.project
                    ].join("/"), {
                        api_key: state.apiKey,        
                        cacheBuster: Math.random()
                    }, "JSON").then(function(response) {
                        if(false && _.get(response, "versions[0].preprocessing.isolate", false)) {
                            // if most recent version has isolate objects, use that
                            // TODO - ensure they haven't changed the preprocs / augs to verify we don't need to regen anyway
                            state.objectsOfInterest.version = response.versions[0].id.split("/").pop();
                        } else if(response.project) {
                            // otherwise, generate one first then use that
                            var preprocs = _.get(response, "project.preprocessing", {});
                            preprocs.isolate = true;

                            var getVersion = function(version) {
                                return new Promise(function(resolve, reject) {
                                    $.get([
                                        "https://api.roboflow.com",
                                        state.objectsOfInterest.project,
                                        version
                                    ].join("/"), {
                                        api_key: state.apiKey,
                                        nocache: Math.random()
                                    }, "JSON").then(function(response) {
                                        if(!response || !response.version) {
                                            setTimeout(function() {
                                                getVersion(version).then(resolve).catch(reject);
                                            }, 2500);
                                            return;
                                        }

                                        if(response && response.version && !response.version.generating) {
                                            resolve();
                                        } else {
                                            var percent = response.version.progress * 100;
                                            progress[0].inProgress = true;
                                            progress[0].progress.current = Math.floor(response.version.progress * response.version.images);
                                            progress[0].progress.total = response.version.images;
                                            progress[0].progress.percent = Math.floor(percent);
                                            render();
                                            
                                            setTimeout(function() {
                                                getVersion(version).then(resolve).catch(reject);
                                            }, 500);
                                        }
                                    });
                                });
                            };
                            
                            $.ajax({
                                url: [
                                    "https://api.roboflow.com", state.objectsOfInterest.project, "generate?api_key=" + state.apiKey
                                ].join("/"),
                                dataType: 'json',
                                type: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({
                                    preprocessing: preprocs,
                                    augmentation: _.get(response, "project.augmentation", {})
                                })
                            }).then(function(response) {
                                if(response && response.version) {
                                    getVersion(response.version).then(function() {
                                        progress[0].inProgress = false;
                                        progress[0].completed = true;
                                        cb(null);
                                    });
                                }
                            });
                        }
                    });
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