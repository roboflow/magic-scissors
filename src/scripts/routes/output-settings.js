const page = require("page");

require("ion-rangeslider");
require(__dirname + "/../../../node_modules/ion-rangeslider/css/ion.rangeSlider.min.css");

module.exports = function(state) {
    return function (ctx, next) {
        // if(!state.apiKey || !state.workspace) {
        //     page("/");
        //     return;
        // }

        var template = require("../../templates/output-settings.hbs");
        $("body").html(template({
            state: state
        }));

        var exponential = function(pow, shouldRound) {
            return function(n) {
                // current position
                var position = (n / this.max);

                // exponential easing
                var modified = Math.pow(position, pow);

                var output = this.min + Math.round(modified * (this.max - this.min));
                if(!shouldRound) return output;

                var rounded = output > 10 ? Math.round(output / 10) * 10 : output;
                if(rounded < this.min) rounded = this.min;

                return rounded;
            }
        };

        $("#outputSize").ionRangeSlider({
            min: 1,
            max: 1000,
            from: 500,
            skin: "round",
            prettify: exponential(2, true)
        });

        $("#objectsPerImage").ionRangeSlider({
            min: 1,
            max: 50,
            from: 1,
            to: 10,
            step: 1,
            skin: "round",
            type: "double",
            drag_interval: true,
            prettify: exponential(1.5, false)
        });

        $("#objectSizeVariance").ionRangeSlider({
            min: 0,
            max: 2,
            from: 0.89,
            to: 1.105,
            step: 0.01,
            skin: "round",
            type: "double",
            drag_interval: true,
            prettify: function(n, raw) {
                // raw = true;

                // hack because pixels don't have enough resolution to get to a +10% default
                if(n == 1.1) n = 1.105;

                // current position
                var position = n;
                var midpoint = (this.min + this.max)/2 + this.min;

                if(position == this.min) return raw ? 0.1 : "10x Smaller";
                if(position == this.max) return raw ? 10 : "10x Larger";
                if(position == midpoint) return raw ? 1 : "No Change";

                var suffix, modified, rounded;
                if(position < midpoint) {
                    // smaller
                    suffix = "Smaller";
                    modified = position * 9/10 + 0.1;
                    
                    if(raw) return Math.round(modified*100)/100;

                    rounded = Math.round((1-modified)*100);
                    if(rounded == 0) return "No Change";
                    if(rounded < 50) return rounded + "% " + suffix;
                    return Math.round(1/modified*10)/10 + "x Smaller";
                } else if(position > midpoint) {
                    // larger
                    suffix = "Larger";
                    position -= 1;

                    modified = position * position * 9;

                    if(raw) return Math.round((1+modified)*100)/100;
                    rounded = Math.round(modified * 100);
                    if(rounded == 0) return "No Change";
                    if(rounded < 100) return rounded + "% " + suffix;
                    return (1+Math.round(modified*10)/10) + "x";
                }

                // should never get here
                return "No Change";
            }
        });

        $("#outputSettingsForm").submit(function (e) {
            e.preventDefault();
            e.stopPropagation();

            var ret = {};

            var slider;

            slider = $("#outputSize").data("ionRangeSlider");
            ret.datasetSize = slider.options.prettify(slider.result.from, true);

            slider = $("#objectsPerImage").data("ionRangeSlider");
            ret.objectsPerImage = {
                min: slider.options.prettify(slider.result.from, true),
                max: slider.options.prettify(slider.result.to, true)
            };
            
            slider = $("#objectSizeVariance").data("ionRangeSlider");
            ret.sizeVariance = {
                min: slider.options.prettify(slider.result.from, true),
                max: slider.options.prettify(slider.result.to, true)
            };

            slider.options.prettify(slider.result.from, true)

            console.log(JSON.stringify(ret, null, 4));

            // page("/generate-dataset");

            return false;
        });
    }
};