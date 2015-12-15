/**
 * Patterns depends - show/hide/disable content based on form status
 *
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012-2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "pat-registry",
    "pat-base",
    "pat-utils",
    "pat-logger",
    "pat-dependshandler",
    "pat-parser"
], function($, patterns, Base, utils, logging, DependsHandler, Parser) {
    var log = logging.getLogger("depends"),
        parser = new Parser("depends");

    parser.addArgument("condition");
    parser.addArgument("action", "show", ["show", "enable", "both"]);
    parser.addArgument("transition", "none", ["none", "css", "fade", "slide"]);
    parser.addArgument("effect-duration", "fast");
    parser.addArgument("effect-easing", "swing");

    return Base.extend({
        name: "depends",
        trigger: ".pat-depends",
        jquery_plugin: true,

        transitions: {
            none: {hide: "hide", show: "show"},
            fade: {hide: "fadeOut", show: "fadeIn"},
            slide: {hide: "slideUp", show: "slideDown"}
        },

        init: function($el, opts) {
            var slave = this.$el[0],
                options = parser.parse(this.$el, opts),
                handler, state;
            this.$modal = this.$el.parents(".pat-modal");

            try {
                handler=new DependsHandler(this.$el, options.condition);
            } catch (e) {
                log.error("Invalid condition: " + e.message, slave);
                return;
            }

            state=handler.evaluate();
            switch (options.action) {
                case "show":
                    if (state)
                        this.show();
                    else
                        this.hide();
                    break;
                case "enable":
                    if (state)
                        this.enable();
                    else
                        this.disable();
                    break;
                case "both":
                    if (state) {
                        this.show();
                        this.enable();
                    } else {
                        this.hide();
                        this.disable();
                    }
                    break;
            }

            var data = {handler: handler,
                        options: options,
                        slave: slave};

            var that = this;
            handler.getAllInputs().each(function(idx, input) {
                if (input.form) {
                    var $form = $(input.form);
                    var slaves = $form.data("patDepends.slaves");
                    if (!slaves) {
                        slaves=[data];
                        $form.on("reset.pat-depends", that.onReset);
                    } else if (slaves.indexOf(data)===-1)
                        slaves.push(data);
                    $form.data("patDepends.slaves", slaves);
                }
                $(input).on("change.pat-depends", null, data, this.onChange.bind(this));
                $(input).on("keyup.pat-depends", null, data, this.onChange.bind(this));
            }.bind(this));
        },

        onReset: function(event) {
            var slaves = $(event.target).data("patDepends.slaves"),
                i;

            setTimeout(function() {
                for (i=0; i<slaves.length; i++) {
                    event.data=slaves[i];
                    this.onChange(event);
                }
            }.bind(this), 50);
        },

        updateModal: function () {
            /* If we're in a modal, make sure that it gets resized.
             */
            if (this.$modal.length) {
                $(document).trigger("pat-update", {pattern: "depends"});
            }
        },

        show: function () {
            this.$el.show();
            this.updateModal();
        },

        hide: function () {
            this.$el.hide();
            this.updateModal();
        },

        enable: function() {
            if (this.$el.is(":input"))
                this.$el[0].disabled=null;
            else if (this.$el.is("a"))
                this.$el.off("click.patternDepends");
            else if (this.$el.hasClass("pat-autosuggest")) {
                this.$el.findInclusive("input.pat-autosuggest").trigger("pat-update", {
                    pattern: "depends",
                    enabled: true
                });
            }
            this.$el.removeClass("disabled");
        },

        disable: function() {
            if (this.$el.is(":input"))
                this.$el[0].disabled="disabled";
            else if (this.$el.is("a"))
                this.$el.on("click.patternDepends", this.blockDefault);
            else if (this.$el.hasClass("pat-autosuggest")) {
                this.$el.findInclusive("input.pat-autosuggest").trigger("pat-update", {
                    pattern: "depends",
                    enabled: false
                });
            }
            this.$el.addClass("disabled");
        },

        onChange: function(event) {
            var handler = event.data.handler,
                options = event.data.options,
                slave = event.data.slave,
                $slave = $(slave),
                state = handler.evaluate();

            switch (options.action) {
                case "show":
                    utils.hideOrShow($slave, state, options, this.name);
                    this.updateModal();
                    break;
                case "enable":
                    if (state)
                        this.enable();
                    else
                        this.disable();
                    break;
                case "both":
                    utils.hideOrShow($slave, state, options, this.name);
                    this.updateModal();
                    if (state)
                        this.enable();
                    else
                        this.disable();
                    break;
            }
        },

        blockDefault: function(event) {
            event.preventDefault();
        }
    });
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
