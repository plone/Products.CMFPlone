/**
 * Patterns forward - Forward click events
 *
 * Copyright 2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-parser",
    "pat-registry"
], function($, Parser, registry) {
    var parser = new Parser("forward");

    parser.addArgument("selector");

    var _ = {
        name: "forward",
        trigger: ".pat-forward",

        init: function($el, opts) {
            return $el.each(function() {
                var $el = $(this),
                    options = parser.parse($el, opts);

                if (!options.selector)
                    return;

                $el.on("click", null, options.selector, _._onClick);
            });
        },

        _onClick: function(event) {
            $(event.data).click();
            event.preventDefault();
            event.stopPropagation();
        }
    };


    registry.register(_);
    return _;
});

// vim: sw=4 expandtab

