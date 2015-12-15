define([
    "pat-registry",
    "jquery.placeholder"
], function(patterns) {
    var pattern_spec = {
        name: "placeholder",
        trigger: ":input[placeholder]",

        init: function($el) {
            return $el.placeholder();
        }
    };

    // This is slightly more accurate test than Modernizr uses.
    if (!("placeholder" in document.createElement("input") &&
          "placeholder" in document.createElement("textarea")))
        patterns.register(pattern_spec);
    return pattern_spec;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
