// helper functions to make all input elements
define([
    "jquery",
    "pat-logger"
], function($, logging) {
    var namespace = "input-change-events",
        log = logging.getLogger(namespace);

    var _ = {
        setup: function($el, pat) {
            if (!pat) {
                log.error("The name of the calling pattern has to be set.");
                return;
            }
            // list of patterns that installed input-change-event handlers
            var patterns = $el.data(namespace) || [];
            log.debug("setup handlers for " + pat);

            if (!patterns.length) {
                log.debug("installing handlers");
                _.setupInputHandlers($el);

                $el.on("patterns-injected." + namespace, function(event) {
                    _.setupInputHandlers($(event.target));
                });
            }
            if (patterns.indexOf(pat) === -1) {
                patterns.push(pat);
                $el.data(namespace, patterns);
            }
        },

        setupInputHandlers: function($el) {
            if (!$el.is(":input")) {
                // We've been given an element that is not a form input. We
                // therefore assume that it's a container of form inputs and
                // register handlers for its children.
                $el.findInclusive(":input").each(_.registerHandlersForElement);
            } else {
                // The element itself is an input, se we simply register a
                // handler fot it.
                _.registerHandlersForElement($el);
            }
        },

        registerHandlersForElement: function() {
            var $el = $(this),
                isText = $el.is("input:text, input[type=search], textarea");

            if (isText) {
                if ("oninput" in window) {
                    $el.on("input." + namespace, function() {
                        log.debug("translating input");
                        $el.trigger("input-change");
                    });
                } else {
                    // this is the legacy code path for IE8
                    // Work around buggy placeholder polyfill.
                    if ($el.attr("placeholder")) {
                        $el.on("keyup." + namespace, function() {
                            log.debug("translating keyup");
                            $el.trigger("input-change");
                        });
                    } else {
                        $el.on("propertychange." + namespace, function(ev) {
                            if (ev.originalEvent.propertyName === "value") {
                                log.debug("translating propertychange");
                                $el.trigger("input-change");
                            }
                        });
                    }
                }
            } else {
                $el.on("change." + namespace, function() {
                    log.debug("translating change");
                    $el.trigger("input-change");
                });
            }

            $el.on("blur", function() {
                $el.trigger("input-defocus");
            });
        },

        remove: function($el, pat) {
            var patterns = $el.data(namespace) || [];
            if (patterns.indexOf(pat) === -1) {
                log.warn("input-change-events were never installed for " + pat);
            } else {
                patterns = patterns.filter(function(e){return e!==pat;});
                if (patterns.length) {
                    $el.data(namespace, patterns);
                } else {
                    log.debug("remove handlers");
                    $el.removeData(namespace);
                    $el.find(":input").off("." + namespace);
                    $el.off("." + namespace);
                }
            }
        }
    };
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
