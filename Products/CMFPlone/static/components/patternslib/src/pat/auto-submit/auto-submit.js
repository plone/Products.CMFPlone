/**
 * Patterns autosubmit - automatic submission of forms
 *
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012 Simplon B.V. - Wichert Akkerman
 * Copyright 2013 Marko Durkovic
 * Copyright 2014-2015 Syslab.com GmbH - JC Brand 
 */
define([
    "jquery",
    "pat-registry",
    "pat-base",
    "pat-logger",
    "pat-parser",
    "pat-input-change-events",
    "pat-utils"
], function($, registry, Base, logging, Parser, input_change_events, utils) {
    var log = logging.getLogger("autosubmit"),
        parser = new Parser("autosubmit");

    // - 400ms -> 400
    // - 400 -> 400
    // - defocus
    parser.addArgument("delay", "400ms");

    return Base.extend({
        name: "autosubmit",
        trigger: ".pat-autosubmit",
        parser: {
            parse: function($el, opts) {
                var cfg = parser.parse($el, opts);
                if (cfg.delay !== "defocus") {
                    cfg.delay = parseInt(cfg.delay.replace(/[^\d]*/g, ""), 10);
                }
                return cfg;
            }
        },

        init: function() {
            this.options = this.parser.parse(this.$el, arguments[1]);
            input_change_events.setup(this.$el, "autosubmit");
            this.registerListeners();
            this.registerTriggers();
            return this.$el;
        },

        registerListeners: function() {
            this.$el.on("input-change-delayed.pat-autosubmit", this.onInputChange);
            this.registerSubformListeners();
            this.$el.on('patterns-injected', this.registerSubformListeners.bind(this));
        },

        registerSubformListeners: function(ev) {
            /* If there are subforms, we need to listen on them as well, so
             * that only the subform gets submitted if an element inside it
             * changes.
             */
            var $el = typeof ev !== "undefined" ? $(ev.target) : this.$el;
            $el.find(".pat-subform").each(function (idx, el) {
                $(el).on("input-change-delayed.pat-autosubmit", this.onInputChange);
            }.bind(this));
        },

        registerTriggers: function() {
            var isText = this.$el.is("input:text, input[type=search], textarea");
            if (this.options.delay === "defocus" && !isText) {
                log.error("The defocus delay value makes only sense on text input elements.");
                return this.$el;
            }
            if (this.options.delay === "defocus") {
                this.$el.on("input-defocus.pat-autosubmit", function(ev) {
                    $(ev.target).trigger("input-change-delayed");
                });
            } else if (this.options.delay > 0) {
                this.$el.on("input-change.pat-autosubmit", utils.debounce(function(ev) {
                    $(ev.target).trigger("input-change-delayed");
                }, this.options.delay));
            } else {
                this.$el.on("input-change.pat-autosubmit", function(ev) {
                    $(ev.target).trigger("input-change-delayed");
                });
            }
        },

        destroy: function($el) {
            input_change_events.remove($el, "autosubmit");
            if (this.$el.is("form")) {
                this.$el.find(".pat-subform").addBack(this.$el).each(function (idx, el) {
                    $(el).off(".pat-autosubmit");
                });
            } else {
                $el.off(".pat-autosubmit");
            }
        },

        onInputChange: function(ev) {
            ev.stopPropagation();
            $(this).submit();
            log.debug("triggered by " + ev.type);
        }
    });
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
