/**
 * Copyright 2012-2013 Syslab.com GmbH - JC Brand
 */
define([
    "jquery",
    "pat-registry",
    "pat-base",
    "pat-utils",
    "pat-logger",
    "pat-parser",
    "underscore"
], function($, patterns, Base, utils, logging, Parser, _) {
    var log = logging.getLogger("scroll"),
        parser = new Parser("scroll");
    parser.addArgument("trigger", "click", ["click", "auto"]);
    parser.addArgument("direction", "top", ["top", "left"]);
    parser.addArgument("selector");
    parser.addArgument("offset");

    return Base.extend({
        name: "scroll",
        trigger: ".pat-scroll",
        jquery_plugin: true,

        init: function($el, opts) {
            this.options = parser.parse(this.$el, opts);
            if (this.options.trigger == "auto") {
               this.smoothScroll();
            } else if (this.options.trigger == "click") {
                this.$el.click(function (ev) {
                    ev.preventDefault();
                    this.smoothScroll();
                }.bind(this));
            }
        },

        smoothScroll: function() {
            var scroll = this.options.direction == "top" ? 'scrollTop' : 'scrollLeft',
                $el, options = {};
            if (typeof this.options.offset != "undefined") {
                $el = this.options.selector ? $(this.options.selector) : this.$el;
                options[scroll] = this.options.offset;
            } else {
                $el = $('body');
                options[scroll] = $(this.$el.attr('href')).offset().top;
            }
            $el.animate(options, 500);
        }
    });
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
