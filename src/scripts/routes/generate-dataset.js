const async = require("async");
const page = require("page");
const _ = require("lodash");

const { getAuth, signInAnonymously } = require("firebase/auth");

module.exports = function (state) {
  return function (ctx, next) {
    if (!state.apiKey || !state.workspace) {
      page("/");
      return;
    }

    // window.state = state;

    var progress = [
      {
        step: "Isolating Objects of Interest",
        inProgress: true,
        progress: {
          percent: 0,
        },
      },
      {
        step: "Processing Backgrounds",
        inProgress: true,
        progress: {
          percent: 0,
        },
      },
      {
        step: "Zipping Objects of Interest",
        todo: true,
        progress: {
          percent: 0,
        },
      },
      {
        step: "Zipping Backgrounds",
        todo: true,
        progress: {
          percent: 0,
        },
      },
      {
        step: "Creating Synthetic Dataset",
        todo: true,
        // progress: {
        //     current: 0,
        //     total: state.settings?.datasetSize || 100,

        //     percent: 0
        // }
      },
    ];

    var diffDOM = require("diff-dom");
    var dd = new diffDOM.DiffDOM();

    var render = function () {
      var template = require("../../templates/generate-dataset.hbs");
      var newHtml = template({
        steps: progress,
      });

      var elem = $("body")[0];
      var diff = dd.diff(elem, "<body>" + newHtml + "</body>");
      dd.apply(elem, diff);
    };

    const auth = getAuth();
    signInAnonymously(auth).then((response) => {
      state.user = response.user;

      render();

      var generateDataset = function (index, identifier, getPreprocsAndAugs) {
        var project = state[identifier].project;
        return function (cb) {
          $.get(
            ["https://api.roboflow.com", project].join("/"),
            {
              api_key: state.apiKey,
              cacheBuster: Math.random(),
            },
            "JSON"
          ).then(function (response) {
            var [preprocs, augs] = getPreprocsAndAugs(response);

            var matchingVersion = _.find(response.versions, function (version) {
              // if an existing version has the same preprocs and augs, use it
              return (
                _.isEqual(version.preprocessing, preprocs) &&
                _.isEqual(version.augmentation, augs)
              );
            });

            if (matchingVersion) {
              // if most recent version has isolate objects, use that
              // TODO - ensure they haven't changed the preprocs / augs to verify we don't need to regen anyway
              state[identifier].version = matchingVersion.id.split("/").pop();
              progress[index].inProgress = false;
              progress[index].completed = true;
              cb(null);
            } else if (response.project) {
              // otherwise, generate one first then use that
              var getVersion = function (version) {
                return new Promise(function (resolve, reject) {
                  $.get(
                    ["https://api.roboflow.com", project, version].join("/"),
                    {
                      api_key: state.apiKey,
                      nocache: Math.random(),
                    },
                    "JSON"
                  ).then(function (response) {
                    if (!response || !response.version) {
                      setTimeout(function () {
                        getVersion(version).then(resolve).catch(reject);
                      }, 2500);
                      return;
                    }

                    if (
                      response &&
                      response.version &&
                      !response.version.generating
                    ) {
                      resolve();
                    } else {
                      var percent = response.version.progress * 100;
                      progress[index].inProgress = true;
                      progress[index].progress.current = Math.floor(
                        response.version.progress * response.version.images
                      );
                      progress[index].progress.total = response.version.images;
                      progress[index].progress.percent = Math.floor(percent);
                      render();

                      setTimeout(function () {
                        getVersion(version).then(resolve).catch(reject);
                      }, 500);
                    }
                  });
                });
              };

              $.ajax({
                url: [
                  "https://api.roboflow.com",
                  project,
                  "generate?api_key=" + state.apiKey,
                ].join("/"),
                dataType: "json",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                  preprocessing: preprocs,
                  augmentation: augs,
                }),
              }).then(function (response) {
                if (response && response.version) {
                  state[identifier].version = response.version;
                  getVersion(response.version).then(function () {
                    progress[index].inProgress = false;
                    progress[index].completed = true;
                    cb(null);
                  });
                }
              });
            }
          });
        };
      };

      var exportCOCO = function (index, identifier) {
        var project = state[identifier].project;
        var version = state[identifier].version;

        return function (cb) {
          var getExport = function () {
            return new Promise(function (resolve, reject) {
              $.get(
                ["https://api.roboflow.com", project, version, "coco"].join(
                  "/"
                ),
                {
                  api_key: state.apiKey,
                  nocache: Math.random(),
                },
                "JSON"
              ).then(function (response) {
                if (!response || !response.progress) {
                  setTimeout(function () {
                    getExport().then(resolve).catch(reject);
                  }, 2500);
                  return;
                }

                if (response.progress >= 1) {
                  resolve();
                } else {
                  var percent = 0;
                  if (response.version.progress) {
                    percent = response.version.progress * 100;
                  } else if (response.progress) {
                    percent = response.progress * 100;
                  }

                  progress[index].inProgress = true;
                  progress[index].progress.percent = Math.floor(percent);
                  render();

                  setTimeout(function () {
                    getExport().then(resolve).catch(reject);
                  }, 500);
                }
              });
            });
          };

          getExport().then(function () {
            progress[index].inProgress = false;
            progress[index].completed = true;
            cb(null);
          });
        };
      };

      async.parallel(
        [
          // isolate objects of interest
          generateDataset(0, "objectsOfInterest", function (response) {
            var preprocs = _.get(response, "project.preprocessing", {});
            preprocs.isolate = true;
            var augs = _.get(response, "project.augmentation", {});
            return [preprocs, augs];
          }),
          // generate backgrounds
          generateDataset(1, "backgrounds", function (response) {
            var preprocs = { "auto-orient": true };
            var augs = {};
            return [preprocs, augs];
          }),
        ],
        function () {
          async.parallel(
            [exportCOCO(2, "objectsOfInterest"), exportCOCO(3, "backgrounds")],
            function () {
              // generate images
              progress[4].todo = false;
              progress[4].inProgress = true;
              render();

              $.ajax({
                url: ["/python/go"].join("/"),
                dataType: "json",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                  apiKey: state.apiKey,
                  objectsOfInterest: [
                    state.objectsOfInterest.project,
                    state.objectsOfInterest.version,
                  ].join("/"),
                  backgrounds: [
                    state.backgrounds.project,
                    state.backgrounds.version,
                  ].join("/"),
                  destination: [state.destination.project].join("/"),
                  settings: state.settings,
                }),
              })
                .done(function (response) {
                  progress[4].inProgress = false;
                  progress[4].completed = true;
                  render();
                  // all done!
                })
                .fail(function (jqXHR, textStatus, errorThrown) {
                  progress[4].inProgress = false;
                  progress[4].failed = true;
                  render();
                  console.log("AJAX request failed: " + textStatus);
                });
            }
          );
        }
      );
    });
  };
};
