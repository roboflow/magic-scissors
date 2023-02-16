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
    }
};