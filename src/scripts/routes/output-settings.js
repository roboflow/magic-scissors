const page = require("page");

require("ion-rangeslider");
require(__dirname + "/../../../node_modules/ion-rangeslider/css/ion.rangeSlider.min.css");

module.exports = function(state) {
    return function (ctx, next) {
        var template = require("../../templates/output-settings.hbs");
        $("body").html(template({
            state: state
        }));

        $("#outputSize").ionRangeSlider({
            min: 1,
            max: 1000,
            from: 500,
            skin: "round",
            prettify: function(n) {
                // current position
                var position = (n / this.max);

                // exponential easing
                var modified = position * position;

                var output = this.min + Math.round(modified * (this.max - this.min));
                var rounded = output > 10 ? Math.round(output / 10) * 10 : output;
                if(rounded < this.min) rounded = this.min;

                return rounded;
            }
        });

        $("#objectSizeVariance").ionRangeSlider({
            min: 0,
            max: 2,
            from: 0.89,
            to: 1.105,
            step: 0.01,
            skin: "round",
            type: "double",
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
                    
                    if(raw) return modified.toFixed(2);

                    rounded = Math.round((1-modified)*100);
                    if(rounded == 0) return "No Change";
                    if(rounded < 50) return rounded + "% " + suffix;
                    return Math.round(1/modified*10)/10 + "x Smaller";
                } else if(position > midpoint) {
                    // larger
                    suffix = "Larger";
                    position -= 1;

                    modified = position * position * 9;

                    if(raw) return (1+modified).toFixed(2);
                    rounded = Math.round(modified * 100);
                    if(rounded == 0) return "No Change";
                    if(rounded < 100) return rounded + "% " + suffix;
                    return (1+Math.round(modified*10)/10) + "x";
                }

                // should never get here
                return "No Change";
            }
        });
    }
};