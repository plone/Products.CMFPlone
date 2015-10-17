/**
 * Patterns subform - scoped submission of form content
 *
 * Copyright 2013 Marko Durkovic
 */
define([
    "jquery",
    "pat-registry",
    "pat-logger",
    "pat-parser",
    "pat-ajax",
    "pat-inject"
], function($, registry, logging, Parser, ajax, inject) {
    var log = logging.getLogger("subform");

    var _ = {
        name: "subform",
        trigger: ".pat-subform",

        init: function($el) {
            return $el.each(function() {
                var $el = $(this);

                $el.submit(_.submit);
                $el.find("button[type=submit]").on("click", _.submitClicked);
                return $el;
            });
        },

        destroy: function($el) {
            $el.off("submit");
        },

        scopedSubmit: function($el) {
            var $form = $el.parents("form"),
                $exclude = $form
                            .find(":input")
                            .filter(function() {
                                return !$(this).is($el.find("*"));
                            });
            // make other controls "unsuccessful"
            log.debug("Hiding unwanted elements from submission.");
            var names = $exclude.map(function() {
                var name = $(this).attr("name");
                return name ? name : 0;
            });
            $exclude.each(function() {
                $(this).attr("name", "");
            });
            if ($el.is(".pat-inject") || $el.is(".pat-modal")) {
                inject.submitSubform($el);
            } else {
                // use the native handler, since there could be event handlers
                // redirecting to inject/ajax.
                $form[0].submit();
            }
            // reenable everything
            log.debug("Restoring previous state.");
            $exclude.each(function(i) {
                if (names[i]) {
                    $(this).attr("name", names[i]);
                }
            });
        },

        submit: function(ev) {
            ev.stopPropagation();

            var $this = $(this),
                $button = $this.find("button[type=submit][formaction]").first();
            if ($button.length) {
                $button.trigger("click");
            } else {
                _.scopedSubmit($this);
            }
        },

        submitClicked: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            ajax.onClickSubmit(ev); // make sure the submitting button is sent with the form

            var $button = $(ev.target),
                $sub = $button.parents(".pat-subform").first(),
                formaction = $button.attr("formaction");

            if (formaction) {
                // override the default action and restore afterwards
                if ($sub.is(".pat-inject")) {
                    var previousValue = $sub.data("pat-inject");
                    $sub.data("pat-inject", inject.extractConfig($sub, {url: formaction}));
                    _.scopedSubmit($sub);
                    $sub.data("pat-inject", previousValue);
                } else if ($sub.is(".pat-modal")) {
                    $sub.data("pat-inject", [$.extend($sub.data("pat-inject")[0], {url: formaction})]);
                    _.scopedSubmit($sub);
                } else {
                    $sub.parents("form").attr("action", formaction);
                    _.scopedSubmit($sub);
                }
            } else {
                _.scopedSubmit($sub);
            }
        }
    };

    registry.register(_);
    return _;
});

// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
