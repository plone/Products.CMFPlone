/* pat-date-picker  - Polyfill for input type=date */
define([
    "underscore",
    "pat-parser",
    "pat-registry",
    "pat-base",
    "pikaday",
    "moment",
    "moment-timezone",
    "modernizr"
], function(_, Parser, registry, Base, Pikaday, moment, momenttimezone) {
    "use strict";
    var parser = new Parser("date-picker");
    parser.addArgument("behavior", "styled", ["native", "styled"]);
    parser.addArgument("week-numbers", [], ["show", "hide"]);
    parser.addArgument("i18n"); // URL pointing to JSON resource with i18n values
    /* JSON format for i18n
     * { "previousMonth": "Previous Month",
     *   "nextMonth"    : "Next Month",
     *   "months"       : ["January","February","March","April","May","June","July","August","September","October","November","December"],
     *   "weekdays"     : ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
     *   "weekdaysShort": ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
     * } */
    parser.addAlias("behaviour", "behavior");

    return Base.extend({
        name: "date-picker",
        trigger: ".pat-date-picker",
        init: function() {
            this.options = $.extend(this.options, parser.parse(this.$el));
            this.polyfill = this.options.behavior === "native";
            if (this.polyfill && Modernizr.inputtypes.date) {
                return;
            }
            if (this.$el.attr("type") === "date") {
                this.$el.attr("type", "text");
            }
            var config = {
                "field": this.$el[0],
                "minDate": this.$el.attr("min") ? moment(this.$el.attr("min")).toDate() : undefined,
                "maxDate": this.$el.attr("max") ? moment(this.$el.attr("max")).toDate() : undefined,
                "showWeekNumber": this.options.weekNumbers === "show",
                "onSelect": function () {
                    $(this._o.field).closest("form").trigger("input-change");
                }
            };
            if (this.options.i18n) {
                $.getJSON(this.options.i18n, 
                    function (data) {
                        config.i18n = data;
                        new Pikaday(config);
                    }
                );
            } else {
                new Pikaday(config);
            }
            return this.$el;
        }
    });
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
