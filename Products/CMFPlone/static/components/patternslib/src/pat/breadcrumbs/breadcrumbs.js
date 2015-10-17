/**
 * Patterns breadcrumbs - breadcrumb trails
 *
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-registry"
], function($, registry) {
    var _ = {
        name: "breadcrumbs",
        trigger: "nav.pat-breadcrumbs",
        init: function($el, opts) {
            if ($el.length > 1) {
                return $el.map(function() {
                    return _.init($(this), opts);
                });
            }

            // wrap elements in a DIV that will be shifted around
            var $content = $el.children()
                    .wrapAll("<div class='pat-breadcrumbs-content'></div>").parent();

            // shift ctrl
            var $ctrl = $("<span class='button shift'>shift</span>")
                    .prependTo($el);

            var shifted = false,
                shifting = false,
                difference = 0;
            var shifter = function(toggle) {
                return function() {
                    var margin;
                    if (toggle) {
                        margin = shifted ? 0 : difference;
                        $content.animate({"margin-left": margin}, function() {
                            $ctrl.toggleClass("shift-right shift-left");
                            shifted = !shifted;
                        });
                    } else {
                        margin = shifted ? difference : 0;
                        $content.css({"margin-left": margin});
                    }
                };
            };

            var maybeshift = function() {
                // account for other stuff on the same line (100px)
                difference = $el.innerWidth() - $content.width() - 100;

                if (difference < 0) {
                    // we should be shifting
                    if (!shifting) {
                        shifting = true;
                        $el.addClass("shifting");
                        $ctrl.removeClass("shift-right");
                        $ctrl.addClass("shift-left");
                        $ctrl.on("click.pat-breadcrumbs", shifter(true));
                        $ctrl.click();
                    } else {
                        // a shifter that keeps state
                        shifter(false)();
                    }
                } else {
                    // we should not be shifting
                    if (shifting) {
                        $content.animate({"margin-left": 0}, function() {
                            shifted = false;
                            shifting = false;
                            $el.removeClass("shifting");
                            $ctrl.removeClass("shift-left shift-right");
                            $ctrl.off(".pat-breadcrumbs");
                        });
                    }
                }
            };
            $(window).on("resize.pat-breadcrumbs", maybeshift);

            var recalculate = function() {
                // set fixed width on content
                var width = $content.children().toArray().reduce(function(acc, el) {
                    // outerWidth is buggy http://bugs.jquery.com/ticket/8443 so
                    // add a magic buffer value of 5.
                    // XXX: maybe make the buffer configurable.
                    return acc + $(el).outerWidth(true) + 5;
                }, 0);
                $content.width(width);
                maybeshift();
            };
            $el.on("pat-breadcrumbs-changed.pat-breadcrumbs", recalculate);
            recalculate();

            return $el;
        },
        destroy: function($el) {
            $el.off(".pat-breadcrumbs");
        }
    };
    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
