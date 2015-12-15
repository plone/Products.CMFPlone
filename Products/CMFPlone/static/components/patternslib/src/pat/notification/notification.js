/**
 * Patterns notification - Display (self-healing) notifications.
 *
 * Copyright 2013 Marko Durkovic
 */
define([
    "jquery",
    "pat-registry",
    "pat-logger",
    "pat-parser",
    "pat-inject"
], function($, patterns, logger, Parser, inject) {
    var log = logger.getLogger("notification"),
        parser = new Parser("notification");

    parser.addArgument("type", "static", ["static", "banner"]);
    parser.addArgument("healing", "5s");
    parser.addArgument("controls", "icons", ["icons", "buttons", "none"]);
    parser.addArgument("class");

    var _ = {
        name: "notification",
        trigger: ".pat-notification",

        // this is generic functionality and should be moved to lib
        parseUnit: function(value, unit) {
            var unitRe = new RegExp(unit+"$"),
                numericRe = new RegExp("^[0-9.]+");

            if (!(unitRe.test(value))) {
                throw "value " + value + "is not in unit " + unit;
            }

            var mod = value.replace(numericRe, "");
            mod = mod.replace(unitRe, "");

            value = parseFloat(value);
            if (!mod.length) {
                return value;
            }

            var factors = {
                M: 1000000,
                k: 1000,
                m: 0.001,
                u: 0.000001
            };

            return value * factors[mod];
        },

        parseUnitOrOption: function(value, unit, options) {
            if (options.indexOf(value) >= 0) {
                return value;
            }

            return _.parseUnit(value, unit);
        },

        count: 0,

        init: function($el, opts) {
            return $el.each(function() {
                var $el = $(this);

                if ($el.is("a,form")) {
                    _._init_inject($el, opts);
                } else {
                    _._initNotification($el, opts);
                }
                return $el;
            });
        },

        _initNotification: function($el, opts) {
            _.count++;

            var options = parser.parse($el, opts);

            $el = $el.wrap("<div/>").parent()
                .attr("id", "pat-notification-" + _.count)
                .addClass("pat-notification-panel")
                .on("mouseenter.pat-notification", _.onMouseEnter)
                .on("mouseleave.pat-notification", _.onMouseLeave);

            if (options["class"]) {
                $el.addClass(options["class"]);
            }

            if (!Array.isArray(options.controls)) {
                options.controls = [ options.controls ];
            }

            // add close icon if requsted
            if (options.controls.indexOf("icons") >= 0) {
                $el.append("<button type='button' class=.close-panel'>Close</button>");
            }

            // add close button if requested
            if (options.controls.indexOf("buttons") >= 0) {
                $el.append("<div class='button-bar'><button type='button' class='close-panel'>Close</button></div>");
            }

            if ($el.find(".close-panel").length) {
                $el.on("click.pat-notification", ".close-panel", _.onClick);
            } else {
                $el.on("click.pat-notification", _.onClick);
            }

            if (options.type === "banner") {
                var $container = $("#pat-notification-banners");
                if (!$container.length) {
                    $container = $("<div/>").attr("id", "pat-notification-banners").addClass("pat-notification-container").appendTo("body");
                }
                $container.append($el);
            }

            var healing = _.parseUnitOrOption(options.healing, "s", ["persistent"]);

            log.debug("Healing value is", healing);
            $el.data("healing", healing);

            $el.animate({"opacity": 1}, "fast", function() {
                _.initRemoveTimer($el);
            });
        },

        _init_inject: function($el) {
            var inject_opts = {
                target: "#pat-notification-temp"
            };
            $el.on("pat-inject-success.pat-notification", function() {
                var $trigger = $(this),
                    cfg = parser.parse($trigger, { type: "banner"});

                var $el = $("#pat-notification-temp").contents().wrapAll("<div/>")
                    .parent()
                    .addClass("pat-notification");

                if ($trigger.is("a")) {
                    $trigger.after($el);
                } else {
                    $el.prependTo($trigger);
                }
                _._initNotification($el, cfg);

                // XXX: Do this later as inject tries to access its target afterwards.
                // This should be fixed in injection.
                setTimeout(function() {
                    $("#pat-notification-temp").remove();
                }, 0);
            });
            inject.init($el, inject_opts);
        },

        initRemoveTimer: function($el) {
            var healing = $el.data("healing");
            if (healing !== "persistent") {
                clearTimeout($el.data("timer"));
                $el.data("timer", setTimeout(function() {
                    _.remove($el);
                }, healing * 1000));
            }
        },

        onMouseEnter: function() {
            $(this).data("persistent", true);
        },

        onMouseLeave: function() {
            var $this = $(this);

            $this.data("persistent", false);
            _.initRemoveTimer($this);
        },

        onClick: function(event) {
            var $this = $(event.delegateTarget);

            $this.data("persistent", false);
            _.remove($this);
        },

        remove: function($el) {
            if ($el.data("persistent") || $el.data("removing")) {
                return;
            }

            $el.data("removing", true);

            $el.stop(true).animate({"opacity": 0}, {
                step: function() {
                    if ($el.data("persistent")) {
                        // remove the timer and show notification
                        clearTimeout($el.data("timer"));
                        $el.stop(true).animate({"opacity": 1});
                        $el.data("removing", false);
                        return false;
                    }
                },

                complete: function() {
                    var $this = $(this);
                    $this.off(".pat-notification");
                    $this.slideUp("slow", function() {
                        $this.remove();
                    });
                }
            });
        }
    };

    patterns.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
