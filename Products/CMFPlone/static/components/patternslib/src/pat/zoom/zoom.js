define([
    "jquery",
    "pat-registry",
    "pat-parser"
], function($, patterns, Parser) {
    var parser = new Parser("zoom");

    parser.addArgument("min", 0);
    parser.addArgument("max", 2);

    var zoom = {
        name: "zoom",
        trigger: ".pat-zoom",

        init: function($el, opts) {
            return $el.each(function() {
                var $block = $(this),
                    options = parser.parse($block, opts),
                    $slider,
                    events;
                $slider=$("<input/>", {type: "range", step: "any", value: 1,
                                       min: options.min, max: options.max});

                if ("oninput" in window) {
                    events = "change input";
                } else {
                    events = "change propertychange";
                }
                $slider
                    .insertBefore($block)
                    .on(events, null, $block, zoom.onZoom);
            });
        },

        onZoom: function(event) {
            var $block=event.data;
            $block.css("zoom", this.value);
        }
    };

    patterns.register(zoom);
    return zoom;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 sts=4 expandtab
