const page = require("page");
const _ = require("lodash");

module.exports = function(state) {
    return function (ctx, next) {
        if(!state.apiKey || !state.workspace) {
            page("/");
            return;
        }

        $.get("https://api.roboflow.com/" + state.workspace, {
            api_key: state.apiKey,
            cacheBuster: Math.random()
        }, "JSON").then(function(response) {
            var projects = _.chain(response.workspace.projects).map(function(p) {
                if(!p.type) p.type = "object-detection";

                if(p.type == "classsification") return null;
                // if(!p.images) return null;

                return p;
            }).filter().value();

            var error = function(message) {
                $('#errorMessage').html("Error: " + message).removeClass("hidden");
                return false;
            };

            var template = require("../../templates/choose-destination.hbs");
            $("body").html(template({
                projects: projects
            }));

            $("#projectSelectForm").submit(function (e) {
                e.preventDefault();
                e.stopPropagation();
    
                // if they selected a project, use it
                // otherwise fall back to what they entered in the text field
                var selectedProject = $("input[name='project']:checked").val();
                var selectedWorkspace = state.workspace;
                if(!selectedProject) {
                    var universeProject = $('#universeProject').val();
                    // if it's a valid URL matching https://universe.roboflow.com/:workspace/:project**, extract the project ID
                    var matches = universeProject.match(/https:\/\/universe\.roboflow\.com\/([^\/]+)\/([^\/]+).*/);
                    if(matches) {
                        selectedWorkspace = matches[1];
                        selectedProject = matches[2];
                    } else {
                        return error("Please enter a valid project URL.");
                    }
                }
    
                if(!selectedProject) return error("Please select a project or enter a project URL.");

                state.backgrounds = {
                    workspace: selectedWorkspace,
                    project: selectedProject
                };

                page("/output-settings");

                return false;
            });
        });
    }
};